import os
import sys

class MsgHandler():
	def __init__(self):
		pass

	def Encode_Sensor_Data(self,SensorData):
		msg='SensorData;'+SensorData+';'

		return msg

	def Decode_Sensor_Data(self,msg):
		code=0
		try:
			msg=msg[6:len(msg)]
		except:
			code=1

		return msg,code

	def Decode_Broadcast_msg(self,msg):
                code=0
                try:
                        Info_array=msg.split(';')
                except:
                        code=1

                return Info_array[1],code

	def Encode_Info_Msg(self,address, energy_level, coor):
		msg='Info;'+address+';'+str(energy_level)+';'+str(coor[0])+';'+str(coor[1])+';'
		#ex: Info;127.0.0.1;100;25;35;

		return msg

	def Decode_Info_Msg(self,msg):
		code=0
		try:
			Info_array=msg.split(';')
			address=Info_array[1]
			energy_level=int(Info_array[2])
			coor=[0,0]
			coor[0]=int(Info_array[3])
			coor[1]=int(Info_array[4])
		except:
			code=1
		return [address, energy_level, coor],code

	def Encode_List_Info_Msg(self,Network):
		msg='List_Info;'
		for info in Network:
			msg=msg+info[0]+';'
			msg=msg+str(info[1])+';'
			msg=msg+str(info[2][0])+';'
			msg=msg+str(info[2][1])+';'
		return msg

	def Decode_List_Info_Msg(self,msg):
		code=0
		try:
			Info_array=msg.split(';')
			number_Element=int((len(Info_array)-2)/4)
			#print(Info_array)
			Network=[]
			i=0
			k=1
			while i<number_Element:
				address=Info_array[3*i+k]
				energy_level=int(Info_array[3*i+k+1])
				coor=[0,0]
				coor[0]=int(Info_array[3*i+k+2])
				coor[1]=int(Info_array[3*i+k+3])
				info=[address,energy_level,coor]
				Network.append(info)
				i+=1
				k+=1
		except:
			code=1

		return Network,code


	def Encode_CH_Change_Msg(self,address,energy_level,coor):
		#ex: CH_chagne;127.0.0.1;
		msg='CH_change;'+address+';'+str(energy_level)+';'+str(coor[0])+';'+str(coor[1])+';'
		return msg

	def Decode_CH_Change_Msg(self,msg):
		code=0
		try:
			Info_array=msg.split(';')
			CH_addresss=Info_array[1]
			energy_level=int(Info_array[2])
			coor=[0,0]
			coor[0]=int(Info_array[3])
			coor[1]=int(Info_array[4])
		except:
			code=1
		return [CH_addresss, energy_level, coor],code

	def Encode(self):
		pass

	def Decode(self,msg):
		type_msg=0
		Info_array=msg.split(';')
		#print(Info_array)
		if Info_array[0]=='CH_change':
			type_msg=1
		elif Info_array[0]=='List_Info':
			type_msg=2
		elif Info_array[0]=='Info':
			type_msg=3
		elif Info_array[0]=='SensorData':
			type_msg=4
                elif Info_array[0]=='Demand_info':
                        type_msg=5
		else:
			type_msg=0

		return type_msg


'''TEST
Msg_Handler=MsgHandler()
address='192.168.0.1'
energy_level=88
coor=[20,25]
Info=(address,energy_level,coor)
Network=[(address,energy_level,coor)]
Network.append(Info)
Network.append(Info)
#print(Network)
Msg=Msg_Handler.Encode_Info_Msg(address, energy_level, coor)

#print(Msg)
address,energy_level,coor=Msg_Handler.Decode_Info_Msg(Msg)
#print(address)
#print(energy_level)
#print(coor)

Msg=Msg_Handler.Encode_List_Info_Msg(Network)
print(Msg)
tmp=Msg_Handler.Decode_List_Info_Msg(Msg)
print(tmp)'''





