import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('--gap',type=float,default=1.0,help='two segments with gap in seconds less than this value will be merged. Set to inf to ignore, default is 1.0')
parser.add_argument('--duration',type=float,default=1.0,help='segment length in seconds less than this value will be merged. Set to inf to ignore, default is 1.0')
args = parser.parse_args()
print(args)
assert args.gap < float('inf') or  args.duration < float('inf'), 'both shouldn\'t be inf'

path = args.path
root,filename = os.path.split(path)

def merge(utt1,utt2,sp='_'):
    utt1 = utt1.split(sp)
    utt2 = utt2.split(sp)
    assert utt1[0] == utt2[0] # prefix should be the same
    start = utt1[1]
    end = utt2[2]
    return sp.join([utt1[0],start,end])

start_prev = 0
end_prev = 0
utt_id_prev = None
rec_id_prev = None
line_out = []
with open(path) as segments:
    for line in segments:
        utt_id,rec_id,start,end = line.strip().split()
        start,end = float(start),float(end)

        gap = start - end_prev
        duration = end - start
        # print(duration,gap)
        if not utt_id_prev is None and gap <= args.gap and duration <= args.duration:
            print(utt_id,duration,gap)
            utt_id_merged = merge(utt_id_prev,utt_id)
            line_out.pop()
            line_out.append('{} {} {} {}\n'.format(utt_id_merged,rec_id,start_prev,end))
            utt_id_prev,rec_id_prev,start_prev,end_prev = utt_id_merged,rec_id,start_prev,end
        else:
            line_out.append(line)
            utt_id_prev,rec_id_prev,start_prev,end_prev = utt_id,rec_id,start,end
        

with open(path + '_merged','w') as out:
    for line in line_out:
        out.write(line)