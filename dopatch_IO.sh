#!/bin/sh
#
# Property of Groundworks Technologies
#
# Firmware modifications of IsatPhone Pro V 4.0.0 to dump In/Out packets


# Install ARM patcher
./isat_hax_echo_arm.py ./isat_blackfin_patcher_secure.bin

##### Write patches
./isat_hax_echo_bf.py ./bfpatch/0000.bin 0x20FF0000 # zero counter
# place packet copier and hook
./isat_hook_bf_call.py ./bfpatch/copyI.bin 0x20180000 0x206b817A
./isat_hook_bf_call.py ./bfpatch/copyO.bin 0x20180100 0x206b8130
# Install echo-peek command
./isat_hax.py ISATPeek-nice.bin
