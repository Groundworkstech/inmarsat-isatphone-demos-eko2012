#
#
# Property of Groundworks Technologies
#
#
# Disables MMU and patch any memory area 
# (useful for blackfin patching)
# usage:
# after uploading to the at@xsh="echo" command, the usage is:
# echo 0xXXXXXXXX
# where 0xXXXXXXXX is a packet with the format: <pointer to write><size of data><data>


    .text 
    .arm
    .global _start

.equ 	get_input_param, 0x04e98500+1
.equ 	atoi, 0x04e9a3fc+1
.equ 	HANDLE,0x214784e8 @UART Handle (see processing of AT commands @ 0x004e3f6ec)
.equ 	PUTS,0x04E8C7E4+1 @PUTS(handle,char *str,int size) function inside firmware
.equ    SPRINTF,0x04EB0960+1 @int SPRINTF(char *buf,char *str,...) function inside firmware

.ascii "STRT"  @ START MARK
_start:
/* save LR */
    push {R1-R7,LR}

	mov r0,r0
	ldr r7,=get_input_param
	blx r7
	@now in r0 is the first param

	@convert param
	mov r0,r0 @ string
	mov r1,#0	@ ??
	mov r2,#0x10 @base
	ldr r7,=atoi
	blx r7

	mov r1,r0
	mov r6,r0 @r6 = patching block

	ldr r1,[r6] @ pointer 
	ldr r2,[r6,#4] @ size

 # MMU disable 
    MRC p15, 0, R0,c1,c0,0
    BIC R0, R0, #0x01
    MCR p15, 0, R0,c1,c0,0
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP

 # copy loop
    add r6, #8
    mov r5, #0
    loop1:
    ldrb r0,[r6,r5] @ read buf
    strb r0,[r1,r5] @ str buf
    add r5,#1
    sub r2,#1
    cmp r2,#0
    bne loop1
/* **************************** */
#    ldr r0, =0x2013b560 /* at$skver */
#    ldr r1, =0x43434343
#    str r1, [r0]

 # MMU enable 
    MRC p15, 0, R0,c1,c0,0
    ORR R0, R0, #0x1
    MCR p15, 0, R0,c1,c0,0
    NOP
    NOP
    NOP
    NOP
    NOP
    NOP
 
done:
    MOV R0, #0
    pop {r1-r7,LR}
    BLX LR
