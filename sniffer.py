from multiprocessing import Manager, Process, Queue
import Queue as q
from wifi_config import setup_real_card,setup_monitors,stop_monitor_all
from csv_output import make_csv
import time
import sys
import signal
import os
from scapy.all import *

root_dir = '/home/joseph/sniffer/'

def sniff_me(monitor,queue):

	def PacketHandler(pkt):
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
	
	sniff(iface=monitor['mon'],prn=PacketHandler)

def start_sniffing():	
	sniff_queue = Queue()

	sniff_data_local = []

	proc_list = []

	mons = setup_monitors()

	if len(mons)<1:
		print 'No monitor cards found. Exiting.'
		sys.exit(0)

	print 'Monitors are: %s'%mons

	for monitor in mons:
		print 'Starting sniffing on [%s]'%monitor['mon']
		proc = Process(target=sniff_me,args=(monitor,sniff_queue))
		proc.start()
		proc_list.append(proc)

	def ctrl_c_handler(signal,frame):
		try:
			print 'Stopping sniff. Captured a total of %i data points.'%len(sniff_data_local)
			filename = raw_input("Filename (*.csv): ")

			print "Saving as: %s"%filename

			make_csv(['monitor','transmitter','time','strength'],sniff_data_local,filename)

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

	def wrap_sniff_queue():
		try:
			return sniff_queue.get(True,0.1)
		except q.Empty as e:
			pass
		return None

	while True:
		queue_next = wrap_sniff_queue()
		counter = 0
		while queue_next != None:
			sniff_data_local.append(queue_next)
			counter+=1
			queue_next = wrap_sniff_queue()

		print 'Got %i new samples. Total: %i'%(counter,len(sniff_data_local))

		time.sleep(1)

if __name__=='__main__':
	if os.geteuid()==0:
		start_sniffing()
	else:
		raise Exception('You must be root.')