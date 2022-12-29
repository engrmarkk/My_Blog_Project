from extensions import db
from flask_login import UserMixin
from datetime import datetime


# creating the Post table in the database
class CommentModel(db.Model, UserMixin):
    # The id of the table is unique and increases serially as new content get committed to the database
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(1500), nullable=False)
    comment_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    commenter = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a representation with two attribute 'title' and 'date_posted'
    def __repr__(self):
        return f"Comment('{self.comment[:10]})"
