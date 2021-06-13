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

FPS = 3
SEGMENTLENGTH = 2 #minutes
segmentlength_frames = SEGMENTLENGTH*60*FPS
cap= cv2.VideoCapture(0)

width= int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True:
  framecount = 0
  timestamp  = get_timestamp()
  print(f"{timestamp}")
  writer= cv2.VideoWriter(f'{VID_DIR}/{timestamp}.mp4', cv2.VideoWriter_fourcc(*'DIVX'), FPS, (width,height))
  while True:
      ret,frame= cap.read()
      writer.write(frame)
      framecount += 1
      if (framecount>=segmentlength_frames):
        break
  writer.release()
  #end of one segment video


cap.release()
cv2.destroyAllWindows()

