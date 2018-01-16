from app.api.models import Urls
from app import db
from os.path import dirname,realpath,join

dir_path = dirname(dirname(dirname(realpath(__file__))))

def make_pod(keyword):
    file_location = join(dir_path,keyword+"_urls_db.csv")
    f = open(file_location,'w')
    for url in db.session.query(Urls).filter_by(keyword=keyword).all():
        l=str(url.id)+","+url.url+","+url.title.replace(',','-')+","+url.snippet.replace(',','-')+","+url.vector+","+url.freqs+","+str(url.cc)
        f.write(l.replace('\r', '').replace('\n','')+'\n')
    f.close()
    return file_location

