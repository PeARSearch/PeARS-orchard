from app.api.models import Urls, version
from app import db
from os.path import dirname,realpath,join,basename
from PIL import Image
import math

dir_path = dirname(dirname(realpath(__file__)))


def make_csv_pod(keyword):
    file_location = join(dir_path,"static","pods",keyword+"_urls_db.csv")
    f = open(file_location,'w')
    f.write("#Pod name:"+keyword+"\n")
    f.write("#Space version:"+version+"\n")
    for url in db.session.query(Urls).filter_by(keyword=keyword).all():
        l=str(url.id)+","+url.url+","+url.title.replace(',','-')+","+url.snippet.replace(',','-')+","+url.vector+","+url.freqs+","+str(url.cc)
        f.write(l.replace('\r', '').replace('\n','')+'\n')
    f.close()
    return file_location

def make_png_pod(keyword):
    pixels = list()
    csv_file_location = join(dir_path,"static","pods",keyword+"_urls_db.csv")
    png_file_location = join(dir_path,"static","pods",keyword+"_urls_db.png")
    f = open(csv_file_location)
    for l in f:
        for char in l:
            a = int(ord(char) / 3)
            b = int((ord(char)-a) / 2)
            c = ord(char) - a - b
            #print(char,ord(char),a,b,c)
            color = (255-a,255-b,255-c)
            pixels.append(color)
    f.close()
    size = int(math.sqrt(len(pixels))) + 1
    image_out = Image.new("RGB", (size,size))
    image_out.putdata(pixels)
    image_out.save(png_file_location)
    return basename(png_file_location)

