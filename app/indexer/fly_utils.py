import re
import json
import pickle
import numpy as np
from scipy.sparse import csr_matrix, vstack
from sklearn.metrics import pairwise_distances
from sklearn import linear_model
from os.path import exists

def read_vocab(vocab_file):
    c = 0
    vocab = {}
    reverse_vocab = {}
    logprobs = []
    with open(vocab_file) as f:
        for l in f:
            l = l.rstrip('\n')
            wp = l.split('\t')[0]
            logprob = -(float(l.split('\t')[1]))
            #logprob = log(lp + 1.1)
            if wp in vocab or wp == '':
                continue
            vocab[wp] = c
            reverse_vocab[c] = wp
            logprobs.append(logprob)
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


def hash_input_vectorized_(pn_mat, weight_mat, percent_hash):
    kc_mat = pn_mat.dot(weight_mat.T)
    #print(pn_mat.shape,weight_mat.shape,kc_mat.shape)
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
    hs = (hs > 0).astype(np.int_)
    return hs


def encode_docs(doc_list, vectorizer, logprobs, power, top_words):
    logprobs = np.array([logprob ** power for logprob in logprobs])
    X = vectorizer.fit_transform(doc_list)
    X = X.multiply(logprobs)
    X = wta_vectorized(X.toarray(),top_words,False)
    X = csr_matrix(X)
    return X


def read_n_encode_dataset(doc=None, vectorizer=None, logprobs=None, power=None, top_words=None, verbose=False):
    # read
    doc_list = [doc]

    # encode
    X = encode_docs(doc_list, vectorizer, logprobs, power, top_words)
    if verbose:
        k = 10
        inds = np.argpartition(X.todense(), -k, axis=1)[:, -k:]
        for i in range(X.shape[0]):
            ks = [list(vectorizer.vocabulary.keys())[list(vectorizer.vocabulary.values()).index(k)] for k in np.squeeze(np.asarray(inds[i]))]
    return X

def train_model(m_train,classes_train,m_val,classes_val,C,num_iter):
    lm = linear_model.LogisticRegression(multi_class='ovr', solver='liblinear',
                                         max_iter=num_iter, C=C, verbose=0)
    lm.fit(m_train, classes_train)
    score = lm.score(m_val,classes_val)
    # print(lm.predict(m_val))
    # print(score)
    return score, lm

