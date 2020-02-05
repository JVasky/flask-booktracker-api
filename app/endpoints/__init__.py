def init_app(app):
    from . import authentication
    from . import authors
    from . import books
    from . import users

    @app.errorhandler(404)
    def page_not_found(e):
        # set the 404 status explicitly
        return {
            "message": "Not found"
        }, 404
