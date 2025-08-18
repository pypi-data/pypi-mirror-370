from Albion import AbGis, Adb
import numpy as np
from enum import Enum
import pandas as pd
import os
import geopandas  as gpd
from shapely import wkt
from io import BytesIO
from PIL import Image

class AdbFieldType(Enum):
    AdbFTNull = 0
    AdbFTBool = 1
    AdbFTInt32 = 2
    AdbFTInt64 = 3
    AdbFTDouble = 4
    AdbFTText = 5
    AdbFTDate = 6
    AdbFTGuid = 7
    AdbFTTime = 8
    AdbFTBin = 9
    AdbFTGeomBEGIN = 32
    AdbFTGeomPoint = AdbFTGeomBEGIN
    AdbFTGeomMultiPoint = 33
    AdbFTGeomPolyline = 34
    AdbFTGeomPolygon = 35
    AdbFTGeomEND = 36
    
class SelectionTypes(Enum):
    AbSetCombineUnion = 0 #			  // (A U B) (Union)
    AbSetCombineSubtractAB = 1 #		// (A - B)
    AbSetCombineSubtractBA = 2 #		// (B - A)
    AbSetCombineIntersect = 3 #		// (A x B) (In both)
    AbSetCombineDifference = 4 #	// (A U B) - (A x B)  aka  Union - Intersection
    AbSetCombineA = 5 #				    // A
    AbSetCombineB = 6 #				    // B
    AbSetCombineEND = 7 #

# Define a new class
class AbTable:
    # Constructor
    def __init__(self, tablename=None, index=None):
        # Init member variables and other stuff
        if tablename is not None:
            self.name = tablename
            self.table = AbGis.GetTableFromTableName(tablename)
            self.layer = None
            
        if index is not None:
            self.table = AbGis.GetTableFromLayerIndex(index)
            #self.layer = AbGis.GetLayerFromIndex(index)
            self.name = AbGis.GetFullLayerNameFromIndex(index)
            self.layer = None
        
    # called in print(obj)
    def __repr__(self):  
        if self.layer is None:
            return "Table: " + self.name + " - Record Count: " + str(self.RecordCount())
    
    def Table(self):
        return self.table
    
    def Exists(self):
        if self.RecordCount == -1:
            return False
        else:
            return True
        
    # Member function/method
    def Name(self):
        return Adb.Name(self.table)    
    
    def GetFieldList(self):
        return Adb.GetFieldList(self.table)
    
    def GetFieldIndex(self, iFieldName):
        fields = Adb.GetFieldList(self.table)    
        # If the field does not exist, exit
        if fields.count(iFieldName) == 0: 
            print(iFieldName + ' not found')
            return -1            
        return Adb.FieldIndex(self.table, iFieldName) 
    
    def IsRecordAlive(self, iRec):
        if iRec < 0:
            return False
        return Adb.IsRecordAlive(self.table, iRec)
    
    def GetData(self, iField, iRec):
        if iField == -1:
            return False
        if iRec < 0:
            return False
        return Adb.Data_Get(self.table, iField, iRec)
    
    def GetDataArray(self, iFieldName):
        field = self.GetFieldIndex(iFieldName)
        if field == -1:
            return None
        return Adb.Data_Get_Array(self.table, field)
    
    def GetDataFrame(self, arrayoffields):
        data = {}
        for column in arrayoffields:
            if self.GetFieldIndex(column) != -1:
                array = self.GetDataArray(column)
                if isinstance(array, (list, np.ndarray)):
                    #print("my_var is either a list or numpy array")
                    data[column] = self.GetDataArray(column)
                else:
                    print("my_var is neither a list nor a numpy array")
        return pd.DataFrame(data)
    
    def GetGeoDataFrame(self, arrayoffields) -> gpd.GeoDataFrame: 
        # Check if the field is already in the list, if not, add it
        if 'Geometry' not in arrayoffields:
            arrayoffields.append('Geometry')
        data = self.GetDataFrame(arrayoffields)
        
        # Check if 'Geometry' column exists in the DataFrame
        if 'Geometry' in data.columns:
            # Convert all WKT records in the 'Geometry' column to Shapely geometries
            data['Geometry'] = data['Geometry'].apply(wkt.loads)
     
        return gpd.GeoDataFrame(data, geometry='Geometry')
        
    def SetDataFrame(self, df):
        #self.BeginTransaction()
        for column in df:
            print(column)
            fld = self.GetFieldIndex(column)
            
            arr = df[column]
            
            print(arr)
            for rec in range(self.RecordCount):
                if self.IsRecordAlive(rec):
                    self.SetData(fld, rec, arr[rec])
                    
        #self.CommitTransaction()
                 
    
    def UpdateDataArray(self, iFieldName, dataarray):
        field = self.GetFieldIndex(iFieldName)
        if field == -1:
            print(iFieldName + ' does not exist')
            return None
        
        self.BeginTransaction()
        try:   
            self.LockForWrite()         
            for i in range(self.RecordCount()):
                self.SetData(field, i, dataarray[i])
        except:
            print('Error while performing UpdateDataArray')
        finally:
            self.CommitTransaction()
            print(self.Name() + ': ' + iFieldName + ' updated.')
        
    
    def SetData(self, iField, iRec, iData):
        if iField == -1:
            return False
        if iRec < 0:
            return False
        
        try:
            Adb.Data_Set(self.table, iField, iRec, iData)
        except:
            print('Failure to set Field: ' + str(iField) + ' Record: ' + str(iRec) + ' Data: ' + str(iData))
            return False
        
    def GetWkt(self, iField, iRec):
        if iField == -1:
            return False
        if iRec < 0:
            return False
        
        return Adb.Data_Get_Wkt(self.table, iField, iRec)
        
    def SetWkt(self, iField, iRec, iWkt):
        if iField == -1:
            return False
        if iRec < 0:
            return False
        
        try:
            return Adb.Data_SetWkt(self.table, iField, iRec, iWkt)
        except:
            print('Failure to set Field: ' + str(iField) + ' Record: ' + str(iRec) + ' Data: ' + str(iWkt))
            return False
        
    def Data_SetLineSegment(self, iField, iRec, x1,y1,x2,y2):
        if iField == -1:
            return False
        if iRec < 0:
            return False
        
        try:
            Adb.Data_SetSegment(self.table, iField, iRec, x1,y1,x2,y2)
        except:
            print('Failure to set Field: ' + str(iField) + ' Record: ' + str(iRec))
            return False
        
    
    def AddRecord(self):
        return Adb.AddRecord(self.table)
    
    def AddField(self, iName, iType: AdbFieldType):
        return Adb.AddField(self.table, iName, iType.value)
    
    def QuerySqlWhere(self, iWhereClause):
        Adb.QuerySqlWhere(self.table, iWhereClause)
        
    def RecordCount(self):
        return Adb.RecordCount(self.table)
    
    def BeginTransaction(self):
        Adb.BeginTransaction(self.table)
    
    def CommitTransaction(self):
        Adb.CommitTransaction(self.table)
    
    def LockForWrite(self):
        Adb.LockForWrite(self.table)
    
    def RefreshLayer(self):
        AbGis.RefreshLayer(self.layer)
        
    def ZoomTo(self):
        AbGis.ZoomToLayerIndex(self.index)
        
    def CurrentSelection(self): 
        return AbGis.GetCurrentSelection(self.table)

    def SetSelection(self, records, iAdd=False,iSelType=SelectionTypes.AbSetCombineUnion,iZoomTo=False):
        AbGis.SetCurrentSelection(self.table, records, iAdd, iSelType.value, iZoomTo)

def ClearSelection():
    AbGis.ClearSelection()

def GetCADWindowScreenshot():
    bmp_bytes = bytes(AbGis.GetBitmap())  # Convert to actual bytes
    return Image.open(BytesIO(bmp_bytes))    
        
def ShowAvailableThemes():
    return AbGis.GetThemes()

def LoadTheme(iTheme):
    AbGis.SetTheme(iTheme)

def RunCommand(iCommand):
    Adb.RunCommandFromString(iCommand)    

def RunCADCommand(iCommand):
    Adb.RunCommandFromString('Cad.' + iCommand)

def RunGISCommand(iCommand):
    Adb.RunCommandFromString('GIS.' + iCommand)

def RunWadisoCommand(iCommand):
    Adb.RunCommandFromString('Wadiso.' + iCommand)

def RunSewsanCommand(iCommand):
    Adb.RunCommandFromString('Sewsan.' + iCommand)

def RunEdisanCommand(iCommand):
    Adb.RunCommandFromString('Edisan.' + iCommand)

def RunHiberniaCommand(iCommand):
    Adb.RunCommandFromString('Hibernia.' + iCommand)

def RefreshAllLayers():
    AbGis.RefreshCadLayers()
    
def GetAllLayerNames():
    return AbGis.GetLayerNames()

def SetLayerStyle(iSubLayerName: str, iStyleFilePath: str):
    AbGis.SetThemeStyle(iSubLayerName, iStyleFilePath)

def GetTableFromLayerSubString(substring) -> AbTable:
    layers = GetAllLayers() 
    
    for i in layers:
        if substring in layers[i]['name']:
            return layers[i]['table']
        
    return None  # Return None if the table name is not found

def GetAllLayers():
    names = []
    #layers = []
    tables = []
    for i in range(AbGis.GetLayerCount()):
        names.append(AbGis.GetFullLayerNameFromIndex(i))
        tables.append(AbTable(index=i))
  

    # Create the dictionary with index as key
    index_dict = {
        i: {
            'name': names[i],
            'table': tables[i]
        }
        for i in range(len(names))
    }
    return index_dict

def AdbTableFromLayerName(iName) -> AbTable:
    layers = GetAllLayerNames()
    if layers.count(iName) == 0:
        return
    
    return AbGis.GetTableFromLayerIndex(layers.index(iName))

def InsertImageFromFile(iFileName: str, iLayerName: str, x = 0.0, y = 0.0, pixel = 1.0):
   
    # Split the file into name and extension
    name, _ = os.path.splitext(iFileName)
    # Return the name with .jpw extension
    filename = f"{name}.jpw"
    
    # pixel size in the x-direction    
    # rotation about the y-axis (usually 0)
    # rotation about the x-axis (usually 0)
    # pixel size in the y-direction (negative if origin is top-left)
    # x-coordinate of the center of the upper-left pixel
    # y-coordinate of the center of the upper-left pixel

    # Define the numbers to be written in the file
    numbers = [pixel, 0.0, 0.0, -pixel, x, y]

    # Write the numbers to the file, each on a new line
    with open(filename, 'w') as file:
        for number in numbers:
            file.write(f"{number}\n")
    
    AbGis.InsertImage(iFileName,iLayerName)
    
def DeleteCADLayer(iLayerName:str):
    AbGis.DeleteCADLayer(iLayerName)
    
def AddCADLayer(iLayerName:str):
    AbGis.AddCADLayer(iLayerName)

def PurgeCADLayer(iLayerName:str):
    AbGis.PurgeCADLayer(iLayerName)
    
def DeleteBitmapRecord(iLayerName:str,iImageName:str):
    AbGis.DeleteBitmapRecord(iLayerName,iImageName)

def ShowCommandList():
    print(AbGis.ListCommands())
    
def UpdateDataFromArray(table, fieldname, data_array):    
    fld = table.GetFieldIndex(fieldname)
    if fld == -1:
        print(fieldname + ' does not exist')
        return
    
    table.BeginTransaction()
    for i in table.RecordCount():
        table.SetData(i, fld, data_array[i])
    table.CommitTransaction()
    print(fieldname + ' updated.')
    
def AddOrGet_PolyLine_Layer(layername) -> AbTable:
    if AbGis.DoesLayerExist(layername):
        print(layername + ' found.')
        return AbTable(layername)
    
    AbGis.CreateAndAddLayer(layername, AdbFieldType.AdbFTGeomPolyline.value, True)
    print(layername + ' created.')
    return AbTable(layername)
    
def AddOrGet_Point_Layer(layername) -> AbTable:
    if AbGis.DoesLayerExist(layername):
        print(layername + ' found.')
        return AbTable(layername)
    
    data = AbGis.CreateAndAddLayer(layername, AdbFieldType.AdbFTGeomPoint.value, True)
    print(layername + ' created.')
    return AbTable(layername)
    
def AddOrGet_Polygon_Layer(layername) -> AbTable:
    if AbGis.DoesLayerExist(layername):
        print(layername + ' found.')
        return AbTable(layername)
    
    data = AbGis.CreateAndAddLayer(layername, AdbFieldType.AdbFTGeomPolygon.value, True)
    print(layername + ' created.')
    return AbTable(layername)
    
def AddOrGet_NonGeom_Layer(layername) -> AbTable:
    if AbGis.DoesLayerExist(layername):
        print(layername + ' found.')
        return AbTable(layername)
    
    data = AbGis.CreateAndAddLayer(layername, AdbFieldType.AdbFTNull.value, True) # AdbFTNull, does not do anything
    print(layername + ' created.')
    return AbTable(layername)
    
        