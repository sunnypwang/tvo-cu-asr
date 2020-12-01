import json
import re
import argparse
import os
from utils import *

parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='?', default='.', help='directory path to JSON files. Default is current directory')
parser.add_argument('--rm_tag',action='store_true',help='remove all tags <> in the output')
parser.add_argument('--unk',action='store_true',help='include unknown speaker')
parser.add_argument('--ts',type=int,default=6,help='timestamp length in utterance-id. Default is 6')

args = parser.parse_args()

INCLUDE_UNK = args.unk
REMOVE_TAG = args.rm_tag
TIMESTAMP_LEN = args.ts
path = args.path
print('Path :',path)

out_path = 'out/'

spk_parser = {'Speaker 1': 'spk1', 'Speaker 2': 'spk2'}
if INCLUDE_UNK:
    spk_parser['Unknown'] = 'unk'


json_path= []
for root,dirs,files in os.walk(path):
    for f in files:
        if f.endswith('.json'):
            json_path.append(os.path.join(root,f))
print('{} JSON files found'.format(len(json_path)))

data = dict()
audio_path = []
rec_id = []
for json_file in json_path:
    print('Reading {}...'.format(json_file), end=' ')
    with open(json_file, encoding='utf-8') as f:
        d = json.load(f)
        print('{} entries found'.format(len(d)))
        for entry in d:
            wav_path = entry['data']['audio']
            entry['hospital'] = parse_hospital(json_file)
            rid = entry['hospital'] + parse_wav(wav_path)
            data[rid] = entry
            if not rid in rec_id:
                rec_id.append(rid)
            if not wav_path in audio_path:
                audio_path.append(wav_path)
        del d
print('\nTotal unqiue entries: {}\n'.format(len(data)))
# print(data['SMPK1585808134.1429'].keys())
# print(len(rec_id))

print('Extracting labels and texts...')
labels = []
texts= []
timestamps = []
for rid in data:
    lb = []
    tx = []
    tm = []
    result = data[rid]['completions'][0]['result']
    j = 0
    while j < len(result): 
        if 'direction' in result[j]: # unused object
            j += 1
            continue
        if j+1 < len(result) and result[j]['id'] == result[j+1]['id']: # match label and text id
            if not INCLUDE_UNK and result[j]['value']['labels'][0] == 'Unknown':
                pass
            else:
                lb.append(result[j]['value']['labels'][0])
                tx.append(clean_text(result[j+1]['value']['text'][0], remove_tag=REMOVE_TAG))
                start,end = result[j+1]['value']['start'],result[j+1]['value']['end']
                tm.append((start,end))
            j += 2
        else:
            print('no matching transcription/label for ID:',result[j]['id'])
            j += 1
        assert len(lb) == len(tx)
    labels.append(lb)
    texts.append(tx)
    timestamps.append(tm)

print('Creating utterrance list...')
utt_id = []
match_rec_id = [] # store matching rec_id for every utt_id
match_spk_id = [] # store matching spk_id for every utt_id
for i in range(len(data)):
    for j in range(len(labels[i])):
        spk_id = '{}-{}'.format(rec_id[i] , spk_parser[labels[i][j]])
        start = format_time(timestamps[i][j][0], TIMESTAMP_LEN)
        end = format_time(timestamps[i][j][1], TIMESTAMP_LEN)
        utt_id.append('{}_{}-{}'.format(spk_id, start, end))
        match_rec_id.append(rec_id[i]) 
        match_spk_id.append(spk_id)

print('Creating kaldi output files...')
# text
with open('text','w', encoding='utf-8') as f:
    flat_texts = flatten(texts)
    for i in range(len(utt_id)):
        f.write('{} {}\n'.format(utt_id[i], flat_texts[i]))

# wav.scp
with open('wav.scp','w', encoding='utf-8') as f:
    for i in range(len(rec_id)):
        f.write('{} {}\n'.format(rec_id[i], audio_path[i]))

# segments
with open('segments','w', encoding='utf-8') as f:
    for i in range(len(utt_id)):
        flat_timestamps = flatten(timestamps)
        f.write('{} {} {} {}\n'.format(utt_id[i], match_rec_id[i], flat_timestamps[i][0], flat_timestamps[i][1]))

# utt2spk
with open('utt2spk','w', encoding='utf-8') as f:
    for i in range(len(utt_id)):
        f.write('{} {}\n'.format(utt_id[i], match_spk_id[i]))

## OPTIONAL
print('Creating optional files...')
# transcript
with open('transcript','w', encoding='utf-8') as f:
    flat_labels = flatten(labels)
    flat_texts = flatten(texts)
    for i in range(len(utt_id)):
        f.write('{} {}\n'.format(flat_labels[i], flat_texts[i]))

print('Done!')