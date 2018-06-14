from app.utils import cosine_similarity, convert_string_to_dict, normalise
import numpy as np


def return_keys(d1, d2):
    k1 = list(d1.keys())
    k2 = list(d2.keys())
    keys = k1 + k2
    return list(set(keys))


def mk_vector(d, dimensions):
    d_vec = np.zeros(len(dimensions))
    for i in range(len(d_vec)):
        if dimensions[i] in d:
            d_vec[i] = int(d[dimensions[i]])
    return d_vec


def binarise(d):
    return (d > 0).astype(int)


def run(q, d1, d2_s):
    d2 = convert_string_to_dict(d2_s)

    dimensions = return_keys(d1, d2)
    v1 = mk_vector(d1, dimensions)
    v2 = mk_vector(d2, dimensions)
    v1_bin = binarise(v1)
    v2_bin = binarise(v2)

    coverage = sum(v1_bin * v2_bin) / len(q.split())

    d1_vec = normalise(v1)
    d2_vec = normalise(v2)

    return cosine_similarity(d1_vec, d2_vec), coverage
