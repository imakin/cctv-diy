#!/usr/bin/env python3
import datetime
import re
import cv2
import time
import os
import sys

from vid import serve

def get_timestamp():
  return re.findall("([\d\-T\:]+)", datetime.datetime.now().isoformat() )[0].replace(":","-")

BASE_DIR = os.path.dirname( os.path.realpath(sys.argv[0]) )
VID_DIR = f"{BASE_DIR}/vid"

FPS = 30
SEGMENTLENGTH = 2 #minutes
segmentlength_frames = SEGMENTLENGTH*60*FPS
cap= cv2.VideoCapture(-1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
#get the actual w.h
time.sleep(1)
width= int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.set(cv2.CAP_PROP_FPS, FPS)
FPS = cap.get(cv2.CAP_PROP_FPS) #get the actual fps
print(width,height,FPS)
firstloop = True
framecount = 0
while True:
  print(framecount)
  if framecount<segmentlength_frames and not(firstloop):
    print(framecount)
    print("something is not right, reinit cv2.VideoCapture")
    time.sleep(10)
    cap = cv2.VideoCapture(-1)
  framecount = 0
  firstloop = False
  timestamp  = get_timestamp()
  print(f"{timestamp}")
  try:
    writer= cv2.VideoWriter(f'{VID_DIR}/{timestamp}-{FPS}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), FPS, (width,height))
    while True:
      ret,frame= cap.read()
      if not ret:
        framecount = 0
        break
      writer.write(frame)
      framecount += 1
      if (framecount>=segmentlength_frames):
        break
    writer.release()
  except cv2.error as e:
    #ramutu ramungkin, cv2 print warning bukan throw exception
    print(e)
    cap = cv2.VideoCapture(-1)
  #end of one segment video


cap.release()
cv2.destroyAllWindows()

