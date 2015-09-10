import logging
from logging import handlers
import os
import traceback
import graypy
import socket

# from config import graylog_address, graylog_port

import communication.api as api

log_format = logging.Formatter("[%(asctime)s] {%(levelname)s} (%(name)s) %(message)s")

sh = logging.StreamHandler()
sh.setFormatter(log_format)

logging.getLogger().addHandler(sh)
logging.getLogger().setLevel(logging.INFO)

# logging.info('WiLoc initializing. GrayLog: (%s,%s)'%(graylog_address,graylog_port))

# graypy_handler = graypy.GELFHandler(graylog_address, graylog_port)
# logging.getLogger().addHandler(graypy_handler)

if('sniffer_logpath' in os.environ):
	add_log_path(os.environ['sniffer_logpath'])

#STfU REQUESTS
logging.getLogger("requests").setLevel(logging.WARNING)

def add_log_path(path):
	logfile = ''

	if '.' in path:
		logfile = path
	else:
		logfile = os.path.join(path,'sniffer.log')

	fh = handlers.RotatingFileHandler(logfile, maxBytes=(1048576*5), backupCount=7)
	fh.setFormatter(sh)
	logging.getLogger().addHandler(fh)

device_id = ''
id_file = None
if(os.path.isfile('/etc/machine-id')):
	id_file = '/etc/machine-id'
elif(os.path.isfile('/var/lib/dbus/machine-id')):
	id_file = '/var/lib/dbus/machine-id'

if id_file:
	with open(id_file,'r') as f:
		device_id = f.read().replace("\n","")

import sys
def log_uncaught_exceptions(ex_cls, ex, tb):

	logging.critical(''.join(traceback.format_tb(tb)))
	logging.critical('{0}: {1}'.format(ex_cls, ex))
	sys.exit(0)

sys.excepthook = log_uncaught_exceptions