import requests
import urlparse

from WiLoc.config import server_address

transmitter_mapping = {}
receiver_mapping = {}

def get(resource, params=dict()):

	params.update({"format":"json"})
	
	return requests.get(urlparse.urljoin(server_address,resource),params=params).json()

def post(resource, params=dict(), data=dict()):

	params.update({"format":"json"})
	headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

	return requests.post(urlparse.urljoin(server_address,resource),params=params,data=data, headers=headers).json()

def get_transmitter_id(mac_addr):
	if mac_addr in transmitter_mapping:
		return transmitter_mapping[mac_addr]

	server_query = get('transmitters', {'mac_addr':mac_addr})

	if len(server_query)==1:
		#This transmitter is known?
		transmitter_mapping[mac_addr] = server_query[0]['pk']
		return server_query[0]['pk']
	else:
		#New transmitter!
		return post('transmitters',data={'mac_addr':mac_addr,'name':'Unknown'})['pk']

def get_receiver_id(mac_addr):
	from WiLoc import host_id

	if mac_addr in receiver_mapping:
		return receiver_mapping[mac_addr]

	server_query = get('receivers', {'mac_addr':mac_addr,'host':host_id})

	if len(server_query)==1:
		#This transmitter is known?
		receiver_mapping[mac_addr] = server_query[0]['pk']
		return server_query[0]['pk']

	return None

def new_recording(transmitter,receiver,rssi):
	post('recordings',data={'transmitter':get_transmitter_id(transmitter),'receiver':get_receiver_id(receiver),'rssi':rssi})


def get_host_id(device_id):
	server_query = get('hosts',{'device_uid':device_id})

	if len(server_query)==1:
		return server_query[0]['pk']

	return None