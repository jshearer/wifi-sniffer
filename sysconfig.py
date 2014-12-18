import netifaces
import wifi
from subprocess import Popen, call, PIPE
import os

#/dev/null
DN = open(os.devnull, 'w')

#Alfa MAC addr prefix
sniffer_mac_beginning = ['00:c0:ca']

real_network = 'Shearer wireless'

def startswith_any(value,arr):
	for checkme in arr:
		if value.startswith(checkme):
			return True
	return False

def get_wlan_ifaces():
	return filter(lambda iface:iface.startswith('wlan'),netifaces.interfaces())

def get_mon_ifaces():
	return filter(lambda iface:iface.startswith('mon'),netifaces.interfaces())

def mac_to_iface():
	mapping = {}
	for iface in get_wlan_ifaces():
		link_addr = netifaces.ifaddresses(iface)
		mapping[iface]=link_addr[netifaces.AF_LINK][0]['addr']
	return mapping

def get_real_card():
	mac_ifaces = mac_to_iface()
	real_iface = None

	for iface in mac_ifaces:
		mac = mac_ifaces[iface]
		if !startswith_any(mac,sniffer_mac_beginning):
			real_iface = iface
			break
	return real_iface

def get_sniffing_cards():
	mac_ifaces = mac_to_iface()
	sniff_ifaces = []

	for iface in mac_ifaces:
		mac = mac_ifaces[iface]
		if startswith_any(mac,sniffer_mac_beginning):
			sniff_ifaces.append(iface)
	return sniff_ifaces

def get_lines(cmd):
	if(type(cmd)==str):
		cmd = cmd.split(' ')
	proc = Popen(cmd, stdout=PIPE, stderr=DN)
	return proc.communicate()[0].split('\n')

def stop_monitor_all():
	for mon in get_mon_ifaces():
		stop_monitor_mode(mon)

def stop_monitor_mode(mon):
	get_lines('airmon-ng stop '+mon)

def start_monitor_mode(device):
	for line in get_lines('airmon-ng start '+device):
		if '(monitor mode enabled on' in line:
			mon = line.split('(monitor mode enabled on ')[1][:-1]
			if mon.startswith('mon'):
				return mon
			else:
				raise Exception('Error parsing line: '+line)
	return None

def setup_real_card():
	real_card = get_real_card()
	if not real_card:
		raise Exception('No non-Alfa card found.') 

	connection_scheme = wifi.Scheme.find(real_card,real_network)
	if connection_scheme:
		connection_scheme.activate()
	else:
		acceptable_cell = wifi.Cell.where(real_card,lambda cell:cell.ssid==real_network)
		connection_scheme = wifi.Scheme.for_cell(real_card,real_network,acceptable_cell)
		connection_scheme.save()
		setup_real_card()

def setup_monitors():
	Get sniffing cards
	Start monitor on all the cards, store which monx is associated to which card, MAC
	Start a process for each monx, write subprocess module
