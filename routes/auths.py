from extensions import db
from flask import render_template, redirect, request, flash, url_for, Blueprint
from flask_login import current_user
from form import LoginForm, RegistrationForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user
from models import User


auth = Blueprint("auth", __name__)


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
