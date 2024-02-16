from urllib.parse import urlparse
from os.path import join
import requests
import sys
import re

def robotcheck(url):
    scheme = urlparse(url).scheme
    domain = scheme + '://' + urlparse(url).netloc
    robot_url = join(domain,"robots.txt")

    disallowed = []
    r = requests.head(robot_url)
    if r.status_code < 400:
        parse = False
        content = requests.get(robot_url).text.splitlines()
        for l in content:
            if 'User-agent: *' in l:
                parse = True
            elif 'User-agent' in l and parse == True:
                parse = False
            elif l == 'Disallow: /' and parse == True:
                disallowed.append(domain)
            elif 'Disallow:' in l and parse == True:
                m = re.search('Disallow:\s*(.+)',l)
                if m:
                    u = m.group(1)
                    if u[0] == '/':
                        u = u[1:]
                    disallowed.append(join(domain,u))

    getpage = True
    for u in disallowed:
        m = re.search(u.replace('*','.*'),url)
        if m:
            error = "ERROR: robotcheck: "+url+" is disallowed because of "+u
            print("\t>>",error)
            getpage = False
    return getpage

def request_url(url):
    print("\n> CHECKING URL CAN BE REQUESTED")
    access = None
    req = None
    errs = []
    headers = {'User-Agent': 'PeARS User Agent'}
    try:
        req = requests.head(url, timeout=10, headers=headers)
        if req.status_code >= 400:
            error = "ERROR: request_url: status code is "+str(req.status_code)
            print("\t>>",error)
            errs.append(error)
            return access, req, errs
        else:
            if robotcheck(url):
                access = True
            else:
                error = "ERROR: request_url: robot.txt disallows the url "+url+"."
                print("\t>>",error)
                errs.append(error)
    except Exception:
        error = "ERROR: request_url: request.head failed trying to access"+url+"."
        print("\t>>",error)
        errs.append(error)
        return access, req, errs
    return access, req, errs


