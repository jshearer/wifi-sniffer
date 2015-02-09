import json
import os
import logging

from WiLoc import device_id

filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config_data.json')
logging.debug("JSON Filename: %s"%filename)

with open(filename,'r') as json_file:
	cfg_data = json.loads(json_file.read())

def get_data():
	if device_id in cfg_data['devices']:
		return cfg_data['devices'][device_id]
	return None

def get_group():
	data = get_data()
	if data:
		return cfg_data['groups'][data['group']]
	return None