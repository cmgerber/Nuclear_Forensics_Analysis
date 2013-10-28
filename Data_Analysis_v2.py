#! /usr/bin/env python 2.7.5

__author__ = 'Colin Gerber'
__python_version = '2.7.5'


import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hcluster
from scipy.cluster import vq
from scipy.spatial.distance import cdist
import pandas


ver = 2.0


def import_excel_data():
	'''This function takes in data from a .csv and stores it in a pandas
	dataframe. The file must be a .csv.'''

	return pandas.read_csv('jimmy-vver-rbmk-Result-09-20-2013 -for-python-pandas.csv')
	

def run_analysis(data, choice, base_column, ltitles):
	
	if choice == 1:
		regression(data, base_column,ltitles)
	elif choice == 2:
		run_kmeans(data, base_column, ltitles)

	elif choice == 3:
		run_hierarchical(data, base_column, ltitles)


def regression(data, base_column,ltitles):
	x = []; y = []
	
	for i, group in data.groupby('reactor'):
		x = group[base_column]
		for item in ltitles:
			y = group[item]
			p = np.poly1d(np.polyfit(x,y, 2))			
			print '%s: %s vs. %s \n \n \n ' % (i, item, base_column), p, '\n \n \n'
			
			
			#this creates a graph for each regression
			xp = np.linspace(0, 1.2, 100)
			plt.plot(x, y, '.', xp, p(xp), '-')
			plt.ylim(-.1,.5)
			plt.ylabel(item); plt.xlabel(base_column)
			plt.title('%s: %s vs. %s' % (i, item, base_column))
			plt.show()
		
def get_reactors(data):
	'''This function creates a list of the reactor names'''

	return [i for i, group in data.groupby('reactor')]



def run_kmeans(data, base_column, ltitles):

	while (True):
		try:
			N = int(raw_input('How many clusters do you have? '))
			break
		except Exception as e:
			print 'Please enter an integer.'

	name = get_name(ltitles)
	

	#loops through each of the combinations of columsn
	for num in range(len(ltitles)):
		#get the next name of the column
		current_name = next(name)
		total_code = np.array([])
		ltotal_cluster = []
		counter = 0
		temp_code = []
		for i, group in data.groupby('burnup'):
			
			#creates a list of the data from two columns at each burnup and then turns it into an array
			temp1 = zip(group[base_column],group[current_name])

			cluster_array = np.array([[x,y] for x, y in temp1])
			#creates a combined list of the ponts from the different burnups to plot
			ltotal_cluster.append(cluster_array)
			center, _ = vq.kmeans(cluster_array, N)

			if counter == 0:
				lcenters = center
			else:
				print 'counter', counter
				print center
				#this finds the distance between the previous kmeans centers
				#and the current ones. Then it makes a new code list so that the 
				#codes can be adjusted so they match the previous ones.
				cent_dist = cdist(center, lcenters, 'euclidean')
				print 'centers\n', cent_dist
				sys.exit()
				for item in cent_dist:
					ltemp = item.tolist()
					temp_code.append(ltemp.index(min(ltemp)))
					del ltemp[:]
				for num in range(len(cent_dist)):
					
				check each combination of centers and find the combination with the lowest average
				#if the two code lists are not the same length then two of the current centers when to the same old center.
				if len(set(code)) != len(set(temp_code)):

					raise Exception('When matching Kmeans codes between burnups at least two centers matched to a single previous center.')
				lcenters = center
				print 'temp', temp_code
				print cent_dist


			code,distance = vq.vq(cluster_array, center)
				
			#creates a combined array of the ponts from the different burnups to plot
			#adjusted for the differences in code labeling
			if counter != 0:
				
				print 'before', code
				for item in range(len(code)):
					code[item] = temp_code[code[item]]
				print 'after', code
			total_code = np.append(total_code,code)

			counter += 1
		#turns the list of arrays back into a single array.
		total_cluster_array = np.vstack(ltotal_cluster)
		del ltotal_cluster[:]
		print 'here'
		plot_results(total_cluster_array, total_code, current_name, base_column, data)
	    
	    
def get_name(ltitles):
	'''This functon creates a way to call for a new name.'''
	for name in ltitles:
		yield name



def run_hierarchical(data, base_column, ltitles):

	while (True):
		try:
			N = int(raw_input('How many clusters do you have? '))
			break
		except Exception as e:
			print 'Please enter an integer.'

	for item in ltitles:
		cluster_array = np.array(data[[base_column, item]])
		code = hcluster.fclusterdata(cluster_array, N, criterion = 'maxclust')

		plot_results(cluster_array, code, item, base_column, data)
		

		

	
def plot_results(cluster_array, code, item, base_column, data):
	cluster_points = []
	colors = ['b', 'r', 'g', 'y', 'o', 'b']
	print 'setcode', set(code)
	reactor_name = get_reactors(data)

	for label in set(code):
		cluster_points.append(cluster_array[code == label])

	#combines n number of graphs, n being the number of sections each reactor is broken up into.
	for num in range(len(cluster_points)):
		plt.scatter(cluster_points[num][:,0], cluster_points[num][:,1], c = colors[num], label = reactor_name[num])
	
	plt.legend()
	plt.ylabel(item); plt.xlabel(base_column)
	plt.title('%s: %s vs. %s' % (', '.join(map(str, reactor_name)), item, base_column))
	#saves the current plot to a temp variable so it can save plot to file after show()
	temp_plot = plt.gcf()
	plt.show()
	saveitem = item.replace('/', '')
	savebase_column = base_column.replace('/', '')
	#saves plot to .png file
	temp_plot.savefig('%s%s%s.png' % (''.join(map(str, reactor_name)), saveitem, savebase_column))



	

def data_analysis():
	data = import_excel_data()


	print 'Please choose which type of analysis you would like to run.'
	print 'Enter 1 for Regression'
	print 'Enter 2 for Kmeans clustering'
	print 'Enter 3 for Hierarchical clustering'

	

	#while (True)
	# try:
	choice = int(raw_input('> '))
	if choice not in [1,2,3]:
		raise
	#else:
		#break
	# except Exception as e:
	# 	print 'Please enter one of the choices on the list'

	while (True):
		try:
			base_column = raw_input('What is the name of the column that the x-axis data is in? ')
			if base_column.lower() == 'end':
				sys.exit()
			base_column = [s for s in data.columns.tolist() if base_column in s]
			if len(base_column) == 1:
				break
			raise
		except Exception as e:
			print 'Please enter a differnt name or enter "end".'
	
	base_column = str(base_column[0])
	ltitles = data.columns.tolist(); ltitles = ltitles[2:]; ltitles.remove(base_column)
	run_analysis(data, choice, base_column, ltitles)


def main():
    data_analysis()
    

#code execution begins and invokes main()
if __name__ == '__main__':
    main()
    
