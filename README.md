Nuclear_Forensics_Cluster_Analysis
==================================

DOCUMENTATION

This program was created to predict what type of Nuclear Reactor an unknown nuclear fuel sample is from.
It does this by taking a set of know fuel samples from a variety of different reactors and comparing the
pu isotopic ratios of the samples. Using one of the isotopes as a baseline (pu239) of the ratio.

The program takes an excel sheet of the known fuel sample ratios and unknown fuel sample ratios as its
input where the known samples are sorted by reactor. The program does a polynomial regression on each
of each reactors set of fuel samples for each of the different combinations of pu ratios. It also finds
the distance between the curve and the unknown fuel sample.

The program outputs a graph for each ratio comparison with all the reactor fuel sample set regression
lines and the unknown sample point. It also has a line between the unknown point and the closest
reactor curve.

TUTORIAL

1. Check the Requirements.txt and make sure you have all the dependencies installed.

2. Create your excel file. The file must have a certain format.
    1. Do not change the names of the sheet tabs. Keep them named Sheet1 and Sheet2
    2. On Sheet1 put all of your known data. 
        1. The first column should be labeled "reactor". Under this put the name of the reactor
        next to every sample.
        2. The second column should be named "enrichment". You can leave this blank for now.
        This will be used if you plan on doing other analysis but the column needs to be there
        for the script to work properly.
        3. Each column from 3 on should have the name of the ratio and then the data. The name
        should be formatted like this: pu238/pu239.
    3. On Sheet2 put the unknown sample data. In the first column and each following column you need
    the name of the ratio and then the data. The name should be formatted like this: pu238/pu239.

3. Run the program. It will prompt you for the name of the excel file you want to analyze.
If the file is not in your current directory it will prompt you to enter the path to 
the file you want to analyze.

4.The program will then ask you what ratio you would like to use as the base ratio. This means
that the program will use that ratio for the X-axis for all of your comparisons and graphs.

5. The program will then run the analysis, print a dictionary of the reactor ratio combinations
and their corresponding distance to the unknown sample, and save an image of each graph in the 
current directory.
