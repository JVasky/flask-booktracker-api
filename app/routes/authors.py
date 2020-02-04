from app import app
from app.models.authors import Author
from app.models.schemas import AuthorSchema
from flask import jsonify, request


@app.route('/authors')
def get_authors():
    page = request.args.get('page')
    if page is not None:
        page = int(page)

    if page is None or page == 0:
        authors = Author.query.order_by(Author.id).all()
    else:
        authors = Author.query.order_by(Author.id).paginate(page, 30, False).items
    if authors is None:
        response = {
            'message': 'there are no authors'
        }
        return jsonify(response), 404
    else:
        authors_schema = AuthorSchema(many=True)
        result = authors_schema.dumps(authors)
        response = {
            'data': result
        }
        return jsonify(response)


@app.route('/authors/<author_id>')
def get_author(author_id):
    author = Author.query.filter_by(id=author_id).first()
    if author is None:
        response = {
            'message': 'author does not exist'
        }
        return jsonify(response), 404
    else:
        author_schema = AuthorSchema()
        result = author_schema.dumps(author)
        response = {
            'data': result
        }
        return jsonify(response)
