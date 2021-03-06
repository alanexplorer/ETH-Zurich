#! /usr/bin/env python

import rospy
import math
import numpy as np
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool, SetBoolResponse

class find():

    def __init__(self):

        self.node_name = rospy.get_name()
        self.laserInit = False
        self.alpha = 0.0
        self.x = 0
        self.y = 0
        self.emergency_stop = False

        sub = rospy.Subscriber('/scan', LaserScan, self.callback)
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        rospy.loginfo("[%s] Initializing " %(self.node_name))

        self.emergency_stop_srv = rospy.Service("/emergency_stop", SetBool, self.emergency_stop_cb)

        self.rate = rospy.Rate(10)

    def run(self):
        while not rospy.is_shutdown():
            self.move()
            self.rate.sleep()

    def move(self):
        vel_msg = Twist()
    
        if self.laserInit == True and self.emergency_stop == False:

            if self.x <= 1:
                vel_msg.linear.x = 0
                vel_msg.linear.y = 0 
                vel_msg.angular.z =0
            else:
                vel_msg.linear.x = self.x * 10
                vel_msg.linear.y = self.y * 10 
                vel_msg.angular.z = -self.alpha
        else:
            vel_msg.linear.x = 0
            vel_msg.linear.y = 0 
            vel_msg.angular.z =0


        self.pub.publish(vel_msg)

    def callback(self, msg):
        radius = 0.0
        #size = len(msg.ranges)
        for i, r in enumerate(msg.ranges):
            if(not math.isnan(r) and not math.isinf(r)):
                radius = r
                self.alpha = msg.angle_min + i*msg.angle_increment

        self.x = radius*math.cos(self.alpha)
        self.y = (-1)*radius*math.sin(self.alpha)
        self.laserInit = True
        
    def emergency_stop_cb(self, req):
        if req.data == True:
            self.emergency_stop = True
        else:
            self.emergency_stop = False
        res = SetBoolResponse()
        res.success = True
        res.message = "recieved"
        return res

if __name__ == '__main__':
    try:
        rospy.init_node('scan_values' , anonymous=True)
        f = find()
        f.run()
    except rospy.ROSInterruptException: pass