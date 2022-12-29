from extensions import db, mail
import random
from flask import render_template, redirect, request, flash, url_for, abort, Blueprint
from flask_login import login_required, current_user
from flask_mail import Message
from form import PostForm, UpdateForm, ContactForm, DmForm, PhotoForm, CommentForm
from models import Post, User, DmModel, CommentModel
from datetime import datetime
from routes.func import save_image, save_post_image


view = Blueprint("view", __name__)


# View function for the home page
@view.route('/')
@view.route('/home')
def home():
    dms = []
    length = []
    posts = Post.query.all()        # This get all the post in the post table in the database
    if current_user.is_authenticated:
        dms = DmModel.query.filter_by(user=current_user.id)
    random.shuffle(posts)           # Shuffles the post randomly
    for dm in dms:
        if dm.dm_type == 'receive':
            length.append(dm)
    num = len(length)
    date = datetime.utcnow().strftime('%Y-%h-%d')
    context = {
        'posts': posts,
        'dms': dms,
        'num': num,
        'date': date
    }
    return render_template('home.html', **context)    # and displays it randomly in the homepage whenever a refresh is done in the homepage


# View function for account page, where you can create your post
@view.route("/account/", methods=['GET', 'POST'])
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
        f = form.image.data
        if f:
            image_file = save_post_image(f)
        else:
            image_file = ''
        # Create an instance of the Post model
        post = Post(title=title, content=post_content,
                    author=current_user, photo=image_file)
        # Add the datas to the Post table in the database
        db.session.add(post)
        # Commit
        db.session.commit()
        # Flash this message to the user and redirect the user to that same page where the data gets displayed on the screen
        flash('Posted!', 'success')
        return redirect(url_for('view.account', id=id))
    # This for a get request, if u click on the link that leads to the account page, this return statement get called upon
    return render_template('account.html', form=form, user=current_user)


# View function for update post
@view.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
            return redirect(url_for('view.account', post_id=post.id))
    # For the get request, if the button that leads to the update page is being clicked, then redirect the user to the update page
    # then update the empty the value of both the title and content field with the queried data from database
    form.title.data = post.title
    form.post_content.data = post.content
    return render_template('update.html',
                           form=form)


# View function for display page, the page that displays a post when the title of the gets clicked
@view.route('/display/<int:blog_id>', methods=['GET', 'POST'])
def display_post(blog_id):
    form = CommentForm()
    # Query from the database the details of the redirected post with the post id and render he details on the display page
    post = Post.query.filter_by(id=blog_id).first()
    if request.method == 'POST':
        comment = form.comment.data
        if not comment:
            flash('box cannot be empty', 'danger')
            return redirect(url_for('view.display_post', blog_id=blog_id))
        new_comment = CommentModel(comment=comment, post_id=blog_id, commenter=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('view.display_post', blog_id=blog_id))
    context = {
        'form': form,
        'post': post,
        'user': current_user
    }
    return render_template('display.html', **context)


@view.route("/contact/", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                fullname = form.fullname.data.title()
                email = form.email.data.lower()
                message = form.message.data.title()
                msg = Message(
                    "MyBlog: from " + fullname,
                    sender=email,
                    recipients=[
                        "atmme1992@gmail.com"
                    ],
                )
                msg.body = f"{message}\nMy email address is: {email}"
                mail.send(msg)
                flash("Message Sent", "success")
                return redirect(url_for("view.contact"))
            except:
                flash("Your data connection is off", category="danger")

    return render_template("contact.html", form=form)


# View function for the about page
@view.route('/about/')
def about():
    # Return this template passing the datetime.utcnow parameter
    return render_template('about.html', date=datetime.utcnow())


# View function for user profile
@view.route('/profile/<int:profile_id>', methods=['GET', 'POST'])
def profile(profile_id):
    form = DmForm()
    # Query the user table in the database using the user id.
    # .first returns the first user with that id...the user is apparently the only user with that id
    user = User.query.filter_by(id=profile_id).first()
    dm_messages = DmModel.query.all()
    # The length of the post in the queried user details (i.e. the number of post the user has created)
    num = len(user.posts)
    if request.method == 'POST':
        dm = form.dm.data
        if not dm:
            return redirect(url_for('view.profile', profile_id=profile_id))
        send_1 = DmModel(dm_type='send', dm_message=dm, user_1=current_user.id,
                         user=profile_id)
        db.session.add(send_1)
        send_2 = DmModel(dm_type='receive', dm_message=dm, user_1=current_user.id,
                         user=profile_id)
        db.session.add(send_2)
        db.session.commit()
        flash('Message sent', 'success')
        return redirect(url_for('view.profile', profile_id=profile_id))
    # Return this templates passing the length of post and user parameter to the template
    context = {
        'num': num,
        'user': user,
        'form': form,
        'dms': dm_messages
    }
    return render_template('profile.html', **context)


# View function for delete_post, it only accepts a post request
@view.route("/post/<int:post_id>/delete", methods=['POST'])
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
    return redirect(url_for('view.account'))


@view.route("/profile_photo/", methods=["GET", "POST"])
@login_required
def add_photo():
    form = PhotoForm()
    user = User.query.get(current_user.id)
    if request.method == "POST":
        try:
            f = form.image.data
            if not f:
                flash('nothing to upload', 'danger')
                return redirect(url_for('view.add_photo'))
            image_file = save_image(f)
            user.photo = image_file
            db.session.commit()
            flash('Profile photo uploaded successfully', 'success')
            return redirect(url_for('view.add_photo'))
        except Exception as e:
            flash(e, 'danger')
    context = {
        'form': form,
        'user': user
    }
    return render_template('add_picture.html', **context)


# View function for delete_post, it only accepts a post request
@view.route("/comment/<int:comment_id>/<int:blog_id>/delete")
@login_required
def delete_comment(blog_id: int, comment_id: int):
    # Query the post you want to delete from the database using the post's id
    comment = CommentModel.query.get_or_404(comment_id)
    # If the user who created the post is not the current user logged-in, abort the process with the status code
    if comment.who != current_user:
        abort(403)
    # If the user who created the post is the current user logged-in, delete the post
    db.session.delete(comment)
    db.session.commit()
    # After a successful delete, redirect the user back to the account page, flashing a success message to the user
    flash('Comment deleted!', 'success')
    return redirect(url_for('view.display_post', blog_id=blog_id))


# View function for delete_post, it only accepts a post request
@view.route("/message/<int:message_id>/<int:profile_id>/delete")
@login_required
def delete_message(message_id: int, profile_id: int):
    # Query the post you want to delete from the database using the post's id
    message = DmModel.query.get_or_404(message_id)
    # If the user who created the post is not the current user logged-in, abort the process with the status code
    # If the user who created the post is the current user logged-in, delete the post
    db.session.delete(message)
    db.session.commit()
    # After a successful delete, redirect the user back to the account page, flashing a success message to the user
    flash('Message deleted!', 'success')
    return redirect(url_for('view.profile', profile_id=profile_id))
