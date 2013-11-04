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
import itertools
from copy import deepcopy


ver = 3.0


def import_data():
    '''This function takes in data from a .csv and stores it in a pandas
    dataframe. The file must be a .csv.'''

    return pandas.read_excel('VVER_RBMK_python_test.xlsx', 'Sheet1')
    

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
        temp_extreme_cluster_points = []; temp_min_cluster_points = []

        for i, group in data.groupby('burnup'):
            
            #creates a list of the data from two columns at each burnup and then turns it into an array
            temp1 = zip(group[base_column],group[current_name])

            cluster_array = np.array([[x,y] for x, y in temp1])
            #creates a combined list of the ponts from the different burnups to plot
            ltotal_cluster.append(cluster_array)
            center, _ = vq.kmeans(cluster_array, N)

            code,distance = vq.vq(cluster_array, center)
            
            if counter == 0:
                #creates a list of the data points organized by their kmeans code
                #and then makes a list of the maximum point from each cluster
                for label in set(code):
                    extreme_point = (0,0)
                    temp_points = cluster_array[code == label]
                    for x,y in temp_points:
                        if x**2 + y**2 > extreme_point[0]**2 + extreme_point[1]**2:
                            extreme_point = (x,y)
                    temp_extreme_cluster_points.append(extreme_point)
                max_array = np.array(temp_extreme_cluster_points)
                del temp_extreme_cluster_points[:]

            else:
                print 'counter', counter
                #creates a list of the data points organized by their kmeans code
                #and then makes a list of the minimum point from each cluster
                for label in set(code):
                    min_point = (100,100)
                    temp_min_points = cluster_array[code == label]
                    for x,y in temp_min_points:
                        if x**2 + y**2 < min_point[0]**2 + min_point[1]**2:
                            min_point = (x,y)
                    temp_min_cluster_points.append(min_point)
                min_array = np.array(temp_min_cluster_points)
                del temp_min_cluster_points[:]


                #this finds the distance between the previous kmeans centers
                #and the current ones. Then it makes a new code list so that the 
                #codes can be adjusted so they match the previous ones.
                extreme_dist = cdist(min_array, max_array, 'euclidean')

             
                temp_code = closest_cluster(extreme_dist)
                print 'cart\n', temp_code
                
                lcenters = center            
                
                #creates a combined array of the ponts from the different burnups to plot
                #adjusted for the differences in code labeling
                
                print 'before', code
                for num in range(len(code)):
                    code[num] = temp_code[code[num]]
                print 'after', code

            total_code = np.append(total_code,code)
            counter += 1
        #turns the list of arrays back into a single array.
        total_cluster_array = np.vstack(ltotal_cluster)
        del ltotal_cluster[:]
        print 'here'
        plot_results(total_cluster_array, total_code, current_name, base_column, data)
        
def closest_cluster(array):
    '''This function generates permutations of an array of the distances between the
    old centers and the new centers where each element is from only one column and row.
    It then takes the average of each permuatation and returns the codes for the 
    permutation with the lowest average.'''

    #following code adapted from: http://stackoverflow.com/questions/19640525/in-python-how-do-you-generate-permutations-of-an-array-where-you-only-have-one
    center_combinations = []
    lowest_distance = 100
    lowest_distance_list = None
    for P in itertools.permutations(range(len(array))):
        center_combinations.append([array[p][i] for i,p in enumerate(P)])

    print 'combinations', center_combinations

    #finds the combination of distances with the lowest distance
    #if there are two with the smallest distance then it checks the next smallest.
    
    for item in center_combinations:
        if lowest_distance_list == None:
            lowest_distance_list = item
            continue
        temp_sorted_c = sorted(lowest_distance_list)
        temp_sorted_t = sorted(item)
        for num in range(len(temp_sorted_t)):
            if temp_sorted_t[num] < temp_sorted_c[num]:
                lowest_distance_list = item
            elif temp_sorted_t[num] == temp_sorted_c[num]:
                continue
            else:
                break

    lowest_distance_code = deepcopy(lowest_distance_list)
    print lowest_distance_list

    #converts averages into codes
    for n in range(len(lowest_distance_list)):
        for k in range(len(array)):
            for num in range(len(array[k])):
                if lowest_distance_list[n] == array[k][num]:
                    lowest_distance_code[k] = num
    print 'item', lowest_distance_code
    return lowest_distance_code



    
        
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

    reactor_name = get_reactors(data)

    #creates a list of the data points organized by their kmeans code
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
    data = import_data()


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
    #     print 'Please enter one of the choices on the list'

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
    
