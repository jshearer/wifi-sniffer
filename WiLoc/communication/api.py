import requests
import urlparse
import logging
import json
import time

from WiLoc.config import server_address

transmitter_mapping = {}
receiver_mapping = {}
recording_buffer = []
req_every = 1
req_size = 400
last_req = time.time()

session = requests.Session()

auth_info = {
	'username': 'wiloc_admin',
	'password': 'wiloc_admin'
}

def fix_url(url):
	return (url if url.endswith('/') else url + '/')

auth_url = fix_url(urlparse.urljoin(server_address,'api-auth/login?next=/'))

#get csrf token
csrf = session.get(auth_url).cookies['csrftoken']

#Authenticate
session.post(auth_url, data=auth_info, headers={'X-CSRFToken':csrf})

session.headers['Content-type'] = 'application/json'

def get(resource, params=dict()):
	params.update({'format':'json'})

	url = urlparse.urljoin(server_address,resource)
	if not url.endswith('/'):
		url = url + '/'
	
	return session.get(url,params=params).json()

def post(resource, params=dict(), data=dict(), run_json=True):
	url = urlparse.urljoin(server_address,resource)
	if not url.endswith('/'):
		url = url + '/'

	response = session.post(url,params=params, data=json.dumps(data))

	return (response.json() if run_json else response)

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
		pdata = post('transmitters',data={'mac_addr':mac_addr,'name':'Unknown'})
		if 'url' in pdata:
			return pdata['url']
		logging.error('Somethign bad happened. Heres the request: '+str(pdata.headers)+", "+str(pdata.data))
		raise Exception('Somethign bad happened. Heres the request: '+str(pdata.headers)+", "+str(pdata.data))

def get_receiver_id(mac_addr):
	from WiLoc import device_id

	if mac_addr in receiver_mapping:
		return receiver_mapping[mac_addr]

	try:
		server_query = get('receivers', {'mac_addr':mac_addr})['results']

		if len(server_query)==1:
			#This transmitter is known?
			receiver_mapping[mac_addr] = server_query[0]['url']
			return server_query[0]['url']
	except requests.exceptions.ConnectionError as e:
		logging.error('Unable to connect to server to get receiver id.')

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

	if transmitter is None or receiver is None:
		import pdb;pdb.set_trace()

	transmitter_id = get_transmitter_id(transmitter)
	receiver_id = get_receiver_id(receiver)

	if receiver_id is None:
		raise Exception('Receiver not in database. Please add: '+str(receiver))

	recording_buffer.append({'transmitter':transmitter_id,'receiver':receiver_id,'rssi':rssi})
	
	if (time.time()-last_req > req_every) or len(recording_buffer)>req_size:
		logging.info('Flushing %i recordings! elapsedtime: %f'%(len(recording_buffer),time.time()-last_req,))
		flush_recordings()

def get_host_id(device_id):
	server_query = get('hosts',{'device_uid':device_id})['results']

	if len(server_query)==1:
		return server_query[0]['url']

	return None