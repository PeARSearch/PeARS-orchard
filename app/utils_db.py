# SPDX-FileCopyrightText: 2022 Aurelie Herbelot, <aurelie.herbelot@unitn.it>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

import joblib
from app import db
from app.api.models import Urls, Pods
from app.api.models import installed_languages
from app.utils import convert_to_array, convert_string_to_dict, convert_to_string, normalise
from app.indexer.mk_page_vector import compute_query_vectors
import numpy as np
from os.path import dirname, realpath, join


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
    DS_vector = np.zeros(256) 
    for u in db.session.query(Urls).filter_by(pod=name).all():
        DS_vector += convert_to_array(u.vector)
    DS_vector = convert_to_string(normalise(DS_vector))
    c = 0
    return DS_vector


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


def pod_from_file(name, lang):
    url = "http://localhost:8080/api/pods/" + name.replace(' ', '+')
    # TODO: pods can't be named any old thing,
    # if they're going to be in localhost URLs
    if not db.session.query(Pods).filter_by(url=url).all():
        p = Pods(url=url)
        p.name = name
        p.description = name
        p.language = lang
        p.registered = True
        db.session.add(p)
        db.session.commit()
    p = Pods.query.filter(Pods.url == url).first()
    p.DS_vector = compute_pod_summary(name)
    db.session.commit()


def update_official_pod_list(lang):
    dir_path = dirname(realpath(__file__))
    print(dir_path)
    local_file = join(dir_path, "static", "webmap", lang, lang + "wiki.summary.fh")
    pod_ids, pod_keywords, pod_matrix = joblib.load(local_file)
    for i in range(len(pod_ids)):
        url = "https://github.com/PeARSearch/PeARS-public-pods-"+lang+"/blob/main/"+lang+"/"+pod_ids[i]+"?raw=true"
        #print(url)
        if not db.session.query(Pods).filter_by(url=url).all():
            p = Pods(url=url)
            db.session.add(p)
            db.session.commit()
        p = Pods.query.filter(Pods.url == url).first()
        p.name = pod_ids[i]
        p.description = pod_keywords[i]
        p.language = lang if lang != "en" else "simple"
        p.DS_vector = convert_to_string(pod_matrix[i])
        #print("PD",p.DS_vector)
        if not p.registered:
            p.registered = False
        db.session.commit()

