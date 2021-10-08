import logging
import re
import requests

from scipy.sparse import csr_matrix, vstack
from bs4 import BeautifulSoup
from math import sqrt
import numpy as np
from urllib.parse import urljoin


# Fruit-fly-related stuff

def read_vocab():
    c = 0
    vocab = {}
    reverse_vocab = {}
    logprobs = []
    with open("./app/static/spm/spmcc.vocab") as f:
        for l in f:
            l = l.rstrip('\n')
            wp = l.split('\t')[0]
            logprob = -(float(l.split('\t')[1]))
            #logprob = log(lp + 1.1)
            if wp in vocab or wp == '':
                continue
            vocab[wp] = c
            reverse_vocab[c] = wp
            logprobs.append(logprob**3)
            c+=1
    return vocab, reverse_vocab, logprobs

def wta_vectorized(feature_mat, k, percent=True):
    # thanks https://stackoverflow.com/a/59405060

    m, n = feature_mat.shape
    if percent:
        k = int(k * n / 100)
    # get (unsorted) indices of top-k values
    topk_indices = np.argpartition(feature_mat, -k, axis=1)[:, -k:]
    # get k-th value
    rows, _ = np.indices((m, k))
    kth_vals = feature_mat[rows, topk_indices].min(axis=1)
    # get boolean mask of values smaller than k-th
    is_smaller_than_kth = feature_mat < kth_vals[:, None]
    # replace mask by 0
    feature_mat[is_smaller_than_kth] = 0
    return feature_mat


def wta(layer, top, percent=True):
    activations = np.zeros(len(layer))
    if percent:
        top = int(top * len(layer) / 100)
    activated_cs = np.argpartition(layer, -top)[-top:]
    for cell in activated_cs:
        activations[cell] = layer[cell]
    return activations

def hash_input_vectorized_(pn_mat, weight_mat, percent_hash):
    kc_mat = pn_mat.dot(weight_mat.T)
    m, n = kc_mat.shape
    wta_csr = csr_matrix(np.zeros(n))
    for i in range(0, m, 2000):
        part = wta_vectorized(kc_mat[i: i+2000].toarray(), k=percent_hash)
        wta_csr = vstack([wta_csr, csr_matrix(part, shape=part.shape)])
    hashed_kenyon = wta_csr[1:]
    return hashed_kenyon

def hash_dataset_(dataset_mat, weight_mat, percent_hash, top_words):
    m, n = dataset_mat.shape
    dataset_mat = csr_matrix(dataset_mat)
    wta_csr = csr_matrix(np.zeros(n))
    for i in range(0, m, 2000):
        part = wta_vectorized(dataset_mat[i: i+2000].toarray(), k=top_words, percent=False)
        wta_csr = vstack([wta_csr, csr_matrix(part, shape=part.shape)])
    hs = hash_input_vectorized_(wta_csr[1:], weight_mat, percent_hash)
    return hs

def return_keywords(vec):
    keywords = []
    vs = np.argsort(vec)
    for i in vs[-10:]:
        keywords.append(i)
    return keywords

def inspect_hash_projections(h,reverse_vocab,fly_projs):
    h = h.toarray()[0]
    top_projs = np.argsort(-h)[:20]
    for proj in top_projs:
        if h[proj] > 0:
            a = np.squeeze(fly_projs[proj].toarray())
            words = [reverse_vocab[i] for i in np.where(a > 0)[0]]
            print(words)


def _extract_url_and_kwd(line):
    # The following regexp pattern matches lines in the form "url;keyword". This
    # accepts both http and https link as of now
    pattern = "(https?://\S+);(.+)"
    return re.match(pattern, line)

def readUrls(url_file):
    urls = []
    keywords = []
    errors = False
    with open(url_file) as fd:
        for line in fd:
            matches = _extract_url_and_kwd(line)
            if matches:
                urls.append(matches.group(1))
                keywords.append(matches.group(2))
            else:
                errors = True
    return urls, keywords, errors

def readBookmarks(bookmark_file, keyword):
    urls = []
    bs_obj = BeautifulSoup(open(bookmark_file), "html.parser")
    links = bs_obj.find_all('a', {'tags' : keyword})
    for l in links:
        urls.append(l['href'])
    return urls


def readPods(pod_file):
    pods = []
    f = open(pod_file, 'r')
    for line in f:
        line = line.rstrip('\n')
        pods.append(line)
    f.close()
    return pods


def normalise(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def convert_to_string(vector):
    vector_str = ""
    for n in vector:
        vector_str = vector_str + "%.6f" % n + " "
    return vector_str[:-1]


def convert_to_array(vector):
    # for i in vector.rstrip(' ').split(' '):
    #    print('#',i,float(i))
    return np.array([float(i) for i in vector.rstrip(' ').split(' ')])


def convert_dict_to_string(dic):
    s = ""
    for k, v in dic.items():
        s += k + ':' + str(v) + ' '
    return s


def convert_string_to_dict(s):
    d = {}
    els = s.rstrip(' ').split()
    for e in els:
        if ':' in e:
            pair = e.split(':')
            if pair[0] != "" and pair[1] != "":
                d[pair[0]] = pair[1]
    return d


def cosine_similarity(v1, v2):
    if len(v1) != len(v2):
        return 0.0
    num = np.dot(v1, v2)
    den_a = np.dot(v1, v1)
    den_b = np.dot(v2, v2)
    return num / (sqrt(den_a) * sqrt(den_b))


def cosine_to_matrix(q, M):
    qsqrt = sqrt(np.dot(q, q))
    if qsqrt == 0:
        return np.zeros(M.shape[0])
    qMdot = np.dot(q, M.T)
    Mdot = np.dot(M, M.T)
    Msqrts = [sqrt(Mdot[i][i]) for i in range(len(Mdot[0]))]
    cosines = []
    for i in range(len(Mdot[0])):
        if Msqrts[i] != 0:
            cosines.append(qMdot[i] / (qsqrt * Msqrts[i]))
        else:
            cosines.append(0)
    return cosines


def sim_to_matrix(dm_dict, vec, n):
    cosines = {}
    c = 0
    for k, v in dm_dict.items():
        try:
            cos = cosine_similarity(vec, v)
            cosines[k] = cos
            c += 1
        except Exception:
            pass
    c = 0
    neighbours = []
    for t in sorted(cosines, key=cosines.get, reverse=True):
        if c < n:
            if t.isalpha():
                print(t, cosines[t])
                neighbours.append(t)
                c += 1
        else:
            break
    return neighbours


def sim_to_matrix_url(url_dict, vec, n):
    cosines = {}
    for k, v in url_dict.items():
        logging.exception(v.url)
        try:
            cos = cosine_similarity(vec, v.vector)
            cosines[k] = cos
        except Exception:
            pass
    c = 0
    neighbours = []
    for t in sorted(cosines, key=cosines.get, reverse=True):
        if c < n:
            # print(t,cosines[t])
            neighbour = [t, url_dict[t].title, url_dict[t].snippet]
            neighbours.append(neighbour)
            c += 1
        else:
            break
    return neighbours


def get_pod_info(url):
    print("Fetching pod", urljoin(url, "api/self/"))
    pod = None
    try:
        r = requests.get(urljoin(url, "api/self/"))
        if r.status_code == 200:
            pod = r.json()
    except Exception:
        print("Problem fetching pod...")
    return pod


def get_pod0_message():
    msg = ""
    try:
        r = requests.get(
            "http://www.openmeaning.org/pod0/api/message/", timeout=1)
        if r.status_code == 200:
            msg = r.json()['message']
    except Exception:
        print("Problem contacting pod0...")
    return msg
