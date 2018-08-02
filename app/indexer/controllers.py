# Import flask dependencies
from flask import Blueprint, request, render_template, Response

from app.api.models import dm_dict_en, Urls
from app.indexer.neighbours import neighbour_urls
from app.indexer import mk_page_vector, spider
from app.utils import readUrls, readBookmarks
from app.utils_db import pod_from_file
from app.indexer.htmlparser import extract_links
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
        file = request.files['file_source']
        file.save(join(dir_path, "bookmarks.html"))
        urls = readBookmarks(join(dir_path,"bookmarks.html"), keyword)
        print(urls)
        f = open(join(dir_path, "urls_to_index.txt"), 'w')
        for u in urls:
            f.write(u + ";" + keyword + "\n")
        f.close()
        return render_template('indexer/progress_file.html')


@indexer.route("/from_url", methods=["POST"])
def from_url():
    if request.form['url'] != "":
        f = open(join(dir_path, "urls_to_index.txt"), 'w')
        url = request.form['url']
        keyword = request.form['url_keyword']
        print(url, keyword)
        f.write(url + ";" + keyword + "\n")
        f.close()
        return render_template('indexer/progress_url.html', url=url)


@indexer.route("/from_crawl", methods=["POST"])
def from_crawl():
    if request.form['site_url'] is not None:
        print("Now crawling", request.form['site_url'])
        f = open(join(dir_path, "urls_to_index.txt"), 'w')
        url = request.form['site_url']
        keyword = request.form['site_keyword']
        f.write(url + ";" + keyword + "\n")
        f.close()
        return render_template('indexer/progress_crawl.html')


'''
Controllers for progress pages.
One controller per ways to index (file, crawl).
The URL indexing uses same progress as file.
'''


@indexer.route("/progress_crawl")
def progress_crawl():
    print("Running progress crawl")
    url, keyword = readUrls(join(dir_path, "urls_to_index.txt"))
    url = url[0]
    keyword = keyword[0]

    def generate():
        # netloc = urlparse(url).netloc
        all_links = [url]
        stack = spider.get_links(url,200)
        indexed = 0
        while len(stack) > 0:
            all_links.append(stack[0])
            print("Processing", stack[0])
            new_page = mk_page_vector.compute_vectors(stack[0], keyword)
            if new_page:
                stack.pop(0)
                indexed += 1
                yield "data:" + str(indexed) + "\n\n"
            else:
                stack.pop(0)
        pod_from_file(keyword)
        yield "data:" + "Finished!" + "\n\n"

    return Response(generate(), mimetype='text/event-stream')


@indexer.route("/progress_file")
def progress_file():
    print("Running progress file")

    def generate():
        urls, keywords = readUrls(join(dir_path, "urls_to_index.txt"))
        for c in range(len(urls)):
            success = mk_page_vector.compute_vectors(urls[c], keywords[c])
            if success:
                pod_from_file(keywords[c])
            else:
                print("Error accessing the URL.")
            c += 1
            yield "data:" + str(int(c / len(urls) * 100)) + "\n\n"

    return Response(generate(), mimetype='text/event-stream')


@indexer.route("/url", methods=["GET", "POST"])
def url_index():
    if request.method == "GET":
        neighbours, num_db_entries = neighbour_urls(
            "http://www.openmeaning.org/", dm_dict_en)
        return render_template(
            "indexer/index.html",
            neighbours=neighbours,
            num_entries=num_db_entries)
    target_url = request.form["target_url"]
    neighbours, num_db_entries = neighbour_urls(target_url, dm_dict_en)
    return render_template(
        "indexer/index.html",
        neighbours=neighbours,
        num_entries=num_db_entries)
