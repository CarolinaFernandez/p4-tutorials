from scapy.all import *
import sys, os

TYPE_CUSTOMDATA = 0x1313
TYPE_IPV4 = 0x0800

class CustomData(Packet):
    name = "CustomData"
    fields_desc = [
        # 16 bits
        ShortField("proto_id", 0),
        ShortField("content_id", 101),
        # 8 bits
        ByteField("ingress_num", 0),
        ByteField("egress_num", 0),
    ]
    def mysummary(self):
        return self.sprintf("proto_id=%proto_id%, content_id=%content_id%, ingress_num=%ingress_num%, egress_num=%egress_num%")


bind_layers(Ether, CustomData, type=TYPE_CUSTOMDATA)
bind_layers(CustomData, IP, proto_id=TYPE_IPV4)
