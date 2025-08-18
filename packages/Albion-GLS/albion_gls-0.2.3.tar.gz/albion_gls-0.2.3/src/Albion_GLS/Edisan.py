from Albion import AbGis, Adb
import Albion_GLS.Albion_int as alb

class EdisanModel:
    
    # Constructor
    def __init__(self):
        self.el_substations = alb.AbTable("el_substations")
        self.el_sources = alb.AbTable("el_sources")
        self.el_nodes = alb.AbTable("el_nodes")
        self.el_breakers = alb.AbTable("el_breakers")
        self.el_supply_points = alb.AbTable("el_supply_points")
        self.el_loads = alb.AbTable("el_loads")  
        self.el_conductors = alb.AbTable("el_conductors")  
        self.ed_appurtenances = alb.AbTable("ed_appurtenances")  
        self.ed_fault_locations = alb.AbTable("ed_fault_locations")  
        
        self.tables = []
        self.tables.append(self.el_substations)
        self.tables.append(self.el_sources)
        self.tables.append(self.el_nodes)
        self.tables.append(self.el_breakers)
        self.tables.append(self.el_supply_points)
        self.tables.append(self.el_loads)
        self.tables.append(self.el_conductors)
        self.tables.append(self.ed_appurtenances)
        self.tables.append(self.ed_fault_locations)
                
    # called in print(obj)
    def __repr__(self):  
        string = ''
        for tab in self.tables:
            string += tab.Name()
        return string     
    
    def GetTables(self):
        return self.tables
        
    def Get_Substation_Data(self, fieldName):
        return self.el_substations.GetDataArray(fieldName)
        
    def Get_Source_Data(self, fieldName):
        return self.el_sources.GetDataArray(fieldName)
        
    def Get_Node_Data(self, fieldName):
        return self.el_nodes.GetDataArray(fieldName)
        
    def Get_Breaker_Data(self, fieldName):
        return self.el_breakers.GetDataArray(fieldName)
        
    def Get_SupplyPoint_Data(self, fieldName):
        return self.el_supply_points.GetDataArray(fieldName)
        
    def Get_Load_Data(self, fieldName):
        return self.el_loads.GetDataArray(fieldName)
        
    def Get_Conductor_Data(self, fieldName):
        return self.el_conductors.GetDataArray(fieldName)
        
    def Get_Appurtenance_Data(self, fieldName):
        return self.ed_appurtenances.GetDataArray(fieldName)
        
    def Get_FaultLocation_Data(self, fieldName):
        return self.ed_fault_locations.GetDataArray(fieldName)
    
    def Update_Substation_Data(self, fieldname, data_array):
        self.el_substations.UpdateDataArray(fieldname, data_array)
        
    def Update_Source_Data(self, fieldname, data_array):
        self.el_sources.UpdateDataArray(fieldname, data_array)
        
    def Update_Node_Data(self, fieldname, data_array):
        self.el_nodes.UpdateDataArray(fieldname, data_array)
        
    def Update_Breaker_Data(self, fieldname, data_array):
        self.el_breakers.UpdateDataArray(fieldname, data_array)
        
    def Update_SupplyPoint_Data(self, fieldname, data_array):
        self.el_supply_points.UpdateDataArray(fieldname, data_array)
        
    def Update_Load_Data(self, fieldname, data_array):
        self.el_loads.UpdateDataArray(fieldname, data_array)     
        
    def Update_Conductor_Data(self, fieldname, data_array):
        self.el_conductors.UpdateDataArray(fieldname, data_array) 
        
    def Update_Appurtenance_Data(self, fieldname, data_array):
        self.ed_appurtenances.UpdateDataArray(fieldname, data_array) 
        
    def Update_FaultLocation_Data(self, fieldname, data_array):
        self.ed_fault_locations.UpdateDataArray(fieldname, data_array)      
