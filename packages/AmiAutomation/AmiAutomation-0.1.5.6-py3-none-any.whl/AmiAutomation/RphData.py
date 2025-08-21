import struct
import io
import os
from datetime import datetime,timedelta,timezone
import pandas as pd


def readString(bytesStream):
    strLen = bytesStream.read(1)[0]
    
    if strLen < 255:
        string = bytesStream.read(strLen).decode()  
    else:
        strLen = struct.unpack("H", bytesStream.read(2))[0]  
        if strLen < 0xfffe:
            string = bytesStream.read(strLen).decode() 
        else:
            strLen = struct.unpack("I", bytesStream.read(4))[0] 
            string = bytesStream.read(strLen).decode() 
            
    return string

class RphData:
    def __init__(self):
        self._fileName = str()
        self._fileType = 'rph'
        self.properties = None

def readStringPython(bytesStream):
    length = int.from_bytes(bytesStream.read(2), "little", signed = False)
    # return bytesStream.unpack(str(length) + 's', length)
    return bytesStream.read(length).decode() 

def rphToDf(path):
    """
    Unpacks rph file into a dataframe
    
    Parameters
    ----------
    path : str
        Complete file path
        
    Returns
    -------
    RphData
        Structure containing most useful data

    """
    
    file = open(path, "rb")
    bytesArray = file.read()
    bytesStream = io.BytesIO(bytesArray)
    
    trends_names = []
    values = []
    timestamps = []
    properties = dict()
    
    properties['MagicNumber'] = int.from_bytes(bytesStream.read(4), "little", signed = False)
    properties['ArchiveType'] = int.from_bytes(bytesStream.read(4), "little", signed = False)
    properties['StartTotalSeconds'] = int.from_bytes(bytesStream.read(4), "little", signed = False)
    properties['EndTotalSeconds'] = int.from_bytes(bytesStream.read(4), "little", signed = False)
    properties['TimeScan'] = int.from_bytes(bytesStream.read(4), "little", signed = False)

## custom read

    properties['Source'] = readString(bytesStream) ### Different reading

    number_of_trends = int.from_bytes(bytesStream.read(2), "little", signed = False)
    
    for trend in range(number_of_trends):
        trends_names.append(readString(bytesStream))

    number_of_samples = int.from_bytes(bytesStream.read(4), "little", signed = False)
    
    for sample in range(number_of_samples):
        num = struct.unpack("H", bytesStream.read(2))[0] #trends
        
        row = []

        for element in range(num):
            row.append(struct.unpack("f", bytesStream.read(4))[0])
            
        values.append(row)
        
    time_stamp_count = int.from_bytes(bytesStream.read(2), "little", signed = False)
        
    if number_of_samples > 65535:
        time_stamp_count =  int.from_bytes(bytesStream.read(4), "little", signed = False)
    
    for timestamp in range(time_stamp_count):
        total_seconds = int.from_bytes(bytesStream.read(4), "little", signed = False)
        milliseconds = int.from_bytes(bytesStream.read(2), "little", signed = False)
        minutesFromUTC0 = int.from_bytes(bytesStream.read(2), "little", signed = True) 
        IsDaylightSavingTime = int.from_bytes(bytesStream.read(2), "little", signed = True) 
        dummy = bytesStream.read(2)
        daylightHours = 1 if IsDaylightSavingTime > 0 else  0
        tzinfo = timezone(offset=timedelta(minutes=-minutesFromUTC0, hours=daylightHours))
        dt = datetime.fromtimestamp(total_seconds, tz= tzinfo)        
        dt += timedelta(milliseconds=milliseconds)
        timestamps.append(dt)
            
    totals = int.from_bytes(bytesStream.read(4), "little", signed = True)
    
    dFrame = pd.DataFrame(values, columns=trends_names)
    dFrame.insert(0,"Timestamp", timestamps)
    
    data = RphData()
    data._fileName = os.path.basename(path)
    data.dataFrame = dFrame
    data.properties = properties
    return data