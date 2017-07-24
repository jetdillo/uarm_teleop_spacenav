#!/usr/bin/env python
import roslib
import rospy
import serial
import math
from std_msgs.msg import UInt16
from sensor_msgs.msg import Range

import sys, select, termios, tty

import zeemote_listener2 as zd

msg = """
Using a Zeemote hand-held joystick to drive a non-Turtle robot

D toggles the E-Stop

CTRL-C to quit
"""

damp = .25
turn = 1

steerval=90
driveval=80
minspeed=driveval
straight=steerval

estop=True

def vels(speed,turn):
	return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":

        # Object creation
        zm = zd.ZeemoteControl()

# Connection
	zm.connect()

	steerpub = rospy.Publisher('steerpwm',UInt16)
        drivepub = rospy.Publisher('drivepwm',UInt16)
	rospy.init_node('teleop_drive_zeemote')

	steerpub.publish(steerval)
	drivepub.publish(driveval)
	
	if estop:
		print("ESTOP IS ENABLED")
	else:
		print("ESTOP IS DISABLED")

	try:
	   	while(1):
			zeepacket=zm.listen()
			if zeepacket['msg_id'] == "\x08":
				
			#directional packet
			#things get a little weird here since this is an analog
			#joystick and it's hard to get it to sit right on U;D;L;R
			#so we have to play some silly buggers with byte values in quadrants
			#As in Y=128 X=0 is UP but the up/left diagonal is 
			#Y=128-0 and X=0-127

				ZX=ord(zeepacket['X'])
				ZY=ord(zeepacket['Y'])
				#if the joystick is not at rest...
				if not ZY==0:
				   if ZY >=128:
				      speedmod = (255-ZY)*damp
				      driveval=minspeed+speedmod
	
				   if ZY <=127:
				      speedmod = ZY*damp
				      driveval=minspeed-speedmod
				   print "ZY=%d driveval=%d" % (ZY,driveval)
				else:
				   driveval=minspeed

			        if not ZX==0:	
				   if ZX >=128:
				      steermod = (255-ZX)*damp
				      steerval=straight+steermod
				
		      		   if ZX <=127:
				      steermod = ZX*damp
				      steerval=straight-steermod
				else:
				   steerval=straight

			if zeepacket['msg_id'] == "\x07":
				print zeepacket
				if zeepacket['Key Code 1'] == "\x00":
				#Button A
				        damp=damp*2
				elif zeepacket['Key Code 1'] == "\x01":
				#Button B
					damp=damp/2
				#elif zeepacket['Key Code 1'] == "\x02":
				#Button C
				#	estop=False
				elif zeepacket['Key Code 1'] == "\x03":
				#Button D
					if estop:
				    	   print("ESTOP IS DISABLED")
					   estop=False
					else:
					   estop=True
				    	   print("ESTOP IS ENABLED")
					   steerpub.publish(straight)
					   drivepub.publish(driveval)
			if not estop:
				steerpub.publish(steerval)
				drivepub.publish(driveval)

	except IOError, (e):
		print "caught exception %s" %e

	finally:
		steerpub.publish(steerval)
		drivepub.publish(driveval)
