from scapy.all import *
#This is a higher order function
#It's purpose is to allow the packet handle to have other arguments.
#Speciically, it's used becuase scapy's sniff function doesn't let you pass arguments to the handler
#PacketHandler returns a function that knows about monitor and queue.
#That function is called with a packet as an argument.

def PacketHandler(monitor,queue):

	def handle(pkt):
		if pkt.haslayer(UDP) and pkt.load=='Hello world!' and pkt.addr3.startswith('ff'):
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

	return handle