import os

from config_reader import get_data, get_group
from WiLoc.sniffing.wifi_config import get_real_card

def setup_wifi():
	grp = get_group()

	if grp and grp['wifi']['enable']:
		#We assume running arch

		wifi = grp['wifi']

		ssid = wifi['ESSID']
		security = wifi['security']
		ip = wifi['ip']
		hidden = (wifi['hidden'] if 'hidden' in wifi else False)

		if security is not 'none':
			key = wifi['key']

		interface = get_real_card()

		filename = "sniff-%s-securedby-%s"%(ssid,security)

		with open(os.path.join('/etc/netctl',filename),'w') as wifi_file:
			wifi_file.write("Description='Set up wifi for sniffing.'\n")
			wifi_file.write("Interface=%s\n"%(interface,))
			wifi_file.write("Connection=wireless\n")
			wifi_file.write("Security=%s\n"%(security,))
			if security is not 'none':
				wifi_file.write("Key='%s'\n"%(key,))
			wifi_file.write("ESSID='%s'\n"%(ssid,))
			wifi_file.write("IP=dhcp\n"%(ssid,))
			if hidden:
				wifi_file.write("Hidden=yes\n")

if __name__=="__main__":
	setup_wifi()