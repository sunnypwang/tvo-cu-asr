#!/bin/bash
filename="${1%.*}"
echo $filename.wav
ffmpeg -i $1 -filter:a "pan=mono|FC=FR" $filename.wav
#sox $filename.wav -r 16k -b 16 -t wav $filename.16k.wav
