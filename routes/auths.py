from extensions import db, mail
from flask import render_template, redirect, request, flash, url_for, Blueprint
from flask_login import current_user
from form import LoginForm, RegistrationForm, ResetForm, SubmitToken, UpdatePasswordForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user
from models import User
from flask_mail import Message
import random


auth = Blueprint("auth", __name__)


token_digit = random.randint(0000, 9999)


# The view function for the login
@auth.route('/login/', methods=['GET', 'POST'])
def login():
    # If the logged-in user is trying to access the login url, redirects the user to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('view.home'))
    # Assign the LoginForm created in the form.py file to a variable 'form'
    form = LoginForm()
    # If the form gets validated on submit
    if form.validate_on_submit():
        # Query the User model and assign the queried data to the variable 'user'
        user = User.query.filter_by(email=form.email.data).first()
        # Check if the user exist in the database and if the inputted password is same with the one attached to the user on the database
        if user and check_password_hash(user.password, form.password.data):
            # If the check passed, login the user and flash a message to the user when redirected to the homepage
            login_user(user, remember=form.remember.data)
            flash('Login Successful', 'success')
            return redirect(url_for('view.home', id=user.id))
        else:
            # If the check failed, flash a message to the user while still on the same page
            flash('Check your Email / Password', 'danger')
            return render_template('login.html', form=form)
    # This for a get request, if u click on the link that leads to the login page, this return statement get called upon
    return render_template('login.html', form=form)


# The view function for Register
@auth.route('/register/', methods=['GET', 'POST'])
def register():
    # If the logged-in user is trying to access the login url, redirects the user to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('view.home'))
    # Assign the RegistrationForm created in the form.py file to a variable 'form'
    form = RegistrationForm()
    # If the request is a post request and the form doesn't get validated, redirect the user to that same page
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('register.html', form=form)
        # If the form gets validated on submit
        else:
            # Check if the username already exist
            user = User.query.filter_by(username=form.username.data.lower()).first()
            # if the username exist
            if user:
                # Flash this message to the user and redirect the user to that same page
                flash('User with this username already exist', category='danger')
                return redirect(url_for('auth.register'))

            # Check if email exist
            existing_email = User.query.filter_by(email=form.email.data.lower()).first()
            # if the email exist
            if existing_email:
                # Flash this message to the user and redirect the user to that same page
                flash('User with this email already exist', category='danger')
                return redirect(url_for('auth.register'))
            # If both the username and email doesn't exist in the database, hash the password
            password_hash = generate_password_hash(form.password.data)

            # to check if the password is the mixture of uppercase, lowercase and a number at least
            letters = set(form.password.data)
            mixed = (
                    any(letter.islower() for letter in letters)
                    and any(letter.isupper() for letter in letters)
                    and any(letter.isdigit() for letter in letters)
            )
            if not mixed:
                flash(
                    "Password should contain at least an uppercase, lowercase and a number",
                    "info",
                )
                return redirect(url_for("auth.register"))
            # Create an instance of the User model, passing all the value of each column to the model and assign it to a
            # variable 'new_user'
            new_user = User(first_name=form.firstname.data.lower(), last_name=form.lastname.data.lower(), username=form.username.data.lower(),
                            email=form.email.data.lower(), password=password_hash)
            # Add the 'new_user'
            db.session.add(new_user)
            # Commit it to the database, the details gets sent to the database directly
            db.session.commit()
            # After committing, flash this message to the user and redirect the user to the login page so he/she can log in
            # into the newly created account
            flash('Registration Successful, You can now Login', category='success')
            return redirect(url_for('auth.login'))
    # This for a get request, if u click on the link that leads to the register page, this return statement get called upon
    return render_template('register.html', form=form)


# View function for the logout
@auth.route('/logout/')
@login_required
def logout():
    # Logout_user() log out the user, it was imported from flask_login
    logout_user()
    # After a successful logout, redirect the user to the homepage and flash this success message to the user
    flash('You\'ve been logged out successfully', 'success')
    return redirect(url_for('view.home'))


@auth.route('/reset-token/', methods=['GET', 'POST'])
def reset():
    form = ResetForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('reset.html', form=form)
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User with this email doesn\'t exist', 'danger')
            return redirect(url_for('auth.reset'))
        try:
            msg = Message(
                "Password Reset Token from myBlog",
                sender='myBlog@admin.com',
                recipients=[
                    email
                ],
                )
            msg.body = f"\nToken to reset your password: {token_digit}"
            mail.send(msg)
            url_token = random.randint(00, 99)
            flash(f"Token Sent to {email}", "success")
            return redirect(url_for("auth.token", email=email, url_token=url_token))
        except:
            flash("Data connection is off", 'info')
            return redirect(url_for('auth.reset'))
    return render_template('reset.html', form=form)


@auth.route('/token/<int:url_token>/<string:email>/', methods=['GET', 'POST'])
def token(email, url_token):
    form = SubmitToken()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('token.html', form=form)
        token_input = form.token.data
        if token_input == token_digit:
            context = {
                'email': email,
                'url_token': url_token,
                'token_dig': token_digit
            }
            return redirect(url_for('auth.updatepassword', **context))
    return render_template('token.html', form=form)


@auth.route('/update-password/<int:url_token>/<string:email>/<int:token_dig>/', methods=['GET', 'POST'])
def updatepassword(email, url_token, token_dig):
    form = UpdatePasswordForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('passreset.html', form=form)
        user = User.query.filter_by(email=email).first()
        password_hash = generate_password_hash(form.newpassword.data)
        # to check if the password is the mixture of uppercase, lowercase and a number at least
        letters = set(form.newpassword.data)
        mixed = (
                any(letter.islower() for letter in letters)
                and any(letter.isupper() for letter in letters)
                and any(letter.isdigit() for letter in letters)
        )
        if not mixed:
            flash(
                "Password should contain at least an uppercase, lowercase and a number",
                "danger",
            )
            return redirect(url_for("auth.updatepassword", email=email, url_token=url_token, token_dig=token_dig))
        user.password = password_hash
        db.session.commit()
        flash('Password changed, you can now login', 'success')
        return redirect(url_for('auth.login'))
    return render_template('passreset.html', form=form)
