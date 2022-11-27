# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

# Import flask dependencies
from flask import Blueprint, request, render_template
from app.api.models import Urls
from app import db
from app.orchard.mk_urls_file import make_fruitfly_pod, del_pod

# Define the blueprint:
orchard = Blueprint('orchard', __name__, url_prefix='/my-orchard')


@orchard.route('/')
@orchard.route('/index', methods=['GET', 'POST'])
def index():
    query = db.session.query(Urls.pod.distinct().label("pod"))
    keywords = [row.pod for row in query.all()]
    print(keywords)
    pears = []
    for keyword in keywords:
        if keyword and '.fh' not in keyword:
            pear_urls = []
            for u in db.session.query(Urls).filter_by(pod=keyword).all():
                pear_urls.append(u)
            pear = [keyword, len(pear_urls)]
            pears.append(pear)
    # for p in sorted(pears, key=lambda p: len(pears[p]), reverse=True):
    #    print(p,len(pears[p]),pears[p][:5])
    return render_template('orchard/index.html', pears=pears)


@orchard.route('/get-a-pod', methods=['POST', 'GET'])
def get_a_pod():
    query = request.args.get('pod')
    hfile = make_fruitfly_pod(query)
    #del_pod(query)
    print(hfile)
    return render_template(
        'orchard/get-a-pod.html',
        query=query,
        location=hfile)
