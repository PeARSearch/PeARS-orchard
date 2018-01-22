# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, Response

from app import db
from app.api.models import dm_dict_en, Urls, Pods
from app.indexer.neighbours import neighbour_urls
from app.indexer import mk_page_vector
from app.utils import readUrls, readPods
from werkzeug import secure_filename
from app.utils_db import url_from_json, pod_from_json
from app.utils import get_pod_info
from app.indexer.htmlparser import extract_links
from urllib.parse import urljoin, urlparse
import requests
from os.path import dirname,join,realpath,isfile

dir_path = dirname(dirname(dirname(realpath(__file__))))

# Define the blueprint:
indexer = Blueprint('indexer', __name__, url_prefix='/indexer')

# Set the route and accepted methods
@indexer.route("/", methods=["GET", "POST"])
def index():
    num_db_entries = len(Urls.query.all())
    if request.method == "GET":
        return render_template("indexer/index.html", num_entries=num_db_entries)


@indexer.route("/from_file", methods=["POST"])
def from_file():
    print("FILE:",request.files['file_source'])
    if request.files['file_source'].filename[-4:] == ".txt":
        file = request.files['file_source']
        filename = secure_filename(file.filename)
        file.save(join(dir_path, "urls_to_index.txt"))
        return render_template('indexer/progress_file.html')


@indexer.route("/from_url", methods=["POST"])
def from_url():
    if request.form['url'] != "":
        f = open(join(dir_path, "urls_to_index.txt"),'w')
        url = request.form['url']
        keyword = request.form['url_keyword']
        print(url,keyword)
        f.write(url+";"+keyword+"\n")
        f.close()
        return render_template('indexer/progress_url.html',url=url)


@indexer.route("/from_pod", methods=["POST"])
def from_pod():
    if request.form['pod'] != None:
        print("Writing to",join(dir_path,"pods_to_index.txt"))
        f = open(join(dir_path, "pods_to_index.txt"),'w')
        pod = request.form['pod']
        f.write(pod+"\n")
        f.close()
    return render_template('indexer/progress_pod.html')


@indexer.route("/from_crawl", methods=["POST"])
def from_crawl():
    if request.form['site_url'] != None:
        print("Now crawling",request.form['site_url'])
        f = open(join(dir_path, "urls_to_index.txt"),'w')
        url = request.form['site_url']
        keyword = request.form['site_keyword']
        f.write(url+";"+keyword+"\n")
        f.close()
        return render_template('indexer/progress_crawl.html')

@indexer.route("/progress_crawl")
def progress_crawl():
    print("Running progress crawl")
    url,keyword = readUrls(join(dir_path, "urls_to_index.txt"))
    url = url[0]
    keyword = keyword[0]
    def generate():
        netloc = urlparse(url).netloc
        all_links = [url]
        links = extract_links(url)
        #stack = list(set([link for link in links if urlparse(link).netloc == netloc]))
        stack = list(set([link for link in links if url in link and '#' not in link]))
        indexed = 0
        while len(stack) > 0:
            all_links.append(stack[0])
            print("Processing",stack[0])
            new_page = mk_page_vector.compute_vectors(stack[0],keyword)
            if new_page:
                new_links = extract_links(stack[0])
                #new_site_links = list(set([link for link in links if urlparse(link).netloc == netloc and link not in all_links and '#' not in link]))
                new_site_links = list(set([link for link in links if url in link and link not in all_links and '#' not in link]))
                stack.pop(0)
                stack=list(set(stack+new_site_links))
                indexed+=1
                yield "data:" + str(indexed) + "\n\n"
            else:
                stack.pop(0)
        yield "data:" + "Finished!" + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')

@indexer.route("/progress_file")
def progress_file():
    print("Running progress file")
    def generate():
        urls, keywords = readUrls(join(dir_path, "urls_to_index.txt"))
        for c in range(len(urls)):
            mk_page_vector.compute_vectors(urls[c],keywords[c])
            c+=1
            yield "data:" + str(int(c/len(urls)*100)) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')

   
@indexer.route("/progress_pod")
def progress_pods():
    print("Running progress pod")
    print("Reading",join(dir_path,"pods_to_index.txt"))
    pod_urls = readPods(join(dir_path, "pods_to_index.txt"))
    urls = []
    for pod_url in pod_urls:
        print(pod_url)
        pod = get_pod_info(pod_url)
        pod_from_json(pod, pod_url)
        pod_entry=db.session.query(Pods).filter_by(url=pod_url).first()
        pod_entry.registered = True
        db.session.commit()
        r = requests.get(pod_url+"api/urls/")
        print(r)
        for u in r.json()['json_list']:
            urls.append([u,pod['name']])
    def generate():
        c = 0
        for pair in urls:
            u = pair[0]
            pod = pair[1]
            url_from_json(u,pod)
            c+=1
            yield "data:" + str(int(c/len(urls)*100)) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')


@indexer.route("/url", methods=["GET", "POST"])
def url_index():
    if request.method == "GET":
        neighbours, num_db_entries = neighbour_urls("http://www.openmeaning.org/", dm_dict_en)
        return render_template("indexer/index.html", neighbours=neighbours, num_entries=num_db_entries)
    target_url = request.form["target_url"]
    neighbours, num_db_entries = neighbour_urls(target_url, dm_dict_en)
    return render_template("indexer/index.html", neighbours=neighbours, num_entries=num_db_entries)


