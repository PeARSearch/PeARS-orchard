# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
import requests
import codecs
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# check http links in same domain

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def write_html_to_cache(html, cached_page):
    # print "Writing to",cached_page,"..."
    cache = codecs.open(cached_page, 'w', encoding='utf8')
    html = html.replace(
        '</head>',
        '<link rel="stylesheet" type="text/css" href="/static/css/offline.css"/>\n</head>'
    )
    cache.write(html)
    cache.close()


def cache_file(url, html):
    '''Write html in local cache directory'''
    url_parsed = urlparse(url)
    path_dirs = url_parsed.path[1:].split('/')
    page = path_dirs[-1]
    print("CACHING", page, "ON", url_parsed.netloc)
    cached_netloc = "./pears/html_cache/" + url_parsed.netloc
    if page == "":
        page = "index.html"
    if page[-5:] != ".html":
        page = page + ".html"
    print("PAGE", page)
    cached_dir = cached_netloc + "/" + '/'.join(path_dirs[:-1]) + "/"
    if not os.path.isdir(cached_dir):
        os.makedirs(cached_dir)
    cached_page = cached_dir + page
    if not os.path.exists(cached_page):
        write_html_to_cache(html, cached_page)


def cache_pdf(url):
    '''Write pdf in local cache directory'''
    try:
        url_parsed = urlparse(url)
        path_dirs = url_parsed.path.rstrip('/')[1:].split('/')
        page = path_dirs[-1]
        cached_netloc = "./pears/html_cache/" + url_parsed.netloc
        cached_dir = cached_netloc + "/" + '/'.join(path_dirs[:-1]) + "/"
        if not os.path.isdir(cached_dir):
            os.makedirs(cached_dir)
        cached_page = cached_dir + page
        if not os.path.exists(cached_page):
            response = requests.get(url)
            with open(cached_page, 'wb') as f:
                f.write(response.content)
    except Exception:
        print("Error caching the pdf...")


def get_images(url):
    """Downloads all the images at 'url' to cache"""
    req = requests.get(url, allow_redirects=True, timeout=20)
    soup = BeautifulSoup(req.text, "lxml")
    # url_parsed = list(urlparse(url))
    for image in soup.findAll("img"):
        print("Image: %(src)s" % image)
        if not image["src"].lower().startswith("http"):
            img_path = urljoin(url, image["src"])
            print(img_path)
            cache_file(img_path)


def get_css(url):
    """Downloads all the css to local cache"""
    req = requests.get(url, allow_redirects=True, timeout=20)
    soup = BeautifulSoup(req.text, "lxml")
    # url_parsed = list(urlparse(url))
    for link in soup.findAll("link"):
        if link["rel"][0] == "stylesheet":
            print("Link: %(href)s" % link)
            if not link["href"].lower().startswith("http"):
                css_path = urljoin(url, link["href"])
                print(css_path)
                cache_file(css_path)


def runScript(url, html):
    print("Caching", url, "...")
    cache_file(url, html)
    # Optional: grab the images and css for that page
    # get_images(url)
    # get_css(url)
