from datetime import datetime
from pony.orm import *
from time import time
import json

from WiLoc.data import *
from WiLoc.config import r
from intersector import find_common_center, jsonifiy_data

max_buffer_size = 10
buf = []

def handle_new_data(data):
	# {	'pattern': None, 
	# 	'type': 'message', 
	# 	'channel': 'sniff', 
	# 	'data': "{
	# 				'transmitter': 'c0:ee:fb:25:4d:c1', 
	# 				'strength': -16, 
	# 				'data': 'Hello world!', 
	# 				'monitor': '00:c0:ca:75:9a:bb', 
	# 				'time': 1420232583.284988
	# 			 }"
	# }


	receiver = get(rec for rec in Receiver if rec.mac_addr==data['data']['monitor'])
	transmitter = get(tr for tr in Transmitter if tr.mac_addr==data['data']['transmitter'])
	
	#If transmitter is not found, make one
	if not transmitter:
		nickname = raw_input("What would you like to nickname the transmitter with MAC address '"+str(data['data']['transmitter'])+"': ")
		transmitter = Transmitter(mac_addr=data['data']['transmitter'],name=nickname)
		print nickname+" created."
		commit()

	#If receiver is not found, you guessed it: make one!
	if not receiver:
		nickname = raw_input("What would you like to nickname the receiver with MAC address '"+str(data['data']['monitor'])+"': ")
		x = float(raw_input(nickname+"'s x coordinate: "))
		y = float(raw_input(nickname+"'s y coordinate: "))

		receiver = Receiver(name=nickname,mac_addr=data['data']['monitor'],x=x,y=y,z=0)

		print nickname+" created."
		commit()

	recording = Recording(	receiver=receiver,
							transmitter=transmitter,
							rssi=data['data']['strength'],
							data=data['data']['data'],
							time=datetime.fromtimestamp(data['data']['time'])
						 )
	rollback()
	buf.append(recording)

	if len(buf)>max_buffer_size:
		global buf
		calculate_new_positions(buf)
		buf = []

def calculate_new_positions(recordings):
	#Split up recordings by transmitter MAC

	transmitters = {}

	for recording in recordings:
		if not recording.transmitter.mac_addr in transmitters.keys():
			transmitters[recording.transmitter.mac_addr] = []

		transmitters[recording.transmitter.mac_addr].append(recording)

	#import pdb;pdb.set_trace()

	for transmitter_mac,recordings in transmitters.items():
		data = find_common_center(recordings,more_data=True)
		pos,uncertainty = data['pos'],data['uncertainty']

		if pos:
			transmitter = get(tr for tr in Transmitter if tr.mac_addr==transmitter_mac)
			calc_pos = CalculatedPosition(time=datetime.fromtimestamp(time()),transmitter=transmitter,uncertainty=uncertainty,x=pos.x,y=pos.y,z=0)
			print "Calculated position for "+str(transmitter.name)+" at: ("+str(round(float(pos.x),3))+","+str(round(float(pos.y),3))+"), uncertainty: "+str(round(float(uncertainty)))+"."

		r.publish('positioning',jsonifiy_data(data))
		