import os
import logging
import requests
import json

from WiLoc.sniffing.wifi_config import get_real_card
from WiLoc.communication.api import get
from WiLoc.config import wifi_backup_filename
from WiLoc import device_id

def setup_wifi():
	try:
		host = get('hosts',{'uid':device_id})['results'][0]
		location = get(host['location'])
		wifi_settings = get(location['wifi_settings'])
		with open(wifi_backup_filename,'w') as f:
			f.write(json.dumps(wifi_settings))
		logging.info("WiFi data pulled from server. Hostname: "+str(host['name'])+" at "+str(location['name'])+", wifi enabled: "+str(wifi_settings['enabled']))
	except requests.exceptions.ConnectionError as e:
		logging.warning("Unable to connect to api. Attempting to fall back to stored wifi data.")
		if os.path.isfile(wifi_backup_filename):
			with open(wifi_backup_filename,'r') as f:
				wifi_settings = json.loads(f.read())
				logging.warning("WiFi loaded from backup. Connecting to: {%s}. This data may be incorrect!"%(wifi_settings['ESSID'],))
		else:
			logging.error("No backup file found. Cannot configure wifi!")
			return


	if wifi_settings['enabled']:
		#We assume running arch

		ssid = wifi_settings['ESSID']
		security = wifi_settings['security']
		ip = wifi_settings['ip']

		if security != 'none':
			key = wifi_settings['key']

		interface = get_real_card()

		filename = "sniff-%s-securedby-%s"%(ssid,security)

		with open(os.path.join('/etc/netctl',filename),'w') as wifi_file:
			wifi_file.write("Description='Set up wifi for sniffing.'\n")
			wifi_file.write("Interface=%s\n"%(interface,))
			wifi_file.write("Connection=wireless\n")
			wifi_file.write("Security=%s\n"%(security,))
			if security != 'none':
				wifi_file.write("Key='%s'\n"%(key,))
			wifi_file.write("ESSID='%s'\n"%(ssid,))
			wifi_file.write("IP=dhcp\n")
			if wifi_settings['hidden']:
				wifi_file.write("Hidden=yes\n")

if __name__=="__main__":
	setup_wifi()
