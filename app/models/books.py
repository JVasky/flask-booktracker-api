from app import db
from .authors import Author
from sqlalchemy.sql import expression


# Book Class/Model
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    approved = db.Column(db.Boolean, server_default=expression.false())
    created_dt = db.Column(db.DateTime, server_default=db.func.now())
    modified_dt = db.Column(db.DateTime, onupdate=db.func.now())
    user_ratings = db.relationship("Ratings", back_populates="book")
    authors = db.relationship(Author, secondary='book_authors')
