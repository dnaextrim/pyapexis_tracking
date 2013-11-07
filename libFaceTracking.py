#!/usr/bin/env python

import sys
import urllib

from pyopencv import *

from apexisconst import *


class FaceTracking:
    
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        
        capture = VideoCapture()
        frame = Mat()
        
        scaleOpt = "--scale="
        cascadeOpt = "--cascade="
        nestedCascadeOpt = "--nested-cascade"
        nestedCascadeOptLen = len(nestedCascadeOpt)
        inputName = ""

        cascade = CascadeClassifier()
        nestedCascade = CascadeClassifier()
        scale = 1.0
        
        cascade.load( cascadeName )
        
        capture.open( "http://%s:%d/videostream.cgi?user=%s&pwd=%s" % (self.ip, self.port, self.username, self.password) )
        
        if capture.isOpened():
            while True:
                capture >> frame
                if frame.empty():
                    break

                self.detectAndTracking( frame, cascade, nestedCascade, scale )

                if waitKey( 10 ) >= 0:
                    break
        
        
        setPosition( 31 )
    
    
    def setPosition(self, cmd ):
        f = urllib.urlopen( ( "http://%s:%d/decoder_control.cgi?user=%s&pwd=%s&command=%d" ) % (self.ip, self.port, self.username, self.password, cmd) )

        s = f.read()
        f.close()
    
    
    def detectAndTracking(self, img, cascade, nestedCascade, scale):
        i = 0
        t = 0.0
        colors =  ( CV_RGB(0,0,255),
            CV_RGB(0,128,255),
            CV_RGB(0,255,255),
            CV_RGB(0,255,0),
            CV_RGB(255,128,0),
            CV_RGB(255,255,0),
            CV_RGB(255,0,0),
            CV_RGB(255,0,255))
        gray = Mat()
        smallImg = Mat( Size(round(img.cols/scale), round(img.rows/scale)), CV_8UC1 )

        cvtColor( img, gray, CV_BGR2GRAY )
        resize( gray, smallImg, smallImg.size(), 0, 0, INTER_LINEAR )
        equalizeHist( smallImg, smallImg )

        t = getTickCount()
        faces = cascade.detectMultiScale( smallImg, 
            1.1, 2, 0
            #|CascadeClassifier.FIND_BIGGEST_OBJECT
            #|CascadeClassifier.DO_ROUGH_SEARCH
            |CascadeClassifier.SCALE_IMAGE
            ,
            Size(30, 30) )
        t = getTickCount() - t
        print( "detection time = %lf ms\n" % (t/(getTickFrequency()*1000.)) )
        
        for i in range(len(faces)):
            r = faces[i]
            color = colors[i%8]
            center = Point(round((r.x + r.width*0.5)*scale), round((r.y + r.height*0.5)*scale))
            radius = round((r.width + r.height)*0.25*scale)
            circle( img, center, radius, color, 3, 8, 0 )

            #move left
            if center.x < ( ( img.cols / 2 ) - radius ):
                setPosition( PAN_LEFT )
                print "Left"
                CMD = PAN_LEFT
            
            #move right
            elif center.x > ( ( img.cols / 2) + radius ):
                setPosition( PAN_RIGHT )
                print "Right"
                CMD = PAN_RIGHT
                
            #is center position
            elif center.x >= ( ( img.cols / 2 ) - radius ) and center.x <= ( ( img.cols / 2) + radius ):
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
                if center.y < ( ( img.rows / 2 ) - radius ):
                    setPosition( TILT_UP )
                    print "Up"
                    CMD = TILT_UP
                
                #move down
                elif center.y > ( ( img.rows / 2 ) + radius ) - 50:
                    setPosition( TILT_DOWN )
                    print "Down"
                    CMD = TILT_DOWN
                
                #is middle position
                elif center.y >= ( ( img.rows / 2 ) - radius ) and center.y <= ( ( ( img.rows / 2) + radius ) - 50 ):
                    print "Middle"
                    setPosition( TILT_UP_STOP )
                    setPosition( TILT_DOWN_STOP )
                    CMD = 0
                    #break
                elif CMD == 0:
                    setPosition( TILT_UP_STOP )
                    setPosition( TILT_DOWN_STOP )
            
            
            if nestedCascade.empty():
                continue
            
            """
            smallImgROI = smallImg(r)
            nestedObjects = nestedCascade.detectMultiScale( smallImgROI, 
                1.1, 2, 0
                #|CascadeClassifier.FIND_BIGGEST_OBJECT
                #|CascadeClassifier.DO_ROUGH_SEARCH
                #|CascadeClassifier.DO_CANNY_PRUNING
                |CascadeClassifier.SCALE_IMAGE
                ,
                Size(30, 30) )
            for nr in nestedObjects:
                center = Point(round((r.x + nr.x + nr.width*0.5)*scale), round((r.y + nr.y + nr.height*0.5)*scale))
                radius = round((nr.width + nr.height)*0.25*scale)
                circle( img, center, radius, color, 3, 8, 0 )
            """
            
        if len(faces) <= 0:
            setPosition( 31 )
            #setPosition( PAN_LEFT_STOP )
            #setPosition( PAN_RIGHT_STOP )
            #setPosition( TILT_UP_STOP )
            #setPosition( TILT_DOWN_STOP )
        
        #imshow( "result", img )
        
