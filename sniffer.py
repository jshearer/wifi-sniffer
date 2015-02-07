from multiprocessing import Manager, Process
import multiprocessing
import Queue as q
import time
import sys
import signal
import os

from wifi_config import setup_real_card,setup_monitors,stop_monitor_all
from csv_output import make_csv
from config import r

def handle_single_queue_elem(queue):
	try:
		elem = queue.get(False)
		r.publish('sniff', elem)
		#print "Remaining: "+str(queue.qsize())
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

	method = raw_input('Which method would you like to use to sniff ([d]umpcap,[s]capy): ')

	if method.startswith('d'):
		from dumpcap_sniffer import sniff_me
	elif method.startswith('s'):
		from scapy_sniffer import sniff_me
	else:
		raise Exception('Sniffing method must start with either \'d\' or \'s\'')

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