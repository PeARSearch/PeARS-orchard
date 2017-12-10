from app.utils import cosine_similarity, convert_string_to_dict, normalise
import numpy as np
from math import sqrt

def return_keys(d1,d2):
    k1 = list(d1.keys())
    k2 = list(d2.keys())
    keys = k1+k2
    return list(set(keys))

def mk_vector(d, dimensions):
    d_vec = np.zeros(len(dimensions))
    for i in range(len(d_vec)):
        if dimensions[i] in d:
            d_vec[i] = int(d[dimensions[i]])
    return d_vec

def run(d1,d2_s):
    d2 = convert_string_to_dict(d2_s)

    dimensions = return_keys(d1,d2)
    d1_vec = normalise(mk_vector(d1,dimensions))
    d2_vec = normalise(mk_vector(d2,dimensions))

    return cosine_similarity(d1_vec,d2_vec)
