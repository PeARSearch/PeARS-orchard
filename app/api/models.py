from app import db
from app.utils import convert_to_array
import numpy as np
import configparser
import joblib
from glob import glob
from os.path import isdir
import sentencepiece as spm

sp = spm.SentencePieceProcessor()

# Build semantic spaces - LEGACY

# Record language codes - LEGACY
language_codes = {}

# New language codes
def get_installed_languages():
    installed_languages = []
    language_paths = glob('./app/api/models/*/')
    for p in language_paths:
        lang = p[:-1].split('/')[-1]
        installed_languages.append(lang)
    print("Installed languages:",installed_languages)
    return installed_languages

installed_languages = get_installed_languages()

# Load model configuration files
def read_configs():
    model_configs = {}
    for lang in installed_languages:
        config_path = './app/api/models/'+lang+'/'+lang+'.hyperparameters.cfg'
        config = configparser.ConfigParser()
        config.read(config_path)
        model_configs[lang] = config
    return model_configs

model_configs = read_configs()

# Load dimensionality reducers
reducers = {}
for lang in installed_languages:
    reducer_type = model_configs[lang]['REDUCER']['type']
    if reducer_type == 'PCA':
        reducers[lang] = joblib.load(f'./app/api/models/{lang}/{lang}wiki-latest-pages-articles.train.pca')
    else:
        reducers[lang] = joblib.load(f'./app/api/models/{lang}/{lang}wiki-latest-pages-articles.train.hacked.umap')

# Load flies
flies = {}
for lang in installed_languages:
    flies[lang] = joblib.load(f'./app/api/models/{lang}/fly.m')


# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())


class Urls(Base):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    vector = db.Column(db.String(7000))
    freqs = db.Column(db.String(7000))
    snippet = db.Column(db.String(1000))
    cc = db.Column(db.Boolean)
    pod = db.Column(db.String(1000))
    keyword = db.Column(db.String(1000))

    def __init__(self,
                 url=None,
                 title=None,
                 vector=None,
                 freqs=None,
                 snippet=None,
                 cc=False,
                 pod=None,
                 keyword=None):
        self.url = url
        self.title = title
        self.vector = vector
        self.freqs = freqs
        self.snippet = snippet
        self.cc = cc
        self.pod = pod
        self.keyword = keyword

    def __repr__(self):
        return self.url

    @property
    def serialize(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'vector': self.vector,
            'freqs': self.freqs,
            'snippet': self.snippet,
            'cc': self.cc,
            'pod': self.pod,
            'keyword': self.keyword
        }


class Pods(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    url = db.Column(db.String(1000))
    description = db.Column(db.String(7000))
    language = db.Column(db.String(1000))
    DS_vector = db.Column(db.String(7000))
    word_vector = db.Column(db.String(7000))
    registered = db.Column(db.Boolean)

    def __init__(self,
                 name=None,
                 url=None,
                 description=None,
                 language=None,
                 DS_vector=None,
                 word_vector=None,
                 registered=False):
        self.name = name
        self.url = url
        self.description = description
        self.language = language

    @property
    def serialize(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'language': self.language,
            'DSvector': self.DS_vector,
            'wordvector': self.word_vector,
            'registered': self.registered
        }


# The urls matrix
def mk_matrix_from_db():
    print("Making URL matrix from database...")
    urls = []
    DS_M = []
    url_to_mat = {}
    mat_to_url = {}
    try:
        urls = Urls.query.all()
        print("Found", len(urls), "records...")
    except Exception:
        print("Database empty")
    if len(urls) > 0:
        c = 0
        DS_M = convert_to_array(urls[0].vector).reshape(1, 400)
        url_to_mat[urls[0].url] = c
        mat_to_url[c] = urls[0].url
        c += 1
        for u in urls[1:]:
            DS_M = np.vstack((DS_M, convert_to_array(u.vector).reshape(1,
                                                                       400)))
            url_to_mat[u.url] = c
            mat_to_url[c] = u.url
            c += 1
    return DS_M, url_to_mat, mat_to_url


# DS_M, url_to_mat, mat_to_url = mk_matrix_from_db()

# db.drop_all()
# db.create_all()
