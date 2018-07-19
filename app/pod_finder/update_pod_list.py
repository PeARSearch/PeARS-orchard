import requests
from bs4 import BeautifulSoup

location = "http://pearsearch.org/pods.html"

def update_pod_list():
    links = []
    try:
        req = requests.get(location, timeout=30)
        req.encoding = 'utf-8'
        bs_obj = BeautifulSoup(req.text, "lxml")
        rows = bs_obj.findAll('tr')
        for row in rows[1:]:	#Don't read header
            h = row.findAll(text=True)
            links.append(h)
    except Exception:
        print("Request failed when trying to index", location, "...")
    #print(links)
    return links
