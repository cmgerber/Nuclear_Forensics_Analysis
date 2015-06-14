#! /usr/bin/env/python

__author__ = 'Colin Gerber'
__python_version__ = '2.7.5'

import sys
import math
import os
from copy import deepcopy
from scipy.optimize import fmin
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import ExcelWriter
import scipy.optimize as optimize

ver = 2.0


def regression(data, ltitles, test_case):
    '''This function does a polynomial regression on each of the reactor ratio pairs
    and then finds the distance from each curve to the unkown sample provided.
    It also plots all of the results and saves them to .png files.'''

    x = []; y = []
    reactor_name = []
    regression_dist_dict = {}
    closest_curve_dict = {}
    react_len = 0

    #counter for new file name for each sample
    name_counter = 0

    #iterate through each unknown sample
    for ix, unknown in test_case.iterrows():
        #update name counter for next sample
        name_counter += 1
        title_tracker = deepcopy(ltitles)

        #iterate through each ratio and compare it to the baseline ratio
        for current_name in title_tracker:
            title_tracker.remove(current_name)
            if len(title_tracker) == 0:
                break
            for base_column in title_tracker:
                color = get_color()
                graph_name = base_column + '/' + current_name

                #set min distance variable for keeping track of the closest curve
                min_dist = ('temp', 'temp', 1000)

                #initiate plot
                fig = plt.figure(figsize=(10, 6))
                ax = fig.add_subplot(111)

                reactor_tracker = []
                for i, group in data.groupby(['reactor', 'enrichment']):
                    #creates list of reactors that have been iterated through
                    if i[0] not in reactor_name:
                        reactor_name.append(i[0])

                    #only calls new color when the iteration reaches a new reactor
                    if react_len != len(reactor_name):
                        #calls next color to be used in graphing. One for each reactor.
                        new_color = next(color)
                    react_len = len(reactor_name)

                    x = list(group[current_name])
                    y = list(group[base_column])
                    unknown_sample = [unknown[current_name], unknown[base_column]]

                    #linespace
                    xp = np.linspace(min(x), max(x), 100)
                    #creates the regression line
                    #old
                    p = np.poly1d(np.polyfit(x,y, 2))

                    # def mod_quadratic(x, a, b, c):
                    #     return a*x**2 + b*x + c

                    # # Fit an exponential
                    # popt, pcov = optimize.curve_fit(mod_quadratic, x, y)
                    # p= mod_quadratic(xp, *popt)
                    # a, b, c = popt[0], popt[1], popt[2]

                    #Force o y-intercept
                    # x = np.asarray(x)
                    # coeff = np.transpose([x*x, x])
                    # ((a, b), _, _, _) = np.linalg.lstsq(coeff, y)
                    # p = np.poly1d([a, b, 0])
                    print '%s enrich: %s: %s vs. %s ' % (i[0], i[1], current_name, base_column)
                    print p

                    #using the coefficients and unknown value calculates the distance from the regression
                    #line to the unknown point.
                    px = unknown_sample[0]; py = unknown_sample[1]; a = p.c[0]; b = p.c[1]; c = p.c[2]
                    print px, py, a, b, c

                    #finds the minimum value of the distance function
                    funct_min_x = fmin(my_distance_formula, 0, args=(px, py, a, b, c))
                    d = my_distance_formula(funct_min_x[0], px, py, a, b, c)
                    print 'distance from %s enrich: %s:' % (i[0], i[1]), d, '\n \n \n'

                    #finds the y value of the min point on the curve
                    funct_min_y = my_curve(funct_min_x, a, b, c)

                    #creates a dictionary containing the distance from the unknown point to all the regression lines
                    if graph_name not in regression_dist_dict:
                        regression_dist_dict[graph_name] = []
                    regression_dist_dict[graph_name].append([i[0], i[1], d])

                    #this creates a graph for each regression
                    #change axis range with np.linespace below

                    #ax.plot(x, y, '.', c=new_color, label='%s: %s' % (i[0], i[1]))
                    if i[0] not in reactor_tracker:
                        ax.plot(x, y, '.', c=new_color, label='%s' % (i[0]))
                        reactor_tracker.append(i[0])
                    else:
                        ax.plot(x, y, '.', c=new_color)

                    ax.plot(xp, p(xp), '-', c=new_color)
                    #ax.plot(xp, p, '-', c=new_color)
                    #plt.ylim(-.1, .5)
                    plt.ylabel(base_column); plt.xlabel(current_name)

                    #finds the closest curve for the current pu ratios and
                    #then plots the unknown point and the curve highlighted in red.
                    for ratio in regression_dist_dict[graph_name]:
                        if ratio[2] < min_dist[2]:
                            min_dist = ratio
                            closest_curve_values = [i[0], i[1], d]
                            line_equation = p
                            new_line_space = xp

                closest_curve_dict[graph_name] = closest_curve_values

                #plots the unknown sample
                #ax.plot(unknown_sample[0], unknown_sample[1], color=next(color), marker='o', label='Uknown Sample')

                #plots the closest curve and highlights it by having it red and thicker.
                #ax.plot(new_line_space, line_equation(new_line_space), '-', c='r', lw=3.0, label='%s: %s - closest' % (closest_curve_values[0], closest_curve_values[1]))
                #ax.plot(new_line_space, line_equation, '-', c='r', lw=3.0, label='%s: %s - closest' % (closest_curve_values[0], closest_curve_values[1]))

                plt.title('%s: %s vs. %s' % (', '.join(map(str, reactor_name)), current_name, base_column))
                ax.set_position([0.1, 0.1, 0.5, 0.8])
                L = ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
                #saves the current plot to a temp variable so it can save plot to file after show()
                temp_plot = plt.gcf()

                #comment below in if you want each graph to pop up when you run the script
                # plt.show()

                #create file name addtion
                name_add = 'sample_%d' % (name_counter)

                saveitem = current_name.replace('/', '')
                savebase_column = base_column.replace('/', '')
                #saves plot to .png file
                temp_plot.savefig('data/%s%s%s_regression_%s.png' % (''.join(map(str, reactor_name)), saveitem, savebase_column, name_add))
                asdfs
                #saving the reactor list for naming of the output
                reactors = deepcopy(reactor_name)
                del reactor_name[:]
        create_output(regression_dist_dict, closest_curve_dict, reactors, name_add)
        regression_dist_dict.clear()
        closest_curve_dict.clear()


def my_curve(x, a, b, c):
    return (a*x)**2 + (b*x) + c


def my_distance_formula(x, px, py, a, b, c):
    '''Creates the formula for finding the distance from the uknown point to the curve
    Ie. Sqrt((x-x0)**2 + (y-y0)**2)'''

    return (((x-px)**2) + ((((a*(x**2)) + (b*x) + c) - py)**2)**0.5)


def get_color():
    '''This function creates and yields a list of colors'''
    for color in ['b', 'g', 'y', 'm', 'c', 'k']:
        yield color


def create_output(regression_dist_dict, closest_curve_dict, reactor_name, name_add):
    '''Converts the dictionaries into dataframes to format for saving as
    an excel. The total resutls on the first sheet and closest curves on the second'''

    #creates a dataframe by looping through the dict and appending the df's together.
    count = 0
    print regression_dist_dict
    for key in regression_dist_dict:
        if count == 0:
            total_results = pd.DataFrame(regression_dist_dict[key], index=[key]*len(regression_dist_dict[key]), columns=['reactor', 'enrichment', 'distance'])
            closest_results = pd.DataFrame([closest_curve_dict[key]], index=[key], columns=['reactor', 'enrichment', 'distance'])
            count += 1
        else:
            total_results = total_results.append(pd.DataFrame(regression_dist_dict[key], index=[key]*len(regression_dist_dict[key]), columns=['reactor', 'enrichment', 'distance']))
            closest_results = closest_results.append(pd.DataFrame([closest_curve_dict[key]], index=[key], columns=['reactor', 'enrichment', 'distance']))

    print 'total_results', total_results
    print 'closest_results', closest_results

    file_name = 'data/%s_regression_results_%s.xlsx' % ('_'.join(map(str, reactor_name)), name_add)

    writer = ExcelWriter(file_name)

    total_results.to_excel(writer, sheet_name='Sheet1')
    closest_results.to_excel(writer, sheet_name='Sheet2')
    writer.save()


def data_analysis(in_data, in_test_data):
    data = in_data
    test_case = in_test_data


    ltitles = data.columns.tolist(); ltitles = ltitles[2:];
    regression(data, ltitles, test_case)


def main():
    data_analysis()


#code execution begins and invokes main()
if __name__ == '__main__':
    main()
