import requests
import joblib
from os.path import dirname, realpath, join
from pathlib import Path
from app.api.models import installed_languages

dir_path = dirname(dirname(realpath(__file__)))

def download_pod_centroids():
    print("Running update pod list")
    for lang in installed_languages:
        URL = "https://github.com/PeARSearch/PeARS-public-pods-"+lang+"/blob/main/"+lang+"/"+lang+"wiki.summary.fh?raw=true"
        try:
            local_dir = join(dir_path, "static", "webmap", lang)
            Path(local_dir).mkdir(exist_ok=True, parents=True)
            local_file = join(dir_path, "static", "webmap", lang, lang + "wiki.summary.fh")
            with open (local_file, "wb") as f:
                f.write(requests.get(URL,allow_redirects=True).content)
        except Exception:
            print("Request failed when trying to index", URL, "...")
