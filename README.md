# uarm_teleop_spacenav
A simple ROS node to allow teleop of the uFactory uArm with the 3Dconnexion SpaceMouse

This is a very bare-bones start of a teleop node to let you drive a uFactory uArm with the 3DConnexions SpaceMouse. Requires ros-$DISTRO-spacenav and spacenavd. 
Currently working: 
Linear cardinal directions drive the arm forward/back, up/down, pan left/right. The left button toggles the gripper (if installed) and the right button toggles the pneumatic pump(if installed). 
TBD: Angular driving and further button hacking. I will probably use the left button for general gripping and the right to toggle driving the arm vs. the end-effector servo. 

