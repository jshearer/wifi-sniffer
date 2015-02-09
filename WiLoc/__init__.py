import logging
from logging import handlers
import os
import sys
import traceback

log_format = logging.Formatter("[%(asctime)s] {%(levelname)s} (%(name)s) %(message)s")

sh = logging.StreamHandler()
sh.setFormatter(log_format)

logging.getLogger().addHandler(sh)
logging.getLogger().setLevel(logging.DEBUG)

if('sniffer_logpath' in os.environ):
	add_log_path(os.environ['sniffer_logpath'])

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
if(os.path.isfile('/etc/machine-id')):
	id_file = '/etc/machine-id'
elif(os.path.isfile('/var/lib/dbus/machine-id')):
	id_file = '/var/lib/dbus/machine-id'

if id_file:
	with open(id_file,'r') as f:
		device_id = f.read()

def log_uncaught_exceptions(ex_cls, ex, tb):

	logging.critical(''.join(traceback.format_tb(tb)))
	logging.critical('{0}: {1}'.format(ex_cls, ex))

sys.excepthook = log_uncaught_exceptions