# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

# Import flask dependencies
import logging

from flask import (Blueprint, flash, request, render_template, Response, make_response, jsonify)
from app import app
from app.api.models import Urls
from app.indexer.neighbours import neighbour_urls
from app.indexer import mk_page_vector, spider
from app.utils import readUrls, readBookmarks, get_language, convert_to_string
from app.utils_db import pod_from_file
from app.indexer.htmlparser import extract_links
from app.indexer.access import request_url
from os.path import dirname, join, realpath

dir_path = dirname(dirname(dirname(realpath(__file__))))

# Define the blueprint:
indexer = Blueprint('indexer', __name__, url_prefix='/indexer')


# Set the route and accepted methods
@indexer.route("/", methods=["GET", "POST"])
def index():
    num_db_entries = len(Urls.query.all())
    if request.method == "GET":
        return render_template(
            "indexer/index.html", num_entries=num_db_entries)


'''
 Controllers for various ways to index
 (from file, from url, from crawl)
'''

@indexer.route("/from_file", methods=["POST"])
def from_file():
    print("FILE:", request.files['file_source'])
    if request.files['file_source'].filename[-4:] == ".txt":
        file = request.files['file_source']
        # filename = secure_filename(file.filename)
        file.save(join(dir_path, "urls_to_index.txt"))
        return render_template('indexer/progress_file.html')

@indexer.route("/from_bookmarks", methods=["POST"])
def from_bookmarks():
    print("FILE:", request.files['file_source'])
    if request.files['file_source'].filename == "bookmarks.html":
        keyword = request.form['bookmark_keyword']
        keyword, lang = get_language(keyword)
        file = request.files['file_source']
        file.save(join(dir_path, "bookmarks.html"))
        urls = readBookmarks(join(dir_path,"bookmarks.html"), keyword)
        print(urls)
        f = open(join(dir_path, "urls_to_index.txt"), 'w')
        for u in urls:
            f.write(u + ";" + keyword + ";" + lang +"\n")
        f.close()
        return render_template('indexer/progress_file.html')

@indexer.route("/from_url", methods=["POST"])
def from_url():
    if request.form['url'] != "":
        f = open(join(dir_path, "urls_to_index.txt"), 'w')
        u = request.form['url']
        keyword = request.form['url_keyword']
        keyword, lang = get_language(keyword)
        print(u, keyword, lang)
        f.write(u + ";" + keyword + ";" + lang +"\n")
        f.close()
        return render_template('indexer/progress_url.html', url=u)


@indexer.route("/from_crawl", methods=["POST"])
def from_crawl():
    if request.form['site_url'] is not None:
        print("Now crawling", request.form['site_url'])
        f = open(join(dir_path, "urls_to_index.txt"), 'w')
        u = request.form['site_url']
        keyword = request.form['site_keyword']
        keyword, lang = get_language(keyword)
        f.write(u + ";" + keyword + ";" + lang +"\n")
        f.close()
        return render_template('indexer/progress_crawl.html')

@indexer.route("/hash", methods=["GET"])
def hash():
    print(request)
    url = request.args['url']
    access, req, request_errors = request_url(url)
    lang = 'simple' # only English for now
    if access:
        try:
            url_type = req.headers['Content-Type']
        except:
            print('>> ERROR: INDEXER: CONTROLLERS: Content type could not be retrieved from header.')
            return 0
    else:
        print(">> ERROR: INDEXER: CONTROLLERS: progress_file: access denied", request_errors)
        return 0

    vector = mk_page_vector.hash_from_url(url, lang)
    r = app.make_response(jsonify(convert_to_string(vector)))
    return r


'''
Controllers for progress pages.
One controller per ways to index (file, crawl).
The URL indexing uses same progress as file.
'''


@indexer.route("/progress_crawl")
def progress_crawl():
    print("Running progress crawl")
    urls, keywords, langs, errors = readUrls(join(dir_path, "urls_to_index.txt"))
    if urls and keywords:
        url = urls[0]
        keyword = keywords[0]
        lang = langs[0]
    def generate():
        # netloc = urlparse(url).netloc
        all_links = [url]
        stack = spider.get_links(url,200)
        indexed = 0
        while len(stack) > 0:
            all_links.append(stack[0])
            print("Processing", stack[0])
            new_page = mk_page_vector.compute_vectors(stack[0], keyword, lang)
            if new_page:
                stack.pop(0)
                indexed += 1
                yield "data:" + str(indexed) + "\n\n"
            else:
                stack.pop(0)
        pod_from_file(keyword, lang)
        yield "data:" + "Finished!" + "\n\n"

    return Response(generate(), mimetype='text/event-stream')


@indexer.route("/progress_file")
def progress_file():
    logging.debug("Running progress file")
    def generate():
        urls, keywords, langs, errors = readUrls(join(dir_path, "urls_to_index.txt"))
        print(urls)
        if errors:
            logging.error('Some URLs could not be processed')
        if not urls or not keywords or not langs:
            logging.error('Invalid file format')
            yield "data: 0 \n\n"

        c = 0
        for url, kwd, lang in zip(urls, keywords, langs):
            access, req, request_errors = request_url(url)
            if access:
                try:
                    url_type = req.headers['Content-Type']
                except:
                    messages.append('ERROR: Content type could not be retrieved from header.')
                    continue
            else:
                print(">> INDEXER: CONTROLLERS: progress_file: access denied", request_errors)

            success = mk_page_vector.compute_vectors(url, kwd, lang)
            if success:
                pod_from_file(kwd, lang)
            else:
                logging.error("Error accessing the URL")
            c += 1
            yield "data:" + str(int(c / len(urls) * 100)) + "\n\n"

    return Response(generate(), mimetype='text/event-stream')

