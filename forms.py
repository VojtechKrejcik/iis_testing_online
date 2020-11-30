from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, IntegerField, Form
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange


class AddUserForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=20)])
    status = SelectField('Status', choices=["admin","profesor","asistent", "student"])
    submit = SubmitField('Create account')

class ChangeEmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    confirm_email = PasswordField('Confirm Email', validators=[DataRequired(), EqualTo('email')])
    submit = SubmitField('Change')

class ChangeNameForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Change')

class ChangePasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change')

class TestConfigForm(Form):
    name = StringField('Test Name',validators=[DataRequired(),Length(min=3)])
    start_date = DateField('Start Date', format='%d/%m/%Y',description="dd/mm/yy")
    end_date = DateField('End Date', format='%d/%m/%Y')
    create = SubmitField('Create test')
    update = SubmitField('Update test')
    cancel = SubmitField('cancel')
    add_full = SubmitField('Add fulltext question')
    add_num = SubmitField('Add number question')
    add_abc = SubmitField('Add abcd question')

class FullTextQuestionForm(Form):
    #TODO: Add immage support
    question = StringField('Question', validators=[DataRequired()])
    value = IntegerField('Point value', validators=[DataRequired(),NumberRange(min=1)])
    create = SubmitField('Create question')