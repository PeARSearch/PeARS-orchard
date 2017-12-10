#Detect whether page is under CC license and a snippet can be extracted from it.

from bs4 import BeautifulSoup
import requests
import sys
import re


def open_site(url):
  '''Checking for wikipedia or SO page'''
  for i in ["wikipedia.org","stackoverflow.com"]:
    if i in url:
      return True
  return False

def cc_img(bs_obj):
  '''Checking for CC logo'''
  imgs = bs_obj.find_all('img')
  for img in imgs:
    src = img['src']
    for i in ["creativecommons.org","cc-by"]:
      if i in src:
        return True
  return False

def is_cc(url, bs_obj):
  '''If page is CC-licensed, get snippet'''
  snippet = ""
  is_open = False

  if open_site(url) or cc_img(bs_obj):
    return True
  else:
    return False
