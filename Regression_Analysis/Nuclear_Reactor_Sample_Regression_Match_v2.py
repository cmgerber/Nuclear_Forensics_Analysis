#! /usr/bin/env/python

__author__ = 'Colin Gerber'
__python_version__ = '2.7.5'

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas
from copy import deepcopy
import shapely.geometry as geom

ver = 2.0

def import_data():
    '''This function takes in data from a .csv and stores it in a pandas
    dataframe. The file must be a .xls or xls.'''

    # while (True):
    #     try:
    #         file_name = raw_input('What is the excel file name you would like to use? ')
    #         data = pandas.read_excel(file_name, 'Sheet1')
    #         test_case = pandas.read_excel(file_name, 'Sheet2')
    #         break
    #     except Exception as e:
    #         print e
    #         print 'The file you entered does not exist in the directory.'
    #         file_path = raw_input('Please enter the path to your file (or enter "try" to retype the file name): ')
    #         if file_path.lower() == 'try':
    #             pass
    #         else:
    #             os.chdir(file_path)

    data = pandas.read_excel('VVER_RBMK_BWR_generated.xlsx', 'Sheet1')
    test_case = pandas.read_excel('VVER_RBMK_BWR_generated.xlsx', 'Sheet2')
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
    
    for current_name in ltitles:
        color = get_color()
        for i, group in data.groupby('reactor'):
            x = group[base_column]
            y = group[current_name]

            #this checks if there is a (0,0) point in the data, if there is not one
            #it will append one to the data so that the regression lines have a y intercept
            #of 0.
            if 0 not in x and 0 not in y:
                x.append(0)
                y.append(0)
                print zip(x,y)
                print 'appended'
            
            reactor_name.append(i)
            new_color = next(color)

            #this calculates the distance of the unknown point to the curve of 
            #each reactor.
            coords = zip(x,y)
            line = geom.LineString(coords)
            unknown_samples = zip(test_case[base_column],test_case[current_name])
            point = geom.Point(unknown_samples)
            

            

            p = np.poly1d(np.polyfit(x,y, 2))            
            print '%s: %s vs. %s \n \n \n ' % (i, current_name, base_column), p, '\n \n \n'
            
            #get the coefficients of the polyfit line 
            coef = p.c

            #using the coefficients and unknown value calculates the distance from the regression
            #line to the unknown point.
            px = unknown_samples[0]; py = unknown_samples[1]; x = 1; a = p.c[1]; b = p.c[0]; c = p.c[2]
            d = math.sqrt((px-(a*x))**2 + (py-(b*x)**2-2)**2)
            print 'distance from %s:' % (i), d

            #creates a dictionary containing the distance from the unknown point to all the regression lines
            if current_name not in regression_dist_dict:regression_dist_dict[current_name] = []
            regression_dist_dict[current_name].append((i, d))

            
            #this creates a graph for each regression
            xp = np.linspace(0, 1.2, 100)
            plt.plot(x, y, '.', c = new_color, label = i)
            plt.plot(xp, p(xp), '-', c = new_color)
            plt.ylim(-.1,.5)
            plt.ylabel(current_name); plt.xlabel(base_column)

            #finds the closest curve for the current pu ratios and
            #then plots the unknown point with a line connecting it to the curve.
            for ratio in regression_dist_dict[current_name]:
                if ratio[1] < min_dist[1]: 
                    min_dist = ratio
                    plot_line = line


        temp_df = data[data['reactor'] == ratio[0]]
        line = geom.LineString(zip(temp_df[base_column], temp_df[current_name]))

        #plots the unknown point and a line connecting it to the curve.
        point_on_line = plot_line.interpolate(plot_line.project(point))
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