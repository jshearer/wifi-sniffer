import csv

# make_csv(['monitor','transmitter','time','strength'],sniff_data_local,filename)
# Fake data
points = [{'monitor':'asdfasdf','transmitter':'dsafdfsa','strength':-24},
		  {'monitor':'asdfasdf','transmitter':'dsafdfa','strength':-21},
		  {'monitor':'asdfasdf','transmitter':'dsafdf','strength':-26},
		  {'monitor':'asdfasdf','transmitter':'safdfsa','strength':-28},
		  {'monitor':'asdfasdf','transmitter':'afdfsa','strength':-20},
		  {'monitor':'asdfasdf','transmitter':'dsfsa','strength':-21},
		  {'monitor':'asdfasdf','transmitter':'dsafda','strength':-23}]
names = ['monitor','transmitter','strength']

def make_csv(column_names,data,filename):
	columns = {}

	for col in column_names:
		columns[col] = [col]

	for point in data:
		for col in column_names:
			columns[col].append(point[col])

	#import pdb;pdb.set_trace()

	col_data = []
	cols = [columns[name] for name in column_names]
	for col in cols:
		col_data.append(col)

	col_data = zip(*col_data)

	total = 1

	with open(filename,'wb') as csvfile:
		writer = csv.writer(csvfile,delimiter=',')
		for row in col_data:
			if total%1000==0:
				print 'Wrote %i rows.'%total
			total+=1
			writer.writerow(row)