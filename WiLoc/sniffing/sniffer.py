from multiprocessing import Manager, Process
import multiprocessing
import Queue as q
import time
import sys
import signal
import os
import logging

from wifi_config import setup_monitors,stop_monitor_all
from csv_output import make_csv
from WiLoc.communication import api

def handle_single_queue_elem(queue):
	try:
		elem = queue.get(False)
		api.new_recording(elem['monitor'],elem['transmitter'],elem['strength'])
		return True
	except q.Empty:
		return False

def handle_all_queue_elems(queue):
	is_more = handle_single_queue_elem(queue)
	while is_more:
		is_more = handle_single_queue_elem(queue)


def start_sniffing(endpoint, mode=None, context=None):
	proc_list = []

	data_queue = multiprocessing.Queue()

	mons = setup_monitors()

	if len(mons)<1:
		logging.info('No monitor cards found. Exiting.')
		sys.exit(0)

	logging.info('Monitors are: %s'%mons)


	method = (mode or raw_input('Which method would you like to use to sniff ([d]umpcap,[s]capy): '))

	if method.startswith('d'):
		from dumpcap_sniffer import sniff_me
	elif method.startswith('s'):
		from scapy_sniffer import sniff_me
	else:
		raise Exception('Sniffing method must start with either \'d\' or \'s\'')

	for monitor in mons:
		logging.info('Starting sniffing on [%s]'%monitor['mon'])

		proc = Process(target=sniff_me,args=(monitor,data_queue))
		proc.start()
		proc_list.append(proc)

	def ctrl_c_handler(signal,frame):
		try:
			logging.info('Stopping sniff. Approximate queue size: '+str(data_queue.qsize()))

			handle_all_queue_elems(data_queue)

			for monitor in mons:
				logging.info('Stopping sniffing on '+monitor['mon']+'. Yum.')

			logging.info('Forcing %i cards to stop sniffing.'%len(proc_list))

			for proc in proc_list:
				proc.terminate()

			logging.info('Complete. Closing down monitor mode.')
			stop_monitor_all()

			sys.exit(0)
		except KeyboardInterrupt:
			logging.warning('Ok ok, quitting')
			sys.exit(0)

	def loop_forever():
		while True:
			handle_single_queue_elem(data_queue)
			time.sleep(0.001)

	signal.signal(signal.SIGINT,ctrl_c_handler)
	if context:
		logging.info("Daemonizing. Bye bye!")
		with context:
			loop_forever()
	else:
		loop_forever()