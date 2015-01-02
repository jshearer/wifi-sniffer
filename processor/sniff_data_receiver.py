import sys
sys.path.append('../')

from config import r
import time
from data_handler import handle_new_data
from pony.orm import db_session

DELAY = 0.01

def start_listening():
	redis_queue = r.pubsub(ignore_subscribe_messages=True)
	redis_queue.subscribe("sniff", "sniff_info")

	print "Listening for messages"

	while True:
		#Poll for messages. If they show up, it'll call new_datapoint
		msg = redis_queue.get_message()
		with db_session:
			while msg is not None:
				if msg['channel']=='sniff_info':
					print msg['data']
				else:
					#start_time = time.time()
					msg['data'] = eval(msg['data'])
					handle_new_data(msg)
					#end_time = time.time()
					#print ("That took: "+str(end_time-start_time)+" seconds.")

				msg = redis_queue.get_message()
		time.sleep(DELAY)

if __name__ == "__main__":
	start_listening()


