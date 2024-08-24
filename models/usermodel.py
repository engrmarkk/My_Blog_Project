from extensions import db
from flask_login import UserMixin


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
    photo = db.Column(db.Text, nullable=False, default='')
    # The password column in the User table in the database, we don't want this column to be empty, hence setting the nullable to false,
    password = db.Column(db.String(60), nullable=False)
    # This is not a column in the database, it's a relationship that binds the user table to the post table,
    # the backref is used to access the user table using a post
    # For example, to get the username of the user of a post, you use the post.author.username to access the username of tha user
    posts = db.relationship('Post', backref='author', lazy=True, cascade='delete', foreign_keys='Post.user_id')
    send_dm = db.relationship('DmModel', backref='owner', lazy=True, foreign_keys='DmModel.user_1')
    pst_cmt = db.relationship('CommentModel', backref='who', lazy=True, foreign_keys='CommentModel.commenter')

    # Define a representation with two attribute 'username' and 'email'
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
