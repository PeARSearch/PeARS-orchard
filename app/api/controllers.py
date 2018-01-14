# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify
from app.api.models import dm_dict_en, Urls, Pods


# Define the blueprint:
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/vectors/<word>/')
def return_vector(word):
    v = list(dm_dict_en[word])
    return jsonify(vector=v)

@api.route('/urls/')
def return_urls():
    return jsonify(json_list=[i.serialize for i in Urls.query.all()])

@api.route('/pods/')
def return_pods():
    return jsonify(json_list = [p.serialize for p in Pods.query.all()])

