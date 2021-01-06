import os
import sys
import ast 

path = sys.argv[1]
root,filename = os.path.split(path)

rec_id = ''
with open(path) as f:
    lines = f.readlines()
    assert len(lines) == 4
    audio_path = lines[0].split()[1]
    print(audio_path)
    audio_name = os.path.split(audio_path)[1]
    print(audio_name)
    rec_id = os.path.splitext(audio_name)[0]
    print(rec_id)
    
    segments = ast.literal_eval(lines[3])

with open(root + '/segments_' + rec_id,'w') as out:
    for start,end in segments:
        utt_id = "{}_{:07d}_{:07d}".format(rec_id,int(round(start*1000)),int(round(end*1000)))
        out.write(u"{} {} {} {}\n".format(utt_id,rec_id,start,end))
    