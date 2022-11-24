# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

import time
import requests
import joblib
from os.path import dirname, realpath, join, getmtime, exists
from pathlib import Path
from app.api.models import installed_languages

dir_path = dirname(dirname(realpath(__file__)))
    
def file_older_than_x_days(filename, n_days): 
    '''Thank you https://stackoverflow.com/a/57639347'''
    file_time = getmtime(filename) 
    # Check against 24 hours 
    return ((time.time() - file_time) / 3600 > 24*n_days)


def download_pod_centroids(lang):
    print("Running update pod list for ", lang)
    URL = "https://github.com/PeARSearch/PeARS-public-pods-"+lang+"/blob/main/"+lang+"/"+lang+"wiki.summary.fh?raw=true"
    try:
        local_dir = join(dir_path, "static", "webmap", lang)
        Path(local_dir).mkdir(exist_ok=True, parents=True)
        local_file = join(dir_path, "static", "webmap", lang, lang + "wiki.summary.fh")
        if not exists(local_file) or file_older_than_x_days(local_file, 1): # Don't check for updates all the time
            with open (local_file, "wb") as f:
                f.write(requests.get(URL,allow_redirects=True).content)
        else:
            print("Using latest version of pod list.")
    except Exception:
        print("Request failed when trying to index", URL, "...")
