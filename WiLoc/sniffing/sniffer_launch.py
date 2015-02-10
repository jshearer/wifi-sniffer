import os
import daemon
import lockfile
import argparse
import logging

from sniffer import start_sniffing
from WiLoc import add_log_path

if __name__=='__main__':
	if os.geteuid()==0:
		parser = argparse.ArgumentParser(description='Launch the sniffer! Mmmmmm')
		parser.add_argument('--mode', choices=['dumpcap','scapy'], default='dumpcap')
		parser.add_argument('--endpoint', required=True)
		parser.add_argument('--pidfile', required=True)
		parser.add_argument('--daemon', action='store_true', default=False, dest="daemon")
		parser.add_argument('--stdout')
		parser.add_argument('--stderr')
		parser.add_argument('--logfile')
		parsed_args = parser.parse_args()

		"""
		Perform the daemonization. Customize the stdout, stderr files for nice debugging

		Set up more signal handlers in self.context.signal_map so that when different signals come in, different things happen.
		"""

		if(parsed_args.logfile):
			add_log_path(parsed_args.logfile)

		stdout = None
		stderr = None
		if parsed_args.stdout:
			stdout = open(parsed_args.stdout,"w+")
		if parsed_args.stderr:
			stderr = open(parsed_args.stderr,"w+")
		context = daemon.DaemonContext(pidfile=lockfile.FileLock(parsed_args.pidfile),
											stdout=stdout,
											stderr=stderr)
		context.signal_map = {
		
		}

		start_sniffing(mode=parsed_args.mode, endpoint=parsed_args.endpoint, context=(context if parsed_args.daemon else None))
	else:
		logging.error('You must be root.')