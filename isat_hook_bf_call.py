#!/usr/bin/python
#
# Property of Groundworks Technologies
#
#
# Uses the command inside isat_blackfin_patcher to upload a blackfin binary
# to the provided pointer
# Additionally, this function insert a call to the binary into a second address provided
# usage:
# after uploading the isat_blackfin_patcher ("isat_hax_echo_arm isat_blackfin_patcher.bin")
# ./isat_hax_echo_bf.py <blackfin binary> [pointer] [pointer to insert relative call]
# by default [pointer] overwrites the at$skver command at firmware 4.0.0


import sys,struct

from serial import *
import time

PATCHADDRESS=0x2059e098 # at$skver command
# serial object
# please adjust to device properties
serial = Serial(port="/dev/ttyACM0",baudrate=115200,bytesize=EIGHTBITS,parity=PARITY_NONE,stopbits=STOPBITS_ONE,timeout=None,xonxoff=0,rtscts=0)


#Load hook function
def loadhook(filename):
	buf=open(filename,"rb").read()
	start=buf.find("STRT")
	end=buf.find("THEEND")
	if start==-1:
		return buf
	return buf[start+4:end]


#Send command via serial
def send(str):
	ret=""
	serial.write(str)
	for i in range(100):
		time.sleep(0.03)
		if serial.inWaiting()==0:
			break
		ret+= serial.read(serial.inWaiting())
	return ret

def send_cmd(str):
	recv_data = send("\r\nat@xsh=\"%s\"\r\n" % str)
	recv_data = recv_data.replace("\r\n\r\n", "")	
	return recv_data

##Main

if (len(sys.argv))<3:
	print "Usage: %s <shellcode> [Position] [callpointer]" % sys.argv[0]
	exit(0)

#Load hook and arguments
print "Loading hook..."
hook=loadhook(sys.argv[1])
print "Loaded %d bytes" % len(hook)

PATCHADDRESS=int(sys.argv[2],16)
print "Address to patch: 0x%08X" % PATCHADDRESS

##Connect to phone and check version
serial.open()
recv_data = send_cmd("version")
verpos = recv_data.find("Ver:")
if (verpos<0):
	print "Error connecting to phone"
	serial.close()
	exit(0)
fwversion = recv_data[verpos+5:verpos+10]
print "Connection OK. Firmware version: %s" % fwversion

## Allocate Memory
print "Allocating memory..."
recv_data = send_cmd("xmm malloc %d" % (len(hook)+100))
sizestrt = recv_data.find("Allocation of")
sizeend = recv_data.find("bytes")
addrstrt = recv_data.find("pointer ")
addrend = recv_data.find("OK")
try:
	sizealloc=int(recv_data[sizestrt+14:sizeend])
	pointer = int(recv_data[addrstrt+8:addrend],16)
except:
	sizealloc = 0
	pass

if (sizealloc!=len(hook)+100):
	print "Error allocating: asked %d, got %d" % (len(hook)+100,sizealloc)
	serial.close()
	exit(0)
print "Successfully allocated %d bytes of memory at 0x%X" % ((len(hook)+100),pointer)

#write patch info in memory
print "Writing shellcode into allocated chunk:"
send_cmd("poke 32 0x%08X 0x%08X" % (pointer,PATCHADDRESS))
send_cmd("poke 32 0x%08X 0x%08X" % (pointer+4,len(hook)))
hook+="AAAA" # padding
#write hook shellcode in memory
for i in range(0,len(hook)-4,4):
	recv_data= send_cmd("poke 32 0x%08X 0x%08X" % (pointer+i+8,ord(hook[i])+256*ord(hook[i+1])+256*256*ord(hook[i+2])+256*256*256*ord(hook[i+3]) ))
	recv_data = recv_data.replace("\nOK\r\n", "")	
	recv_data = recv_data.replace("\n", "")	
	recv_data = recv_data.replace("\r", "")	
	print "%s" % recv_data

print "Aplying patch..."
patchoutput = send_cmd("echo 0x%08X" % (pointer))
print patchoutput

print "Calculating call code..."
callpointer=int(sys.argv[3],16)
print "Instruction: 0x%08X: CALL 0x%08X" % (callpointer,PATCHADDRESS)
num = (PATCHADDRESS-callpointer)/2
if (num<0): num=0x100000000+num
print "%x" % num
callinstr=struct.pack("BBBB",(num>>16)&0xFF,0xE3,num&0xFF,(num>>8)&0xFF)
callcode=struct.unpack("<L",callinstr)[0]
print "Instruction bytes: 0x%08X" % callcode
print "Writing call code into allocated chunk:"
send_cmd("poke 32 0x%08X 0x%08X" % (pointer,callpointer))
send_cmd("poke 32 0x%08X 0x%08X" % (pointer+4,4))
send_cmd("poke 32 0x%08X 0x%08X" % (pointer+8,callcode))
print "Aplying patch..."
patchoutput = send_cmd("echo 0x%08X" % (pointer))
print patchoutput

serial.close()

