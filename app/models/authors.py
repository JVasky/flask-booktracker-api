from app import db
from sqlalchemy import UniqueConstraint


# Book Class/Model
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_dt = db.Column(db.DateTime, server_default=db.func.now())
    modified_dt = db.Column(db.DateTime, onupdate=db.func.now())
    books = db.relationship('Book', secondary='book_authors')
    __table_args__ = (UniqueConstraint('first_name', 'middle_name', 'last_name', name='_author_name_uc'),)
