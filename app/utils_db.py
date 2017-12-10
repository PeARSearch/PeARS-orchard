from app import db
from app.api.models import Urls
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
    
