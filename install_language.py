# SPDX-FileCopyrightText: 2022 PeARS Project, <community@pearsproject.org> 
#
# SPDX-License-Identifier: AGPL-3.0-only

import sys
import requests
from pathlib import Path
from os.path import dirname, realpath, join

if len(sys.argv) != 2:
    print("Please specify the language you want to install. English is pre-installed. The following other languages are supported: [fr]")
    sys.exit()

lang = sys.argv[1]

if len(lang) != 2:
    print("Your language code should just be a two-letter string. \nEXAMPLE USAGE: python install_language.py ml.")
    sys.exit()

dir_path = dirname(realpath(__file__))
local_dir = join(dir_path, "app", "api", "models", lang)
Path(local_dir).mkdir(exist_ok=True, parents=True)

repo_path = 'https://github.com/PeARSearch/PeARS-public-pods-'+lang+'/blob/main/models/'

paths = ['fly.m', lang+'.hyperparameters.cfg', lang+'wiki-latest-pages-articles.train.hacked.umap', lang+'wiki.expansion.m', lang+'wiki.model', lang+'wiki.vocab']

for p in paths:
    path = join(repo_path, p+'?raw=true')
    local_file = join(local_dir,p)
    print("Downloading",path,"to",local_file,"...")
    try:
        with open(local_file,'wb') as f:
            f.write(requests.get(path,allow_redirects=True).content)
    except Exception:
        print("Request failed when trying to index", path, "...")
