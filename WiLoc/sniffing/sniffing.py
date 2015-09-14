from scapy.all import *
import logging
#This is a higher order function
#It's purpose is to allow the packet handle to have other arguments.
#Speciically, it's used becuase scapy's sniff function doesn't let you pass arguments to the handler
#PacketHandler returns a function that knows about monitor and queue.
#That function is called with a packet as an argument.

def PacketHandler(monitor,queue):

	def handle(pkt):
		try:
			extra = pkt.notdecoded
			signal_strength = -(256-ord(extra[-4:-3]))
		except:
			signal_strength = -255
			logging.warning('No signal strength found')
		
		try:
			if pkt.addr2 and pkt.addr2.lower()=="c0:ee:fb:25:4d:c1":
				dat = {'monitor':monitor['mac'],'transmitter':pkt.addr2,'strength':signal_strength,'time':time.time()}
				queue.put(dat)
		except AttributeError as e:
			logging.warning("Bad packet. AttributeError: "+str(e))


	return handle