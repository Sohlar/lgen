from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class TokenPurchaseForm(FlaskForm):
    num_tokens = IntegerField('Number of tokens', validators=[DataRequired(), NumberRange(min=1)])
    stripe_tokens = StringField('Stripe Token', validators=[DataRequired()])
    submit = SubmitField('Purchase')