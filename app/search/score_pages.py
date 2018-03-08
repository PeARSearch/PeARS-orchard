import os, requests
import re
import webbrowser
from urllib.parse import urlparse
import math
from app.api.models import Urls, Pods
from app import db
#from app.api.models import DS_M, url_to_mat
from app.utils_db import get_db_url_snippet, get_db_url_title, get_db_url_cc, get_db_url_pod

from .overlap_calculation import score_url_overlap, generic_overlap
from app.search import term_cosine
from app.utils import cosine_similarity, cosine_to_matrix, convert_to_array
from app.indexer.mk_page_vector import compute_query_vectors

def score(query, query_dist, query_freqs, pod):
    """ Get various scores -- This is slow, slow, slow. Add code for vec to matrix calculations """
    DS_scores = {}
    URL_scores = {}
    title_scores = {}
    term_scores = {}
    coverages = {}
    #cosines = cosine_to_matrix(query_dist,DS_M)	#Code for vec to matrix cosine calculation -- work in progress
    for u in db.session.query(Urls).filter_by(pod=pod).all():
        DS_scores[u.url] = cosine_similarity(convert_to_array(u.vector), query_dist)
        #DS_scores[u.url] = cosines[url_to_mat[u.url]]
        URL_scores[u.url] = score_url_overlap(query, u.url)
        title_scores[u.url] = generic_overlap(query, u.title)
        term_scores[u.url], coverages[u.url] = term_cosine.run(query, query_freqs, u.freqs)
    return DS_scores, URL_scores, title_scores, term_scores, coverages

def score_pods(query, query_dist, query_freqs):
    '''Score pods for a query'''
    pod_scores = {}
    score_sum = 0.0
    pods=db.session.query(Pods).filter_by(registered=True).all()
    for p in pods:
        DS_score = cosine_similarity(convert_to_array(p.DS_vector), query_dist)
        term_score, coverage = term_cosine.run(query, query_freqs, p.word_vector)
        score = DS_score + term_score + 2 * coverage
        if math.isnan(score):
            score = 0
        pod_scores[p.name] = score
        score_sum+=score
    print(pod_scores)

    '''If all scores are rubbish, search entire pod collection (we're desperate!)'''
    if score_sum < 1:
         return list(pod_scores.keys())
    else:
        best_pods = []
        for k in sorted(pod_scores, key=pod_scores.get, reverse=True):
            if len(best_pods) < 1:
                best_pods.append(k)
            else:
                break
        return best_pods

def score_docs(query, query_dist, query_freqs, pod):
    '''Score documents for a query'''
    document_scores = {}  # Document scores
    DS_scores, URL_scores, title_scores, term_scores, coverages = score(query,query_dist,query_freqs, pod)
    for url in list(DS_scores.keys()):
        #print(url,DS_scores[url], title_scores[url], term_scores[url])
        document_scores[url] = DS_scores[url] + title_scores[url] + term_scores[url] + 2 *coverages[url]
        if math.isnan(document_scores[url]):  # Check for potential NaN -- messes up with sorting in bestURLs.
            document_scores[url] = 0
    return document_scores


def bestURLs(doc_scores):
    best_urls = []
    netlocs_used = [] #Don't return 100 pages from the same site
    c = 0
    for w in sorted(doc_scores, key=doc_scores.get, reverse=True):
        loc = urlparse(w).netloc
        if c < 50:
          if loc not in netlocs_used and doc_scores[w] > 0:
              #print(w,doc_scores[w])
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
            results.append([u, get_db_url_title(u), get_db_url_snippet(u), get_db_url_cc(u)])
            pod = get_db_url_pod(u)
            if pod not in pods:
                pods.append(pod)
            #print(results)
    return results, pods


def run(query, pears):
    document_scores = {}
    q_dist, q_freqs = compute_query_vectors(query)
    best_pods = ["Me"]+score_pods(query, q_dist, q_freqs)
    for pod in best_pods:
        print(pod)
        document_scores.update(score_docs(query, q_dist, q_freqs, pod))
    best_urls = bestURLs(document_scores)
    return output(best_urls)

