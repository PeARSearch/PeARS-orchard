from math import sqrt
import numpy as np
import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def readDM(dm_file):
    dm_dict = {}
    version = ""
    with open(dm_file) as f:
        dmlines = f.readlines()
    f.close()

    # Make dictionary with key=row, value=vector
    for l in dmlines:
        if "#Version:" in l:
            version = l.rstrip('\n').replace("#Version:", "")
        items = l.rstrip().split()
        row = items[0]
        vec = [float(i) for i in items[1:]]
        vec = np.array(vec)
        dm_dict[row] = vec
    return dm_dict, version


def readUrls(url_file):
    urls = []
    keywords = []
    f = open(url_file, 'r')
    for line in f:
        try:
            line = line.rstrip('\n').split(';')
            urls.append(line[0])
            keywords.append(line[1])
        except:
            print("ERROR: Problem reading",line)
    f.close()
    return urls, keywords

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
