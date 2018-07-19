from app import db
from app.api.models import Urls, Pods
from app.utils import (
    convert_to_array, convert_string_to_dict, convert_to_string, normalise)
from app.indexer.mk_page_vector import compute_query_vectors
import numpy as np


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


def get_db_url_pod(url):
    url_pod = Urls.query.filter(Urls.url == url).first().pod
    return url_pod


def get_db_pod_description(url):
    pod_description = Pods.query.filter(Pods.url == url).first().description
    return pod_description


def get_db_pod_language(url):
    pod_language = Pods.query.filter(Pods.url == url).first().language
    return pod_language


def compute_pod_summary(name):
    '''This function is very similar to 'self' in PeARS-pod'''
    DS_vector = np.zeros(400)
    word_vector = ""
    freqs = {}
    for u in db.session.query(Urls).filter_by(pod=name).all():
        DS_vector += convert_to_array(u.vector)
        for k, v in convert_string_to_dict(u.freqs).items():
            if k in freqs:
                freqs[k] += int(v)
            else:
                freqs[k] = int(v)
    DS_vector = convert_to_string(normalise(DS_vector))
    c = 0
    for w in sorted(freqs, key=freqs.get, reverse=True):
        word_vector += w + ':' + str(freqs[w]) + ' '
        c += 1
        if c == 300:
            break
    return DS_vector, word_vector


def url_from_json(url, pod):
    # print(url)
    if not db.session.query(Urls).filter_by(url=url['url']).all():
        u = Urls(url=url['url'])
        u.url = url['url']
        u.title = url['title']
        u.vector = url['vector']
        u.freqs = url['freqs']
        u.snippet = url['snippet']
        u.pod = pod
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


def pod_from_file(name):
    url = "http://localhost:8080/api/pods/" + name.replace(
        ' ', '+'
    )
    # TODO: pods can't be named any old thing,
    # if they're going to be in localhost URLs
    if not db.session.query(Pods).filter_by(url=url).all():
        p = Pods(url=url)
        p.name = name
        p.description = name
        p.language = "UNK"
        p.registered = True
        db.session.add(p)
        db.session.commit()
    p = Pods.query.filter(Pods.url == url).first()
    p.DS_vector, p.word_vector = compute_pod_summary(name)
    db.session.commit()

def pod_from_scratch(name,url,language,description):
    if not db.session.query(Pods).filter_by(url=url).all():
        p = Pods(url=url)
        db.session.add(p)
        db.session.commit()
    p = Pods.query.filter(Pods.url == url).first()
    p.name = name
    p.description = description
    p.language = language
    #Using compute_query_vector as hack to get vectors from pod's name 
    vector, freqs = compute_query_vectors(name.lower()+' '+description.lower())
    p.DS_vector = convert_to_string(normalise(vector))
    word_vector = ""
    c = 0
    for w in sorted(freqs, key=freqs.get, reverse=True):
        word_vector += w + ':' + str(freqs[w]) + ' '
        c += 1
        if c == 300:
            break
    p.word_vector = word_vector
    if not p.registered:
        p.registered = False
    db.session.commit()
