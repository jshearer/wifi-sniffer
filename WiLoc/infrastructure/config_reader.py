import json
from WiLoc import device_id

cfg_data = json.loads('config_data.json')

def get_data():
	if device_id in cfg_data['devices']:
		return cfg_data['devices'][device_id]
	return None

def get_group():
	data = get_data()
	if data:
		return cfg_data['groups'][data['group']]
	return None