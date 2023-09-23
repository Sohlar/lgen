from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    IntegerField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Email,
    EqualTo,
    ValidationError,
)
from app.main.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class TokenPurchaseForm(FlaskForm):
    num_tokens = StringField(
        "Number of tokens", validators=[DataRequired(), NumberRange(min=10)]
    )
    card_details = StringField("Card Details", validators=[DataRequired()])
    cost = StringField("Cost", render_kw={'readonly': True})
    submit = SubmitField("Purchase")




class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class SearchForm(FlaskForm):
    query = StringField("Query", validators=[DataRequired()])
    # engine = SelectField('Engine', choices=[('engine1', 'Engine 1'), ('engine2', 'Engine 2')], validators=[DataRequired()])
    desired_results = IntegerField("Tokens", validators=[DataRequired()], default=None)
    location = StringField("Location", validators=[DataRequired()], default=None)
    radius = IntegerField("Radius", validators=[DataRequired()], default=None)
    submit = SubmitField("Search")


class AddTokensForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    tokens = IntegerField("Tokens", validators=[DataRequired()])
    submit = SubmitField("Add Tokens")


class CallToActionForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")
