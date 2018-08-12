import math
from app import db
from app.api.models import Pods
from app.utils_db import (
    get_db_pod_name, get_db_pod_description, get_db_pod_language)

from app.search import term_cosine
from app.utils import cosine_similarity, convert_to_array
from app.indexer.mk_page_vector import compute_query_vectors


def score(query, query_dist, query_freqs):
    """ Get distributional score """
    DS_scores = {}
    term_scores = {}
    coverages = {}
    for p in db.session.query(Pods).filter_by(registered=False).all():
        DS_scores[p.url] = cosine_similarity(convert_to_array(p.DS_vector), query_dist)
        term_scores[p.url], coverages[p.url] = term_cosine.run(query, query_freqs, p.word_vector)
        #print(p.url,DS_scores[p.url], term_scores[p.url])
    return DS_scores, term_scores


def score_pods(query, query_dist, query_freqs):
    """ Score pods for a query """
    pod_scores = {}  # Pod scores
    DS_scores, term_scores = score(query, query_dist, query_freqs)
    for pod in list(DS_scores.keys()):
        pod_scores[pod] = DS_scores[pod] + term_scores[pod]
        if math.isnan(
                pod_scores[pod]
        ):  # Check for potential NaN -- messes up with sorting in bestURLs.
            pod_scores[pod] = 0

    return pod_scores


def bestPods(pod_scores):
    best_pods = []
    c = 0
    for w in sorted(pod_scores, key=pod_scores.get, reverse=True):
        if c < 3:
            best_pods.append(w)
            c += 1
        else:
            break
    return best_pods


def output(best_pods):
    results = []
    if len(best_pods) > 0:
        for p in best_pods:
            results.append([
                p,
                get_db_pod_name(p),
                get_db_pod_language(p),
                get_db_pod_description(p)
            ])
            #print(results)
    return results


def run(query):
    print("Looking for pods for query", query)
    best_pods = []
    if query != "":
        q_dist, q_freqs = compute_query_vectors(query)
        pod_scores = score_pods(query, q_dist, q_freqs)  # with URL overlap
        best_pods = bestPods(pod_scores)
    else:
        all_pods = [p.url for p in db.session.query(Pods).filter_by(registered=False).all()]
        best_pods = all_pods
    return output(best_pods)
