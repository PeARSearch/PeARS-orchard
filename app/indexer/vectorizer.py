from sklearn.feature_extraction.text import CountVectorizer
from app.indexer.fly_utils import read_vocab, read_n_encode_dataset
from sklearn import preprocessing

def init_vectorizer(lang): 
    spm_vocab = f"app/api/models/{lang}/{lang}wiki.vocab"
    vocab, reverse_vocab, logprobs = read_vocab(spm_vocab)
    vectorizer = CountVectorizer(vocabulary=vocab, lowercase=True, token_pattern='[^ ]+')
    return vectorizer, logprobs

def vectorize(lang, text, logprob_power, top_words):
    '''Takes input file and return vectorized /scaled dataset'''
    vectorizer, logprobs = init_vectorizer(lang)
    dataset = read_n_encode_dataset(text, vectorizer, logprobs, logprob_power, top_words)
    dataset = dataset.todense()
    return dataset

def scale(dataset):
    #scaler = preprocessing.MinMaxScaler().fit(dataset)
    scaler = preprocessing.Normalizer(norm='l2').fit(dataset)
    return scaler.transform(dataset)

def vectorize_scale(lang, text, logprob_power, top_words):
    dataset = vectorize(lang, text, logprob_power,top_words)
    return scale(dataset)
