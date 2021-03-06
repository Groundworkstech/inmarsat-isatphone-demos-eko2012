# This function is designed to be called from inside the EncodeECC function to copy a packet about to be sent
# can be placed anywhere. Ex.:
#./isat_hook_bf_call.py ./blackfin_sdk/copyI.bin 0x20180000 0x206b817A

.section .rodata
 
 
.text
.align 4
.global _main;
.type _main, STT_FUNC;

.equ    PACKETLEN,0x20 # 184 bits frame
.equ    MAXPACKETS,0x400
.ascii "STRT" ;

_main:
	/* Blackfin requires at least 12 bytes when calling functions */
	LINK 0x0c
	# Save registers
	[--SP] = RETS;
	[--SP] = ASTAT;
	[--SP] = (R7:0);
	[--SP] = (P5:0);
	[--SP] = I0;
	[--SP] = M0;
	CLI R6

	P5=[P0] # R0=SRC stream

	P0.L=0x0000 # Packet counter position
	P0.H=0x20ff # 0x20ff0000

	R1=MAXPACKETS # Max packets allowed on buffer

	R0=W[P0](Z)
	R0+=1
	CC = R0 < R1
	if CC JUMP noover
	# overflow
	R0=0
noover:
	W[P0]=R0; # Write new buffer pointer
	P0+=4
	[P0]=R7  # Write source pointer

	# Copy Packet to buffer
	R1.L=0x1000 # Packet destination buffer position
	R1.H=0x20ff # 0x20ff1000
	I0=R1 #R1=dst pointer

	# Packet dst calculation
	R1=PACKETLEN
	R0+=-1
	R0*=R1
	M0=R0
	I0+=M0
	P1=I0


	# Check SRC pointer for invalid pointer
	P0=P5 #P0=src pointer
	P2.L=0x1000
	P2.H=0x0000 # 0x208A1100
	CC=P0<P2
	if CC JUMP end


	# copy loop
	R1=PACKETLEN-1 #R1=count
loop3:
	R0=B[P0++] (Z)
	B[P1++]=R0
	R1+=-1
	CC=R1==0
	if !CC JUMP loop3

	# Write I/O marker (We are I)
	R0=0x49 # 'I'
	B[P1++]=R0

	# Check for packet modification request
	P0=P5 #P0=src pointer

	P2.L=0x9000 # packet modification request location:
	P2.H=0x20ff # 0x20ff9000

	R1=3 # comparation bytes (first R1 bytes)
	R3=0 # diff counter
loopComp:
	R0 = B[P0++] (Z)
	R2 = B[P2++] (Z)
	R4 = R2 - R0
	R3 = R3 + R4
	R1 += -1
	CC = R1 == 0
	if !CC JUMP loopComp

	CC = R3 == 0
	if !CC JUMP end

	# header matches, modify
	R1 = 12 # copy bytes (MCD (7,8) == 56 bits)
loopModif:
	R0 = B[P2++] (Z)
	B[P0++]=R0
	R1 += -1
	CC = R1 == 0
	if !CC JUMP loopModif


end:
	# restore registers
	STI R6
	M0 = [SP++];
	I0 = [SP++];
	(P5:0) = [SP++]; // Restore registers from Stack
	(R7:0) = [SP++];
	ASTAT = [SP++];
	RETS = [SP++];
	UNLINK

	# stolen instr
	R2 = P5;
	R1 = P0;
	RTS;
.align 4
pad_string: .string   "AAAA"
end_string: .string   "THEEND"
.size _main,.-_main;
