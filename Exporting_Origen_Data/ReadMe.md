Exporting Origen Data
==================================

DOCUMENTATION

This is a series of programs, one python file (.py) and two ipython notebooks (.ipynb) which will help you export data from Origen (which exports .out files) and convert them into one final summary excel file which can be used to analyze the data.

TUTORIAL

1. Put a copy of Convert_to_csv_batch.py into the folder of .out files you want to extract data from.

2. You may have to make a few small changes to the file depending on what data you are trying to extract.
    
    1. Check the range in the first for loop. The second number (the larger one) should be equal to one more than the amount of out files you have in the directory.

    2. The out files should be named '1.out', '2.out' ect... (this is the normal file naming output for Origen). If they are not you will have to tweek the first for loop to fit the file names you have.

    3. The next to for loops are responsible for finding the data in the ,out file by looking for a combination of keywords that only occur around the data. If you want to target different data then the pu238 - pu242 data then you will have to change the strings the program is looking for to match the lines before and after the data you want to extract.

    4. If you are changing the target data then you will also have to change the target strings in the compile_dictionary function to reflect the data you are intending to pull out.

3. After you make the necessary change run the program and it will output a csv for each .out file and then a compiled file that combined the ratios from all the .out files.

4. Repeat the steps above in each of the .out directories (ie. each enrichment output would be a different directory) for your reactor type and then run the [Combining CSV's.ipynb notebook]("http://nbviewer.ipython.org/urls/raw.githubusercontent.com/cmgerber/Nuclear_Forensics_Cluster_Analysis/master/Exporting_Origen_Data/Combining_CSVs.ipynb?create=1) to combine all of the compiled csv's into an excel.  The notebook has instructions in it. You will need ipython to run the notebook.

5. Once you reapeat this process for all of the reactor types you plan to export from Origen you can run the [Combining_Excel.ipynb notebook](https://raw.githubusercontent.com/cmgerber/Nuclear_Forensics_Cluster_Analysis/master/Exporting_Origen_Data/Combining_Excel.ipynb) to combine all of the excel files you created into one summary excel file. You can then use this excel file for analysis.
