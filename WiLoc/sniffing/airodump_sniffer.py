from subprocess import Popen, PIPE, call

try:
	from subprocess import DEVNULL # py3k
except ImportError:
	import os
	DEVNULL = open(os.devnull, 'wb')

from scapy.all import *

from sniffing import PacketHandler
import logging

class STDInRawPcapReader(RawPcapReader):
	def __init__(self,input_file):
		self.f = input_file
		magic = self.f.read(4)
		if magic == "\xa1\xb2\xc3\xd4": #big endian
			self.endian = ">"
		elif  magic == "\xd4\xc3\xb2\xa1": #little endian
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
		rp = STDInRawPcapReader.read_packet(self,size)
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
	call(['rm', '-f', monitor['mon']+"-capture-01.cap"])
	airodump_proc = Popen(['airodump-ng', '--output-format', 'pcap', '-w', monitor['mon']+"-capture", monitor['mon']], stdout=DEVNULL, stderr=DEVNULL)
	time.sleep(1)
	with open(monitor['mon']+"-capture-01.cap", 'r') as capture_file:
		reader = STDInPcapReader(capture_file)

		pkt = reader.read_packet()

		while True:
			if pkt is not None:
				PacketHandler(monitor,queue)(pkt)
			pkt = reader.read_packet()