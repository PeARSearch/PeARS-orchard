# Import flask dependencies
from flask import Blueprint, request, render_template, Response
from werkzeug import secure_filename
import requests, csv, sys
from os.path import dirname, join, realpath
from app import db
from app.api.models import Pods, Urls
from app.utils import readPods, get_pod_info
from app.utils_db import pod_from_json, url_from_json, pod_from_file, pod_from_scratch
from app.pod_finder import score_pods, index_pod_file
from app.pod_finder.update_pod_list import update_pod_list

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
    pods = update_pod_list()
    for p in pods:
        pod_from_scratch(p[0],p[1],p[2],p[3])
    query = request.args.get('search-pod')
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
    if filename[-3:] == "csv":
        file.save(join(dir_path, "app", "static", "pods", "urls_from_pod.csv"))
    if filename[-3:] == "png":
        file.save(join(dir_path, "app", "static", "pods", "urls_from_pod.png"))
        index_pod_file.convert_img_to_csv()
    return render_template('pod_finder/progress_file.html')


@pod_finder.route("/progress_file")
def progress_file():
    def generate():
        c = 0
        urls = list()
        pod_name = ""
        print(len(urls))
        f = open(
            join(dir_path, "app", "static", "pods", "urls_from_pod.csv"),
            'r',
            encoding="utf-8")
        for l in f:
            if "#Pod name" in l:
                pod_name = l.rstrip('\n').replace("#Pod name:", "")
            fields = l.rstrip('\n').split(',')
            if len(fields) == 7:
                url, title, snippet, vector, freqs, cc = index_pod_file.parse_line(fields)
                if not db.session.query(Urls).filter_by(url=url).all():
                    u = Urls(
                        url=url,
                        title=title,
                        snippet=snippet,
                        pod=pod_name,
                        vector=vector,
                        freqs=freqs,
                        cc=cc)
                    urls.append(u)
        f.close()
        if len(urls) == 0:
            print("All URLs already known.")
            yield "data:" + "100" + "\n\n"
        else:
            for u in urls:
                db.session.add(u)
                db.session.commit()
                c += 1
                yield "data:" + str(int(c / len(urls) * 100)) + "\n\n"
                pod_from_file(pod_name)

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
        with requests.Session() as s:
            download = s.get(pod_url)
            decoded_content = download.content.decode('utf-8')
            crows = csv.reader(decoded_content.splitlines(), delimiter=',')
            records = list(crows)
        pod_entry = db.session.query(Pods).filter_by(url=pod_url).first()
        for u in records:
            if len(u) == 7:
                url, title, snippet, vector, freqs, cc = index_pod_file.parse_line(u)
                if not db.session.query(Urls).filter_by(url=url).all():
                    u = Urls(
                        url=url,
                        title=title,
                        snippet=snippet,
                        pod=pod_entry.name,
                        vector=vector,
                        freqs=freqs,
                        cc=cc)
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
