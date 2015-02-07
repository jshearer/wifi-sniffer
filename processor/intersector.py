from sympy import Point, Circle, Polygon, Segment
from pony.orm import get, db_session
from data import Receiver, Recording
from itertools import permutations

#This function assumes that the data has already been filtered by transmitter's MAC
#As such, only one transmitter MAC should show up. If more than one exist, that's an error

#Returns: (center, uncertainty)

#uncertainty is the perimiter of the uncertainty polygon/circle

#mode_data: If this is True, data such as the positions and radii of receivers, acceptable points and uncertainty polygon will be returned

#Modes are used to handle the case where there are multiple data points for each receiver:
#min: Take the smallest data point
#avg: Take the average of all the data points
#max: Take the largest data point
#Default: avg
def find_common_center(recordings, mode='avg', more_data = False):
	# Create circles:
	#	Find radius for each receiver
	#		take min, avg, or max
	#	Get center from database

	if not mode in ['min','max','avg']:
		raise Exception("Unrecognized singularization mode: "+str(mode))

	circles = {}
	transmitter = None

	#Collect transmitter -> strength array mapping
	for recording in recordings:
		if not transmitter:
			transmitter = recording.transmitter.mac_addr
		else:
			if transmitter != recording.transmitter.mac_addr:
				raise Exception("Multiple transmitters found. Please filter by transmitter.")

		if recording.receiver.mac_addr not in circles.keys():
			circles[recording.receiver.mac_addr] = []

		circles[recording.receiver.mac_addr].append(recording.rssi)

	#Perform singularization on strength arrays
	#Create Circle instances
	for (transmitter,radii) in circles.items():
		if mode=='min':
			radius = min(radii)
		elif mode=='max':
			radius = max(radii)
		elif mode=='avg':
			radius = sum(radii)/len(radii)
		else:
			raise Exception("Unrecognized singularization mode: "+str(mode))

		with db_session:
			rec = get(rec for rec in Receiver if rec.mac_addr==transmitter)
			if rec:
				x = rec.x
				y = rec.y
			else:
				raise Exception("Unknown receiver found. Please enter data for: "+str(transmitter))

		circles[transmitter] = Circle(Point(x,y),abs(radius))

	# Find all circle intersection points, store in set
	intersects = set()
	#For each permutation of circles, two at a time
	#Find all intersection points
	for c1,c2 in permutations(circles.values(),2):
		intersects.update(c1.intersection(c2))


	# For each circle, prune all points not inside, inclusive (including points on the edge of the circle)
	for circle in circles.values():
		for intersection in set(intersects):
			if float(circle.center.distance(intersection))>float(circle.radius):
				intersects.discard(intersection)

	# If points remaining>=3, create polygon from points, get polygon's area and centroid. That is predicted position, uncertainty
	# If points remaining==2, create circle centered around midpoint, with d=distance between the points. Circle's center is predicted position, area is incertainty
	# If points remaining==1, that is predicted position. Uncertainty is zero
	# If points remaining<1, return None
	ret = tuple()
	uncertainty_shape = None
	if len(intersects)>=3:
		poly = Polygon(*intersects)
		ret = (poly.centroid,poly.area)

		uncertainty_shape = poly
	elif len(intersects)==2:
		seg = Segment(*intersects)
		circ = Circle(seg.midpoint,seg.length/2.0)
		ret = (circ.center,circ.area)

		uncertainty_shape = seg
	elif len(intersects)==1:
		ret = (intersects.pop(),0)
	else:
		ret = (None,None)

	if more_data:
		return {'receivers':circles,'intersects':intersects,'uncertainty_shape':uncertainty_shape,'pos':ret[0],'uncertainty':ret[1]}
	else:
		return ret

def jsonifiy_data(more_data):

	def jsonify_point(pt):
		if not pt:
			return {'x':0,'y':0}

		return {'x':float(pt.x),'y':float(pt.y)}

	def jsonify_circle(cr):
		return {'center':jsonify_point(cr.center),'radius':float(cr.radius)}

	def jsonify_polygon(po):
		return [jsonify_point(vertex) for vertex in po.vertices]

	def jsonify_segment(se):
		return [jsonify_point(se.p1),jsonify_point(se.p2)]

	jsonified_data = {}

	jsonified_data['receivers'] = [jsonify_circle(cr) for cr in more_data['receivers'].values()]
	jsonified_data['intersects'] = [jsonify_point(pt) for pt in more_data['intersects']]
	if type(more_data['uncertainty_shape']) is Polygon:
		jsonified_data['uncertainty_shape'] = jsonify_polygon(more_data['uncertainty_shape'])
	elif type(more_data['uncertainty_shape']) is Segment:
		jsonified_data['uncertainty_shape'] = jsonify_segment(more_data['uncertainty_shape'])
	else:
		jsonified_data['uncertainty_shape'] = None

	jsonified_data['pos'] = jsonify_point(more_data['pos'])
	jsonified_data['uncertainty'] = float(more_data['uncertainty'] or 0)

	return jsonified_data



#TODO: Implement a function to fitler by transmitter. For the moment only one tramsitter exists
#so it won't be too much of an issue