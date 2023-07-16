from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main_bp
from app.main.forms import LoginForm, TokenPurchaseForm, RegistrationForm, CallToActionForm
from app.main.models import User, SearchHistory, SearchResult, ContactInfo, Email, Phone
from app.extensions import db, celery
from app.services.search_engines import GoogleSearch
from app.services.search_engine_factory import SearchEngineFactory
from app.services.utils import search_and_record, drop_non_results
from app.main.forms import TokenPurchaseForm, SearchForm, AddTokensForm
from .helpers import get_profile_css_class
from datetime import datetime
from flask_mail import Mail, Message 
import time
from app.extensions import celery
from .tasks import search_engine_task



import stripe
TOKENS_PER_RESULT = 1

@main_bp.route('/')
@main_bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Handles requests for the application's home page.

    A GET request returns the home page with a blank SearchForm.

    A POST request (i.e., when the SearchForm is submitted) begins the process of a search request. 
    This involves:
    - Forming the search query based on form inputs.
    - Calculating the cost of the search in tokens.
    - Checking if the current user is authenticated. If not, they're redirected to the register page.
    - If the user is authenticated, it checks if they have enough tokens for the search.
        - If they don't, a flash message prompts them to purchase more tokens.
        - If they do, tokens are deducted from their account, the search query is saved to their 
          search history, and a search task is enqueued with Celery. The user is also notified that 
          their search request is processing.

    :return: The home page with either a blank or filled-in SearchForm, and possibly a flash message 
             (if a search request was submitted).
    """
    form = SearchForm()
    results = []
    flash('Do not navigate while search is running.', 'danger')
    if form.validate_on_submit():
        my_query = f"{form.query.data}" 
        if form.location.data:
            my_query += (f" {form.location.data}")
        if form.radius.data:
            my_query += (f" within {form.radius.data} miles")
        # Currently only using Bing, but will combine all search together concurrent
        my_engine = 'google'
        desired_results = form.desired_results.data
        #calculate the cost of the search
        cost = TOKENS_PER_RESULT * int(desired_results)
        if not current_user.is_authenticated:
            return redirect(url_for('main.register'))
        if current_user.is_authenticated and current_user.tokens is not None:
            #print('User is auth and not None\n')
        #check if user has enough
            if current_user.tokens >= cost:
                #print('User has enough Tokens \n')
                current_user.tokens -= cost
                # Save search history
                search_history = SearchHistory(user_id=current_user.id, query=my_query, engine=my_engine, timestamp=datetime.utcnow())
                db.session.add(search_history)
                db.session.commit()
                # Create a search engine using the factory
                #search_engine = SearchEngineFactory().create_search_engine(my_engine)
                # Perform the search and record the results
                search_engine_task.delay('google', search_history.id, my_query, cost)
                #search_engine_task('google', search_history.id, my_query, cost)
            else:
                flash('Not enough tokens. Please purchase more tokens to continue.')
    return render_template('index3.html', title='Home', form=form)


@main_bp.route('/search_history', methods=['GET'])
@login_required
def search_history():
    search_history = sorted(current_user.search_history, key=lambda x: x.timestamp, reverse=True)
    return render_template('search_history.html', search_history=search_history, title='Search History', get_profile_css_class=get_profile_css_class)

@main_bp.route('/view_search/<int:search_history_id>', methods=['GET'])
@login_required
def view_search(search_history_id):
    search_history_item = SearchHistory.query.get_or_404(search_history_id)
    if search_history_item.user_id != current_user.id:
        abort(403)
    search_results = search_history_item.results.all()
    return render_template('view_search.html', search_history_item=search_history_item, title='View Search', get_profile_css_class=get_profile_css_class)

@main_bp.route('/profile.html', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html', title='Profile', user=current_user)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        #print("User added to the database")
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


@main_bp.route('/buy_tokens', methods=['GET', 'POST'])
@login_required
def buy_tokens():
    """
    Process the purchase of tokens by the user using the TokenPurchaseForm. Validates the form data,
    creates a Stripe charge for the token purchase, updates the user's token balance in the
    database, and returns an appropriate response depending on the success of the operation.

    :return: A JSON response indicating the status ('error' or 'success') and a message
             describing the result of the operation.
    """
    form = TokenPurchaseForm()

    #Check if form is submitted and vlidated
    if form.validate_on_submit():
        #calc token cost  
        num_tokens = form.num_tokens.data * 110
        user = current_user
        
        #Variable to track payment success
        success = False
        try:
            #Create a stripe charge for the token purchase
            create_stripe_charge(num_tokens, form.stripe_token.data, user.username)

            #Update user's token balance
            current_user.tokens += form.num_tokens.data
            db.session.commit()

            #Show success message
            flash(f'Success! You have purchased {form.num_tokens.data} tokens.', 'success')
            success = True
        
        except stripe.error.CardError as e:
            return jsonify({'status': 'error', 'message': f'Error occurred while processing the payment: {str(e)}'})

        if success:
            user.tokens += num_tokens
            db.session.commit()
            return jsonify({'status': 'error', 'message': 'Success'})
    return render_template('buy_tokens.html', title='Buy Tokens', form=form)


def create_stripe_charge(amount, token, username):
    stripe.Charge.create(
        amount=amount,
        currency='usd',
        source=token,
        description=f'Token purchase for {username}'
    )


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', title='Sign In', form=form, get_profile_css_class=get_profile_css_class)

@main_bp.route('/logout')
@login_required
def logout():
    flash('Successfully logged out')
    logout_user()
    return redirect(url_for('main.index'))


@main_bp.route('/admin/add_tokens', methods=['GET','POST'])
@login_required
def add_tokens():
    if not current_user.is_admin:
        abort(403)
    
    form = AddTokensForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.tokens += form.tokens.data
            db.session.commit()
            flash(f'{form.tokens.data} tokens added')
        else:
            flash('User not found', 'danger')
        return redirect(url_for('main.add_tokens'))
    return render_template('add_tokens.html', form=form)

@main_bp.route('/send_mail', methods=["POST"])
def mail_results():
    search_result_id = request.json.get('history_id')
    msg = Message("Search Result", recipients=["recipient@example.com"])  # recipient's email
    msg.body = "Here is your search result: \n" + str(search_result_id)
    Mail.send(msg)
    return 'Email sent!'
