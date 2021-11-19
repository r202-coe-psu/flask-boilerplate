from flask import Blueprint

module = Blueprint("sites", __name__)


@module.route("/")
def index():
    return {"message": "Hello, Flask!", "success": True}
