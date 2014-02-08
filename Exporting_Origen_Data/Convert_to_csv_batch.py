#! /usr/bin/env python2.7.5

import csv
import os

ver = 3.0


def convert_to_csv():
	'''takes an .out file with specific type of output in it and takes a prespecified section 
	of it to output to a csv file.'''
	dcompiled = {}
	#creates a list to iterate through the 50 files
	for num in range(1,51):
		infile = open(str(num)+'.out', 'r')					#opens specified file.
		doutput = dict()
		filename = str(num)+'.out'

		#this is where you target the data you are interested in
		#change the string target to get different data.
		
		for line in infile:
			if 'nuclide   1.000E-03' in line:			#if the line includes the string 'nuclide   1.000E-03' the loop stops. This sets the placement for getting the wanted string in next section.
				break
		for line in infile:
			if '--------' in line:						#this line skips over an unwanted line
				continue
			if 'subtotal' in line:						#this line tells the for loop where to stop
				break
			loutput = line.split(' ')
			loutput = map(str.strip, loutput)
			loutput = filter(None, loutput)				#this removes all of the blank space from the list
			doutput[loutput[0]] = loutput[1]			#this creates a dictionary of all of the wanted information.
		infile.close()
		write_file(doutput, filename)
		
		dcompiled = compile_dictionary(doutput, dcompiled)
	write_file_compiled(dcompiled, 'compiled.out')


def write_file(doutput, filename):
	'''This function takes a dictionary as an input and creates a new csv file
	with the contents of the dictionary'''
	writer = csv.writer(open(filename[:len(filename)-4] + '_export.csv', 'wb'))			#this opens a new file to write in.
	for key, value in doutput.items():													#this loops through the dictionary and writes its contents.
		writer.writerow([key, value])
	print (filename[:len(filename)-4] + '_export.csv' + ' saved.')		

def write_file_compiled(doutput, filename):
	'''This function takes a dictionary as an input and creates a new csv file
	with the contents of the dictionary'''
	writer = csv.writer(open(filename[:len(filename)-4] + '_export.csv', 'wb'))			#this opens a new file to write in.
	for key, value in doutput.items():													#this loops through the dictionary and writes its contents.
		#writer.writerow([key, value])
		writer.writerow([key])
		for item in value:
			writer.writerow([item])
	print (filename[:len(filename)-4] + '_export.csv' + ' saved.')

def compile_dictionary(doutput, dcompiled):
	if 'pu238/pu239' in dcompiled:
		dcompiled['pu238/pu239'].append(float(doutput['pu238'])/float(doutput['pu239']))
	else:
		dcompiled['pu238/pu239'] = [(float(doutput['pu238'])/float(doutput['pu239']))]

	if 'pu240/pu239' in dcompiled:
		dcompiled['pu240/pu239'].append(float(doutput['pu240'])/float(doutput['pu239']))
	else:
		dcompiled['pu240/pu239'] = [(float(doutput['pu240'])/float(doutput['pu239']))]

	if 'pu241/pu239' in dcompiled:
		dcompiled['pu241/pu239'].append(float(doutput['pu241'])/float(doutput['pu239']))
	else:
		dcompiled['pu241/pu239'] = [(float(doutput['pu241'])/float(doutput['pu239']))]

	if 'pu242/pu239' in dcompiled:
		dcompiled['pu242/pu239'].append(float(doutput['pu242'])/float(doutput['pu239']))
	else:
		dcompiled['pu242/pu239'] = [(float(doutput['pu242'])/float(doutput['pu239']))]

	return dcompiled

def main():
	#while (True):
		#directory = raw_input('Enter the path of the directory your files are in: ')
		#try:
		#os.chdir(directory)
	convert_to_csv()
		#except Exception as e:
			#print (e)
			#print ('That path does not work, please try entering it again.')
    

#code execution begins and invokes main()
if __name__ == '__main__':
    main()
    
