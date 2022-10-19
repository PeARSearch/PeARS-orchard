# SPDX-FileCopyrightText: 2022 Aurelie Herbelot, <aurelie.herbelot@unitn.it>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

# Import flask dependencies
from flask import Blueprint, request, render_template, Response
from werkzeug.utils import secure_filename
import requests, csv, sys
from os.path import dirname, join, realpath
from app import db
from app.api.models import Pods, Urls
from app.utils import readPods, get_pod_info, convert_to_string, get_language
from app.utils_db import pod_from_json, url_from_json, pod_from_file, update_official_pod_list
from app.pod_finder import score_pods, index_pod_file
from app.pod_finder.download_pod_list import download_pod_centroids
import joblib
import re

dir_path = dirname(dirname(dirname(realpath(__file__))))
csv.field_size_limit(sys.maxsize)

# Define the blueprint:
pod_finder = Blueprint('pod_finder', __name__, url_prefix='/pod_finder')



@pod_finder.route('/')
@pod_finder.route('/index', methods=['GET', 'POST'])
def index():
    pods = []
    for p in db.session.query(Pods).filter_by(registered=True).all():
        print(p.name, p.description)
        pods.append([p.name, p.description])
    return render_template('pod_finder/index.html', pods=pods)


'''Find a pod'''
@pod_finder.route('/find-a-pod/')
def find_a_pod():
    print("Running progress pod update")
    query = request.args.get('search-pod')
    _, lang = get_language(query)
    download_pod_centroids(lang)
    update_official_pod_list(lang)
    #print(request, request.args, query)
    pods = score_pods.run(query)
    if len(pods) > 0:
        return render_template('pod_finder/find-a-pod.html', pods=pods, msg="")
    else:
        return render_template(
            'pod_finder/find-a-pod.html',
            pods=[],
            msg="Sorry, no pod found for your query :(")


@pod_finder.route("/subscribe", methods=["POST"])
def subscribe():
    if request.form.getlist('pods') is not None:
        print("Writing to", join(dir_path, "pods_to_index.txt"))
        f = open(join(dir_path, "pods_to_index.txt"), 'w')
        for pod in request.form.getlist('pods'):
            print(pod)
            f.write(pod + "\n")
        f.close()
    return render_template('pod_finder/progress_pod.html')


'''Subscribe from URL'''


@pod_finder.route("/subscribe-from-url", methods=["POST"])
def subscribe_from_url():
    if request.form['pod'] is not None:
        print("Writing to", join(dir_path, "pods_to_index.txt"))
        f = open(join(dir_path, "pods_to_index.txt"), 'w')
        pod = request.form['pod']
        print(pod)
        f.write(pod + "\n")
        f.close()
    return render_template('pod_finder/progress_pod.html')


'''Record pod file'''


@pod_finder.route("/subscribe-from-file", methods=["POST"])
def subscribe_from_file():
    print("Running progress for subscribe from file")
    file = request.files['file_source']
    filename = secure_filename(file.filename)
    file.save(join(dir_path, "app", "static", "pods", "urls_from_pod.fh"))
    return render_template('pod_finder/progress_file.html')


@pod_finder.route("/progress_file")
def progress_file():
    def generate():
        c = 0
        new_urls = list()
        pod_name = ""
        hfile = join(dir_path, "app", "static", "pods", "urls_from_pod.fh")
        pod_name, lang, m, titles, urls = joblib.load(hfile)
        pod_entry = db.session.query(Pods).filter_by(name=pod_name).first()
        for i in range(len(titles)):
            title = titles[i]
            url = urls[i]
            vector = convert_to_string(m[i])
            if not db.session.query(Urls).filter_by(url=url).all():
                u = Urls(
                    url=url,
                    title=title,
                    snippet=title, #FIX
                    pod=pod_name,
                    vector=vector,
                    cc=True if 'wikipedia.org' in url else False)
                new_urls.append(u)
        db.session.commit()
        
        if len(new_urls) == 0:
            print("All URLs already known.")
            yield "data:" + "100" + "\n\n"
        else:
            c = 0
            for u in new_urls:
                #print("Adding",u.url,"to DB")
                try:
                    db.session.add(u)
                    db.session.commit()
                    c += 1
                except:
                    print("Failed to add",u.url,"to DB...")
                yield "data:" + str(int(c / len(urls) * 100)) + "\n\n"
                pod_from_file(pod_name, lang)        
    return Response(generate(), mimetype='text/event-stream')


'''Take a file of pod URLs and index all URLs on each pod.'''


@pod_finder.route("/progress_pod")
def progress_pods():
    print("Running progress pod")
    print("Reading", join(dir_path, "pods_to_index.txt"))
    pod_urls = readPods(join(dir_path, "pods_to_index.txt"))
    urls = []
    for pod_url in pod_urls:
        print(pod_url)
        m = re.search('/([a-z]*)wiki',pod_url)
        lang = m.group(1)
        try:
            local_dir = join(dir_path, "app", "static", "webmap", lang)
            local_file = join(local_dir,pod_url.split('/')[-1].replace('?raw=true',''))
            with open (local_file, "wb") as f:
                f.write(requests.get(pod_url,allow_redirects=True).content)
            print("Pod downloaded to",local_file)
        except Exception:
            print("Request failed when trying to index", pod_url, "...")

        m, titles = joblib.load(local_file)
        pod_entry = db.session.query(Pods).filter_by(url=pod_url).first()
        print(m.shape,len(titles),titles[0])
        for i in range(len(titles)):
            title = titles[i]
            url = 'https://'+lang+'.wikipedia.org/wiki/'+title.replace(' ','_') #Hack, URLs should of course be provided
            vector = convert_to_string(m[i].toarray()[0])
            print(vector)
            if not db.session.query(Urls).filter_by(url=url).all():
                u = Urls(
                    url=url,
                    title=title,
                    snippet=title, #FIX
                    pod=pod_url.split('/')[-1].replace('?raw=true',''), #FIX
                    vector=vector,
                    cc=True if 'wikipedia.org' in url else False)
                urls.append(u)
        pod_entry.registered = True
        db.session.commit()
    def generate():
        if len(urls) == 0:
            print("All URLs already known.")
            yield "data:" + "100" + "\n\n" 
        else:
            c = 0
            for u in urls:
                #print("Adding",u.url,"to DB")
                try:
                    db.session.add(u)
                    db.session.commit()
                    c += 1
                except:
                    print("Failed to add",u.url,"to DB...")
                yield "data:" + str(int(c / len(urls) * 100)) + "\n\n"

    return Response(generate(), mimetype='text/event-stream')


'''Unsubscribe'''


@pod_finder.route('/unsubscribe/', methods=["POST"])
def unsubscribe():
    if request.form.getlist('pods') is not None:
        unsubscribed_pods = request.form.getlist('pods')
        for pod in unsubscribed_pods:
            print("Unsubscribing pod...", pod)
            pod_entries = db.session.query(Urls).filter_by(pod=pod).all()
            if pod_entries is not None:
                for e in pod_entries:
                    db.session.delete(e)
                    db.session.commit()
            pod_entry = db.session.query(Pods).filter_by(name=pod).first()
            if "localhost" in pod_entry.url:
                db.session.delete(pod_entry)
                db.session.commit()
            else:
                pod_entry.registered = False
                db.session.commit()
    return render_template(
        'pod_finder/unsubscribe-success.html', pods=unsubscribed_pods)
