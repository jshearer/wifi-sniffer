import sys
import traceback
import logging

def log_uncaught_exceptions(ex_cls, ex, tb):

	logging.critical(''.join(traceback.format_tb(tb)))
	logging.critical('{0}: {1}'.format(ex_cls, ex))
	sys.exit(0)

sys.excepthook = log_uncaught_exceptions