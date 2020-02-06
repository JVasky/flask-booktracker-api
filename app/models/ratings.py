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
    rating = db.Column(db.SmallInteger, nullable=False)
    __table_args__ = (db.CheckConstraint('rating BETWEEN 0 AND 10', name='valid_rating_check'),)
