# The imported classes, functions nd object from the dependencies for this project
import random
from flask import Flask, render_template, url_for, request, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
# Importing the created Forms using WTForms from the form.py
from form import RegistrationForm, LoginForm, UpdateForm, PostForm, ContactForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required, UserMixin, LoginManager
from datetime import datetime
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

# Instantiate the Flask imported from flask
app = Flask(__name__)

# The configuration for the URI of the database, the myblog.db is the name of this project's database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'myblog.db')
# The configuration for the track modification
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# The configuration to set up a secret key to strengthen the security of your database
app.config["SECRET_KEY"] = '026b0eb800ec2934fb5cf2e7'

# Instantiate the SQLAlchemy to inherit from flask instantiation 'app'
db = SQLAlchemy(app)
# Initialize the database
db.init_app(app)

# Create an instance of the login manager to inherit from the flask instantiation 'app'
login_manager = LoginManager(app)


# creating the User table in the database
class User(db.Model, UserMixin):
    # The id of the table is unique and increases serially as new content get committed to the database
    id = db.Column(db.Integer, primary_key=True)
    # The first name column in the User table in the database, we don't want this column to be empty, hence setting the nullable to false
    first_name = db.Column(db.String(50), nullable=False)
    # The last name column in the User table in the database, we don't want this column to be empty, hence setting the nullable to false
    last_name = db.Column(db.String(50), nullable=False)
    # The username column in the User table in the database, we don't want this column to be empty, hence setting the nullable to false,
    # we also don't want a two or more users to have the same username, that resulted to setting the unique to be True
    username = db.Column(db.String(20), unique=True, nullable=False)
    # The email column in the User table in the database, we don't want this column to be empty, hence setting the nullable to false,
    # we also don't want a two or more users to have the same email, that resulted to setting the unique to be True
    email = db.Column(db.String(70), unique=True, nullable=False)
    # The password column in the User table in the database, we don't want this column to be empty, hence setting the nullable to false,
    password = db.Column(db.String(60), nullable=False)
    # This is not a column in the database, it's a relationship that binds the user table to the post table,
    # the backref is used to access the user table using a post
    # For example, to get the username of the user of a post, you use the post.author.username to access the username of tha user
    posts = db.relationship('Post', backref='author', lazy=True)

    # Define a representation with two attribute 'username' and 'email'
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# creating the Post table in the database
class Post(db.Model, UserMixin):
    # The id of the table is unique and increases serially as new content get committed to the database
    id = db.Column(db.Integer, primary_key=True)
    # The title column in the Post table in the database, we don't want this column to be empty, hence setting the nullable to false
    title = db.Column(db.String(100), nullable=False)
    # The date and time column for each post, the default value is set to be the current time at which a post is being committed to the database
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # The content column in the Post table in the database, we don't want this column to be empty, hence setting the nullable to false
    content = db.Column(db.Text, nullable=False)
    # This column is used to access the user of a particular post, it takes the id of the user of the post
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a representation with two attribute 'title' and 'date_posted'
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# creating the Contact table in the database
class Contact(db.Model, UserMixin):
    # The id of the table is unique and increases serially as new content get committed to the database
    id = db.Column(db.Integer, primary_key=True)
    # The full name column in the Contact table in the database, we don't want this column to be empty, hence setting the nullable to false
    full_name = db.Column(db.String(50), nullable=False)
    # The email column in the Contact table in the database, we don't want this column to be empty, hence setting the nullable to false
    email = db.Column(db.String(70), nullable=False)
    # The message column in the Contact table in the database, we don't want this column to be empty, hence setting the nullable to false
    message = db.Column(db.Text, nullable=False)
    # The date and time column for each message sent, the default value is set to be the current time at which the message is being committed to the database
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Define a representation
    def __repr__(self):
        return f"Post('{self.full_name}', '{self.email}')"


# The decorator that loads the user using the user's id
@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


# If the user isn't logged in and tries to access a login required route, this decorator allows the page to
# redirect page to the homepage
@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('Login to access this page', category='info')
    return redirect(url_for('login'))


# View function for the home page
@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()        # This get all the post in the post table in the database
    random.shuffle(posts)           # Shuffles the post randomly
    return render_template('home.html', posts=posts)    # and displays it randomly in the homepage whenever a refresh is done in the homepage


# The view function for the login
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # If the logged-in user is trying to access the login url, redirects the user to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
            return redirect(url_for('home', id=user.id))
        else:
            # If the check failed, flash a message to the user while still on the same page
            flash('Check your Email / Password', 'danger')
            return render_template('login.html', form=form)
    # This for a get request, if u click on the link that leads to the login page, this return statement get called upon
    return render_template('login.html', form=form)


# The view function for Register
@app.route('/register/', methods=['GET', 'POST'])
def register():
    # If the logged-in user is trying to access the login url, redirects the user to the homepage
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Assign the RegistrationForm created in the form.py file to a variable 'form'
    form = RegistrationForm()
    # If the request is a post request and the form doesn't get validated, redirect the user to that same page
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('register.html', form=form)
        # If the form gets validated on submit
        else:
            # Check if the username already exist
            user = User.query.filter_by(username=form.username.data).first()
            # if the username exist
            if user:
                # Flash this message to the user and redirect the user to that same page
                flash('User with this username already exist', category='danger')
                return redirect(url_for('register'))

            # Check if email exist
            existing_email = User.query.filter_by(email=form.email.data).first()
            # if the email exist
            if existing_email:
                # Flash this message to the user and redirect the user to that same page
                flash('User with this email already exist', category='danger')
                return redirect(url_for('register'))
            # If both the username and email doesn't exist in the database, hash the password
            password_hash = generate_password_hash(form.password.data)
            # Create an instance of the User model, passing all the value of each column to the model and assign it to a
            # variable 'new_user'
            new_user = User(first_name=form.firstname.data, last_name=form.lastname.data, username=form.username.data,
                            email=form.email.data, password=password_hash)
            # Add the 'new_user'
            db.session.add(new_user)
            # Commit it to the database, the details gets sent to the database directly
            db.session.commit()
            # After committing, flash this message to the user and redirect the user to the login page so he/she can log in
            # into the newly created account
            flash('Registration Successful, You can now Login', category='success')
            return redirect(url_for('login'))
    # This for a get request, if u click on the link that leads to the register page, this return statement get called upon
    return render_template('register.html', form=form)


# View function for account page, where you can create your post
@app.route("/account/", methods=['GET', 'POST'])
# The login_required decorator indicates that this route can only be accessed when signed in
@login_required
def account():
    # Assign the PostForm created in the form.py file to a variable 'form'
    form = PostForm()
    # If the form gets validated on submit
    if form.validate_on_submit():
        # Assign the data from the title field to a variable 'title'
        title = form.title.data
        # Assign the data from the post content field to a variable 'post_content'
        post_content = form.post_content.data
        # Create an instance of the Post model
        post = Post(title=title, content=post_content, author=current_user)
        # Add the datas to the Post table in the database
        db.session.add(post)
        # Commit
        db.session.commit()
        # Flash this message to the user and redirect the user to that same page where the data gets displayed on the screen
        flash('Posted!', 'success')
        return redirect(url_for('account', id=id))
    # This for a get request, if u click on the link that leads to the account page, this return statement get called upon
    return render_template('account.html', form=form, user=current_user)


# View function for update post
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
# The login_required decorator indicates that this route can only be accessed when signed in
@login_required
def update_post(post_id):
    # Assign the UpdateForm created in the form.py file to a variable 'form'
    form = UpdateForm()
    # Query a particular post from the Post table from the database
    post = Post.query.get_or_404(post_id)
    # If the user who created the post is not same with the current logged-in user, abort the process
    if post.author != current_user:
        abort(403)
    # If the request is a post method and the form gets validated on submit
    if request.method == 'POST':
        if form.validate_on_submit():
            # title of the post from database should be updated with the new(if True or False) title from the title field from the update form
            post.title = form.title.data
            # content of the post from database should be updated with the new(if True or False) title from the title field from the update form
            post.content = form.post_content.data
            # After the update, commit the changes to the database
            db.session.commit()
            # then redirect the user to the account page and flash the user a message
            flash('Your post has been updated!', 'success')
            return redirect(url_for('account', post_id=post.id))
    # For the get request, if the button that leads to the update page is being clicked, then redirect the user to the update page
    # then update the empty the value of both the title and content field with the queried data from database
    form.title.data = post.title
    form.post_content.data = post.content
    return render_template('update.html',
                           form=form)


# View function for display page, the page that displays a post when the title of the gets clicked
@app.route('/display/<int:blog_id>')
def display_post(blog_id):
    # Query from the database the details of the redirected post with the post id and render he details on the display page
    post = Post.query.filter_by(id=blog_id).first()
    return render_template('display.html', post=post, user=current_user)


# View function for contact
@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    # Assign the ContactForm created in the form.py file to a variable 'form'
    form = ContactForm()
    # If the request is a post method
    if request.method == 'POST':
        # Assign the data from the full name field to a variable 'fullname'
        fullname = form.fullname.data
        # Assign the data from the email field to a variable 'email'
        email = form.email.data
        # Assign the data from the message field to a variable 'message'
        message = form.message.data
        # If a user is logged-in
        if current_user.is_authenticated:
            # If the message field is not empty
            if message:
                # Create an instance for the Contact model,
                # set the fullname column to be the current_user's firstname and lastname (concatenation helped in getting this done)
                # also set the email column to be the current_user's email, then get the message data from the user
                # This is done so the current user don't have to input his/her email address or full name since we have that already in the database
                send_contact = Contact(full_name=current_user.first_name + ' ' + current_user.last_name, email=current_user.email, message=message)
                # Add the details
                db.session.add(send_contact)
                # Commit and send the details to the contact table in the database
                db.session.commit()
                # After sending, redirect the user to that same page and flash him/her a success message
                flash('Message sent', 'success')
                return redirect(url_for('contact'))
        # If the user is not logged-in
        # This make sure the fullname, email and message fields aren't empty, if the fields are not empty
        if fullname and email and message:
            # create an instance with the data from the fields
            send_contact = Contact(full_name=fullname, email=email, message=message)
            # Add the details
            db.session.add(send_contact)
            # Commit and send the details to the contact table in the database
            db.session.commit()
            # After sending, redirect the user to that same page and flash him/her a success message
            flash('Message sent', 'success')
            return redirect(url_for('contact'))
        else:
            # If the fields are empty, redirect to that sae page and flash an error message to the user
            flash('All fields are required', 'danger')
            return redirect(url_for('contact'))
    # For the get request, if the button that leads to the update page is being clicked, then redirect the user to the contact page
    # where the user gets to fill the form and send
    return render_template('contact.html', form=form, user=current_user)


# View function for the about page
@app.route('/about/')
def about():
    # Return this template passing the datetime.utcnow parameter
    return render_template('about.html', date=datetime.utcnow())


# View function for user profile
@app.route('/profile/<int:profile_id>')
def profile(profile_id):
    # Query the user table in the database using the user id.
    # .first returns the first user with that id...the user is apparently the only user with that id
    user = User.query.filter_by(id=profile_id).first()
    # The length of the post in the queried user details (i.e. the number of post the user has created)
    num = len(user.posts)
    # Return this templates passing the length of post and user parameter to the template
    return render_template('profile.html', num=num, user=user)


# View function for the logout
@app.route('/logout/')
@login_required
def logout():
    # Logout_user() log out the user, it was imported from flask_login
    logout_user()
    # After a successful logout, redirect the user to the homepage and flash this success message to the user
    flash('You\'ve been logged out successfully', 'success')
    return redirect(url_for('home'))


# View function for delete_post, it only accepts a post request
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # Query the post you want to delete from the database using the post's id
    post = Post.query.get_or_404(post_id)
    # If the user who created the post is not the current user logged-in, abort the process with the status code
    if post.author != current_user:
        abort(403)
    # If the user who created the post is the current user logged-in, delete the post
    db.session.delete(post)
    db.session.commit()
    # After a successful delete, redirect the user back to the account page, flashing a success message to the user
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('account'))


# This line of code allows me to execute the code when the file runs as a script
# Debug is set to be True: this allows me to get a debugger when I run into errors, it also enables me to  see my changes on the
# browser without having to run the file again
if __name__ == '__main__':
    app.run(debug=True)
