from scapy.all import sniff
from sniffing import PacketHandler

def sniff_me(monitor, queue):
	
	sniff(iface=monitor['mon'],prn=PacketHandler(monitor,queue))