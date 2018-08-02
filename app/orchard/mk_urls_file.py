from app.api.models import Urls, Pods, version
from app import db
from os.path import dirname, realpath, join, basename
from PIL import Image, ImageDraw
import math

dir_path = dirname(dirname(realpath(__file__)))


def make_csv_pod(keyword):
    url_keyword = keyword.replace(' ', '_')
    file_location = join(dir_path, "static", "pods",
                         url_keyword + "_urls_db.csv")
    f = open(file_location, 'w', encoding="utf-8")
    f.write("#Pod name:" + keyword + "\n")
    f.write("#Space version:" + version + "\n")
    for url in db.session.query(Urls).filter_by(keyword=keyword).all():
        line = str(url.id) + "," + url.url + "," + url.title.replace(
            ',', '-') + "," + url.snippet.replace(
                ',', '-') + "," + url.vector + "," + url.freqs + "," + str(
                    url.cc)
        f.write(line.replace('\r', '').replace('\n', '') + '\n')
    f.close()
    return file_location


def del_pod(keyword):
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
                break


def draw_image(pixels, keyword):
    url_keyword = keyword.replace(' ', '_')
    png_file_location = join(dir_path, "static", "pods",
                             url_keyword + "_urls_db.png")
    '''This will be the transparency pixel -- super important so that Twitter
    and co don't convert the png to jpg.'''
    pixels.append((255, 255, 255))
    size = int(math.sqrt(len(pixels))) + 1
    image_out = Image.new("RGB", (size, size))
    image_out.putdata(pixels)

    mask = Image.new('L', image_out.size, color=255)
    draw = ImageDraw.Draw(mask)
    draw.point((size - 1, size - 1), fill=0)
    image_out.putalpha(mask)
    image_out.save(png_file_location)
    return basename(png_file_location)


def convert_to_pixels(l):
    pixels = list()
    for char in l:
        a = int(ord(char) / 3)
        b = int((ord(char) - a) / 2)
        c = ord(char) - a - b
        # print(char,ord(char),a,b,c)
        color = (255 - a, 255 - b, 255 - c)
        pixels.append(color)
    return pixels


def make_png_pod(keyword):
    header = ""
    pixels = []
    url_keyword = keyword.replace(' ', '_')
    csv_file_location = join(dir_path, "static", "pods",
                             url_keyword + "_urls_db.csv")
    f = open(csv_file_location, encoding="utf-8")
    image_lines = []
    for l in f:
        image_lines.append(l)
    f.close()
    for line in image_lines:
        pixels += convert_to_pixels(line)
    return draw_image(pixels, keyword)
