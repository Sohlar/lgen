from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main_bp
from app.main.forms import LoginForm, TokenPurchaseForm
from app.main.models import User
from app import db
from app.services.search_engines import GoogleSearch, BingSearch
from app.services.search_engine_factory import SearchEngineFactory
from app.services.utils import search_and_record, drop_non_results

import stripe


@main_bp.route('/')
@main_bp.route('/index', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        engine = request.form.get('engine')
        desired_results = int(request.form.get('desired results'))

        #calculate the cost of the search
        cost = desired_results * TOKENS_PER_RESULT

        #check if user has enough
        if current_user.tokens >= cost:
            current_user.tokens -= cost
            db.session.commit()

            # Create a search engine using the factory
            search_engine = SearchEngineFactory().create_search_engine(engine)
            # Perform the search and record the results
            results = search_and_record(search_engine, query)
            return render_template('index.html', results=results, title='Home')

        else:
            flash('Not enough tokens. Please purchase more tokens to continue.')

    #Process the results and render them in the template
    return render_template('index.html', title='Home')

@main_bp.route('/buy_tokens', methods=['GET', 'POST'])
@login_required
def buy_tokens():
    form = TokenPurchaseForm()
    if form.validate_on_submit():
        #calc token cost
        
        num_tokens = form.num_tokens.data * 110
        user = current_user
        
        success = False
        try:
            charge = stripe.Charge.create(
                amount=num_tokens,
                currency='usd',
                source=form.stripe_token.data,
                description=f'Token purchase for {current_user.username}'
            )

            #Update user's token balance
            current_user.tokens += form.num_tokens.data
            db.session.commit()

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
    return render_template('login.html', title='Sign In', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


