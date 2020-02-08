from app import db


class Ratings(db.Model):
    __tablename__ = "ratings"
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True
    )
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('book.id'),
        primary_key=True
    )
    book = db.relationship("Book", back_populates="user_ratings")
    user = db.relationship("User", back_populates="book_ratings")
    rating = db.Column(db.SmallInteger, nullable=False)
    notes = db.Column(db.Text)
    __table_args__ = (db.CheckConstraint('rating BETWEEN 0 AND 10', name='valid_rating_check'),)
