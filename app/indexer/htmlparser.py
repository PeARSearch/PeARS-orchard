import logging
import requests
import justext
from app.indexer import detect_open
from bs4 import BeautifulSoup
from langdetect import detect

def remove_boilerplates(response):
    text = ""
    paragraphs = justext.justext(response.content, justext.get_stoplist("English"), max_link_density=0.3, stopwords_low=0.1, stopwords_high=0.3, length_low=30, length_high=100)
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            text+=paragraph.text+" "
    return text

def extract_from_url(url):
    '''From history info, extract url, title and body of page,
    cleaned with BeautifulSoup'''
    title=""
    body_str=""
    snippet=""
    cc=False
    req=None
    try:
        req = requests.get(url, allow_redirects=True, timeout=30)
        req.encoding = 'utf-8'
    except:
        print("Request failed when trying to index",url,"...")
        return title, body_str, snippet, cc
    if req.status_code is not 200:
        logging.exception("Warning: "  + str(req.url) + ' has a status code of: ' \
        + str(req.status_code) + ' omitted from database.\n')
        return title, body_str, snippet, cc
    bs_obj = BeautifulSoup(req.text,"lxml")
    if hasattr(bs_obj.title, 'string') & (req.status_code == requests.codes.ok):
        if url.startswith('http'):
           title = bs_obj.title.string
           if title is None:
               title=""
           body_str=remove_boilerplates(req)
           try:
               language=detect(title+" "+body_str)
               print("Language for",url,":",language)
           except:
               title=""
               return title, body_str, snippet, cc
               
           if detect(title+" "+body_str) != "en":
               print("Ignoring",url,"because language is not supported.")
               title=""
               return title, body_str, snippet, cc
           try:
               cc = detect_open.is_cc(url,bs_obj)
           except:
               print("Failed to get CC status for",url,"...")
           if cc: 
               snippet = body_str[:100].replace(',','-')
           else:
               snippet = body_str[:40].replace(',','-')
    return title, body_str, snippet, cc
