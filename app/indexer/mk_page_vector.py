import re
import numpy as np
import string
from app import db
from app.api.models import Urls, installed_languages, model_configs, reducers, flies, sp
from app.indexer.htmlparser import extract_from_url
from app.utils import convert_to_string, convert_dict_to_string, normalise
from app.indexer.apply_models import return_hash

num_dimensions = 400

stopwords = [
    "", "(", ")", "a", "about", "an", "and", "are", "around", "as", "at",
    "away", "be", "become", "became", "been", "being", "by", "did", "do",
    "does", "during", "each", "for", "from", "get", "have", "has", "had", "he",
    "her", "his", "how", "i", "if", "in", "is", "it", "its", "made", "make",
    "many", "most", "not", "of", "on", "or", "s", "she", "some", "that", "the",
    "their", "there", "this", "these", "those", "to", "under", "was", "were",
    "what", "when", "where", "which", "who", "will", "with", "you", "your"
]


def tokenize_text(lang, text):
    print(text)
    sp.load(f'app/api/models/{lang}/{lang}wiki.model')
    text = ' '.join([wp for wp in sp.encode_as_pieces(text.lower())])
    return text


def compute_freq_vector(text):
    freqs = {}
    for w in text:
        if w not in stopwords and w not in string.punctuation:
            if w in freqs:
                freqs[w] += 1
            else:
                freqs[w] = 1
    return freqs


def compute_dist_vector(text, dm_dict):
    vbase = np.zeros(num_dimensions)
    for w in text:
        if w not in stopwords and w in dm_dict:
            vbase += dm_dict[w]
    return vbase


def compute_fly_hash(lang, text):
    ridge = reducers[lang]
    fly = flies[lang]
    hs = return_hash(lang, text, ridge, fly, int(model_configs[lang]['PREPROCESSING']['logprob_power']))
    #print("FRUIT FLY HS:",hs.toarray()[0])
    return hs.toarray()[0]

def compute_vectors(target_url, keyword):
    print("Computing vectors for", target_url)
    if not db.session.query(Urls).filter_by(url=target_url).all():
        u = Urls(url=target_url)
        title, body_str, snippet, cc = extract_from_url(target_url)
        if title != "":
            text = title + " " + body_str
            text = tokenize_text('simple', text)
            vector = compute_fly_hash('simple', text)
            freqs = compute_freq_vector(text)
            u.title = str(title)
            u.vector = convert_to_string(vector)
            u.freqs = convert_dict_to_string(freqs)
            if keyword == "":
                keyword = "generic"
            u.keyword = keyword
            u.pod = keyword
            if snippet != "":
                u.snippet = str(snippet)
            else:
                u.snippet = u.title
            if cc:
                u.cc = True
            print(u.url,u.title,u.vector,u.snippet,u.cc,u.pod)
            db.session.add(u)
            db.session.commit()
            return True
        else:
            return False
    else:
        return True


def compute_query_vectors(query):
    """ Make distribution for query """
    #query = query.rstrip('\n')
    #words = query.split()
    text = tokenize_text('simple', query)
    print(text)
    vector = compute_fly_hash('simple', text)
    #print("FFH",vector,vector.shape)
    #freqs = compute_freq_vector(words)
    return vector
