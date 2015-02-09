from pony.orm import Database

#Alfa MAC addr prefix
sniffer_mac_beginning = ['00:c0:ca']
real_network = 'ShearerWireless'
DEBUG=True

db = Database("sqlite", "database.sqlite", create_db=True)

