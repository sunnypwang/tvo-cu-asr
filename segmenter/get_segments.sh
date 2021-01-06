#/bin/bash
set -x # echo on
if [ $# -lt 1 ]; then
    echo "usage: $0 wav_path"
    exit
fi
wav_path=$1
wav_name=`basename $1` || exit 1
python3 n_segmenter.py $wav_path > segments-output/tmp || exit 1
python3 format_nsegment_output.py segments-output/tmp || exit 1
rm segments-output/tmp