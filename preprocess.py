import json
import argparse
import os
from utils import *

parser = argparse.ArgumentParser()
parser.add_argument('path',
                    help='directory path to JSON files.')
parser.add_argument('path_out',
                    help='output path')
parser.add_argument('--rm_tag', action='store_true',
                    help='remove all tags <> in the output')
parser.add_argument('--unk', action='store_true',
                    help='include unknown speaker')
parser.add_argument('--ts', type=int, default=6,
                    help='timestamp length in utterance-id. Default is 6')

args = parser.parse_args()

INCLUDE_UNK = args.unk
REMOVE_TAG = args.rm_tag
TIMESTAMP_LEN = args.ts
print(args)

spk_parser = {'Speaker 1': 'spk1', 'Speaker 2': 'spk2'}
if INCLUDE_UNK:
    spk_parser['Unknown'] = 'unk'


json_path = []
for root, dirs, files in os.walk(args.path):
    for f in files:
        if f.endswith('.json'):
            json_path.append(os.path.join(root, f))
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
            rid = entry['hospital'] + '_' + parse_wav(wav_path)
            data[rid] = entry
            if not rid in rec_id: #if not yet added before
                rec_id.append(rid)
                audio_path.append(wav_path)
        del d
print('\nTotal unqiue entries: {}\n'.format(len(data)))
# print(data['SMPK1585808134.1429'].keys())
# print(len(rec_id),len(audio_path))

print('Extracting labels and texts...')
labels = []
texts = []
timestamps = []
for rid in data:
    lb = []
    tx = []
    tm = []
    result = data[rid]['completions'][0]['result']
    j = 0
    # each recording has a list of utterances, which alternates between label and text, so we will check two at a time
    while j+1 < len(result):
        if 'id' in result[j] and 'id' in result[j+1] and result[j]['id'] == result[j+1]['id']:  # check if id exists and matches
            id = result[j]['id']
            assert result[j]['type'] == 'labels', 'not a label at ID: ' + id
            assert result[j+1]['type'] == 'textarea', 'not a textarea at ID: ' + id

            label_obj = result[j]['value']
            text_obj = result[j+1]['value']

            # check if speaker is Unknown, if needed
            if label_obj['labels'][0] != 'Unknown' or INCLUDE_UNK:
                try:
                    label = label_obj['labels'][0].strip()
                    text = text_obj['text'][0].strip()
                    text = clean_text(text, remove_tag=REMOVE_TAG)
                    start = label_obj['start']
                    end = label_obj['end']
                    lb.append(label)
                    tx.append(text)
                    tm.append((start, end))
                except KeyError:
                    print('[KeyError] at ID: {}. skipping...'.format(id))
            j += 2
        else:
            print('no matching transcription/label for ID:', result[j]['id'])
            j += 1
        assert len(lb) == len(tx) == len(tm)
    labels.append(lb)
    texts.append(tx)
    timestamps.append(tm)

print('Creating utterrance list...')
utt_id = []
match_rec_id = []  # store matching rec_id for every utt_id
match_spk_id = []  # store matching spk_id for every utt_id
for i in range(len(data)):
    for j in range(len(labels[i])):
        spk_id = '{}-{}'.format(rec_id[i], spk_parser[labels[i][j]])
        start = format_time(timestamps[i][j][0], TIMESTAMP_LEN)
        end = format_time(timestamps[i][j][1], TIMESTAMP_LEN)
        utt_id.append('{}_{}-{}'.format(spk_id, start, end))
        match_rec_id.append(rec_id[i])
        match_spk_id.append(spk_id)
print('Total utterances:',len(utt_id))

print('Creating kaldi output files...')
if not os.path.exists(args.path_out):
    os.makedirs(args.path_out)

# text
with open(os.path.join(args.path_out,'text'), 'w', encoding='utf-8') as f:
    flat_texts = flatten(texts)
    for i in range(len(utt_id)):
        f.write('{} {}\n'.format(utt_id[i], flat_texts[i]))

# wav.scp
with open(os.path.join(args.path_out,'wav.scp'), 'w', encoding='utf-8') as f:
    for i in range(len(rec_id)):
        f.write('{} {}\n'.format(rec_id[i], audio_path[i]))

# segments
with open(os.path.join(args.path_out,'segments'), 'w', encoding='utf-8') as f:
    for i in range(len(utt_id)):
        flat_timestamps = flatten(timestamps)
        f.write('{} {} {} {}\n'.format(
            utt_id[i], match_rec_id[i], flat_timestamps[i][0], flat_timestamps[i][1]))

# utt2spk
with open(os.path.join(args.path_out,'utt2spk'), 'w', encoding='utf-8') as f:
    for i in range(len(utt_id)):
        f.write('{} {}\n'.format(utt_id[i], match_spk_id[i]))

# OPTIONAL
print('Creating optional files...')
# transcript
with open('transcript', 'w', encoding='utf-8') as f:
    flat_labels = flatten(labels)
    flat_texts = flatten(texts)
    for i in range(len(utt_id)):
        f.write('{} {}\n'.format(flat_labels[i], flat_texts[i]))

print('Done!')
