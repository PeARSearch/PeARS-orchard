# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

'''Spider code, heavily influenced by http://www.netinstructions.com/how-to-make-a-web-crawler-in-under-50-lines-of-python-code/.'''

from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse

'''LinkParser inherits from HTMLParser'''
class LinkParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        '''Extending HTMLParser's function'''
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    new_url = parse.urljoin(self.base, value)
                    self.links = self.links + [new_url]

    def getLinks(self, url):
        '''New function not in HTMLParser'''
        self.links = []
        self.base = url
        response = urlopen(url)
        if 'text/html' in response.getheader('Content-Type'):
            htmlBytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString, self.links
        else:
            return "",[]

def get_links(base_url, max_pages):  
    pages_to_visit = [base_url]
    pages_visited = []
    number_visited = 0
    while number_visited < max_pages and pages_to_visit != []:
        number_visited+=1
        # Start from base url
        url = pages_to_visit[0]
        if not url.startswith(base_url):
            continue
        pages_visited.append(url)
        pages_to_visit = pages_to_visit[1:]
        try:
            print(number_visited, "Scraping:", url)
            parser = LinkParser()
            data, links = parser.getLinks(url)
            for link in links:
                if link not in pages_visited and link not in pages_to_visit and '#' not in link and base_url in link:
                    pages_to_visit.append(link)
        except:
            print(" **Failed visiting current url!**")
    return pages_visited
