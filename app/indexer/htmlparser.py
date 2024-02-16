# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

import logging
import requests
import justext
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from langdetect import detect
from app.indexer.access import request_url
from app.indexer import detect_open
from app.api.models import installed_languages
from app import LANGUAGE_CODES

def remove_boilerplates(response, lang):
    if lang not in LANGUAGE_CODES:
        print(">> ERROR: INDEXER: HTMLPARSER: remove_boilerplates: language not in language codes.")
        return response.content
    text = ""
    print("REMOVING BOILERPLATES FOR LANG",lang,"(",LANGUAGE_CODES[lang],").")
    paragraphs = justext.justext(
        response.content,
        justext.get_stoplist(LANGUAGE_CODES[lang]),
        max_link_density=0.3,
        stopwords_low=0.1,
        stopwords_high=0.3,
        length_low=30,
        length_high=100)
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            text += paragraph.text + " "
    return text


def BS_parse(url):
    bs_obj = None
    req = None
    headers = {'User-Agent': 'PeARS User Agent'}
    try:
        req = requests.head(url, timeout=10, headers=headers)
        if "text/html" not in req.headers["content-type"]:
            print("\t>> ERROR: BS_parse: Not a HTML document...")
            return bs_obj, req
    except Exception:
        print("\t>> ERROR: BS_parse: request.head failed trying to access", url, "...")
        pass
    try:
        #headers = {'User-Agent': 'Customer User Agent'}
        req = requests.get(url, allow_redirects=True, timeout=30, headers=headers)
        req.encoding = 'utf-8'
    except Exception:
        print("\t>> ERROR: BS_parse: request failed trying to access", url, "...")
        return bs_obj, req
    bs_obj = BeautifulSoup(req.text, "lxml")
    return bs_obj, req


def extract_links(url):
    links = []
    try:
        req = requests.head(url, timeout=10)
        if req.status_code >= 400:
            print("\t>> ERROR: extract_links: status code is",req.status_code)
            return links
        if "text/html" not in req.headers["content-type"]:
            print("\t>> ERROR: Not a HTML document...")
            return links
    except Exception:
        return links
    bs_obj, req = BS_parse(url)
    if not bs_obj:
        return links
    hrefs = bs_obj.findAll('a', href=True)
    for h in hrefs:
        if h['href'].startswith('http') and '#' not in h['href']:
            links.append(h['href'])
        else:
            links.append(urljoin(url, h['href']))
    return links


def extract_html(url):
    '''From history info, extract url, title and body of page,
    cleaned with BeautifulSoup'''
    title = ""
    body_str = ""
    snippet = ""
    cc = False
    language = 'en'
    error = None
    bs_obj, req = BS_parse(url)
    if not bs_obj:
        error = "\t>> ERROR: extract_html: Failed to get BeautifulSoup object."
        return title, body_str, snippet, cc, error
    if hasattr(bs_obj.title, 'string'):
        if url.startswith('http'):
            og_title = bs_obj.find("meta", property="og:title")
            og_description = bs_obj.find("meta", property="og:description")
            #print("OG TITLE",og_title)
            #print("OG DESC",og_description)

            # Process title
            if not og_title:
                title = bs_obj.title.string
                if title is None:
                    title = ""
            else:
                title = og_title['content']
            title = ' '.join(title.split()[:11]) #11 to conform with EU regulations
            print(">> INFO: TITLE",title)

            # Process snippet
            if og_description:
                snippet = 'og desc:'+og_description['content'][:1000]
                #print(">> INFO: SNIPPET FROM OG",snippet)
            else:
                body_str = remove_boilerplates(req, language)
                try:
                    language = detect(title + " " + body_str)
                    print("\t>> INFO: Language for", url, ":", language)
                except Exception:
                    title = ""
                    error = "\t>> ERROR: extract_html: Couldn't detect page language."
                    return title, body_str, snippet, cc, error
                if language == 'en':
                    language = 'simple' # because training on simple wiki
                if language not in installed_languages:
                    error = "\t>> ERROR: extract_html: language is not supported."
                    title = ""
                    return title, body_str, snippet, cc, error
                snippet = ' '.join(body_str.split()[:11]) #11 to conform with EU regulations
    return title, body_str, snippet, cc, error
