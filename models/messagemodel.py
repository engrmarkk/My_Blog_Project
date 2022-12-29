from extensions import db
from flask_login import UserMixin
from datetime import datetime


# creating the Post table in the database
class DmModel(db.Model, UserMixin):
    # The id of the table is unique and increases serially as new content get committed to the database
    id = db.Column(db.Integer, primary_key=True)
    dm_type = db.Column(db.String(10), nullable=False)
    dm_message = db.Column(db.String(500), nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_1 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.Column(db.Integer, nullable=False)

    # Define a representation with two attribute 'title' and 'date_posted'
    def __repr__(self):
        return f"Dm('{self.dm_message[:10]})"
