#!/usr/bin/env python3
import subprocess
import os,sys
MERGEAMOUNT = 5
filename = sys.argv[1] #a fullpath
subprocess.check_output(f"ffmpeg -i {filename} -vcodec libx265 -crf 28 {filename}.x265.mp4 > converting.log 2>&1",shell=True)
#os.rename(f"{filename}.log", "/tmp/"+os.path.basename(f"{filename}.log"))
os.remove(filename)
os.remove(f"converting.log")
with open("list.txt", "a") as f:
  f.write(f"file {filename}.x265.mp4") #LINEFORMAT, filename is already fullpath
with open("list.txt") as f:
  list = f.read().split("\n")
  list0 = list[0]
  list10 = list[-1]
  mergename = list[0].split(".")[0]+list10.split("T")[1]
  if len(list)>=MERGEAMOUNT:
    print(f"merge {MERGEAMOUNT} small vids {mergename}")
    subprocess.check_output(f"ffmpeg -f concat -safe 0 -i list.txt -c copy vid/{mergename}"
    print("done merge, deleting unmerged files")
    for l in list:
      filename = l[len("file "):] #LINEFORMAT
      os.remove(filename)
      print(f"deleted {filename}")
