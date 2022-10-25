import joblib
import re
from scipy.sparse import csr_matrix
from scipy.spatial.distance import hamming
import pathlib
import multiprocessing
import numpy as np
from tqdm import tqdm
from sklearn_extra.cluster import KMedoids


class DeployedFly:
    def __init__(self):
        self.pn_size = None
        self.kc_size = None
        self.wta = None
        self.projections = None
        self.top_words = None
        self.hyperparameters = None
from app.indexer.mk_page_vector import compute_query_vectors


def show_pod(pod_path):
    """
    Print the content of the pod
    :param pod_path: str, path to pod
    """
    m, titles = joblib.load(pod_path)
    print(type(m))
    print("\n## Pod", pod_path, "##\n")
    print("Matrix shape:", m.shape)
    print("Page titles length:", len(titles))
    print("\nFirst 50 titles:", titles[:50])


def create_dataset(n_doc_per_pod=10, save_path=None):
    """
    Create a set of queries. For each pod, choose randomly n_doc_per_pod page's titles.
    :param n_doc_per_pod: int, number of chosen page's title in each pod
    :param save_path: str
    :return: list, list
    """
    query_list, label_list = [], []
    for i in range(300):
        mm, titles = joblib.load(f'./data_test_simple/fhs/simplewiki-latest-pages-articles.xml.{i}.fh')
        chosen_idx = np.random.default_rng(i).choice(range(len(titles)), n_doc_per_pod)
        for idx in chosen_idx:
            query_list.append(titles[idx])
            label_list.append(i)

    if save_path:
        with open(save_path, 'w') as f:
            for j in range(len(query_list)):
                f.write(query_list[j] + '\t' + str(label_list[j]) + '\n')

    return query_list, label_list


def hash_dataset(query_list, save_path=None):
    """
    Pass each query to the hash function (fruitfly and variances) to obtain the binary hash.
    :param query_list: list, list of queries
    :param save_path: str
    :return: list, list of binary hashes
    """
    hash_list = []
    for query in tqdm(query_list):
        vector = compute_query_vectors(query=query, lang='simple')
        hash_list.append(vector)
    hash_list = np.array(hash_list)

    if save_path:
        np.save(save_path, hash_list)
    return hash_list


def find_medoid(pod_idx):
    """
    Find the medoid vector in a collection of hashes.
    :param pod_idx: int
    :return: numpy 1D array, medoid vector
    """
    m_pod, _ = joblib.load(f'./data_test/en_fhs_256/enwiki.{pod_idx}.fh')
    GetMedoid = lambda vX: KMedoids(n_clusters=1).fit(vX).cluster_centers_
    medoid = GetMedoid(m_pod.toarray())[0]
    return medoid


def find_centroid(pod_idx):
    """
    Find the centroid vector in a collection of hashes. Then binarize it.
    :param pod_idx: int
    :return: numpy 1D array, binary centroid vector
    """
    m_pod, _ = joblib.load(f'./data_test/en_fhs_256/enwiki.{pod_idx}.fh')
    centroid = np.mean(m_pod.toarray(), axis=0)
    centroid = (centroid > 0.5).astype(np.int_)
    return centroid


def compute_pod_vector(method='medoid', save_path=None):
    """
    Find the representative vectors for all pod (aka pod vector).
    :param method: str, either medoid or centroid
    :param save_path: str
    :return: numpy 2D matrix, a collection of pod vector
    """
    if method == 'medoid':
        pod_vector_list = joblib.Parallel(n_jobs=MAX_THREAD, prefer="threads")(
            joblib.delayed(find_medoid)(i) for i in range(499))
    elif method == 'centroid':
        pod_vector_list = joblib.Parallel(n_jobs=MAX_THREAD, prefer="threads")(
            joblib.delayed(find_centroid)(i) for i in range(499))
    else:
        raise

    pod_vector_list = np.array(pod_vector_list)
    if save_path:
        np.save(save_path, pod_vector_list)
    return pod_vector_list


def compute_distance(doc_hash_list, pod_repr, save_path=None):
    """

    :param doc_hash_list: numpy 2D matrix, the collection of hashes of all queries
    :param pod_repr: numpy 2D matrix, the collection of pod vectors
    :param save_path: str
    :return: numpy 2D matrix, distances for each doc's hash to all pod vectors
    """
    def _dist_one_doc(doc_hash):
        dist_list_one_doc = [hamming(doc_hash, pod_repr[j]) for j in range(pod_repr.shape[0])]
        return dist_list_one_doc

    dist_list_all_doc = joblib.Parallel(n_jobs=MAX_THREAD, prefer="threads")(
        joblib.delayed(_dist_one_doc)(doc_hash_list[i]) for i in range(doc_hash_list.shape[0]))
    dist_list_all_doc = np.array(dist_list_all_doc)

    if save_path:
        np.save(save_path, dist_list_all_doc)
    return dist_list_all_doc


def compute_pre_at_k(distance_mat, label_list):
    """
    precsion@k, k = 1, 5, 10
    :param distance_mat: numpy 2D matrix,
    :param label_list: list of labels
    :return: numpy 2D matrix, precision@k for all queries
    """
    prec_at_k = np.array([0, 0, 0])  # k = 1, 5, 10
    rank_list = np.argsort(distance_mat)
    for i in range(rank_list.shape[0]):
        if label_list[i] in rank_list[i][:1]:
            prec_at_k += 1
        elif label_list[i] in rank_list[i][:5]:
            prec_at_k[1] += 1
            prec_at_k[2] += 1
        elif label_list[i] in rank_list[i][:10]:
            prec_at_k[2] += 1
        else:
            pass
    return prec_at_k / len(label_list)


if __name__ == '__main__':
    MAX_THREAD = int(0.7 * multiprocessing.cpu_count())

    # 1. create queries consisting of page's titles
    pathlib.Path('./data_test_simple/dataset/').mkdir(parents=True, exist_ok=True)
    query_list, label_list = create_dataset(n_doc_per_pod=20, save_path='./data_test_simple/dataset/dataset.txt')

    # 2. hash the queries
    # query_list = []
    # with open('./data_test_simple/dataset/dataset.txt') as f:
    #     for line in f:
    #         query_list.append(line.split('\t')[0])
    # print(query_list)
    hash_dataset(query_list=query_list, save_path='./data_test_simple/dataset/hash_ridge.npy')

    # 3. find pod vectors
    method = 'medoid'
    pathlib.Path('./data_test_simple/res/').mkdir(parents=True, exist_ok=True)
    compute_pod_vector(method=method, save_path=f'./data_test_simple/res/pod_{method}_ridge.npy')

    # 4. compute hamming distances for each hash to all pod vectors
    doc_hash_list = np.load('./data_test_simple/dataset/hash_ridge.npy')
    pod_repr = np.load(f'./data_test_simple/res/pod_{method}_ridge.npy')
    compute_distance(doc_hash_list=doc_hash_list,
                     pod_repr=pod_repr,
                     save_path=f'./data_test_simple/res/dist_{method}_ridge.npy')

    # 5. compute pre@k
    # label_list = []
    # with open('./data_test_simple/dataset/dataset.txt') as f:
    #     for line in f:
    #         label = line.strip().split('\t')[1]
    #         label_list.append(int(label))
    distance_mat = np.load(f'./data_test_simple/res/dist_{method}_ridge.npy')
    res = compute_pre_at_k(distance_mat=distance_mat, label_list=label_list)
    print(res)

    #####################################################
    # inspect
    # pod_path = './en_fhs_256/enwiki.424.fh'
    # show_pod(pod_path=pod_path)

    # XX = np.load('./data_test_simple/dataset/hash_ridge.npy')
    # print(sum(XX.sum(axis=0) == 6000))
