from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
from app.main import main_bp
from app.main.forms import LoginForm
from app.main.models import User
from app import db
from services.search_engines import GoogleSearch, BingSearch
from services.search_engine_factory import SearchEngineFactory
from services.utils import search_and_record, drop_non_results

@main_bp.route('/')
@main_bp.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')
        engine = request.form.get('engine')

        search_engine = SearchEngineFactory().create_search_engine(engine)
        results = search_and_record(search_engine, query)


    return render_template('index.html', results=results, title='Home')

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
