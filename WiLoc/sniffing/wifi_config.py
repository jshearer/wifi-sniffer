from subprocess import Popen, call, PIPE
import netifaces
import os
import logging
import re

from WiLoc.config import sniffer_mac_beginning
#/dev/null
DN = open(os.devnull, 'w')

mons = {}

monitor_on = re.compile("(.*)monitor mode (.*) enabled(.*)")

def startswith_any(value,arr):
	for checkme in arr:
		if value.startswith(checkme):
			return True
	return False

def get_wlan_ifaces():
	return filter(lambda iface:iface.startswith('wlan'),netifaces.interfaces())

def get_mon_ifaces():
	return filter(lambda iface:iface.endswith('mon'),netifaces.interfaces())

def iface_to_mac():
	mapping = {}
	for iface in get_wlan_ifaces():
		link_addr = netifaces.ifaddresses(iface)
		mapping[iface]=link_addr[netifaces.AF_LINK][0]['addr']
	return mapping

def get_real_card():
	mac_ifaces = iface_to_mac()
	real_iface = None

	for iface in mac_ifaces:
		mac = mac_ifaces[iface]
		if not startswith_any(mac,sniffer_mac_beginning):
			real_iface = iface
			break
	return real_iface

def get_sniffing_cards():
	mac_ifaces = iface_to_mac()
	sniff_ifaces = []

	for iface in mac_ifaces:
		mac = mac_ifaces[iface]
		if startswith_any(mac,sniffer_mac_beginning):
			sniff_ifaces.append(iface)
	return sniff_ifaces

def get_lines(cmd):
	if(type(cmd)==str):
		cmd = cmd.split(' ')

	logging.info('[exec]: '+' '.join(cmd))

	proc = Popen(cmd, stdout=PIPE, stderr=DN)
	return proc.communicate()[0].split('\n')

def stop_monitor_all():
	for mon in get_mon_ifaces():
		stop_monitor_mode(mon)

def stop_monitor_mode(mon):
	if mon in mons:
		stop_monitor_mode(mons[mon])
		del mons[mon]

	get_lines('airmon-ng stop '+mon)
	if not mon.startswith('mon'):
		get_lines('ifconfig '+mon+' up')

def set_device_channel(device,channel):
	get_lines('iwconfig '+device+' channel '+str(channel))

def start_monitor_mode(device, channel=6):
	get_lines('ifconfig '+device+' down')
	for line in get_lines('airmon-ng start '+device):
		if monitor_on.match(line):
			mon = device+"mon"
			mons[mon] = device
			set_device_channel(mon,channel)
			return mon
	raise Exception('Error starting monitor mode on: '+device)

def setup_monitors():
	stop_monitor_all()
	sniff_ifaces = get_sniffing_cards()
	mac_mapping = iface_to_mac()
	monitors = []

	for sniffer in sniff_ifaces:
		monitors.append({
							'mon': start_monitor_mode(sniffer),
							'iface': sniffer,
							'mac': mac_mapping[sniffer]
						})

	return monitors
