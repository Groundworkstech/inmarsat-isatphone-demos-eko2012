######
###### Decode GMRv2 Layer 3 frames
###### 
#
# Property of Groundworks Technologies
#
#

import sys,math

# Color class
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

## Print hexadecimal buffer
def printHex(buf):
	str=""
	for c in buf:
		str+=" %02X" % ord(c)
	str+="|"
	for c in buf:
		echar=ord(c)
		if (echar<32) or (echar>128): echar=ord('.')
		str+="%c" % echar
	return str


## Return single bit from string
def getbit(buf,bitnum):
	bitpos = bitnum % 8
	bytepos=math.floor(bitnum/8)
	byte = buf[int(bytepos)]
	if (ord(byte) & (1<<bitpos)) != 0:
		return True
	else:	return False

## Return arbitrary bits from string
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


## Print packet data
## See GMR-2 04.006 (ETSI TS 101 377-4-5 V1.1.1)
def parseGMR(buf):
	# Direction
	if buf[0x1f]=='O':
		direction="SAT-to-MES"
	else:	direction="MES-to-SAT"
	print "Direction: %s" % direction
	#----- ADDRESS FIELD
	# Address Field extension bit
	EA = ord(getbits(buf[0],0,0))
	if (EA==1): EAstr="Final octet"
	else:	EAstr="extension"

	# Command/Response (Assume Received packet)
	CR = ord(getbits(buf[0],1,1))
	if (CR==1): CRstr="Command"
	else:	CRstr="Response"

	# Service Access Point Identifier (SAPI)
	SAPI=ord(getbits(buf[0],2,4))
	SAPIstr="Reserved"
	if (SAPI==1): SAPIstr="Call control signaling"
	if (SAPI==3): SAPIstr="Short message service"
	
	LPD =ord(getbits(buf[0],5,6))
	SPAR=ord(getbits(buf[0],7,7))

	print "Address Field: EA=%d (%s) CR=%d (%s) SAPI=%d (%s) LPD=%d SPAR=%d" % (EA,EAstr,CR,CRstr,SAPI,SAPIstr,LPD,SPAR)

	#----- CONTROL FIELD
	CF1 = ord(getbits(buf[1],0,0))
	FFormat="I"
	if CF1==1:
		CF1=ord(getbits(buf[1],0,1))
		if CF1==3:
			FFormat="U"
		else:	FFormat="S"
	PF=ord(getbits(buf[1],4,4))
	NS=0
	NR=0
	if FFormat=="I":
		NS=ord(getbits(buf[1],1,3))
		NR=ord(getbits(buf[1],5,7))
	if FFormat=="S":
		SS=ord(getbits(buf[1],2,3))
		NR=ord(getbits(buf[1],5,7))
		CMD=""
		if SS==0: CMD="Receive Ready"
		if SS==1: CMD="Receive not Ready"
		if SS==2: CMD="Reject"
	if FFormat=="U":
		UU=ord(getbits(buf[1],2,3))
		UUU=ord(getbits(buf[1],5,7))

	if FFormat=="S": cmdStr= " Command: %s" % CMD
	else:	cmdStr=""

	print "Control Field %02x: Format=%s (%d) NS=%d PF=%d NR=%d %s" % (ord(buf[1]),FFormat,CF1,NS,PF,NR,cmdStr)

	#----- LENGTH INDICATOR FIELD

	# Address Field extension bit
	EL = ord(getbits(buf[2],0,0))
	if (EL==1): ELstr="Final octet"
	else:	ELstr="extension"

	M = ord(getbits(buf[2],1,1))
	Mstr=""
	if M==1: Mstr="segmented L3"
	
	LI = ord(getbits(buf[2],2,7))
	if LI==0:LIstr="No Information field"
	else: LIstr=""
		
	print "Len. Indicator Field %02x: EL=%d (%s) M=%d (%s) Lenght=%d octets (%s)" % (ord(buf[2]),EL,ELstr,M,Mstr,LI,LIstr)
	if FFormat=="I":
		if LI>0:
			datastr = buf[3:3+LI]
			fillstr = buf[3+LI:23]
			# for printing to screen
			dataprint=datastr[:10]
			fillprint=fillstr[:10]
			print " Data: "+bcolors.FAIL+ printHex(dataprint) + bcolors.ENDC
			print " Fill: "+bcolors.FAIL+ printHex(fillprint) + bcolors.ENDC
			return (datastr,fillstr)
	print " Data: None"
	print " Fill: None"
	return (False,False)

## Return 7-bit decoded packet data 
## See GMR-2 04.006 (ETSI TS 101 377-4-5 V1.1.1)
def parseGMROut(buf):
	start=buf.find("\x98\xF8") # alignment hax! horrible, just for demo.
	if (start>-1):
		buf=buf[start+6:]
		r1=0
		r2=1
	else:	
		r1=4
		r2=5
	str=""
	for q in range(r1,r2):
		bin=""
		for i in range(0,len(buf)*8-14,7):
			c = getbits(buf,q+i,q+i+6)
			bin+=c
			if (ord(c)>=32) and (ord(c)<=126):
				str+=c	
			else:	str+="."
	return str

			

###### MAIN
def main():
	if len(sys.argv)<3:
		print "Usage: %s <file> [channel]" % (sys.argv[0])

	infile=open(sys.argv[1])

	recordlen=0x20
	if len(sys.argv)>2:
		channel=int(sys.argv[2])
	else:	channel=0x0d

	#buf=infile.read(recordlen-1)
	msg=""
	buf=infile.read(recordlen-1)
	while(True):
		packetDir=infile.read(1)
		buf=infile.read(recordlen-1)
		if len(buf)<(recordlen-1):
			break
		#print "------------------------------------------------------"
		#print packetDir
		if packetDir=='O':
			if ord(buf[0])==channel:
					(data,fill)=parseGMR(buf+packetDir)
					if (data!=False):
						msg+=data

	#print printHex(msg)
	print "hex: %s" % printHex(msg)
	print "decoded: %s" % parseGMROut(msg)

if __name__ == "__main__":
    main()

