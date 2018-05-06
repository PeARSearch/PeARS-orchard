# Import flask dependencies
from flask import Blueprint, render_template

from app.api.models import Pods

# Define the blueprint:
pages = Blueprint('pages', __name__, url_prefix='')


@pages.route('/faq/')
def return_faq():
    return render_template("pages/faq.html")


@pages.route('/acknowledgements/')
def return_acknowledgements():
    return render_template("pages/acknowledgements.html")
