""" Compares the query to each document
Called by ./mkQueryPage.py
"""

import os, requests
import re
import sys
from urllib.parse import urlparse
from operator import itemgetter
import math
import numpy
from app.api.models import Urls
from app.utils_db import get_db_url_snippet, get_db_url_title, get_db_url_cc, get_db_url_pod

from .overlap_calculation import score_url_overlap, generic_overlap
from app.search import term_cosine
from app.utils import cosine_similarity, convert_to_array
from app.indexer.mk_page_vector import compute_query_vectors

def score(query, query_dist, query_freqs):
    """ Get distributional score """
    DS_scores = {}
    URL_scores = {}
    title_scores = {}
    term_scores = {}
    coverages = {}
    for u in Urls.query.all():
        DS_scores[u.url] = cosine_similarity(convert_to_array(u.vector), query_dist)
        URL_scores[u.url] = score_url_overlap(query, u.url)
        title_scores[u.url] = generic_overlap(query, u.title)
        term_scores[u.url], coverages[u.url] = term_cosine.run(query, query_freqs, u.freqs)
    return DS_scores, URL_scores, title_scores, term_scores, coverages


def score_docs(query, query_dist, query_freqs):
    """ Score documents for a pear """
    document_scores = {}  # Document scores
    DS_scores, URL_scores, title_scores, term_scores, coverages = score(query,query_dist,query_freqs)
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
              print(w,doc_scores[w])
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
    webbrowser.open_new_tab(
            "https://duckduckgo.com/?q=" +
            duckquery.rstrip('+'))
    return

def output(best_urls):
    results = []
    pods = []
    # If documents matching the query were found on the pear network...
    if len(best_urls) > 0:
        for u in best_urls:
            results.append([u, get_db_url_title(u), get_db_url_snippet(u), get_db_url_cc(u)])
            pod = get_db_url_pod(u)
            if pod not in pods:
                pods.append(pod)
            #print(results)
    return results, pods


def run(query, pears):
    best_urls = []
    q_dist, q_freqs = compute_query_vectors(query)
    for pear in pears:
        #print(pear)
        document_scores = score_docs(query, q_dist, q_freqs)	#with URL overlap
        best_urls = bestURLs(document_scores)
    return output(best_urls)

