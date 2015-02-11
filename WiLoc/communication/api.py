import requests
import urlparse
import logging
import json
import time

from WiLoc.config import server_address

transmitter_mapping = {}
receiver_mapping = {}
recording_buffer = []
req_every = 2
last_req = time.time()

def get(resource, params=dict()):

	params.update({"format":"json"})
	headers = {'Content-type': 'application/json'}

	url = urlparse.urljoin(server_address,resource)
	if not url.endswith('/'):
		url = url + '/'
	
	return requests.get(url,params=params, headers=headers).json()

def post(resource, params=dict(), data=dict()):

	headers = {'Content-type': 'application/json'}

	url = urlparse.urljoin(server_address,resource)
	if not url.endswith('/'):
		url = url + '/'

	response = requests.post(url,params=params, data=json.dumps(data), headers=headers)

	return response.json()

def get_transmitter_id(mac_addr):
	if mac_addr in transmitter_mapping:
		return transmitter_mapping[mac_addr]

	server_query = get('transmitters', {'mac_addr':mac_addr})['results']

	if len(server_query)==1:
		#This transmitter is known?
		transmitter_mapping[mac_addr] = server_query[0]['url']
		return server_query[0]['url']
	else:
		#New transmitter!
		return post('transmitters',data={'mac_addr':mac_addr,'name':'Unknown'})['url']

def get_receiver_id(mac_addr):
	from WiLoc import host_id

	if mac_addr in receiver_mapping:
		return receiver_mapping[mac_addr]

	server_query = get('receivers', {'mac_addr':mac_addr,'host':host_id})['results']

	if len(server_query)==1:
		#This transmitter is known?
		receiver_mapping[mac_addr] = server_query[0]['url']
		return server_query[0]['url']

	return None

def flush_recordings():
	global last_req
	global recording_buffer
	
	post('recordings',data=recording_buffer)
	recording_buffer = []
	last_req = time.time()

def new_recording(transmitter,receiver,rssi):
	global recording_buffer
	global req_every
	global last_req

	transmitter_id = get_transmitter_id(transmitter)
	receiver_id = get_receiver_id(receiver)

	if receiver_id is None:
		raise Exception("Receiver not in database. Please add: "+str(receiver))

	recording_buffer.append({'transmitter':transmitter_id,'receiver':receiver_id,'rssi':rssi})
	
	if time.time()-last_req > req_every:
		logging.info("Flushing %i recordings! elapsedtime: %f"%(len(recording_buffer),time.time()-last_req,))
		flush_recordings()

def get_host_id(device_id):
	server_query = get('hosts',{'device_uid':device_id})['results']

	if len(server_query)==1:
		return server_query[0]['url']

	return None