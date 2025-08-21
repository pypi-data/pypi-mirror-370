import zlib, struct, os, io
import datetime as dt
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from collections import OrderedDict

class Properties:
    def Unserialize(bytesStream):
        
        properties = dict()
        
        version = bytesStream.read(1)[0]
            
        if version != 0:
            print ("Error unserializing properties, version " + str.from_bytes(version) + " is not supported")
            
        itemsCount = bytesStream.read(4)
        intItemsCount = int.from_bytes(itemsCount, "little")
        
        for items in range(intItemsCount): 
            
            strLen = bytesStream.read(1)[0]
            
            key = bytesStream.read(strLen).decode()
            
            dataTypeEnum = bytesStream.read(1)[0]
            
            value = _readTypeValue(dataTypeEnum, bytesStream)
                        
            properties[key] = value
            
        if 'Increment' in properties:
            properties['Increment'] = dt.timedelta(milliseconds = properties['Increment'] )
                
        return properties

class Binary:
    def __init__(self):
        self._header = FrameHeader("BLOB")
        self._buffer = []
        self._properties = dict()
    
    def Unserialize(self,bytesStream, oldSerialize):
        #Properties  
        self._properties = Properties.Unserialize(bytesStream)
        #Inner
        innerLength = struct.unpack('i', bytesStream.read(4))[0]            
        self._buffer = bytesStream.read(innerLength)

class Composite:
    def __init__(self):
        self._header = FrameHeader("CPST")
        self._frames = []
        self._hash = dict()
        self._properties = dict()
        
    def Unserialize(self,bytesStream, oldSerialize=True):
        if not oldSerialize:
            self._header.Unserialize(bytesStream)
            if self._header._version != 0:
                raise Exception (f"Error unserializing properties, version {self._header._version}, is not supported")
        
        #Properties  
        self._properties = Properties.Unserialize(bytesStream)
        #Inner
        count = struct.unpack("h", bytesStream.read(2))[0]      
        #Unserialize inner 
        for element in range(count):
            
            bag = Bag()
            
            if oldSerialize:
                contains = struct.unpack("?", bytesStream.read(1))[0]
                if contains:
                    strLen = bytesStream.read(1)[0]
                    bag.Key= bytesStream.read(strLen).decode()
                    self._hash[bag.Key] = bag
                    
            frameHeader = FrameHeader(None)
            frameHeader.Unserialize(bytesStream)
            frameBase = FrameBase(frameHeader._tag) 
            frameBase._header = frameHeader
            frameBase._baseframe.Unserialize(bytesStream, oldSerialize)
      
            bag._frame = frameBase
            self._frames.append(bag)   
            
        if not oldSerialize:
            count = struct.unpack("h", bytesStream.read(2))[0]
            for element in range(count):
                key = _readString(bytesStream)
                index = struct.unpack("h", bytesStream.read(2))[0]
                #Hash table section, skipping
        
class Table:
    def __init__(self):
        self._version = 0
        self._properties = dict()
        self._columns = None
        self._dataLines = []
        self._has_none = None
        
    def Unserialize(self, bytesStream, oldSerialize):
        self._version = bytesStream.read(1)[0]
        
        if self._version != 0:
            raise Exception("Error unserializing Table, unknown version")
            
        self._properties = Properties.Unserialize(bytesStream)
        self._columns = ColumnSet()
        self._columns.Unserialize(bytesStream)
        self._has_none = [False] * len(self._columns._columns)
        
        count = struct.unpack("h", bytesStream.read(2))[0]      
        for element in range(count):    
            dataLine = DataLine(self._columns)
            dataLine.Unserialize(bytesStream)
            self._has_none = [a or b for a,b in zip(self._has_none,dataLine._has_none)]
            self.Add(dataLine)
            
    def Add(self, dataLine):
        if self._columns == None or len(self._columns._columns) <= 0:
            raise Exception ("You can't add a data line to a table without first assigning a column to the table.")
            return
        self._dataLines.append(dataLine)
      
class ColumnSet:
    def __init__(self):
        self._columns = dict()
        
    def Unserialize(self,bytesStream):
        count = struct.unpack("h", bytesStream.read(2))[0]      
        for element in range(count):
            dtype = bytesStream.read(1)[0]
            strLen = bytesStream.read(1)[0]
            name = bytesStream.read(strLen).decode()
            # dataType, size = _getDatatype(dtype)
            
            self._columns[name] = Column(name,dtype)
            
class Column:
    def __init__(self,name,col_type):
        self._name = name
        self._type = col_type
        self._has_none = False

class DataLine:
    def __init__(self, columns):
        self._columns = columns
        self._dataLine = [None] * len(columns._columns)
        self._has_none = [False] * len(columns._columns);
        
    def Unserialize(self,bytesStream):
        count = _read7BitEncodedInt(bytesStream)
        missing_values = OrderedDict()
        num2 = 0
        for element in range(count):
            num3 = _read7BitEncodedInt(bytesStream)
            num2 += num3
            missing_values[num2] = num3 
            
        supportList = list(self._columns._columns.values())
        
        for element in range(len(self._columns._columns)):
            if element in missing_values:
                self._dataLine[element] = None
                self._has_none[element] = True
            else:
                self._dataLine[element] = _readTypeValue(supportList[element]._type, bytesStream)
                
class Collection:
    def __init__(self):
        self._header = FrameHeader("COLL")
        self._properties = dict()
        # self._arrayList = []  #key, type, value
        self._arrayList = dict()  #key, type, value

    def Unserialize(self, bytesStream, oldSerialize):
        if self._header._version != 0:
            raise Exception("Tag Version " , self._header._version , " is not supported" )
        self._properties = Properties.Unserialize(bytesStream)
        
        count = struct.unpack("h", bytesStream.read(2))[0]  

        for element in range(count):
            dtype = bytesStream.read(1)[0]
            key = _readString(bytesStream)
            # self._arrayList.append( Element(key,dtype) )
            self._arrayList[key]=dtype
            
        empty = OrderedDict()
        count = _read7BitEncodedInt(bytesStream)
        accum = 0
        
        for element in range(count):
            relative = _read7BitEncodedInt(bytesStream)
            accum += relative
            empty[accum] = relative
                
        keys = list(self._arrayList)
        for element in range(len(self._arrayList)):
            if element in empty:
                self._arrayList[keys[element]] = None
            else:
                self._arrayList[keys[element]] = _readTypeValue(self._arrayList[keys[element]],bytesStream)      
                
        # Add Loop type based on collection name
        if 'Name' in self._properties:
            if 'External' in self._properties['Name']:
                self._arrayList['Loop'] = 'External'
            else:
                self._arrayList['Loop'] = 'Internal'
                
class Bag:
    def __init__(self):
        self.Key = str()
        self._frame = None

class FrameHeader:
    def __init__(self, tag):
        self._version = 0;
        self._flags = 0;
        self._rawSize = 0;
        self._tag = tag; 
    
    def Unserialize(self, bytesStream):
        self._tag = bytesStream.read(4)
        self._version = bytesStream.read(1)[0]
        if self._version == b'\xFF':
            raise Exception("Corrupt header, invalid version.")
        self._flags = bytesStream.read(1)[0] & 0xF0 #Only read what I understand
        self._rawSize = struct.unpack("i", bytesStream.read(4))[0]
        if self._rawSize == 0:
            raise Exception("Corrupt header, tag size can't be zero.")
            
class FrameBase:
    def __init__(self, tagName):
        self._header = FrameHeader(tagName)
        if tagName == b'BLOB':
            self._baseframe = Binary()
        elif tagName == b'CPST':
            self._baseframe = Composite()
        elif tagName == b'STBL':
            self._baseframe = Table()
        elif tagName == b'COLL': 
            self._baseframe = Collection()
        else:
            raise Exception("Invalid tag", tagName, "for FrameBase")

class LogData:
    def __init__(self):
        self._fileName = str()
        self._fileType = 'bin'
        self.properties = None

def _getDatatype (dataTypeEnum):
    thisdict = {
    3: ("?",1), #bool
    4: ("c",1), #char
    5: ("b",1), #signed char (SByte)
    6: ("B",1), #unsigned char (Byte)
	7: ("h",2), #short (Int16)
	8: ("H",2), #unsigned short (UInt16)
	9: ("i",4), #int (Int32)
	10: ("I",4), #unsigned int (UInt32)
	11: ("q",8), #long long (Int64)
	12: ("Q",8), #unsigned long long (UInt64)
	13: ("f",4), #float (Single)
	14: ("d",8), #double (Double)
	15: ("d",16), #(Decimal) May not work
    16: ("D",8), #(DateTime) May not work
    18: ("s",1), #char[] (String) 
	19: ("Q",16), #(Guid) May not work
	20: ("p",1), #char [] (Binary)
    }
    return thisdict[dataTypeEnum]

def _getCDataType (dataTypeEnum):
    thisdict = {
        5:'SByte',
        6:'Byte',
        7:'Int16',
        8:'UInt16',
        9:'Int32',
        10:'UInt32',
        11:'Int64',
        12:'UInt64',
        4:'Char',
        13:'Single',
        14:'Double',
        3:'Boolean',
        15:'Decimal',
        16:'DateTime',
        }
    return thisdict[dataTypeEnum]

def _readTypeValue(dataTypeEnum, bytesStream):
    dataType, size = _getDatatype(dataTypeEnum)
    if dataType == "s":#string
        value = _readString(bytesStream)
    elif dataType == "D":#Datetime
        value = _readString(bytesStream)
        
        try:  # for .cpst
            value = dt.datetime.strptime(value, "%m-%d-%Y %H:%M:%S.%f")
        except:# for heatlogs
            decimals = value.split('.')[-1][0:5] #Remove trailing 0s
            value = value.split('.')[0] + '.' + decimals
            value = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    else:    
        value = struct.unpack(dataType, bytesStream.read(size))[0]
    return value

def _IntModeDivisor(mode):
    intMode = mode % 100
    switcher = {
        0: 100, #impedance
        1: 100, #current
        2: 100 #resistance
    }
    if intMode in switcher:
        return switcher[intMode]
    else:
        return 1
    
def _ExtModeDivisor(mode):
    extMode =mode / 100 
    switcher = {
        1: 100, #current
        2: 10, #voltage
        3: 10000, #PF
        4: 100, #MW
        5: 10 #RWI
    }
    if extMode in switcher:
        return switcher[extMode]
    else:
        return 1

def _RegModeDivisor(mode):
    div = _ExtModeDivisor(mode)
    if div ==1:
        return _IntModeDivisor(mode)
    else:
        return div

def _getDivisorsMatrix(divList, RegModeList):
    divMatrix = []
    for j,regMode in enumerate(RegModeList):
        divColumnReturn = _getDivisors(divList, regMode)
        divMatrix.append(divColumnReturn)
    return divMatrix

def _getDivisors(divList, regMode):
    divColumnReturn = []
    for i,div in enumerate(divList):
        if div<0:
            if (div == -1): #Int. mode
                divColumnReturn.append(_IntModeDivisor(regMode))
            elif (div == -2): #Ext. mode
                divColumnReturn.append(_ExtModeDivisor(regMode))
            elif (div== -3): #Int. or Ext. mode
                divColumnReturn.append(_RegModeDivisor(regMode))
        else:
            divColumnReturn.append(div)
    return divColumnReturn

def _read7BitEncodedInt(bytesStream):
    #https://docs.microsoft.com/en-us/openspecs/sharepoint_protocols/ms-spptc/1eeaf7cc-f60b-4144-aa12-4eb9f6e748d1?redirectedfrom=MSDN
    index = 0
    value = 0
    while True:
        length = bytesStream.read(1)[0]
        value |= (length & 0x7F) << (7*index)
        index += 1

        if length & 0x80 == 0: #Number complete
            break
    return value

def _readString(bytesStream):
    strLen = _read7BitEncodedInt(bytesStream)
    value = bytesStream.read(strLen).decode()  
    
    return value

def _processBag(definition, bag):
    
    if bag.Key != "RawData":
        root = ET.fromstring(bag._frame._baseframe._properties["Definition"])
    else:
        root = ET.fromstring(definition)  
    
    nodes = root.findall(".//object[@logged='y']/field")
    
    varNames = []
    trendsNames = []
    divisors = []
    fieldTypes = []
    
    listBitMapElement = []
    d_c = []
    
    for index, field in enumerate(nodes):
        fieldType = field.attrib['type']
        fieldTypes.append(fieldType if fieldType == "s" else None)
        if field.attrib['type'] == "s":
                        
            varName = field.text.strip()
            varNames.append(varName)
            if varName != "":
                trendsNames.append(varName)
                option = field.attrib['div']
                try:
                    divisor = float(option)
                    if divisor == 0:
                        divisor = 1
                except:
                    if option == 'I':
                        divisor = -1
                    elif option == "E":
                        divisor = -2
                    elif option == "I|E":
                        divisor = -3
                divisors.append(divisor)
                
        else:
            listBitMapElement.append(index)
            bit = 0
            for bits in field:
                bit += 1
                varNames.append(bits.text)
                if varNames[-1]:
                    trendsNames.append(varNames[-1])
                    divisors.append(1)
    
            d_c.append(bit)

    listOfSamples = []
    
    #Obtain stream data from InnerBuffer
    appendListOfSamples = listOfSamples.append
    
    bytesArray = bag._frame._baseframe._buffer
    bufferSize = len(bytesArray)
    
    dataArray = np.ndarray(shape=(int((bufferSize/2)/len(fieldTypes)),len(fieldTypes)), dtype='h', buffer=bytesArray)
    
    bitMapCount = 0    
    for i in range(len(dataArray[0,:])):
        if (bitMapCount < len(listBitMapElement)):
            if listBitMapElement[bitMapCount] == i:
                for bit in range(d_c[bitMapCount]):
                    series = dataArray[:,i] >> bit & 1
                    appendListOfSamples(series)
                bitMapCount+=1
                continue
        appendListOfSamples(dataArray[:,i])
        
    arraySamples = np.transpose(listOfSamples, axes=None)

    logData = LogData()
    logData._data = arraySamples
    logData._mainTrendsNames = trendsNames
    logData._mainDivisors = divisors
    
    return logData

def _processVersionN(version, composite, logData):
    """
    Unpacks binary file according to its properties

    Parameters
    ----------
    version : int
        binary version  
        
    composite : Composite
        Composite containing properties and frames
    
    Returns
    -------
    LogData
        Structure containing most file data

    """
    # utcStartTime = composite._properties['StartTime']
    # incrementMillisecs = composite._properties['Increment']
    # incrementTicks = incrementMillisecs * 10000.0
    # definition = composite._properties['Definition']
    
    root = ET.fromstring(composite._properties["Definition"])
    
    if version == 3: ##TODO: Use full definition instead of definition
        # root = ET.fromstring(composite._properties["FullDefinition"])
        nodes = root.findall(".//object[@logged='y']/field")
    elif version == 2:
        nodes = root.findall(".//object[@logged='y']/field")
    elif version == 1:
        nodes = root.findall("//object/field")
    else:
        print("Unknown packet version: ", version)
        
    varNames = []
    trendsNames = []
    divisors = []
    fieldTypes = []
    
    listBitMapElement = []
    d_c = []
    
    for index, field in enumerate(nodes):
        fieldType = field.attrib['type']
        fieldTypes.append(fieldType if fieldType == "s" else None)
        if field.attrib['type'] == "s":
                        
            varName = field.text.strip()
            varNames.append(varName)
            if varName != "":
                trendsNames.append(varName)
                option = field.attrib['div']
                try:
                    divisor = float(option)
                    if divisor == 0:
                        divisor = 1
                except:
                    if option == 'I':
                        divisor = -1
                    elif option == "E":
                        divisor = -2
                    elif option == "I|E":
                        divisor = -3
                divisors.append(divisor)
                
        else:
            listBitMapElement.append(index)
            bit = 0
            for bits in field:
                bit += 1
                varNames.append(bits.text)
                if varNames[-1]:
                    trendsNames.append(varNames[-1])
                    divisors.append(1)
    
            d_c.append(bit)

    listOfSamples = []
    
    #Obtain stream data from InnerBuffer
    appendListOfSamples = listOfSamples.append
    
    bytesArray = composite._hash["RawData"]._frame._baseframe._buffer
    bufferSize = len(composite._hash["RawData"]._frame._baseframe._buffer)
    
    dataArray = np.ndarray(shape=(int((bufferSize/2)/len(fieldTypes)),len(fieldTypes)), dtype='h', buffer=bytesArray)
    
    bitMapCount = 0    
    for i in range(len(dataArray[0,:])):
        if (bitMapCount < len(listBitMapElement)):
            if listBitMapElement[bitMapCount] == i:
                for bit in range(d_c[bitMapCount]):
                    series = dataArray[:,i] >> bit & 1
                    appendListOfSamples(series)
                bitMapCount+=1
                continue
        appendListOfSamples(dataArray[:,i])
        
    arraySamples = np.transpose(listOfSamples, axes=None)
    
    logData._data = arraySamples
    logData._mainTrendsNames = trendsNames
    logData._mainDivisors = divisors
    logData.properties = composite._properties
    
    return logData

def binStreamToDF(file, extension = 'bin', null_promoting={}):
    """
    Unpacks binary file stream into LogData
    
    Parameters
    ----------
    file : stream
        stream of binary file
       
    extension : str, optional
        read file extention, value must be "bin", "cpst" or "hist"
        default: bin
        
    null_promoting : dict
        A dictionary with a .NET Source Type key and a value of either one of 
        the following (default, object, float, Int64, string, error).

    Returns
    -------
    LogData
        Structure containing most file data

    """  
    
    # Validate extension
    accepted_extensions = ['bin','cpst','rph','hist']
    if extension not in accepted_extensions:
        raise Exception(f"Given extension \"{extension}\" is not a compatible extension")
    
    logData = LogData()
    logData._fileType = extension

    #header
    TAGS = file.read(4)
    if TAGS != b'TAGS':
        raise Exception("Missing TAGS header")
    versionHeader = file.read(1)
    if versionHeader == b'\xFF':
        raise Exception("Corrupt header, version can never reach 255")
    flags = file.read(1)
    if flags.hex() == '40':
        compressed = True
    else:
        compressed = False
    
    composite = Composite()

    if compressed:
        bytesArray = zlib.decompress(file.read())
    else:
        bytesArray = file.read()
    bytesStream = io.BytesIO(bytesArray)
        
    oldSerialize = (logData._fileType == 'bin' or logData._fileType == 'hist')
    
    composite.Unserialize(bytesStream, oldSerialize)
    
    if logData._fileType == 'bin':# HeatLogs    
        if 'Version' in composite._properties:
            if composite._properties['Version'] == 1:
                logData = _processVersionN(1, composite, logData)
            elif composite._properties['Version'] == 2:
                logData = _processVersionN(2, composite, logData)
            elif composite._properties['Version'] == 3:
                logData = _processVersionN(3, composite, logData)
            else:
                raise Exception("Unknown version")
        
        dFrame = pd.DataFrame(logData._data, columns=logData._mainTrendsNames )
    
        step = np.arange(start = 0, stop=len(logData._data), step=1, dtype=np.int16)
        listOfTimeStamps = logData.properties['StartTime']+logData.properties['Increment']*pd.Series(step)
        
        countRegModes = len(dFrame["RegStatus.RegulationMode"].unique())

        try:
            #We can optimize, there is only one regulation mode
            if(countRegModes==1):
                regMode = dFrame["RegStatus.RegulationMode"][0]
                divColumns = _getDivisors(logData._mainDivisors,regMode)
                logData.dataFrame = dFrame.div(divColumns, axis='columns')
            else:
                divColumns = _getDivisorsMatrix(logData._mainDivisors,dFrame["RegStatus.RegulationMode"])
                #divColumns(NxM) and dFrame(NxM)
                divisorsDF =  pd.DataFrame(divColumns, columns=dFrame.columns)
                logData.dataFrame = dFrame/divisorsDF
        except:
            divColumns = logData._mainDivisors
            logData.dataFrame = dFrame.div(divColumns, axis='columns')        

        del logData._data
        
        logData.dataFrame.insert(0,"Timestamp", listOfTimeStamps)
        # logData.dataFrame.set_index("Timestamp",inplace=True)
            
        return logData

    elif logData._fileType == 'cpst': # cpst

        # Get elements, convert tables to dataframe
        for bag in composite._frames:
            frame = bag._frame
            if frame._header._tag == b'STBL':
                # Retrieve datalines
                data = []
                for dataline in frame._baseframe._dataLines:
                    data.append(dataline._dataLine)
                    
                if any(frame._baseframe._has_none): ##Null handling
                    #Transpose data array
                    data = list(map(list, zip(*data)))
                    series = []
                    dFrame = pd.DataFrame()
                    #Iterate through columns and handle null values accordingly
                    for col,has_none,col_data in zip(frame._baseframe._columns._columns.values(),frame._baseframe._has_none,data ):
                        #Create a pandas series for each column
                        if (has_none):
                            # Lookup desired handling
                            type_str = _getCDataType(col._type)
                            if type_str in null_promoting:
                                desired_type = null_promoting[type_str]
                            else:
                                series.append(pd.Series(col_data, name=col._name))
                                continue;
                                
                            if desired_type == 'default':
                                series.append(pd.Series(col_data, name=col._name))
                            elif desired_type == 'error':
                                raise Exception(F"Null values encountered in column {col._name} of type {type_str}")
                            else:
                                series.append(pd.Series(col_data, name=col._name, dtype=desired_type))
                        else:     
                            series.append(pd.Series(col_data, name=col._name))
                        
                    dFrame = pd.concat(series, axis=1)
                
                else: #Default dataframe construction
                    dFrame = pd.DataFrame(data, columns=frame._baseframe._columns._columns.keys())
                    
                logData.dataFrame = dFrame
                logData.properties = frame._baseframe._properties
                
        return logData
                    
    elif logData._fileType == 'hist': #hist
        logData.properties = composite._properties
        
        coll_properties = []
        
        for bag in composite._hash.values():
            if 'Count' in bag._frame._baseframe._properties:
                coll_properties.append(bag._frame._baseframe._properties)
        
        logData.collections = pd.DataFrame(coll_properties).set_index('Name')
        series = []
        #Get into collections
        for frame in composite._frames:
            frame_name = frame.Key
            
            series = series + getCollection(frame, frame_name)
            
        logData.dataFrame = pd.DataFrame(series)
        
        return logData
    else:
        print ("unknown extension, returning composite")
        return composite
        
def getCollection(frame, name):
    series = []
    for inner_frame in frame._frame._baseframe._frames:
        if inner_frame._frame._header._tag == b'COLL':            
            
            serie = pd.Series(data=inner_frame._frame._baseframe._arrayList,name = str(name + '_' + inner_frame.Key ))
            
            series = series + [serie]

        else:       
            next_frame = inner_frame
            if next_frame.Key != '':
                new_name = str(name + '_' + next_frame.Key)
            else:
                new_name = name
            
            series = series + getCollection(next_frame, new_name)
            
    return series
        
def binFileToDF(path, extension=None, null_promoting={}):
    """
    Unpacks binary file into LogData
    
    Parameters
    ----------
    path : str
        Complete file path
        
    extension : str, optional
        Read file extention, value must be "bin", "cpst" or "hist".
        If no value is given, it will be infered from the file name
        default: bin
        
    null_promoting : dict
        A dictionary with a .NET Source Type key and a value of either one of 
        the following (default, object, float, Int64, string, error).\n
        
        The possible dictionary keys are the .NET simple types:
            * SByte
            * Byte
            * Int16
            * UInt16
            * Int32
            * UInt32
            * Int64
            * UInt64
            * Char
            * Single
            * Double
            * Boolean
            * Decimal
            * DateTime
            
        This dictionary values determines how null values in deserialization affect 
        the resulting LogData dataframe column:
            
            * default: use pandas automatic inference when dealing with null values on a column
            * object: The returned type is the generic python object type
            * float: The returned type is the python float type
            * Int64: The returned type is the pandas Nullable Integer Int64 type
            * string: Values are returned as strings
            * error: Raises and exception when null values are encountered 
            
    Returns
    -------
    LogData
        Structure containing most file data

    """
    _, file_extension = os.path.splitext(path)
      
    if extension == None:
        if '.' not in file_extension:
            print("Warning, unidentified file extension, assuming .bin")
            file_extension = '.bin'
            
        extension = file_extension.strip('.')
        
    file = open(path, "rb")
      
    try:
        logData = binStreamToDF(file, extension, null_promoting)
    except Exception as ex:
        raise Exception(f"Failed to process file {path}") from ex
        
    logData._fileName = os.path.basename(path)
    
    file.close()
    return logData    