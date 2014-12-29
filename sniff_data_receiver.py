from config import r
import time

def start_listening():
	def new_datapoint(message):
		print "NEW DATA POINT: "+str(message)

	redis_queue = r.pubsub(ignore_subscribe_messages=True)
	redis_queue.subscribe("sniff", "sniff-info")

	print "Listening for messages"

	while True:
		#Poll for messages. If they show up, it'll call new_datapoint
		msg = redis_queue.get_message()
		while msg is not None:
			new_datapoint(msg)
			msg = redis_queue.get_message()
		time.sleep(0.0001)

if __name__ == "__main__":
	start_listening()


