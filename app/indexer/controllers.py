# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, Response


from app.api.models import dm_dict_en, KnownPods, Urls
from app.indexer.neighbours import neighbour_urls
from app.indexer import mk_page_vector
from app.utils import readUrls
from werkzeug import secure_filename
from app.utils_db import url_from_json
import requests
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Define the blueprint:
indexer = Blueprint('indexer', __name__, url_prefix='/indexer')

# Set the route and accepted methods
@indexer.route("/", methods=["GET", "POST"])
def index():
    known_pods = KnownPods.query.all()
    pods_urls = [p.url for p in known_pods]
    print(pods_urls)
    num_db_entries = len(Urls.query.all())
    if request.method == "GET":
        return render_template("indexer/index.html", num_entries=num_db_entries, pods=pods_urls)

    if request.method == 'POST':
        print("FILE:",request.files['file_source'])
        if request.files['file_source'].filename[-4:] == ".txt":
            file = request.files['file_source']
            filename = secure_filename(file.filename)
            file.save(os.path.join(dir_path, "urls_to_index.txt"))
            return render_template('indexer/progress1.html')

        if request.form['url'] != None:
            f = open(os.path.join(dir_path, "urls_to_index.txt"),'w')
            url = request.form['url']
            f.write(url+"\n")
            f.close()
            return render_template('indexer/progress3.html')

        if request.form['pods'] != None:
            f = open(os.path.join(dir_path, "pods_to_index.txt"),'w')
            pods = [request.form['pods']]
            for pod in pods:
                f.write(pod+"api/urls/\n")
            f.close()
            return render_template('indexer/progress2.html')
                    

@indexer.route("/progress1")
def progress_file():
    print("Running progress file")
    def generate():
        urls = readUrls(os.path.join(dir_path, "urls_to_index.txt"))
        c = 0
        for u in urls:
            mk_page_vector.compute_vectors(u)
            c+=1
            yield "data:" + str(int(c/len(urls)*100)) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')

   
@indexer.route("/progress2")
def progress_pods():
    print("Running progress pod")
    pods = readUrls(os.path.join(dir_path, "pods_to_index.txt"))
    urls = []
    for pod in pods:
        print(pod)
        r = requests.get(pod)
        print(r)
        for u in r.json()['json_list']:
            urls.append(u)
    def generate():
        c = 0
        for u in urls:
            url_from_json(u)
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


