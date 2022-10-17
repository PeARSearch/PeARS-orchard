from app.api.models import Urls, Pods
from app import db
from os.path import dirname, realpath, join, basename
import numpy as np
from scipy.sparse import vstack
from collections import Counter
import joblib

dir_path = dirname(dirname(realpath(__file__)))


def make_fruitfly_pod(keyword):
    url_keyword = keyword.replace(' ', '_')
    hfile = join(dir_path, "static", "pods", url_keyword + ".fh")
    name = keyword
    langs = []
    titles = []
    urls = []
    m = []
    for url in db.session.query(Urls).filter_by(keyword=keyword).all():
        m.append(np.array([int (b)for b in url.vector.split()]))
        titles.append(url.title)
        urls.append(url.url)
        pod = db.session.query(Pods).filter_by(name=url.pod).first()
        langs.append(pod.language)
    main_lang = Counter(langs).most_common(1)[0][0]
    m = np.array(m)
    joblib.dump([name, main_lang, m, titles, urls], hfile)
    return hfile


def del_pod(keyword):
    print("Deleting pod")
    for url in db.session.query(Urls).filter_by(keyword=keyword).all():
        print("Deleting "+url.url+" "+url.pod)
        if url.pod == "Me":
            db.session.delete(url)
            db.session.commit()
        pod_entries = db.session.query(Pods).filter_by(description=keyword).all()
        for pod_entry in pod_entries:
            if "localhost" in pod_entry.url:
                db.session.delete(pod_entry)
                db.session.commit()


