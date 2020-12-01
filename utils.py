def parse_hospital(filename):
    return filename.strip().split('-')[-1].split('.')[0]

def parse_wav(filename):
    return filename.strip().split('-')[-1][:-4]

def clean_text(txt, remove_tag=False):
    if remove_tag:
        txt = re.sub(r'<\w*>','',txt)
    return txt

def flatten(l):
    return [y for x in l for y in x]

def format_time(t, length=6): # convert 12.3456789 into 012345
    str_f = '{:0' + str(length) + 'd}'
    return str_f.format( int(t * 1000))