from extensions import db
from flask_login import UserMixin
from datetime import datetime


# creating the Post table in the database
class Post(db.Model, UserMixin):
    # The id of the table is unique and increases serially as new content get committed to the database
    id = db.Column(db.Integer, primary_key=True)
    # The title column in the Post table in the database, we don't want this column to be empty, hence setting the nullable to false
    title = db.Column(db.String(100), nullable=False)
    # The date and time column for each post, the default value is set to be the current time at which a post is being committed to the database
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    photo = db.Column(db.Text, nullable=False, default='')
    # The content column in the Post table in the database, we don't want this column to be empty, hence setting the nullable to false
    content = db.Column(db.Text, nullable=False)
    # This column is used to access the user of a particular post, it takes the id of the user of the post
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.relationship('CommentModel', backref='comm', lazy=True, cascade='delete', foreign_keys='CommentModel.post_id')

    # Define a representation with two attribute 'title' and 'date_posted'
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
