#! /usr/bin/env/python

__author__ = 'Colin Gerber'
__python_version__ = '2.7.5'

import sys
import math
from scipy.optimize import fmin
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import shapely.geometry as geom

ver = 2.0

def import_data():
    '''This function takes in data from a .csv and stores it in a pandas
    dataframe. The file must be a .xls or xls.'''

    # while (True):
    #     try:
    #         file_name = raw_input('What is the excel file name you would like to use? ')
    #         data = pd.read_excel(file_name, 'Sheet1')
    #         test_case = pd.read_excel(file_name, 'Sheet2')
    #         break
    #     except Exception as e:
    #         print e
    #         print 'The file you entered does not exist in the directory.'
    #         file_path = raw_input('Please enter the path to your file (or enter "try" to retype the file name): ')
    #         if file_path.lower() == 'try':
    #             pass
    #         else:
    #             os.chdir(file_path)

    #use for easy testing.
    data = pd.read_excel('VVER_RBMK_BWR_enrichment_generated.xlsx', 'Sheet1')
    test_case = pd.read_excel('VVER_RBMK_BWR_enrichment_generated.xlsx', 'Sheet2')
    return data, test_case

def run_analysis(data, choice, base_column, ltitles, test_case):
    
    if choice == 1:
        regression(data, base_column,ltitles, test_case)

def regression(data, base_column,ltitles, test_case):
    '''This function does a polynomial regression on each of the reactor ratio pairs
    and then finds the distance from each curve to the unkown sample provided. 
    It also plots all of the results and saves them to .png files.'''

    x = []; y = []
    reactor_name = []
    regression_dist_dict = {}
    min_dist = ('temp', 1000)
    react_len = 0
    
    #iterate through each ratio and compare it to the baseline ratio
    for current_name in ltitles:
        color = get_color()

        #initiate plot
        fig = plt.figure(figsize=(10,6))
        ax  = fig.add_subplot(111)

        for i, group in data.groupby(['reactor', 'enrichment']):
            #creates list of reactors that have been iterated through
            if i[0] not in reactor_name:
                reactor_name.append(i[0])

            #only calls new color when the iteration reaches a new reactor
            if react_len != len(reactor_name):
                #calls next color to be used in graphing. One for each reactor.
                new_color = next(color)
            react_len = len(reactor_name)

            print '\n \n \n Reactor: ', i[0]
            print 'Enrichment: ', i[1]

            x = list(group[base_column])
            y = list(group[current_name])
            unknown_sample = [test_case[base_column], test_case[current_name]]

            #this checks if there is a (0,0) point in the data, if there is not one
            #it will append one to the data so that the regression lines have a y intercept
            #of 0.
            if 0 not in x and 0 not in y:
                x.append(0)
                y.append(0)
                print 'appended'
            

            #used to draw a connecting line line from the uknown point to the curve.
            coords = zip(x,y)
            line = geom.LineString(coords)
            unknown_samples = zip(list(test_case[base_column]),list(test_case[current_name]))
            point = geom.Point(unknown_samples)
            
            print 'Uknown sample: ', unknown_samples                            

            #creates the regression line
            p = np.poly1d(np.polyfit(x,y, 2))            
            print '%s enrich: %s: %s vs. %s ' % (i[0], i[1], current_name, base_column), p
            
            #using the coefficients and unknown value calculates the distance from the regression
            #line to the unknown point.
            px = unknown_samples[0][0]; py = unknown_samples[0][1]; a = p.c[0]; b = p.c[1]; c = p.c[2]
            print px,py, a, b, c
            print type(a)
            # d = math.sqrt(((px-(a*xx))**2) + ((py-((b*xx)**2)-c)**2))
            #finds the minimum value of the distance function
            funct_min_x = fmin(my_distance_formula, 0,args=(px,py,a,b,c))
            d = my_distance_formula(funct_min_x[0],px,py,a,b,c)
            print 'distance from %s enrich: %s:' % (i[0], i[1]), d, '\n \n \n'

            #finds the y value of the min point on the curve
            funct_min_y = my_curve(funct_min_x, a, b, c)

            #creates a dictionary containing the distance from the unknown point to all the regression lines
            if current_name not in regression_dist_dict:regression_dist_dict[current_name] = []
            regression_dist_dict[current_name].append((i, d))

            
            #this creates a graph for each regression
            #change axis range with np.linespace below
            xp = np.linspace(0, 1.2, 100)
            ax.plot(x, y, '.', c = new_color, label = i)
            ax.plot(xp, p(xp), '-', c = new_color)
            plt.ylim(-.1,.5)
            plt.ylabel(current_name); plt.xlabel(base_column)

            #finds the closest curve for the current pu ratios and
            #then plots the unknown point with a line connecting it to the curve.
            for ratio in regression_dist_dict[current_name]:
                if ratio[1] < min_dist[1]: 
                    min_dist = ratio
                    plot_line = line
                    min_point = [funct_min_x, funct_min_y]

        print 'MIN_DIST: ', min_dist
        print 'CURRENT NAME', current_name
        print unknown_sample, min_point

        #plots the unknown point and a line connecting it to the curve.
        # ax.plot([unknown_sample[0], min_point[0]], [unknown_sample[1],min_point[1]], color= next(color), marker='o', label = 'Uknown Sample1' )
        # point_on_line = plot_line.interpolate(plot_line.project(point))
        # ax.plot([point.x, point_on_line.x], [point.y, point_on_line.y], color= next(color), marker='o', label = 'Uknown Sample')

        ax.plot(unknown_sample[0], unknown_sample[1], color= next(color), marker='o', label = 'Uknown Sample')

        plt.title('%s: %s vs. %s' % (', '.join(map(str, reactor_name)), current_name, base_column))
        ax.set_position([0.1,0.1,0.5,0.8])
        ax.legend(loc = 'center left', bbox_to_anchor = (1.0, 0.5))
        #saves the current plot to a temp variable so it can save plot to file after show()
        temp_plot = plt.gcf()

        #comment below in if you want each graph to pop up when you run the script
        # plt.show()

        saveitem = current_name.replace('/', '')
        savebase_column = base_column.replace('/', '')
        #saves plot to .png file
        temp_plot.savefig('%s%s%s_regression.png' % (''.join(map(str, reactor_name)), saveitem, savebase_column))
        del reactor_name[:]
    print 'dict', regression_dist_dict
    return regression_dist_dict

def my_curve(x, a, b, c):
    return (a*x)**2 + (b*x) + c

def my_distance_formula(x, px, py, a, b, c):
    '''Creates the formula for finding the distance from the uknown point to the curve
    Ie. Sqrt((x-x0)**2 + (y-y0)**2)'''

    return (((x-px)**2) + ((((a*(x**2)) + (b*x) + c) - py)**2)**0.5)
    

def get_color():
    '''This function creates and yields a list of colors'''
    for color in ['b', 'r', 'g', 'y', 'm', 'c']:
        yield color    

def data_analysis():
    data, test_case = import_data()

    print 'Please choose which type of analysis you would like to run.'
    print 'Enter 1 for Regression'

    

    #while (True)
    # try:
    choice = int(raw_input('> '))
    if choice not in [1]:
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
        except Exception:
            print 'Please enter a differnt name or enter "end".'
    
    base_column = str(base_column[0])
    ltitles = data.columns.tolist(); ltitles = ltitles[2:]; ltitles.remove(base_column)
    run_analysis(data, choice, base_column, ltitles, test_case)

def main():
    data_analysis()
    

#code execution begins and invokes main()
if __name__ == '__main__':
    main()