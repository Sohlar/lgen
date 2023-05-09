from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    subscription = db.Column(db.String(10))
    tokens = db.Column(db.Integer, default=30)
    search_history = db.relationship('SearchHistory', back_populates='user', lazy='dynamic')
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    query = db.Column(db.String(256))
    engine = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user = db.relationship('User', back_populates='search_history')
    results = db.relationship('SearchResult', back_populates='search_history', lazy='dynamic')

class SearchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_history_id = db.Column(db.Integer, db.ForeignKey('search_history.id'))
    url = db.Column(db.String(256))

    search_history = db.relationship('SearchHistory', back_populates='results')
    contact_info = db.relationship('ContactInfo', back_populates='search_result', uselist=False)

class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_result_id = db.Column(db.Integer, db.ForeignKey('search_result.id'))
    emails = db.relationship('Email', back_populates='contact_info')
    phones = db.relationship('Phone', back_populates='contact_info')

    search_result = db.relationship('SearchResult', back_populates='contact_info')

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_info_id = db.Column(db.Integer, db.ForeignKey('contact_info.id'))
    email = db.Column(db.String(256))

    contact_info = db.relationship('ContactInfo', back_populates='emails')

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_info_id = db.Column(db.Integer, db.ForeignKey('contact_info.id'))
    phone = db.Column(db.String(64))

    contact_info = db.relationship('ContactInfo', back_populates='phones')