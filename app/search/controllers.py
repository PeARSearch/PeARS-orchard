# SPDX-FileCopyrightText: 2022 Aurelie Herbelot, <aurelie.herbelot@unitn.it>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

# Import flask dependencies
from flask import Blueprint, request, render_template, send_from_directory
from flask import current_app

# Import the database object from the main app module
from app.api.models import Urls
from app.search import score_pages

# Import utilities
import re
import logging


LOG = logging.getLogger(__name__)

# Define the blueprint:
search = Blueprint('search', __name__, url_prefix='')


@search.route('/')
@search.route('/index')
def index():  
    results = []
    internal_message = ""
    if Urls.query.count() == 0:
        internal_message = "Hey there! It looks like you're here\
         for the first time :) To understand how to use PeARS,\
         go to the FAQ (link at the top of the page)."
    query = request.args.get('q')
    if not query:
        LOG.info("No Querry")
        return render_template(
            "search/index.html",
            internal_message=internal_message)
    else:
        results = []
        query = query.lower()
        pears = ['0.0.0.0']
        results, pods = score_pages.run(query, pears)
        if not results:
            pears = ['no pear found :(']
            score_pages.ddg_redirect(query)

        return render_template(
            'search/results.html', pears=pods, query=query, results=results)


@search.route('/html_cache/<path:filename>')
def custom_static(filename):
    return send_from_directory('html_cache', filename)
