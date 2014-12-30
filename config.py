import redis
#Alfa MAC addr prefix
sniffer_mac_beginning = ['00:c0:ca']
real_network = 'ShearerWireless'
DEBUG=True

root_dir = '/home/joseph/sniffer/'

r = redis.StrictRedis(host='localhost', port=6379)

