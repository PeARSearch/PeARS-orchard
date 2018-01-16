# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify, Response
from app.api.models import dm_dict_en, Pods
from app.utils_db import pod_from_json
from app import db
from app.pod_finder import score_pods
import requests
from os.path import dirname,join,realpath,isfile

dir_path = dirname(dirname(dirname(realpath(__file__))))

# Define the blueprint:
pod_finder = Blueprint('pod_finder', __name__, url_prefix='/pod_finder')

@pod_finder.route('/')
@pod_finder.route('/index', methods=['GET','POST'])
def index():
    pods = []
    for p in db.session.query(Pods).filter_by(registered=True).all():
        print(p.name,p.description)
        pods.append([p.name,p.description])
    return render_template('pod_finder/index.html',pods=pods)

'''Update pod list'''

@pod_finder.route('/update-pod-list/', methods=['POST','GET'])
def update_pod_list():
    return render_template('pod_finder/progress_pod_update.html')

@pod_finder.route("/progress_pod_update")
def progress_pod_update():
    print("Running progress pod update")
    pods = []
    r = requests.get("http://www.openmeaning.org/pod0/api/pods/")
    for pod in r.json()['json_list']:
        pods.append(pod)
    def generate():
        c = 0
        for pod in pods:
            pod_from_json(pod,pod['url'])
            c+=1
            yield "data:" + str(int(c/len(pods)*100)) + "\n\n"
    return Response(generate(), mimetype= 'text/event-stream')

'''Find a pod'''

@pod_finder.route('/find-a-pod/')
def find_a_pod():
    query = request.args.get('search-pod')
    print(request,request.args,query)
    pods = score_pods.run(query)
    return render_template('pod_finder/find-a-pod.html',pods=pods)

@pod_finder.route("/subscribe", methods=["POST"])
def subscribe():
    if request.form.getlist('pods') != None:
        print("Writing to",join(dir_path,"pods_to_index.txt"))
        f = open(join(dir_path, "pods_to_index.txt"),'w')
        for pod in request.form.getlist('pods'):
            print(pod)
            f.write(pod+"\n")
        f.close()
    return render_template('indexer/progress_pod.html')


'''Unsubscribe'''
@pod_finder.route('/unsubscribe/')
def unsubscribe():
    return render_template('pod_finder/index.html',pods=[])

