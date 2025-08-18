from Albion import AbGis, Adb
import Albion_GLS.Albion_int as alb    
 
def GetGravityTable() -> alb.AbTable:
    return alb.AbTable("Se_Gravity_Tables")

def GetRisingTable() -> alb.AbTable:
    return alb.AbTable("Se_Rising_Tables")

def GetStructureTable() -> alb.AbTable:
    return alb.AbTable("Se_Structures_Tables")

def GetPumpTable() -> alb.AbTable:
    return alb.AbTable("Se_Pump_Tables")

def GetDiversionTable() -> alb.AbTable:
    return alb.AbTable("se_diversions")

def GetUserHydrographTable() -> alb.AbTable:
    return alb.AbTable("se_userhydro")

def GetSewsanModelTables():
    tables = []
    tables.append(GetGravityTable())
    tables.append(GetRisingTable())
    tables.append(GetStructureTable())
    tables.append(GetPumpTable())
    tables.append(GetDiversionTable())
    tables.append(GetUserHydrographTable())
    return tables