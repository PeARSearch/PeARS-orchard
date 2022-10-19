# SPDX-FileCopyrightText: 2022 Aurelie Herbelot, <aurelie.herbelot@unitn.it>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

import sys
import joblib
import pickle
from glob import glob
from os.path import join, exists
from sklearn.linear_model import Ridge
from scipy.sparse import csr_matrix
from scipy.sparse import vstack
from collections import Counter
import numpy as np
from app.indexer.vectorizer import vectorize_scale
from app.indexer.fly_utils import hash_dataset_ 
from app.api.models import expanders


def apply_ridge(lang, text, ridge, logprob_power, top_words):
    dataset = vectorize_scale(lang, text, logprob_power, top_words)
    dataset = ridge.predict(dataset)
    #print("RIDGE VECTOR:",dataset)
    return dataset


def fly_hash(fly, m):
    hashed_data = hash_dataset_(m, fly.projections, fly.wta, fly.top_words)
    return hashed_data


def return_hash(lang, text, ridge, fly, logprob_power):
    #print("FLY TOP WORDS",fly.top_words)
    #print(len(text))
    #m = apply_ridge(lang, text, ridge, logprob_power, fly.top_words) #FIX FLY!
    m = apply_ridge(lang, text, ridge, logprob_power, min(len(text),fly.top_words))
    if len(text) < 70:
        expander = expanders[lang]
        m = expander.predict(m)

    hs = fly_hash(fly, m)
    return hs
