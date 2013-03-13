@ Shellcode that prints $PC
@ Usage:
@   python isat_hax.py ./ISATHello.bin

.thumb

.ascii "STRT"  @ START MARK

@+1 because blx+1 is a jump to Thumb code
.equ 	HANDLE,0x214784e8 @PRINTF function inside firmware
.equ 	PUTS,0x04E8C7E5 @PRINTF function inside firmware
.equ 	STRING,0x04c8bf44
.equ 	ADDR  ,0x04EF6800
	push {R1-R7,LR}
	ldr r0,=HANDLE
	add R0,#0xFF
	add R0,#0x65
	mov r2,#10
	ldr r1,=STRING
	ldr r7,=PUTS
	adr R1,debugstr
	blx r7
	ldr r0,=0x81200002
	pop {R1-R7,PC}

.align 4
debugstr:
	.asciz "HOLA MUNDO\n"
