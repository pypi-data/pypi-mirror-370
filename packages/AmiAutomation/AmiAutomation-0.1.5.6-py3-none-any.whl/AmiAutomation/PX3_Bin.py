#Load dependencies
import sys
import clr
import os
import pandas
import datetime
import tempfile, shutil
from io import StringIO

sys.path.append(os.getcwd())

clr.AddReference("System.Windows.Forms")
clr.AddReference("DigitArcPX3.Tools.DataToPython")
from DigitArcPX3.Tools.DataToPython import *

def __getDfFromNET(args, verbose): 
    df_array = []
    program = Bin2Table()
    idx = 0
    # Uncomment for extra verbosity
    #if verbose:
    #    args.append('-v')
    for string in program.GetResults(args):
        if not(string):
            pass
        string2file = StringIO(string)
        df_array.append(pandas.read_csv(string2file,low_memory=False))
        df_array[-1].index = df_array[-1].index + idx
        idx += len(df_array[-1])
    del (program)

    if not(df_array):
        raise NameError("The binaries contained no information")

    if verbose:
        print (len(df_array), "files processed")

    df = pandas.concat(df_array, axis=0)

    return df

def file_to_df(path = '', file = '', start_date= datetime.datetime.now(), end_date = datetime.datetime.now(), verbose = False):
    """
    This function returns a single pandas dataframe containing extracted data from the provided
    file, path or path with constrained dates 
    """
    isPath = (path != '')
    isFile = (file != '')
    isDate = (start_date != end_date)
    isEndTimeGreater = (end_date-start_date) > datetime.timedelta(0)

    if isFile and isPath:
        raise NameError('Please provide a path or a file path, not both')
    if not(isFile) and not(isPath):
        raise NameError('Please provide a folder path or a file path')
    if isFile and isDate:
        raise NameError('Cannot provide a date for a single file')

    if isFile:
        if not(os.path.isfile(file)):
            raise NameError('Provided file path is not a file')
        if (os.path.splitext(file)[-1] != '.bin'):
            raise NameError('Provided file is not *.bin')
        args = ['-f',file]
        return __getDfFromNET(args, verbose)

    if isPath and not(isDate):
        if not(os.path.isdir(path)): 
            raise NameError('Provided path is invalid')
        args = ['-d',path]
        return __getDfFromNET(args, verbose)

    if not(isEndTimeGreater):
        raise NameError('End date must be greater than Start Date')
        
    listfiles= []
    for r, d, f in os.walk(path):
        for single_file in f:
            if single_file.endswith(".bin"):
                listfiles.append((r,single_file)) 

    if not(listfiles):
        raise NameError('No binaries where found on the provided folder')
    
    validFiles = []
    for (r,single_file) in listfiles:
        auxText=single_file.split("T", 1)
        year=int(auxText[0][0:4])
        month=int(auxText[0][4:6])
        day = int(auxText[0][6:8])
        hour = int(auxText[1][0:2])
        minute = int(auxText[1][2:4])
        second = int(auxText[1][4:6])
        dateOfFile = datetime.datetime(year,month,day,hour, minute, second)
        if start_date<=dateOfFile<=end_date:
            validFiles.append(os.path.join(r, single_file))
    
    if not(validFiles):
        raise NameError('No files matched the requested timespan')
    args = ['-f'] + validFiles
    
    return __getDfFromNET(args, verbose)

if __name__ == "__main__":

    print("This is a module")