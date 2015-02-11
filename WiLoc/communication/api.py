import requests
import urlparse
import logging
import json

from WiLoc.config import server_address

transmitter_mapping = {}
receiver_mapping = {}

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
	logging.debug(response)
	#import pdb;pdb.set_trace()

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

def new_recording(transmitter,receiver,rssi):
	transmitter_id = get_transmitter_id(transmitter)
	receiver_id = get_receiver_id(receiver)

	if receiver_id is None:
		raise Exception("Receiver not in database. Please add: "+str(receiver))

	resp = post('recordings',data={'transmitter':transmitter_id,'receiver':receiver_id,'rssi':rssi})

	logging.debug("Created new recording: "+str(resp.content))

def get_host_id(device_id):
	server_query = get('hosts',{'device_uid':device_id})['results']

	if len(server_query)==1:
		return server_query[0]['url']

	return None