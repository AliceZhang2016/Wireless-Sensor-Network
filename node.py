#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import threading
import time
import random
import socket
from readPhotoresistance import *

# photoresistor
import PCF8591 as ADC
import RPi.GPIO as GPIO


global timerSendMsg
global buffMsg
global buffSize, BS_addr, BS_Port	

class Node():
    def __init__(self, nodeIndex, nodeName):
        #initialization of all the base parameters
        self.nodeIndex = nodeIndex
        self.nodeName = nodeName
        self.energy = 500
	self.energyCapacity = 1000 # max level of energy
	self.energyThreshlod = 0.3
        self.addr = "202.120.000.000"
        self.coordinate = [23,35]  #[x,y]
        self.codeStatus = 1  # 1: alive ; 0: dead
        # time between every two msg sent
        self.period = random.randint(5,15) # property of the node.
        self.clusterHead=()
        # [] for ordinary node but a list of all nodes for the cluster head
        self.network = [] # a list of [(nodeAddr, nodePort),...]
        
        self.energyUsedParam = 0.2
		
	self.simulateData = 0
	if self.simulateData:
		self.sensor = photoresistorSimulator()
	else:
		self.sensor = photoresistor()
			
    
    def send(self, addr_des, port_des, msg):
        code=0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (addr_des, port_des)
        try:
            s.sendto(msg, addr)
            print 'sent:' + msg
        except:
            code=1
        finally:
            #time.sleep(3)
            sock.close()
        # send msg from addr_source to addr_des
        
        # return action status code:
        # 0: success
        # 1: fail
        return code
    
    def receive(self,addr_source, port_source):
        code=0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.bind((addr_source, port_source)) 
        msgHandler=MsgHandler()
        while True:                                          
            data, addr = s.recvfrom(1024)
            print 'received' + data
            type_msg=msgHandler.Decode(data)
            if type_msg==1:
                temp,code=msgHandler.Decode_CH_Change_Msg(msg)
                if code==0:
                    self.clusterHead=temp
                    self.RefreshNetwork(temp)
                    print 'CH changed:' + self.clusterHead
                else:
                    print "error in decoding CH change msg."
            elif type_msg==2:
                temp,code=msgHandler.Decode_List_Info_Msg(msg)
                if code==0:
                    self.network=temp
                    print self.network
                else:
                    print "error in decoding list of info msg"
            elif type_msg==3:
                temp,code=msgHandler.Decode_Info_Msg(msg)
                if code==0:                 
                    Ischanged=self.RefreshNetwork(temp)
                    print temp
                    print Ischanged
                else:
                    print 'Error in decoding info msg'
                
            elif type_msg==0:
                print 'error in decode message'
            #analyze data
        # connect to the speicified address and port
        # receive message
        # analyze message
        # store important information into the msg

        # return action status code
        # 0: success
        # 1: fail
        return code

    def RefreshNetwork(self,info):
        code=0
        address=info[0]
        energy_level=info[1]
        coor=[0,0]
        coor=info[2]
        IsChange=False
        try:
            for i in range(len(self.network)):
                if self.network[i][0]== address:
                    self.network[i][1]=energy_level
                    self.network[i][2]=coor
                    IsChange=True
                    break

            if IsChange==False:
                self.network.append(info)
        except :
            print 'info updata failed.'
            code=1

        # return action status code
        # 0: success
        # 1: fail
        return code
    
    def energyDissipated(self, source, des):
        # receive the coordinate of source and destination
        # [xs,ys] and [xd,yd]
        # return the energy needed
        return self.energyUsedParam * ((xs-xd)**2+(ys-yd)**2)
    
    def getEnergy(self):
        # obtain the current value mesured by photoresistor
        return self.energy
		
    def rechargeEnergy(self):
	# larger value, less solar energy
	# add the energy to the self.energy
	valuePhotoresistor = self.sensor.dataRead()
	energy += 300 - valuePhotoresistor
	self.energy = min(energy, self.energyCapacity)
	if self.energy > self.energyCapacity * self.energyThreshlod:
		self.codeStatus = 1
	time.sleep(1)
        
    def getNodeStatus(self):
        return self.codeStatus

    def broadcast(self):
        # used by cluster head 
        # broadcast msg to all the neighboring nodes to call for the energy info...
        # return action status code (success or not)
        return code
    
    def selectNextHead(self):
        # collect all the msg from other nodes
        # sort their energies
        # tell all the nodes in the network the new cluster head
        # update self.clusterHeadIndex
        self.clusterHeadIndex = newClusterHeadIndex
        return code
    
if __name__ == '__main__':
    node = Node(1,'node1')
    #timerSendMsg = threading.Timer()
    buffSize = 10 # for the cluster head
    beginTime = time.time()
    timerUpdateHead = time.time()
    lastSend = time.time()
    CH_start = 0 # 1: Yes ;  0: No
    
    thread.start_new_thread(node.rechargeEnergy, ())
	
    while (1):
        # judge if current node is cluster node
        if (node.clusterHeadIndex == node.nodeIndex):
            if not CH_start:
                CH_start = 1
                timerUpdateHead = time.time()
                lastSend = time.time()
            
            duree = time.time() - timerUpdateHead
            if (duree > 100):
                node.selectNextHead()
            
            timeBetweenLast = time.time() - lastSend
            if (timeBetweenLast > 20):
                node.send(BS_addr, BS_port, buff)
                lastSend = time.time()
                #buff = []
            #elif (len(buff)==buffSize):
            #    node.send(BS_addr, BS_port, buff)
            #    lastSend = time.time()
            
            for nodeInfo in node.network:
                recvmsg = ''
                node.recv(nodeInfo[0], nodeInfo[1], recvmsg) # collect all the info from neighboring nodes
                if (recvmsg!=''):
                    buff.append(recvmsg)
            
            
            '''
            timerUpdateHead = threading.Timer(100, node.selectNextHead)
            timerSendBS = threading.Timer(
                    20, node.send, 
                    args=[BS_addr, BS_port, msg])
            timerUpdateHead.start()
            timerSendBS.start()
            '''
                
        else:
            CH_start = 0
            node.send(CH_addr, CH_port, msg)
            

            
            
        
    
        
        
