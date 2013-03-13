# This function is designed to be embedded inside the call_DECODE_PACKET function to show a decoded packet

.section .rodata
 
 
.text
.align 4
 
.global _main;
.type _main, STT_FUNC;

.equ    puts,0x2059d58c # void puts(short handle, char *str) function inside firmware
.equ    str1,0x2011c72c # "%02x ",0x00

.ascii "STRT" ;

_main:
	#jump.s _main;
	SSYNC;
	/* Blackfin requires at least 12 bytes when calling functions */
	LINK 0x0c
	[--SP] = ASTAT;
	[--SP] = RETS;
	[--SP] = (R7:0);
	[--SP] = (P5:0);

	R7=0;

	// Dump position
	R0=[P5]
	#R0.L=0x0000
	#R0.H=0x2000 
	[SP-0x0C]=R0

	R5=0x3;
loop2:
	R5+=-1;
	[SP-0x04]=R5;

	R6=0x10;
loop1:
	R6+=-1;
	[SP-0x08]=R6;
	
	// Printf

	R0=SP
	R1=-0x10
	R0=R0+R1 // r0=stack buffer

	R1.L=0xc72c
	R1.H=0x2011 // "%02x "
	
	P0=[SP-0x0c]
	R2=B[P0++](Z);
	[SP-0x0c]=P0

	P1.L=0x8720
	P1.H=0x2071 # sprintf
	SP+=-0x30
	call (P1)
	SP+=0x30

	// puts

	P1.L=0xd58c
	P1.H=0x2059 # puts


	R0=SP
	R1=-0x10
	R1=R0+R1 // buffer

	R0=R7; //stdout?
	SP+=-0x30
	call (P1)
	SP+=0x30


	R6=[SP-0x08];
	CC= R6 == 0 ;
	if !CC JUMP loop1;


	// puts

	P1.L=0xd58c
	P1.H=0x2059 # puts


	R1.L=0xB57C
	R1.H=0x2013 # CRLF

	R0=R7; //stdout?
	SP+=-0x30
	//call (P1)
	SP+=0x30


	R5=[SP-0x04];
	CC= R5 == 0 ;
	if !CC JUMP loop2;


	(P5:0) = [SP++]; // Restore registers from Stack
	(R7:0) = [SP++];
	RETS = [SP++];
	ASTAT = [SP++];
	UNLINK
	SSYNC;
	RTS;
.align 4
pad_string: .string   "AAAA"
end_string: .string   "THEEND"
.size _main,.-_main;
