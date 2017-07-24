#!/usr/bin/env python
import sys
import roslib
import rospy
import serial
import math
from std_msgs.msg import UInt16
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
import pyuarm

class uarm_teleop(object):
    
   def __init__(self,mode="twist"):
  
      self.gripper_btn=0
      self.selector_btn=1
 
      self.arm_pos=[]
      self.mode = mode 
      self.arm = pyuarm.get_uarm()
      self.arm.set_gripper(0)
      self.arm.set_pump(0)
      
      self.gripstate = False
      self.selectorstate = False
      self.gripdb=0
      self.selectordb=0

      rospy.init_node('uarm_teleop',anonymous=False)
      #Set a small queue size so we don't drink from the firehose too much
      self.spnav=rospy.Subscriber("/spacenav/joy",Joy,self.spnavCB,queue_size=10)

      #while not rospy.is_shutdown(): 

      #self.arm_pos = self.arm.get_position()
     
      rospy.spin()

   def spnavCB(self,spnav):
      
      print spnav
      posx=0.0
      posy=0.0
      posz=0.0 

      arm_data = Joy()
 
      if spnav.buttons[self.gripper_btn]:
         self.gripdb +=1 
         if self.gripdb >5: 
            self.gripstate = not self.gripstate
            self.arm.set_gripper(self.gripstate)
            self.gripdb=0
 
      if spnav.buttons[self.selector_btn]: 
         self.selectordb +=1
         if self.selectordb >5: 
            self.selectorstate = not self.selectorstate
            print "selectorstate is now %s" % self.selectorstate
            self.selectordb=0
        
      arm_data.axes = spnav.axes 
      #filter out dominant axes vs. noise
      self.arm_pos = self.arm.get_position()
      #If we're manipulating the main arm... 
      if not self.selectorstate:
         posx=self.arm_pos[0]+(arm_data.axes[0]*100)
         posz=self.arm_pos[2]+(arm_data.axes[2]*100)
         if self.mode == "slide":
            posy=self.arm_pos[1]+(arm_data.axes[1]*100)
         if self.mode == "twist": 
            ady=arm_data.axes[5] *-1
            posy=self.arm_pos[1]+(ady*100) 
           
      #We set a high velocity because we're mostly dealing w/ a flood of messages that result in small moves 
         self.arm.set_position(posx,posy,posz,5000)
      #We're in wrist-mode
      else:
         wrist_input_angle = spnav.axes[5]*-1
         self.eff_angle = self.arm.get_servo_angle(3)+(wrist_input_angle*100)
         self.arm.set_wrist(self.eff_angle) 
   
   def shutdown(self):
      print "Got shutdown notice!"
      self.arm.close()
      sys.exit(1)


if __name__ == '__main__':
   try:
      uarm_teleop("twist")   
   except rospy.ROSInterruptException():
      print "Shutting down!" 
      sys.exit(1)
