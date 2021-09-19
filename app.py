#!/usr/bin/env python3
import datetime
import re
import cv2
import time
import os
import sys
import subprocess
import traceback

from vid import serve

is_windows = False
try:
  os.environ['WINDIR']
  is_windows = True
except:pass


OLED_DISPLAY = False
ser = None
try:
    import serial
    if sys.argv[1]=="oled":
        OLED_DISPLAY = True
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
except:
    print("argument 'oled' to enable oled display")

OLED_MSG_HEAD = " "
def display(text):
    print(text)
    if OLED_DISPLAY:
        text = OLED_MSG_HEAD+str(text)
        if text[-1]!="\n": text+="\n"
        ser.write(text.encode('utf8'))

def get_timestamp():
  return re.findall("([\d\-T\:]+)", datetime.datetime.now().isoformat() )[0].replace(":","-")

BASE_DIR = os.path.dirname( os.path.realpath(sys.argv[0]) )
VID_DIR = f"{BASE_DIR}/vid"
if is_windows:
    os.chdir(BASE_DIR)
    VID_DIR = "./vid"
CAP = -1
if is_windows:
  CAP = 0
class Main(object):
  def __init__(self):
    try:
      self.main()
    finally:
      traceback.print_exc()
      self.cap.release()
      cv2.destroyAllWindows()
      try:
          ser.close()
          display("serial closed")
      except:pass

  def main(self):
    font = cv2.FONT_HERSHEY_SIMPLEX
    WIDTH = 640
    HEIGHT = 480
    FPS = 30
    if is_windows:
      WIDTH = 1920
      HEIGHT = 1080
      FPS = 30
    SEGMENTLENGTH = 2 #minutes, low performance would self.capture less and have fast forwarded video and segment length is getting longer
    segmentlength_frames = SEGMENTLENGTH*60*FPS
    
    #cap init
    self.cap = cv2.VideoCapture(CAP)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,WIDTH)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,HEIGHT)
    #get the actual w.h
    time.sleep(1)
    width= int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height= int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    self.cap.set(cv2.CAP_PROP_FPS, FPS)
    FPS = self.cap.get(cv2.CAP_PROP_FPS) #get the actual fps
    display("{},{},{}".format(width,height,FPS))
    segmentlength_frames = SEGMENTLENGTH*60*FPS
    #end of cap init
    
    firstloop = True
    framecount = 0
    while True:
      display(framecount)
      if framecount<segmentlength_frames and not(firstloop):
        display(framecount)
        display("something is not right, reinit cv2.VideoCapture")
        time.sleep(10)
        #cap init
        self.cap = cv2.VideoCapture(CAP)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,HEIGHT)
        #get the actual w.h
        time.sleep(1)
        width= int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height= int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        FPS = self.cap.get(cv2.CAP_PROP_FPS) #get the actual fps
        display("{},{},{}".format(width,height,FPS))
        segmentlength_frames = SEGMENTLENGTH*60*FPS
        #end of cap init
      framecount = 0
      firstloop = False
      timestamp  = get_timestamp()
      display(f"{timestamp}")
      try:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') #.mp4
        fourcc = cv2.VideoWriter_fourcc(*'MJPG') #.avi
        filename = f'{VID_DIR}/{timestamp}.avi'
        writer= cv2.VideoWriter(filename, fourcc, FPS, (width,height))
        lastimg = None
        idle = True
        d = 1
        idle_limit = 4
        idle_sampling = idle_limit
        while True:
          ret,frame= self.cap.read()
          if not ret:
            framecount = 0
            break
          if idle:
            img = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            img = cv2.calcHist([img], [0], None, [32], [0,256])
            if (lastimg is not None):
              d = cv2.compareHist(img,lastimg, cv2.HISTCMP_CORREL)
              display(d)
              if d<0.998 and idle_sampling<=0: #start recording only when detect movement
                idle = False
                display("movement detected, start recording")
                timestamp = get_timestamp() #start timestamp
                cv2.putText(frame,timestamp,(50,50),font,1,(0,255,255),2,cv2.LINE_4)
                cv2.imwrite(f"{filename}.png",frame)
                idle_sampling = idle_limit
              if d<0.998 and idle_sampling>0:
                idle_sampling -= 1
                #if we start counting idle sampling, dont update last img
                img = lastimg
            lastimg = img
          else: #not idle
            cv2.putText(frame,get_timestamp(),(50,50),font,1,(0,255,255),2,cv2.LINE_4)
            writer.write(frame)
            framecount += 1
          #time.sleep(2/FPS) #to self.capture the same frame amount for longer record time, (N/FPS) result in N times fastforward video
          if (framecount>=segmentlength_frames):
            break
        writer.release()
        if is_windows:
            subprocess.check_output(f"python convert.py {filename}  > converting.txt  2>&1 &",shell=True)
        else:
            subprocess.check_output(f"nohup python3 convert.py {filename}  > /dev/null 2>&1 &",shell=True)
      except cv2.error as e:
        #ramutu ramungkin, cv2 print warning bukan throw exception
        display(e)
        traceback.print_exc()
        raise Exception("wagu")
      #end of one segment video



if __name__=="__main__":
  app = Main()
    
