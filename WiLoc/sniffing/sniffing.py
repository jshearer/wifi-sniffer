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
		except:
			extra = None
		if extra!=None:
			signal_strength = -(256-ord(extra[-4:-3]))
		else:
			signal_strength = -255
			logging.warning('No signal strength found')

		#It might be addr1?
		dat = {'monitor':monitor['mac'],'transmitter':pkt.addr2,'strength':signal_strength,'data':pkt.load,'time':time.time()}
		queue.put(dat)

		logging.debug("1,2,3: (%s,%s,%s)"%(pkt.addr1,pkt.addr2,pkt.addr3))


	return handle