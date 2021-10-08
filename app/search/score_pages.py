import numpy as np
import math
import pickle
import webbrowser
from urllib.parse import urlparse
import app
from app.api.models import Urls, Pods
from app import db
from .overlap_calculation import score_url_overlap, generic_overlap
from app.search import term_cosine
from app.indexer.mk_page_vector import compute_query_vectors
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist


def score_pods(q_hash,top):
    distances = cosine_similarity(q_hash,app.webmap.m)[0]
    #distances = cdist(np.array(q_hash.toarray()),app.webmap.m,'hamming')[0]
    print(distances)
    best_sim = np.argpartition(distances, -top)[-top:]
    best_pods= [app.webmap.metacats[i] for i in best_sim]
    return best_pods


def score_docs(q_hash, pod):
    '''Score documents for a query'''
    pod_mp = "./app/static/pods/"+pod+"/"+pod+".hs"
    pod_up = "./app/static/pods/"+pod+"/"+pod+".url"
    pod_m = pickle.load(open(pod_mp,'rb'))
    pod_urls = pickle.load(open(pod_up,'rb'))
    distances = cosine_similarity(q_hash,pod_m)[0]
    print(distances)
    top = min(20,len(distances)) #Number of docs to return
    best_sim = np.argpartition(distances, -top)[-top:]
    best_docs= {pod_urls[i]:distances[i] for i in best_sim}
    print(best_docs)
    return best_docs


def bestURLs(doc_scores):
    best_urls = []
    netlocs_used = []  # Don't return 100 pages from the same site
    c = 0
    for w in sorted(doc_scores, key=doc_scores.get, reverse=True):
        loc = urlparse(w).netloc
        if c < 50:
            if doc_scores[w] > 0:
                if netlocs_used.count(loc) < 10:
                    # print(w,doc_scores[w])
                    best_urls.append(w)
                    netlocs_used.append(loc)
                    c += 1
        else:
            break
    return best_urls


def ddg_redirect(query):
    print("No suitable pages found.")
    duckquery = ""
    for w in query.rstrip('\n').split():
        duckquery = duckquery + w + "+"
    webbrowser.open("https://duckduckgo.com/?q=" + duckquery.rstrip('+'))
    return


def output(best_urls):
    results = []
    pods = []
    if len(best_urls) > 0:
        for u in best_urls:
            results.append([
                u,u,u,u
                #get_db_url_title(u),
                #get_db_url_snippet(u),
                #get_db_url_cc(u)
            ])
            #pod = get_db_url_pod(u)
            pod = "TEST"
            if pod not in pods:
                pods.append(pod)
            # print(results)
    return results, pods


def run(query, pears):
    document_scores = {}
    q_hash = compute_query_vectors(query)
    best_pods = score_pods(q_hash,1) #Change 1 here if you want to return more than the top pod
    for pod in best_pods:
        print(pod)
        document_scores.update(score_docs(q_hash, pod))
    best_urls = bestURLs(document_scores)
    return output(best_urls)
