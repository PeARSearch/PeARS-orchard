from app.api.models import Urls

f = open("urls_db.csv",'w')
for url in Urls.query.all():
    l=str(url.id)+","+url.url+","+url.title.replace(',','-')+","+url.snippet.replace(',','-')+","+url.vector+","+url.freqs+","+str(url.cc)
    f.write(l.replace('\r', '').replace('\n','')+'\n')
f.close()

