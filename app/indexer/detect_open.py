# Detect whether page is under CC license and
# a snippet can be extracted from it.


def open_site(url):
    file = open("Opensites.txt",'r').readlines()
    urls = [line.rstrip('\n') for line in file]
    for i in urls:
        if i in url:
            return True
        return False


def cc_img(bs_obj):
    '''Checking for CC logo'''
    imgs = bs_obj.find_all('img')
    for img in imgs:
        src = img['src']
        for i in ["creativecommons.org", "cc-by"]:
            if i in src:
                return True
    return False


def is_cc(url, bs_obj):
    '''If page is CC-licensed, get snippet'''
    if open_site(url) or cc_img(bs_obj):
        return True
    else:
        return False
