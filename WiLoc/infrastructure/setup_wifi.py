import os
import logging

from WiLoc.sniffing.wifi_config import get_real_card
from WiLoc.communication.api import get
from WiLoc import device_id

def setup_wifi():
	host = get('hosts',{'uid':device_id})[0]
	location = get(host['location'])[0]
	wifi_settings = get(location['wifi_settings'])[0]

	logging.info("Wifi setup. Hostname: "+str(host['name'])+" at "+str(location['name'])+", wifi enabled: "+str(wifi_settings['enabled']))

	if host and wifi_settings['enabled']:
		#We assume running arch

		ssid = wifi_settings['ESSID']
		security = wifi_settings['security']
		ip = wifi_settings['ip']
		hidden = (wifi_settings['hidden'] if 'hidden' in wifi else False)

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
			if hidden:
				wifi_file.write("Hidden=yes\n")

if __name__=="__main__":
	setup_wifi()
