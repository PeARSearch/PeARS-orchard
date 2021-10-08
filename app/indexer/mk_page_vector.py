import re
import numpy as np
import string
import glob
import pickle
import app
from app import db
from app.api.models import Urls
from scipy.sparse import csr_matrix, vstack
from app.utils import  wta, return_keywords, hash_dataset_, inspect_hash_projections
from app.indexer.htmlparser import extract_from_url


def hash(doc):
    # Move vocab and vectorizer defs -- they should be at the top level
    top_words=250
    ll = app.sp.encode_as_pieces(doc)
    X = app.vectorizer.fit_transform([" ".join(ll)])
    X = csr_matrix(X)
    pn_mat = X.multiply(app.logprobs)
    hashes= [np.array([])]
    hashes = np.append(hashes, X)
    hs_mat = hash_dataset_(dataset_mat=vstack(hashes), weight_mat=app.fruitfly.projection,
                     percent_hash=app.fruitfly.wta, top_words=top_words)

    #Abusing wta
    hs = wta(X.toarray()[0], top_words, percent=False)
    kwds = [app.reverse_vocab[w] for w in return_keywords(hs)]
    return hs_mat, kwds

def compute_vectors(target_url, category):
    print("Fly",app.fruitfly.kc_size)
    print("Computing vectors for", target_url)
    if not db.session.query(Urls).filter_by(url=target_url).all():
        u = Urls(url=target_url)
        title, body_str, snippet, cc = extract_from_url(target_url)
        if title != "":
            text = title + " " + body_str
            vector,keywords = hash(text)
            u.title = str(title)
            u.category = category.replace(' ','_')
            u.pod = "Me"
            if snippet != "":
                u.snippet = str(snippet)
            else:
                u.snippet = u.title
            if cc:
                u.cc = True
            print(u.url,u.title,u.snippet,u.cc)
            db.session.add(u)
            db.session.commit()
            hs_file='./app/static/pods/'+u.category+".hs"
            if not hs_file in glob.glob('./app/static/pods/*.hs'):
                print("This category is unknown.")
                pickle.dump(vector, open(hs_file, 'wb'))
                pickle.dump([target_url], open(hs_file.replace(".hs", ".urls"), 'wb'))
            else:
                print("This category is already known.")
                old_mat = pickle.load(open(hs_file, 'rb'))
                hs_matrix = vstack([old_mat, vector])
                pickle.dump(hs_matrix, open(hs_file, 'wb'))

                urls = pickle.load(open(hs_file.replace(".hs", ".urls"), 'rb'))
                urls.append(target_url)
                pickle.dump(urls, open(hs_file.replace(".hs", ".urls"), 'wb'))
            return True
        else:
            return False
    else:
        return True


def compute_query_vectors(query):
    q_hash,keywords = hash(query)
    print(q_hash)
    print(keywords)
    print("QHASH")
    inspect_hash_projections(q_hash,app.reverse_vocab,app.fruitfly.projection)
    return q_hash
