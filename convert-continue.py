#!/usr/bin/env python3
import traceback
import subprocess
import os,sys
import requests
is_windows = False
try:
  os.environ['WINDIR']
  is_windows = True
except:pass
with open("password") as f:
  upload_password = f.read()
  upload_password = upload_password.replace("\n","")

MERGEAMOUNT = 10
filename = sys.argv[1] #a fullpath
try:
  print("ffmpeg process: >>>>")
  print(subprocess.check_output("ps -ef | grep ffmpeg",shell=True))
  print("<<<<")
  cmd = f"""ffmpeg -i "{filename}" -vcodec libx265 -crf 28 "{filename}.x265.mp4" > converting.log 2>&1"""
  print(cmd)
  subprocess.check_output(cmd,shell=True)

  #os.rename(f"{filename}.log", "/tmp/"+os.path.basename(f"{filename}.log"))
  os.remove(filename)
  os.remove(f"converting.log")
  
  print("uploading")
  r = requests.post(f"https://izzulmakin.com/hashfile/",
    files={
      'file':open(f"{filename}.x265.mp4", 'rb')
    },
    data={
      "hashxxx_password":upload_password,
      "hashxxx_hashid":"cctv"
    }
  )
  print(r.text)
  
  with open("list.txt", "a") as f:
    f.write(f"file {filename}.x265.mp4\n") #LINEFORMAT, filename is already fullpath
except:
  traceback.print_exc()
with open("list.txt") as f:
  list = f.read().split("\n")
  list = [s for s in list if len(s)>0]
  list0 = list[0][5:]
  list10 = list[-1]
  if list10=="":
    list10 = list[-2]
  list10 = list10[5:]
  print(list0, list10)
  mergename = list0.split(".")[0]+\
    list10.split("T")[1]
  if len(list)>=MERGEAMOUNT:
    print(f"merge {MERGEAMOUNT} small vids {mergename}")
    subprocess.check_output(f"ffmpeg -f concat -safe 0 -i list.txt -c copy {mergename}",shell=True)
    print("done merge, deleting unmerged files")
    for l in list:
      filename = l[len("file "):] #LINEFORMAT
      os.remove(filename)
      print(f"deleted {filename}")
    #startover/clear list.txt
    with open("list.txt","w") as f: f.close()
