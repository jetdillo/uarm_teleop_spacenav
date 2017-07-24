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
    
   def __init__(self):
  
      self.gripper_btn=0
      self.pump_btn=1
 
      self.arm_pos=[]
      
      self.arm = pyuarm.get_uarm()
      self.arm.set_gripper(0)
      self.arm.set_pump(0)
      
      self.gripstate = False
      self.pumpstate = False
      self.gripdb=0
      self.pumpdb=0

      rospy.init_node('uarm_teleop',anonymous=False)
      #Set a small queue size so we don't drink from the firehose too much
      self.spnav=rospy.Subscriber("/spacenav/joy",Joy,self.spnavCB,queue_size=10)

      #while not rospy.is_shutdown(): 

      #self.arm_pos = self.arm.get_position()
     
      rospy.spin()

   def spnavCB(self,spnav):
      
      print spnav
 
      arm_data = Joy()
 
      if spnav.buttons[self.gripper_btn]:
         self.gripdb +=1 
         if self.gripdb >5: 
            self.gripstate = not self.gripstate
            self.arm.set_gripper(self.gripstate)
            self.gripdb=0
 
      if spnav.buttons[self.pump_btn]: 
         self.pumpdb +=1
         if self.pumpdb >5: 
            self.pumpstate = not self.pumpstate
            self.arm.set_pump(self.pumpstate)
            self.pumpdb=0
        
      arm_data.axes = spnav.axes 
      #filter out dominant axes vs. noise
      self.arm_pos = self.arm.get_position()

      posx=self.arm_pos[0]+(arm_data.axes[0]*100)
      posy=self.arm_pos[1]+(arm_data.axes[1]*100)
      posz=self.arm_pos[2]+(arm_data.axes[2]*100)
      #We set a high velocity because we're mostly dealing w/ a flood of messages that result in small moves 
      self.arm.set_position(posx,posy,posz,5000)
   
   def shutdown(self):
      print "Got shutdown notice!"
      self.arm.close()
      sys.exit(1)


if __name__ == '__main__':
   try:
      uarm_teleop()   
   except rospy.ROSInterruptException():
      print "Shutting down!" 
      sys.exit(1)
