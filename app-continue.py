#!/usr/bin/env python3
import datetime
import re
import cv2
import time
import os
import sys
import subprocess
import traceback
import requests

from vid import serve

is_windows = False
try:
  os.environ['WINDIR']
  is_windows = True
except:pass

with open("password") as f:
  upload_password = f.read()
  upload_password = upload_password.replace("\n","")


WIDTH = 640
HEIGHT = 480
FPS = 30
if is_windows:
  WIDTH = 1920
  HEIGHT = 1080
  FPS = 30

OLED_DISPLAY = False
ser = None
if "oled" in sys.argv:
  import serial
  OLED_DISPLAY = True
  ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
else:
  print("argument 'oled' to enable oled display")

img_only = False
if "img" in sys.argv:
  img_only = True
else:
  print("argument 'img' to capture only img and upload to izzulmakin.com/hashfile/cctv-img")
  

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
      if img_only:
        self.main_img_only()
      else:
        self.main()
    finally:
      traceback.print_exc()
      self.cap.release()
      cv2.destroyAllWindows()
      try:
          ser.close()
          display("serial closed")
      except:pass
  
  def cap_init(self):
    global WIDTH
    global HEIGHT
    global FPS
    #cap init, set to global variable WIDTH,HEIGHT,FPS
    #@return tuple of the actual (width,height,fps)
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
    return (width,height,FPS)
    #end of cap init

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
          cv2.putText(frame,get_timestamp(),(50,50),font,1,(0,255,255),2,cv2.LINE_4)
          writer.write(frame)
          framecount += 1
          #time.sleep(2/FPS) #to self.capture the same frame amount for longer record time, (N/FPS) result in N times fastforward video
          if (framecount>=segmentlength_frames):
            print("saving current frame to shot.png")
            cv2.imwrite(f"shot.png",frame)
            self.upload("cctv-img","shot.png")
            break
        writer.release()

        start = time.time()
        print("converting")
        self.convert(filename)
        delta = time.time()-start
        print(f"converting done in {delta} seconds")

      except cv2.error as e:
        #ramutu ramungkin, cv2 print warning bukan throw exception
        display(e)
        traceback.print_exc()
        raise Exception("wagu")
      #end of one segment video


  def main_img_only(self):
    font = cv2.FONT_HERSHEY_SIMPLEX
        
    self.cap_init()
  
    timestamp  = get_timestamp()
    display(f"{timestamp}")
    
    while True:
      ret,frame= self.cap.read()
      if not ret:
        print("camera error, reinit")
        time.sleep(30)
        self.cap_init()
        time.sleep(5)
        continue
      cv2.putText(frame,get_timestamp(),(50,50),font,1,(0,255,255),2,cv2.LINE_4)
      filename = f"/tmp/shot{get_timestamp()}.jpg"
      display(f"saving current frame to {filename}")
      cv2.imwrite(f"{filename}",frame)
      self.upload("cctv-img",filename)
      self.cap.release()
      time.sleep(60)
      self.cap_init()
    #end of one segment video

    

  def upload(self, hashid, filename):
    #hashid: the id of hashfile to store (cctv, or cctv-img)
    #filename: path to file
    try:
      print(f"uploading {filename}")
      r = requests.post(f"https://izzulmakin.com/hashfile/",
        files={
          'file':open(f"{filename}", 'rb')
        },
        data={
          "hashxxx_password":upload_password,
          "hashxxx_hashid":hashid
        }
      )
      print(r.text)
    except:
      traceback.print_exc()


  def convert(self,filename):
    #filename: a fullpath
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
      
      self.upload("cctv", f"{filename}.x265.mp4")
    except:
      traceback.print_exc()


if __name__=="__main__":
  app = Main()
    
