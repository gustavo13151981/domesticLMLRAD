#!/usr/bin/env python

# Domestic ML activated LRAD 
# Roni Bandini, @RoniBandini
# November 2022
# Usage: sudo python lrad.py

import cv2
import os
import sys, getopt
import signal
import time
import subprocess
import RPi.GPIO as GPIO
import tm1637
import numpy as np
from datetime import datetime
from edge_impulse_linux.image import ImageImpulseRunner

runner = None
show_camera = False

model = "domestic-ml-lrad-2-linux-armv7-v8.eim"
detectionLimit=0.75
relayPin=4
isPlaying=0
playSeconds=5

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relayPin, GPIO.OUT)

# Creating 4-digit 7-segment display object
tm = tm1637.TM1637(clk=3, dio=2)  # Using GPIO
clear = [0, 0, 0, 0]  # Defining values used to clear the display

# 7 segment intro
tm.write(clear)
time.sleep(1)
s = 'LRAD started'
tm.scroll(s, delay=250)
time.sleep(5)

# turn off amp just in case
GPIO.output(relayPin, GPIO.LOW)

def now():
    return round(time.time() * 1000)

def get_webcams():
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" %port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName =camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('Usage: python lrad.py')

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args)>= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('Cannot find any webcams')
                if len(args)<= 1 and len(port_ids)> 1:
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                videoCaptureDeviceId = int(port_ids[0])

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            os.system('clear')
            print('Domestic LRAD with computer vision trigger')
            print('Roni Bandini, November 2022')
            print('')
            print('Machine Learning model: ' + modelfile)

            next_frame = 0 # limit to ~10 fps here

            for res, img in runner.classifier(videoCaptureDeviceId):
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)

                #print('classification runner response', res)

                if "classification" in res["result"].keys():

                    print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')

                    for label in labels:

                        score = res['result']['classification'][label]

                        print('%s: %.2f\t' % (label, score), end='')

                        if (score>detectionLimit and label=='fighting'):

                            # turn on amp
                            print("Turn on amp...")
                            GPIO.output(relayPin, GPIO.HIGH)

                            # display info
                            tm.write(clear)
                            time.sleep(1)
                            s = 'Fight'
                            tm.scroll(s, delay=250)

                            # play mp3

                            print("Play wav 1")
                            process = subprocess.Popen("aplay lrad1.wav", shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)

                            time.sleep(playSeconds)

                            print("Stop mp3...")
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

                            # turn off amp
                            print("Turn off amp...")
                            GPIO.output(relayPin, GPIO.LOW)
                        else:
                            #print("Not a fight - "+label+" -> "+str(score))

                            if (label=='fighting'):
                                tm.numbers(int(score*100), 0, colon=True)

                    print('', flush=True)

                next_frame = now() + 1000

                print("...")
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
   main(sys.argv[1:])
