# This function is designed to be called from inside the DECODEPACKET function to copy a received packet
# can be placed anywhere. Ex.:
#./isat_hook_bf_call.py ./blackfin_sdk/copyO.bin 0x20180000 0x206b8130
.section .rodata
 
 
.text
.align 4
 
.global _main;
.type _main, STT_FUNC;

.equ    PACKETLEN,0x20 # 120 bits frame
.ascii "STRT" ;

_main:
	/* Blackfin requires at least 12 bytes when calling functions */
	LINK 0x0c
	[--SP] = ASTAT;
	[--SP] = RETS;
	[--SP] = (R7:0);
	[--SP] = (P5:0);
	[--SP] = I0;
	[--SP] = M0;
	#CLI R6

	P5=[P5] # R0=SRC stream

	P0.L=0x0000
	P0.H=0x20ff # 0x20E00000

	R1=0x400 # Buffer pos Counter

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

	############# Copy Packet
	R1.L=0x1000
	R1.H=0x20ff # 0x20E01000
	I0=R1 #P1=dst pointer

	R1=PACKETLEN
	R0+=-1
	R0*=R1
	M0=R0
	I0+=M0
	P1=I0


	// Check SRC pointer
	P0=P5 #P0=src pointer
	P2.L=0x1000
	P2.H=0x0000 # 0x208A1100
	CC=P0<P2
	if CC JUMP end

	R1=PACKETLEN-1 #R1=count
loop3:
	R0=B[P0++] (Z)
	B[P1++]=R0
	R1+=-1
	CC=R1==0
	if !CC JUMP loop3
	// Write I/O marker (We are O)
	R0=0x4F # 'O'
	B[P1++]=R0



end:
	#STI R6
	M0 = [SP++];
	I0 = [SP++];
	(P5:0) = [SP++]; // Restore registers from Stack
	(R7:0) = [SP++];
	RETS = [SP++];
	ASTAT = [SP++];
	UNLINK
	RTS;
.align 4
pad_string: .string   "AAAA"
end_string: .string   "THEEND"
.size _main,.-_main;
