# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

from app.api.models import Urls
from app.api.models import dm_dict_en
from app.search import score_pages

# Import utilities
from app.indexer.neighbours import neighbour_urls
import re

# Define the blueprint:
search = Blueprint('search', __name__, url_prefix='')


def get_cached_urls(urls):
  urls_with_cache = urls
  for u in urls_with_cache:
      cache = re.sub(r"http\:\/\/|https\:\/\/", "", u[0])
      if cache[-5:] != ".html":
          cache+=".html"
      print(cache)
      u.append(cache)
  return urls_with_cache

@search.route('/')
@search.route('/index')
def index():
    results = []
    internal_message = ""
    if len(Urls.query.all()) == 0:
        internal_message = "Hey there! It looks like you're here for the first time :) Go and index some pages from Pod0\
         by clicking on 'Indexer' at the top of your screen."
    query = request.args.get('q')
    print(request,request.args,query)
    if not query:
        print("no query")
        return render_template("search/index.html", internal_message=internal_message)
    else:
        results = []
        query = query.lower()
        pears = ['0.0.0.0']
        results = score_pages.run(query, pears)
        if not results:
            pears = ['no pear found :(']
            score_pages.ddg_redirect(query)

        #results = get_cached_urls(results)
        return render_template('search/results.html', pears=pears,
                               query=query, results=results)

@search.route('/html_cache/<path:filename>')
def custom_static(filename):
    return send_from_directory('html_cache', filename)

