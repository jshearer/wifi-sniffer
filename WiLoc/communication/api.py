import requests
import urlparse

from WiLoc.config import server_address

def get(resource, args=dict()):

	args.update({"format":"json"})
	
	return requests.get(urlparse.urljoin(server_address,resource),params=args).json()