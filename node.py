#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import thread
import threading
import time
import random
import socket
from readPhotoresistance import *
from MsgHandler import MsgHandler

# photoresistor
import PCF8591 as ADC
import RPi.GPIO as GPIO


global timerSendMsg
global buffMsg, recvMsg
global buffSize, BS_addr, BS_port   

BS_addr = '192.168.1.106'
BS_port = 23333

PORT=10086

class Node():
    def __init__(self, nodeIndex, nodeName):
        #initialization of all the base parameters
        self.nodeIndex = nodeIndex
        self.nodeName = nodeName
        self.energy = 1000
        self.energyLock = threading.Lock()
        self.energyCapacity = 1000 # max level of energy
        self.energyThreshold = 0.3
        #self.addr = "202.120.000.000"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        self.addr = s.getsockname()[0]
        s.close()
        self.coordinate = [random.randint(0,40), random.randint(0,40)]
        #self.coordinate = [23,35]  #[x,y]
        self.codeStatus = 1  # 1: alive ; 0: dead
        # time between every two msg sent
        self.period = random.randint(1,5) # property of the node.
        # default set
        #!!!!!!!!!!!!!!!!!!!!!!!!!!# Add port!!!!!!!!################################ [addr, port, energy, coor]
        #self.clusterHead=["192.168.1.193", 500, [23,35]] #[address, energy, coordinate]
        self.clusterHead=[]
        # [] for ordinary node but a list of all nodes for the cluster head
        self.network = [] # a list of [(nodeAddr, nodePort),...]
        self.network.append([self.addr,self.energy,self.coordinate])
        
        self.energyUsedParam = 0.2

        self.allSensorData = ""
        
        self.simulateData = 0
        if self.simulateData:
            self.sensor = photoresistorSimulator()
        else:
            self.sensor = photoresistor()
            
    
    def send(self, addr_des, port_des, msg):
        if self.codeStatus == 0:
            return
        self.energyDissipated(addr_des, port_des)
        code=0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (addr_des, port_des)
        try:
            s.sendto(msg, addr)
            print 'sent:' + msg + ' to ' + addr_des
        except:
            code=1
        finally:
            #time.sleep(3)
            s.close()
            
        # send msg from addr_source to addr_des
        
        # return action status code:
        # 0: success
        # 1: fail
        return code
    

    def calculateCoor(self, x, y):
        distance = sqrt((x[0]-y[0])**2 + (x[1]-y[1])**2)
        if distance > 50:
            return 0
        else:
            return 1
        
    
    def receive(self,addr_source, port_source):
        code=0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.bind((addr_source, port_source)) 
        msgHandler=MsgHandler()
        while True:                                          
            data, addr = s.recvfrom(1024)
            #print 'received' + data
            type_msg=msgHandler.Decode(data)
            if type_msg==1:
                temp,code=msgHandler.Decode_CH_Change_Msg(data)
                if code==0:
                    judge = self.calculateCoor(temp[2], self.coor)
                    if judge:
                        self.clusterHead=temp
                        self.RefreshNetwork(temp)
                        print '******************************'
                        print 'received: CH change message: ' + str(temp)
                    else:
                        newInfo = [self.addr, self.energy, self.coor]
                        self.clusterHead = newInfo
                        self.RefreshNetwork(newInfo)
                        print '******************************'
                        print 'received: CH change message: ' + str(newInfo)

                    print 'CH changed to:'  + str(self.clusterHead)
                else:
                    print "error in decoding CH change msg."
            elif type_msg==2:
                temp,code=msgHandler.Decode_List_Info_Msg(data)
                if code==0:
                    self.network=temp
                    print 'received: ' + addr_source
                    print self.network
                else:
                    print "error in decoding list of info msg"
            elif type_msg==3:
                temp,code=msgHandler.Decode_Info_Msg(data)
                if code==0:                 
                    Ischanged=self.RefreshNetwork(temp)
                    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                    #print temp[0]
                    print 'received Info from:  ' + str(temp)
                    #print temp
                    #print Ischanged
                else:
                    print 'Error in decoding info msg'
            elif type_msg==4:
                temp,code=msgHandler.Decode_Sensor_Data(data)
                if code==0:
                    self.allSensorData=self.allSensorData+temp  
                    print 'received sensor data: '  + str(temp)
                else:
                    print 'Error in decoding sensor data'               
                #TODO: boradcast response 
            elif type_msg==5:
                 addr_des,code=msgHandler.Decode_Broadcast_msg(data)
                 if code==0:
                    print '^^^^^^^^^^^^^^^^^'
                    print 'Received broadcast from:' + addr_des
                    print 'Own address' + self.addr
                    msg=msgHandler.Encode_Info_Msg(self.addr,self.energy,self.coordinate)
                    IsSent = self.send(addr_des, PORT,msg)
                    #print 'IsSent; ' + str(IsSent)
                 else:
                    print 'Error in decoding broadcast message.'   
            elif type_msg==0:
                print 'error in decode message' + data
        #analyze data
        # connect to the speicified address and port
        # receive message
        # analyze message
        # store important information into the msg

        # return action status code
        # 0: success
        # 1: fail
        return code

    def initReceive(self):
        code=0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.bind(('', PORT)) 
        msgHandler=MsgHandler()
        while True:
            data, addr = s.recvfrom(1024)
            #print 'received' + data
            type_msg=msgHandler.Decode(data)
            if type_msg==1:
                temp,code=msgHandler.Decode_CH_Change_Msg(data)
                if code==0:
                    self.clusterHead=temp
                    self.RefreshNetwork(temp)
                    print '******************************'
                    print 'received CH change message: ' + str(temp)
                    print 'CH changed to:' + str(self.clusterHead)
                else:
                    print "error in decoding CH change msg."
                s.close()
                break
        return code

        
    def RefreshNetwork(self,info):
        code=0
        #print '-----------Refresh-------------'
        #print(info)
        address=info[0]
        energy_level=int(info[1])
        coor=[0,0]
        coor=info[2]
        IsChange=False
        #try:
        for i in range(len(self.network)):
            if self.network[i][0]== address:
                self.network[i][1]=int(energy_level)
                self.network[i][2]=coor
                IsChange=True
                break

        if IsChange==False:
            self.network.append(info)
        #except :
            #print 'info updata failed.'
            #code=1

        # return action status code
        # 0: success
        # 1: fail
        return code
    
    
    def energyDissipated(self, des_addr, des_port, flag=0):
        # receive the coordinate of source and destination
        # [xs,ys] and [xd,yd]
        # return the energy needed
        #return self.energyUsedParam * ((xs-xd)**2+(ys-yd)**2)
        self.energyLock.acquire()
        if (des_addr == BS_addr):
            self.energy -= 100
        else:
            self.energy -= 30
        if self.energy <= self.energyCapacity * self.energyThreshold:
            self.codeStatus = 0
            
        self.energyLock.release()
        #print "Energy remained" + str(self.energy)
        
        
    def getEnergy(self):
        # obtain the current value mesured by photoresistor
        return self.energy
        
        
    def rechargeEnergy(self):
        # larger value, less solar energy
        # add the energy to the self.energy
        valuePhotoresistor = self.sensor.dataRead()
        #print "valuePhotoresistor: " + str(valuePhotoresistor)
        print "Recharged Energy: " + str(((300 - valuePhotoresistor)/20)**2)
        energy = self.energy + ((300 - valuePhotoresistor)/20)**2
        self.energyLock.acquire()
        self.energy = min(energy, self.energyCapacity)
        if self.energy > self.energyCapacity * self.energyThreshold:
            self.codeStatus = 1
        self.energyLock.release()
        #print "Energy Level: " + str(self.energy)
        time.sleep(1)
    
    
    def rechargeEnergyThread(self):
        while 1:
            self.rechargeEnergy()
        
        
    def getNodeStatus(self):
        return self.codeStatus


    def broadcast(self):
        code=0
        try:
            # used by cluster head 
            # broadcast msg to all the neighboring nodes to call for the energy info...
            # return action status code (success or not)
            broadcast = '<broadcast>'
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_addr = (broadcast, PORT)
            #myname = socket.getfqdn(socket.gethostname())
            #myaddr = socket.gethostbyname(myname)
            
            demand_msg='Demand_info;'+self.addr+';'
            #print demand_msg
            s.sendto(demand_msg, broadcast_addr)
            s.close()
        
            self.energyDissipated('','',flag=1)
        except:
            code=1
        return code

        
    def selectNextHead(self):
        code=0
        try:
            self.network.sort(key= lambda x : x[1], reverse=True)
            self.clusterHead=self.network[0]
        except:
            code=1
        return code
    
    
if __name__ == '__main__':
    buff = []
    node = Node(1,'node1')
    MS_Handler=MsgHandler()
    print node.clusterHead
    node.send(BS_addr, BS_port, MS_Handler.Encode_Info_Msg(node.addr, node.energy, node.coordinate))
    node.initReceive()
    print node.clusterHead
    
    #timerSendMsg = threading.Timer()
    #buffSize = 10 # for the cluster head
    beginTime = time.time()
    timerUpdateHead = time.time()
    lastSend = time.time()
    CH_start = 0 # 1: Yes ;  0: No
    HOST=''
    try:
        thread.start_new_thread(node.rechargeEnergyThread, ())
        thread.start_new_thread(node.receive,(HOST,PORT,))
    except:
        print 'Thread Create Failed.'
    
    while (1):
        # judge if current node is cluster node
        if (node.clusterHead[0] == node.addr):
            if not CH_start:
                CH_start = 1
                timerUpdateHead = time.time()
                lastSend = time.time()
            
            # receive the fake data from sensor
            if (node.allSensorData!=""):
                buff.append(node.allSensorData)
                node.allSensorData = ""
            #for nodeInfo in node.network:

                #recvmsg = ''
                #node.receive(nodeInfo[0], nodeInfo[1]) # collect all the info from neighboring nodes
                #if (recvmsg!=''):
                #    buff.append(recvmsg)
            
            timeBetweenLast = time.time() - lastSend
            if (timeBetweenLast > 20):
                sendMsg = ''
                for i in range(0, len(buff)):
                    sendMsg += '\t'+ buff[i]

                node.send(BS_addr, BS_port, sendMsg)
                lastSend = time.time()
                buff = []


            duree = time.time() - timerUpdateHead
            # change cluster head
            if (duree > 40):
                print "Find next clusterhead"
                node.broadcast()
                time.sleep(2)
                print "Broadcast end"
                print "Before change: " + str(node.clusterHead[0])
                print node.network
                node.selectNextHead()
                print "Select end"
                print "After change: " + str(node.clusterHead[0])
                print node.network
                
                # tell the BS the information of the network
                node.send(BS_addr, BS_port, MS_Handler.Encode_List_Info_Msg(node.network))
                # send information to the new cluster head to let him be the new cluster head
                for eachNode in node.network:

                    code=node.send(eachNode[0], PORT, MS_Handler.Encode_CH_Change_Msg(node.clusterHead[0],node.clusterHead[1],node.clusterHead[2]))
                    print '++++++++++++++++'
                    #print code
                #timerUpdateHead=
                CH_start=0
        
            
            
            #elif (len(buff)==buffSize):
            #    node.send(BS_addr, BS_port, buff)
            #    lastSend = time.time()
            
           
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
            nodeTime = time.time() - lastSend


        if nodeTime > node.period: 
            temperature = random.randint(20,25)
            sensorData = str(temperature)
            sensorData=MS_Handler.Encode_Sensor_Data(sensorData)
            node.send(node.clusterHead[0], PORT, sensorData)
            lastSend = time.time()         
                   
