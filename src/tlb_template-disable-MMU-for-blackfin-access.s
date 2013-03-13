#
#
# Property of Groundworks Technologies
#
#

    .text 
    .arm
    .global _start

.ascii "STRT"  @ START MARK
_start:
/* save LR */
    push {R1-R7,LR}

 #
 #/* **************************** */
 #/* MMU disable */
    MRC p15, 0, R3,c1,c0
    BIC R3, #0xFF
    MCR p15, 0, R3,c1,c0
    NOP
    NOP
    NOP
    NOP
 

/* PATCHES here: */
/* **************************** */
    ldr r0, =0x2013b560 #at$skver
    ldr r1, =0x43434343
    str r1, [r0]

 #/* MMU enable */
    MRC p15, 0, R4,c1,c0
    BIC R4, #0xFF
    ORR R4, #7
    MCR p15, 0, R4,c1,c0
 
done:

    MOV R0, #0
    pop {r1-r7,LR}
    BLX LR
