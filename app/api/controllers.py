# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

# Import flask dependencies
from flask import Blueprint, jsonify
from app.api.models import Urls, Pods
from app import db

# Define the blueprint:
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/urls/')
def return_urls():
    return jsonify(json_list=[i.serialize for i in Urls.query.all()])


@api.route('/pods/')
def return_pods():
    return jsonify(json_list=[p.serialize for p in Pods.query.all()])


@api.route('/pods/<pod>/')
def return_pod(pod):
    pod = pod.replace('+', ' ')
    p = db.session.query(Pods).filter_by(name=pod).first()
    return jsonify(p.serialize)
