#!/usr/bin/python
#
# Property of Groundworks Technologies
#
#
# Requires execution of dopatch_custom_frame.sh or dopath_IO.sh first to modify firmware.
#!/usr/bin/python
import sys,struct,os
from serial import *
import time,math
import decodepackets

# Color class
class bcolors:
    COLOR2 = '\033[96m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# serial object
# please adjust to device properties
serial = Serial(port="/dev/ttyACM0",baudrate=9600,bytesize=EIGHTBITS,parity=PARITY_NONE,stopbits=STOPBITS_ONE,timeout=None,xonxoff=0,rtscts=0)


#Send command via serial
def send(str):
	ret=""
	serial.write(str)
	for i in range(100):
		time.sleep(0.02)
		if serial.inWaiting()==0:
			break
		ret+= serial.read(serial.inWaiting())
	return ret

def send_cmd(str):
	recv_data = send("\r\nat@xsh=\"%s\"\r\n" % str)
	recv_data = recv_data.replace("\r\n\r\n", "")	
	return recv_data

#return single bit from string
def getbit(buf,bitnum):
	bitpos = bitnum % 8
	bytepos=math.floor(bitnum/8)
	byte = buf[int(bytepos)]
	if (ord(byte) & (1<<bitpos)) != 0:
		return True
	else:	return False

def getbits(buf,start,end):
	end+=1
	val=0
	cnt=0
	str=""
	for i in range(start,end):
		if getbit(buf,i):
			val+=1<<cnt
		if (cnt!=0):
			if (cnt % 7)==0:
				str+=chr(val)
				val=0
				cnt=-1
		cnt+=1
	if cnt!=0:
		str+=chr(val)
	return str

# read blackfin memory address. Size is in multiples of 0x10 (0x10 is the minimum). 
# Optionally prints an hex dump
def readMemory(addr,size,doprint=False):
	data=""
	recv_data = send_cmd("echo %08X" % addr)
	recv_data=recv_data.split()	
	#print recv_data
	for i in range(size/0x10):
		str=recv_data[i*0x11]
		for c in range(0x10):
			str+=" %s" % recv_data[i*0x11+c+1]
		str+="|"
		for c in range(0x10):
			echar = int(recv_data[i*0x11+c+1],16);
			data+="%c" % echar
			if (echar<32) or (echar>128): echar=ord('.')
			str+="%c" % echar
		if doprint==True: print str
	return data

##Main
oldpackets=0
inputs=[""]*17
outputs=[""]*17
while(True):
	try:
		data = readMemory(0x20ff0000,0x10)
		num=struct.unpack("<H",data[0:2])[0]
		data=""
		if (num<2000): # sanity check
			if (num!=oldpackets):
				for p in range(oldpackets,num):
					oldpackets=num
					buf = readMemory(0x20ff1000+p*0x20-0x20,0x20)
					##DEBUG: write output
					a=open("output.bin","ab")
					a.write(buf)
					a.close()
					#------
					os.system("clear")
					print bcolors.COLOR2+("------------Packet %d (total %d)---------" % (p,num-1))+bcolors.ENDC
					# print packet info
					(data,fill) = decodepackets.parseGMR(buf)
					if data != False:
						# parse channels
						chanAddress=ord(buf[0])
						if chanAddress<0x10:
							if buf[0x1f]=='O':
								if (ord(buf[1])==0):
									inputs[chanAddress]=""
								inputs[chanAddress]+=data
							else:	
								if (ord(buf[1])==0):
									outputs[chanAddress]=""
								outputs[chanAddress]+=data
					# print input channels
					print bcolors.WARNING+"------- INPUT CHANNELS"+bcolors.ENDC
					for i in range(16):
						if (len(inputs[i])>0):
							print ("%d:" % i )+bcolors.OKGREEN+decodepackets.parseGMROut(inputs[i])+bcolors.ENDC
					# print output channels
					print bcolors.OKBLUE+"------- OUTPUT CHANNELS"+bcolors.ENDC
					for i in range(16):
						if (len(outputs[i])>0):
							print ("%d:" % i )+bcolors.OKGREEN+decodepackets.parseGMROut(outputs[i])+bcolors.ENDC
				oldpackets=num
				time.sleep(0.05)
	except: pass

