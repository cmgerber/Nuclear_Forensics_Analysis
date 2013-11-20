#! /usr/bin/env/python_2.7.5

__author__ = 'Colin Gerber'
__python_version__ = '2.7.5'


import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hcluster
from scipy.cluster import vq
from scipy.cluster.vq import whiten
from scipy.spatial.distance import cdist
import pandas
import itertools
from copy import deepcopy
import shapely.geometry as geom

ver = 3.0


def import_data():
    '''This function takes in data from a .csv and stores it in a pandas
    dataframe. The file must be a .xls or xls.'''

    data = pandas.read_excel('VVER_RBMK_python_test_3_category.xlsx', 'Sheet1')
    test_case = pandas.read_excel('VVER_RBMK_python_test_3_category.xlsx', 'Sheet2')
    return data, test_case
    

def run_analysis(data, choice, base_column, ltitles, test_case):
    
    if choice == 1:
        regression(data, base_column,ltitles, test_case)
    elif choice == 2:
        run_kmeans(data, base_column, ltitles, test_case)

    elif choice == 3:
        run_hierarchical(data, base_column, ltitles)
        

def regression(data, base_column,ltitles, test_case):
    '''This function does a polynomial regression on each of the reactor ratio pairs
    and then finds the distance from each curve to the unkown sample provided. 
    It also plots all of the results and saves them to .png files.'''

    x = []; y = []
    reactor_name = []
    regression_dist_dict = {}
    min_dist = 1000
    
    for current_name in ltitles:
        color = get_color()
        for i, group in data.groupby('reactor'):
            x = group[base_column]
            y = group[current_name]
            reactor_name.append(i)
            new_color = next(color)

            #this calculates the distance of the unknown point to the curve of 
            #each reactor.
            coords = zip(x,y)
            line = geom.LineString(coords)
            unknown_samples = zip(test_case[base_column],test_case[current_name])
            point = geom.Point(unknown_samples)
            print 'distance from %s:' % (i), point.distance(line)

            if current_name not in regression_dist_dict:regression_dist_dict[current_name] = []
            regression_dist_dict[current_name].append((i, point.distance(line)))

            p = np.poly1d(np.polyfit(x,y, 2))            
            print '%s: %s vs. %s \n \n \n ' % (i, current_name, base_column), p, '\n \n \n'
            
            
            #this creates a graph for each regression
            xp = np.linspace(0, 1.2, 100)
            plt.plot(x, y, '.', c = new_color, label = i)
            plt.plot(xp, p(xp), '-', c = new_color)
            plt.ylim(-.1,.5)
            plt.ylabel(current_name); plt.xlabel(base_column)

        #finds the closest curve for the current pu ratios and
        #then plots the unknown point with a line connecting it to the curve.
        for ratio in regression_dist_dict[current_name]:
            if ratio[1] < min_dist: min_dist = ratio

        temp_df = data[data['reactor'] == ratio[0]]
        line = geom.LineString(zip(temp_df[base_column], temp_df[current_name]))

        #plots the unknown point and a line connecting it to the curve.
        point_on_line = line.interpolate(line.project(point))
        plt.plot([point.x, point_on_line.x], [point.y, point_on_line.y], color= next(color), marker='o', label = 'Uknown Sample')

        #plt.plot(test_case[base_column],test_case[current_name], '^', c = next(color), label = "Uknown Sample")
        plt.title('%s: %s vs. %s' % (', '.join(map(str, reactor_name)), current_name, base_column))
        plt.legend()
        #saves the current plot to a temp variable so it can save plot to file after show()
        temp_plot = plt.gcf()
        plt.show()
        saveitem = current_name.replace('/', '')
        savebase_column = base_column.replace('/', '')
        #saves plot to .png file
        temp_plot.savefig('%s%s%s_regression.png' % (''.join(map(str, reactor_name)), saveitem, savebase_column))
        del reactor_name[:]
    print 'dict', regression_dist_dict
    return regression_dist_dict


def run_kmeans(data, base_column, ltitles, test_case):

    while (True):
        try:
            N = int(raw_input('How many clusters do you have? '))
            break
        except Exception as e:
            print 'Please enter an integer.'

    name = get_name(ltitles)
    unknown_results_dict = {key:(100,100) for key in ltitles}


    #loops through each of the combinations of columsn
    for num in range(len(ltitles)):
        #get the next name of the column
        current_name = next(name)
        total_code = np.array([])
        ltotal_cluster = []
        counter = 0
        temp_code = []
        temp_extreme_cluster_points = []; temp_min_cluster_points = []


        for i, group in (data.groupby('enrichment')):
            
            #creates a list of the data from two columns at each enrichment and then turns it into an array
            temp1 = zip(group[base_column],group[current_name])

            cluster_array = np.array([[x,y] for x, y in temp1])

            # #Normalize a group of observations on a per feature basis
            # cluster_array = whiten(cluster_array)

            #creates a combined list of the points from the different burnups to plot
            ltotal_cluster.append(cluster_array)
            
            center, _ = vq.kmeans(cluster_array, N)

            code,distance = vq.vq(cluster_array, center)
            
            if counter == 0:
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

            else:
                print 'counter', counter
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

                #this finds the distance between the previous kmeans centers
                #and the current ones. Then it makes a new code list so that the 
                #codes can be adjusted so they match the previous ones.
                extreme_dist = cdist(max_array, min_array, 'euclidean')

                #creates a list of the data points organized by their kmeans code
                #and then makes a list of the minimum point from each cluster to use for the next time around.
                for label in set(code):
                    min_point = (100,100)
                    temp_min_points = cluster_array[code == label]
                    for x,y in temp_min_points:
                        if x**2 + y**2 < min_point[0]**2 + min_point[1]**2:
                            min_point = (x,y)
                    temp_min_cluster_points.append(min_point)
                min_array = np.array(temp_min_cluster_points)
                del temp_min_cluster_points[:]

             
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

            #Test the unknown each time kmeans is run to find the closes center.
            test_unknown(test_case, center, code, base_column, current_name, unknown_results_dict)

        #turns the list of arrays back into a single array.
        total_cluster_array = np.vstack(ltotal_cluster)
        del ltotal_cluster[:]
        plot_results(total_cluster_array, total_code, current_name, base_column, data, test_case)
        
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
    print 'lowest distance', lowest_distance_list

    #converts averages into codes
    for n in range(len(lowest_distance_list)):
        for k in range(len(array)):
            for num in range(len(array[k])):
                if lowest_distance_list[n] == array[k][num]:
                    lowest_distance_code[k] = num
    print 'item', lowest_distance_code
    return lowest_distance_code

def test_unknown(test_case, center, code, base_column, current_name, unknown_results_dict):
    '''This function takes an uknown sample and matches it to the closest
    kmeans center. It currently only works with one unknown sample at a time.
    It does this for each isotope that is being looked at and stores the plot_results
    in a dictionary.'''

    unknown_samples = zip(test_case[base_column],test_case[current_name])

    unknown_dist = cdist(unknown_samples,center, 'euclidean')
    unknown_dist = unknown_dist[0].tolist()
    print 'unknown_dist', unknown_dist
    
    #creates an ordered set of the elements in the code list.
    #will be used to match the kmeans center chosen to the overall code for plotting
    #and reactor identification.
    code_ordered_set_list = []
    for item in code:
        if item not in code_ordered_set_list:
            code_ordered_set_list.append(item)

    #find the minimum distance from a center and then adds it to a 
    #dictionary if the distance is smaller than the existing distance
    #in the dictionary is for the current key (key = pu isotope)
    min_dist = min(unknown_dist)
    if min_dist < unknown_results_dict[current_name][0]:
        unknown_results_dict[current_name] = (min_dist, code_ordered_set_list[unknown_dist.index(min_dist)])
    
    print 'unknown_results_dict', unknown_results_dict
    
        
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
        

def get_reactors(data):
    '''This function creates a list of the reactor names'''

    return [i for i, group in data.groupby('reactor')]

def get_color():
    '''This function creates and yields a list of colors'''
    for color in ['b', 'r', 'g', 'y', 'm', 'c']:
        yield color        

    
def plot_results(cluster_array, code, current_name, base_column, data, test_case):

    print 'fix maching name of clusters to reactor'

    cluster_points = []
    color = get_color()

    reactor_name = get_reactors(data)

    #creates a list of the data points organized by their kmeans code
    for label in set(code):
        cluster_points.append(cluster_array[code == label])

    #combines n number of graphs, n being the number of sections each reactor is broken up into.
    for num in range(len(cluster_points)):
        plt.scatter(cluster_points[num][:,0], cluster_points[num][:,1], c = next(color), label = reactor_name[num])

    #this plots the unknown sample
    plt.scatter(test_case[base_column], test_case[current_name], c = next(color), marker = '^', label = 'Unknown Sample')
    
    plt.legend()
    plt.ylabel(current_name); plt.xlabel(base_column)
    plt.title('%s: %s vs. %s' % (', '.join(map(str, reactor_name)), current_name, base_column))
    #saves the current plot to a temp variable so it can save plot to file after show()
    temp_plot = plt.gcf()
    plt.show()
    saveitem = current_name.replace('/', '')
    savebase_column = base_column.replace('/', '')
    #saves plot to .png file
    temp_plot.savefig('%s%s%s_kmeans.png' % (''.join(map(str, reactor_name)), saveitem, savebase_column))



    

def data_analysis():
    data, test_case = import_data()

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
    run_analysis(data, choice, base_column, ltitles, test_case)


def main():
    data_analysis()
    

#code execution begins and invokes main()
if __name__ == '__main__':
    main()
    
