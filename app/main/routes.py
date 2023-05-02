from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main_bp
from app.main.forms import LoginForm, TokenPurchaseForm, RegistrationForm
from app.main.models import User, SearchHistory, SearchResult
from app import db
from app.services.search_engines import GoogleSearch, BingSearch
from app.services.search_engine_factory import SearchEngineFactory
from app.services.utils import search_and_record, drop_non_results
from app.main.forms import TokenPurchaseForm
from .helpers import get_profile_css_class
from datetime import datetime

""" import stripe
 """
TOKENS_PER_RESULT = 100


@main_bp.route('/')
@main_bp.route('/index', methods=['GET', 'POST'])
def index():
    form = TokenPurchaseForm()
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        engine = request.form.get('engine')
        desired_results = request.form.get('desired results')

        #calculate the cost of the search
        cost = TOKENS_PER_RESULT

        #check if user has enough
        if current_user.tokens >= cost:
            current_user.tokens -= cost
            db.session.commit()

            # Save search history
            search_history = SearchHistory(user_id=current_user.id, query=query, engine=engine, timestamp=datetime.utcnow())
            db.session.add(search_history)
            db.session.commit()

            # Create a search engine using the factory
            search_engine = SearchEngineFactory().create_search_engine(engine)
            # Perform the search and record the results
            results = search_and_record(search_engine, query)
            for result in results:
                search_result = SearchResult(search_history_id=search_history.id, email=search_history.email, phone=search_history.phone, url=result.url)
                db.session.add(search_result)
            db.session.commit()

            return render_template('index.html', results=results, title='Home', get_profile_css_class=get_profile_css_class)
        else:
            flash('Not enough tokens. Please purchase more tokens to continue.')

    #Process the results and render them in the template
    return render_template('index.html', title='Home', form=form, get_profile_css_class=get_profile_css_class)

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
        print(form.errors)
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        print("User added to the database")
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
            charge = stripe.Charge.create(
                amount=num_tokens,
                currency='usd',
                source=form.stripe_token.data,
                description=f'Token purchase for {current_user.username}'
            )

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
    return jsonify({'status': 'error', 'message': 'Invalid form submission'})

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


