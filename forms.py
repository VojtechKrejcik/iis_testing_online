from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class AddUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=20)])
    status = SelectField('Status', choices=["admin","profesor","asistent", "student"])
    submit = SubmitField('Create account')

class ChangeEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    confirm_email = PasswordField('Confirm Email', validators=[DataRequired(), EqualTo('email')])
    submit = SubmitField('Change')

class ChangeNameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Change')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change')