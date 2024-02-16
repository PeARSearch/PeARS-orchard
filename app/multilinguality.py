from os.path import dirname, join, realpath, isfile

def read_language_codes():
    dir_path = dirname(dirname(realpath(__file__)))
    ling_dir = join(dir_path,'app','static','ling')
    LANGUAGE_CODES = {}
    with open(join(ling_dir,'language_codes.txt'),'r') as f:
        for l in f:
            fields = l.rstrip('\n').split(';')
            LANGUAGE_CODES[fields[0]] = fields[1]
    return LANGUAGE_CODES

def read_stopwords(lang):
    dir_path = dirname(dirname(realpath(__file__)))
    ling_dir = join(dir_path,'app','static','ling','stopwords')
    STOPWORDS = []
    with open(join(ling_dir,lang),'r') as f:
        STOPWORDS = f.read().splitlines()
    return STOPWORDS

