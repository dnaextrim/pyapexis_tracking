#!/usr/bin/env python

from pyopencv import *
from ctypes import c_int
import sys
import urllib

from apexisconst import *

class PeopleTracking:
    
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        
        capture = VideoCapture()
        frame = Mat()
        
        hog = HOGDescriptor()
    
        hog.setSVMDetector(HOGDescriptor.getDefaultPeopleDetector())
        
        capture.open( "http://%s:%d/videostream.cgi?user=%s&pwd=%s" % (self.ip, self.port, self.username, self.password) )
        
        if capture.isOpened():
            while True:
                capture >> frame
                if frame.empty():
                    break
                
                self.detectAndTracking( frame, hog, "video" )
                #imshow("people detector", frame)
                if waitKey( 10 ) >= 0:
                    break
        
        setPosition( 31 )
        


    def setPosition( self, cmd ):
        f = urllib.urlopen( "http://%s:%d/decoder_control.cgi?user=%s&pwd=%s&command=%d" % (self.ip, self.port, self.username, self.password, cmd) )

        s = f.read()
        f.close()
    
    
    def detectAndTracking( self, img, hog, type ):
        
        t = getTickCount()
        # run the detector with default parameters. to get a higher hit-rate
        # (and more false alarms, respectively), decrease the hitThreshold and
        # groupThreshold (set groupThreshold to 0 to turn off the grouping completely).
        #found = hog.detectMultiScale(img, 0, Size(8,8), Size(32,32), 1.05, 5)
        found = hog.detectMultiScale(img, 0, Size(8,8), Size(24,16), 1.05, 2)
        t = float(getTickCount()) - t
        print("Detection time = %gms\n" % (t*1000./getTickFrequency()))
        
        #if ( type.lower() == 'image' ):
        for r in found:
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            r.x += round(r.width*0.1)
            r.y += round(r.height*0.1)
            r.width = round(r.width*0.8)
            r.height = round(r.height*0.8)
            rectangle(img, r.tl(), r.br(), Scalar(0,255,0), 1)
            
            #move left
            if r.x < ( ( img.cols / 2 ) - ( r.width / 2 ) ):
                setPosition( PAN_LEFT )
                print "Left"
                CMD = PAN_LEFT
            
            #move right
            elif r.x > ( ( img.cols / 2) + ( r.width / 2 ) ):
                setPosition( PAN_RIGHT )
                print "Right"
                CMD = PAN_RIGHT
                
            #is center position
            elif r.x >= ( ( img.cols / 2 ) - ( r.width / 2 ) ) and r.x <= ( ( img.cols / 2) + ( r.width / 2 ) ):
                print "Center"
                setPosition( PAN_LEFT_STOP )
                setPosition( PAN_RIGHT_STOP )
                CMD = 0
                #break
            elif CMD == 0:
                setPosition( PAN_LEFT_STOP )
                setPosition( PAN_RIGHT_STOP )
            
            if CMD == 0:
                #move up
                if r.y < ( ( img.rows / 2 ) - ( r.height / 2 ) ):
                    setPosition( TILT_UP )
                    print "Up"
                    CMD = TILT_UP
                
                #move down
                elif r.y > ( ( img.rows / 2 ) + ( r.height / 2 ) ):
                    setPosition( TILT_DOWN )
                    print "Down"
                    CMD = TILT_DOWN
                
                #is middle position
                elif r.y >= ( ( img.rows / 2 ) - ( r.height / 2 )  ) and r.y <= ( ( img.rows / 2) + ( r.height / 2 ) ):
                    print "Middle"
                    setPosition( TILT_UP_STOP )
                    setPosition( TILT_DOWN_STOP )
                    CMD = 0
                    #break
                elif CMD == 0:
                    setPosition( TILT_UP_STOP )
                    setPosition( TILT_DOWN_STOP )
                
        if len(found) <= 0:
            setPosition( 31 )

if __name__ == "__main__":
    capture = VideoCapture()
    frame = Mat()
    img = Mat()
    if len(sys.argv) > 1:
        img = imread(sys.argv[1])
    
    """    
    if img.empty():
        print( "ERROR: no image was specified\n" if len(sys.argv) == 1 else "ERROR: the specified image could not be loaded\n")
        print( "Usage: peopledetect <inputimage>\n" )
        sys.exit(-1)
    """
    namedWindow("people detector", 1)
    #namedWindow("process people detector", 1)
    
    hog = HOGDescriptor()
    
    hog.setSVMDetector(HOGDescriptor.getDefaultPeopleDetector())
    
    if img.empty():
        capture.open( "http://192.168.1.105:8082/videostream.cgi?user=admin&pwd=" )
    
    if capture.isOpened():
        while True:
            capture >> frame
            if frame.empty():
                break
            
            PeopleDetect( frame, hog, "video" )
            imshow("people detector", frame)
            if waitKey( 10 ) >= 0:
                break
    else:
        PeopleDetect( img, hog, "image" )
        imshow("people detector", img)
        waitKey(0)
    
    setPosition( 31 )
