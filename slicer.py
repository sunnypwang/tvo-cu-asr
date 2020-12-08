import sys
import os

in_folder = sys.argv[1]
out_folder = sys.argv[2]
slice_id_file = sys.argv[3]
slice_id = []
with open(slice_id_file, encoding='utf-8') as f:
    for line in f:
        slice_id.append(line.strip())
print(slice_id)     

target = ['segments','text','wav.scp','utt2spk']

if not os.path.exists(in_folder + '/' + out_folder):
    os.makedirs(in_folder + '/' + out_folder)

for t in target:
    with open(in_folder + '/' + t, encoding='utf-8') as f:
        with open(in_folder + '/' + out_folder + '/' + t, 'w', encoding='utf-8') as out:
            for line in f:
                for id in slice_id:
                    if str(id) in line:
                        out.write(line)