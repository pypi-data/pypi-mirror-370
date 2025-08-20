from flask import Flask


def setup_app(content: str = "Hello, World!") -> Flask:
    """Initialize the Flask application."""
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "<h1>{}</h1>".format(content)

    return app


# Example usage
app = setup_app("HI")
