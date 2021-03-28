from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField, PasswordField
from wtforms.validators import InputRequired


class EditForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    subject = SelectField('Subject', validate_choice=False)
    preview = StringField('Preview', validators=[InputRequired()])
    contents = TextAreaField('Contents', validators=[InputRequired()])
    is_featured = BooleanField('Featured')
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Submit')


class SubjectForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Submit')
