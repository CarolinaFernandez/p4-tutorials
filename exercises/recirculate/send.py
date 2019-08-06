#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from customdata_header import CustomData

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to use")
    parser.add_argument('message', type=str, help="The message to include in packet")
    parser.add_argument('--custom', action="store_true", default=False, help="Flag indicating whether to use CustomData (defaults to false). If only this flag is provided, custom_id is set to 101 by default")
    parser.add_argument('--custom_id', type=int, default=None, help="The ID of the custom content")
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    custom_data = args.custom
    custom_id = args.custom_id
    iface = get_if()

    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    print "sending on interface {} to IP addr {}".format(iface, str(addr))
    if (custom_data is True or custom_id is not None):
        if (custom_id is None):
            custom_id = 101
        pkt = pkt / CustomData(content_id=custom_id, ingress_num=0, egress_num=0)
        pkt = pkt / IP(dst=addr) / args.message
    else:
        pkt = pkt / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / args.message

    pkt.show2()
#    hexdump(pkt)
#    print "len(pkt) = ", len(pkt)
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
