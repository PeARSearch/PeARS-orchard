# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify
from app.api.models import dm_dict_en


# Define the blueprint:
pod_finder = Blueprint('pod_finder', __name__, url_prefix='/pod_finder')

@pod_finder.route('/')
@pod_finder.route('/index')
def return_pods():
    return render_template('pod_finder/index.html')
