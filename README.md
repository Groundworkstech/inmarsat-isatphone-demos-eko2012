inmarsat-isatphone-demos-eko2012
================================

This projects is about the analysis and modiﬁcation of the ﬁrmware of the Analog Devices AD6900 (LeMans) Baseband processor used in the Inmarsat IsatPhone Pro satellite terminal.

Techniques for code ex- ecution in both the CPU and the DSP are documented, the main result being the instrumentation of functions inside the blackﬁn DSP with the objective of control, monitoring and emission of Layer-1 GEO- Mobile Radio interface packets.


Content
-------

bfpatch : Directory containing blackfin binary patches
src : Directory containing sources
decodepackets.py : GMR-2 python parser
dopatch_custom_frame.sh : Serial patcher of IsatPhone Pro 4.0.0 firmware, inject custom frame
dopatch_IO.sh : Serial patcher of IsatPhone Pro 4.0.0 firmware, dump packets
dumpIO.py : Python script that decodes and show packets in real-time. Needs to execute dopatch_custom_frame.sh or dopath_IO.sh first.
isat_hax_echo_arm.py : Insert custom shellcode into ARM AT command "echo" (first stage)
isat_hax_echo_bf.py : Use AT command "echo" to insert a custom shellcode into blackfin code
isat_hax.py : Insert custom shellcode into ARM (thumb version)
isat_hook_bf_call.py : Upload a blackfin binary to the provided pointer. Additionally, this function insert a call to the binary into a second address provided.
