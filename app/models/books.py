from app import db, ma
from sqlalchemy.orm import relationship
from .authors import Author


# Book Class/Model
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    authors = relationship(Author, secondary='book_authors')
