from app import db
from app.api.models import Urls, Pods
import json

def get_db_url_vector(url):
    url_vec = Urls.query.filter(Urls.url == url).first().vector
    return url_vec

def get_db_url_snippet(url):
    url_snippet = Urls.query.filter(Urls.url == url).first().snippet
    return url_snippet

def get_db_url_title(url):
    url_title = Urls.query.filter(Urls.url == url).first().title
    return url_title

def get_db_url_cc(url):
    url_cc = Urls.query.filter(Urls.url == url).first().cc
    return url_cc

def get_db_pod_name(url):
    pod_name = Pods.query.filter(Pods.url == url).first().name
    return pod_name

def get_db_pod_description(url):
    pod_description = Pods.query.filter(Pods.url == url).first().description
    return pod_description

def get_db_pod_language(url):
    pod_language = Pods.query.filter(Pods.url == url).first().language
    return pod_language

def url_from_json(url):
    #print(url)
    if not db.session.query(Urls).filter_by(url=url['url']).all():
        u = Urls(url=url['url'])
        u.url = url['url']
        u.title = url['title']
        u.vector = url['vector']
        u.freqs = url['freqs']
        u.snippet = url['snippet']
        if url['cc']:
            u.cc = True
        db.session.add(u)
        db.session.commit()

def pod_from_json(pod, url):
    if not db.session.query(Pods).filter_by(url=url).all():
        p = Pods(url=url)
        db.session.add(p)
        db.session.commit()
    p = Pods.query.filter(Pods.url == url).first()
    p.name = pod['name']
    p.description = pod['description']
    p.language = pod['language']
    p.DS_vector = pod['DSvector']
    p.word_vector = pod['wordvector']
    if not p.registered:
        p.registered = False
    db.session.commit()
        
    
