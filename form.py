from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    firstname = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    lastname = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=30)])
    post_content = TextAreaField('Post Content', validators=[DataRequired()])
    submit = SubmitField('Update Post')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=30)])
    image = FileField(validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    post_content = TextAreaField('Post Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class ContactForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class DmForm(FlaskForm):
    dm = StringField('Dm', validators=[DataRequired()])


class PhotoForm(FlaskForm):
    image = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
