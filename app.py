import random
from flask import Flask, render_template, url_for, request, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from form import RegistrationForm, LoginForm, UpdateForm, PostForm, ContactForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required, UserMixin, LoginManager
from datetime import datetime
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'myblog.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '026b0eb800ec2934fb5cf2e7'

db = SQLAlchemy(app)
db.init_app(app)

login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Contact(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(70), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.full_name}', '{self.email}')"


with app.app_context():
    db.create_all()


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('Login to access this page', category='info')
    return redirect(url_for('login'))


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    random.shuffle(posts)
    return render_template('home.html', posts=posts)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login Successful', 'success')
            return redirect(url_for('home', id=user.id))
        else:
            flash('Check your Email / Password', 'danger')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('register.html', form=form)
        else:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                flash('User with this username already exist', category='danger')
                return redirect(url_for('register'))

            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('User with this email already exist', category='danger')
                return redirect(url_for('register'))

            password_hash = generate_password_hash(form.password.data)
            new_user = User(first_name=form.firstname.data, last_name=form.lastname.data, username=form.username.data,
                            email=form.email.data, password=password_hash)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration Successful, You can now Login', category='success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route("/account/", methods=['GET', 'POST'])
@login_required
def account():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        post_content = form.post_content.data
        post = Post(title=title, content=post_content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Posted!', 'success')
        return redirect(url_for('account', id=id))
    return render_template('account.html', form=form, user=current_user)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    form = UpdateForm()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if request.method == 'POST':
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.post_content.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('account', post_id=post.id))

    form.title.data = post.title
    form.post_content.data = post.content
    return render_template('update.html',
                           form=form)


@app.route('/display/<int:blog_id>')
def display_post(blog_id):
    post = Post.query.filter_by(id=blog_id).first()
    return render_template('display.html', post=post, user=current_user)


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        fullname = form.fullname.data
        email = form.email.data
        message = form.message.data
        if current_user.is_authenticated:
            if message:
                send_contact = Contact(full_name=current_user.first_name + ' ' + current_user.last_name, email=current_user.email, message=message)
                db.session.add(send_contact)
                db.session.commit()
                flash('Message sent', 'success')
                return redirect(url_for('contact'))
        if fullname and email and message:
            send_contact = Contact(full_name=fullname, email=email, message=message)
            db.session.add(send_contact)
            db.session.commit()
            flash('Message sent', 'success')
            return redirect(url_for('contact'))
        else:
            flash('All fields are required', 'danger')
            return redirect(url_for('contact'))
    return render_template('contact.html', form=form, user=current_user)


@app.route('/about/')
def about():
    return render_template('about.html', date=datetime.utcnow())


@app.route('/profile/<int:profile_id>')
def profile(profile_id):
    user = User.query.filter_by(id=profile_id).first()
    num = len(user.posts)
    return render_template('profile.html', num=num, user=user)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You\'ve been logged out successfully', 'success')
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('account'))


if __name__ == '__main__':
    app.run(debug=True)
