from scapy.all import *
from subprocess import Popen, PIPE
from multiprocessing import Manager, Process
import multiprocessing
from wifi_config import setup_real_card,setup_monitors,stop_monitor_all
from csv_output import make_csv
from config import r
import time
import sys
import signal
import os
import Queue as q

class STDInRawPcapReader(RawPcapReader):
	def __init__(self,input_file):
		self.f = input_file
		self.f.read(8) #8 junk bytes
		magic_bytes = self.f.read(4)
		magic = ""
		for ch in magic_bytes:
			magic += hex(ord(ch))

		if magic == "x1a0x2b0x3c0x4d": #big endian
			self.endian = ">"
		elif  magic == "0x4d0x3c0x2b0x1a": #little endian
			self.endian = "<"
		else:
			raise Scapy_Exception("Not a pcap capture file (bad magic)")
		hdr = self.f.read(20)
		if len(hdr)<20:
			raise Scapy_Exception("Invalid pcap file (too short)")
		vermaj,vermin,tz,sig,snaplen,linktype = struct.unpack(self.endian+"HHIIII",hdr)

		self.linktype = linktype

class STDInPcapReader(STDInRawPcapReader):
	def __init__(self, input_file):
		STDInRawPcapReader.__init__(self, input_file)
		try:
			self.LLcls = conf.l2types[self.linktype]
		except KeyError:
			warning("PcapReader: unknown LL type [%i]/[%#x]. Using Raw packets" % (self.linktype,self.linktype))
			self.LLcls = conf.raw_layer
	def read_packet(self, size=MTU):
		print "Reading packet"
		rp = STDInRawPcapReader.read_packet(self,size)
		print rp
		if rp is None:
			return None
		s,(sec,usec,wirelen) = rp
		
		try:
			p = self.LLcls(s)
		except KeyboardInterrupt:
			raise
		except:
			if conf.debug_dissector:
				raise
			p = conf.raw_layer(s)
		p.time = sec+0.000001*usec
		return p
	def read_all(self,count=-1):
		res = STDInRawPcapReader.read_all(self, count)
		import plist
		return plist.PacketList(res,name = os.path.basename(self.filename))
	def recv(self, size=MTU):
		return self.read_packet(size)

def sniff_me(monitor, queue):
	def PacketHandler(pkt):
		print "Got packet"
		if pkt.haslayer(UDP) and pkt.load=='Hello world!' and pkt.addr3.startswith('ff'):
			try:
				extra = pkt.notdecoded
			except:
				extra = None
			if extra!=None:
				signal_strength = -(256-ord(extra[-4:-3]))
			else:
				signal_strength = -255
				print 'No signal strength found'

			#It might be addr1?
			dat = {'monitor':monitor['mac'],'transmitter':pkt.addr2,'strength':signal_strength,'data':pkt.load,'time':time.time()}
			queue.put(dat)

	tshark_proc = Popen(['dumpcap', '-i'+monitor['mon'], '-f', 'udp port 9001', '-P', '-w', '-'], stdout=PIPE)
	time.sleep(1)
	reader = STDInPcapReader(tshark_proc.stdout)

	pkt = reader.read_packet()

	while True:
		if pkt != None:
			PacketHandler(packet)
		pkt = reader.read_packet()
		time.sleep(0.001)

def handle_single_queue_elem(queue):
	try:
		elem = queue.get(False)
		r.publish('sniff', elem)
		print "Remaining: "+str(queue.qsize())
		return True
	except q.Empty:
		return False

def handle_all_queue_elems(queue):
	is_more = handle_single_queue_elem(queue)
	while is_more:
		is_more = handle_single_queue_elem(queue)


def start_sniffing():
	proc_list = []

	data_queue = multiprocessing.Queue()

	mons = setup_monitors()

	if len(mons)<1:
		print 'No monitor cards found. Exiting.'
		sys.exit(0)

	print 'Monitors are: %s'%mons

	for monitor in mons:
		print 'Starting sniffing on [%s]'%monitor['mon']

		r.publish('sniff_info', "Starting to sniff on "+monitor['mon']+", smells good!")

		proc = Process(target=sniff_me,args=(monitor,data_queue))
		proc.start()
		proc_list.append(proc)

	def ctrl_c_handler(signal,frame):
		try:
			print 'Stopping sniff. Approximate queue size: '+str(data_queue.qsize())

			handle_all_queue_elems(data_queue)

			for monitor in mons:
				r.publish('sniff_info', 'Stopping sniffing on '+monitor['mon']+'. Yum.')

			print 'Forcing %i cards to stop sniffing.'%len(proc_list)

			for proc in proc_list:
				proc.terminate()

			print 'Complete. Closing down monitor mode.'
			stop_monitor_all()

			sys.exit(0)
		except KeyboardInterrupt:
			print 'Ok ok, quitting'
			sys.exit(0)

	signal.signal(signal.SIGINT,ctrl_c_handler)

	while True:
		handle_single_queue_elem(data_queue)
		time.sleep(0.001)

if __name__=='__main__':
	if os.geteuid()==0:
		start_sniffing()
	else:
		raise Exception('You must be root.')