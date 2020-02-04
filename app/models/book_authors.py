from app import db


class BookAuthors(db.Model):
    __tablename__ = 'book_authors'
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('author.id'),
        primary_key=True
    )
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('book.id'),
        primary_key=True
    )
