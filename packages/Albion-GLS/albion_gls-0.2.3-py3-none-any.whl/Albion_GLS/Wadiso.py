from Albion import AbGis, Adb
import Albion_GLS.Albion_int as alb
import Albion_GLS.Charts as charts
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys, os

from epyt_flow.simulation import ScenarioSimulator, ParallelScenarioSimulation, ScadaData
from epyt_flow.uncertainty import ModelUncertainty, UniformUncertainty
from epyt_flow.utils import plot_timeseries_data

class WadisoModel:
    
    # Constructor
    def __init__(self):
        self.pipe = alb.AbTable("Wa_pipe")
        self.valve = alb.AbTable("Wa_valve")
        self.pump = alb.AbTable("Wa_pump")
        self.tank = alb.AbTable("Wa_tank")
        self.node = alb.AbTable("Wa_node")
        self.app = alb.AbTable("wa_appurtenances")  
        
        self.tables = []
        self.tables.append(self.pipe)
        self.tables.append(self.valve)
        self.tables.append(self.pump)
        self.tables.append(self.tank)
        self.tables.append(self.node)
        self.tables.append(self.app)
                
    # called in print(obj)
    def __repr__(self):  
        string = ''
        for tab in self.tables:
            string += tab.Name()
        return string     
    
    def GetTables(self):
        return self.tables
        
    def Get_Pipe_Data(self, fieldName) -> alb.AbTable:
        return self.pipe.GetDataArray(fieldName)
        
    def Get_Valve_Data(self, fieldName) -> alb.AbTable:
        return self.valve.GetDataArray(fieldName)
        
    def Get_Pump_Data(self, fieldName) -> alb.AbTable:
        return self.pump.GetDataArray(fieldName)
        
    def Get_Tank_Data(self, fieldName) -> alb.AbTable:
        return self.tank.GetDataArray(fieldName)
        
    def Get_Node_Data(self, fieldName) -> alb.AbTable:
        return self.node.GetDataArray(fieldName)
        
    def Get_Appurtenance_Data(self, fieldName):
        return self.app.GetDataArray(fieldName)
    
    def Update_Pipe_Data(self, fieldname, data_array):
        self.pipe.UpdateDataArray(fieldname, data_array)
        
    def Update_Valve_Data(self, fieldname, data_array):
        self.valve.UpdateDataArray(fieldname, data_array)
        
    def Update_Pump_Data(self, fieldname, data_array):
        self.pump.UpdateDataArray(fieldname, data_array)
        
    def Update_Tank_Data(self, fieldname, data_array):
        self.tank.UpdateDataArray(fieldname, data_array)
        
    def Update_Node_Data(self, fieldname, data_array):
        self.node.UpdateDataArray(fieldname, data_array)
        
    def Update_Appurtenance_Data(self, fieldname, data_array):
        self.app.UpdateDataArray(fieldname, data_array)          

def RunWadisoCommand(iCommand):
    Adb.RunCommandFromString('Wadiso.' + iCommand)

def Matplotlib_BoxAndWhisker_Pipes(filename, fieldX, fieldY):
    model = WadisoModel()
    
    if model.pipe.GetFieldIndex(fieldX) == -1:
        print(fieldX + ' does not exist')
        return 
        
    if model.pipe.GetFieldIndex(fieldY) == -1:
        print(fieldY + ' does not exist')
        return         
    
    dataX = model.pipe.GetDataArray(model.pipe.GetFieldIndex(fieldX))
    dataY = model.pipe.GetDataArray(model.pipe.GetFieldIndex(fieldY))
    
    charts.Matplotlib_BoxAndWhisker(filename, fieldX, dataX, fieldY, dataY)
    
    
def Monte_Carlo_Simulation(inp_output_path, numberOfSims, perc_uncertainty):
    #print('Start')
    
    #sys.stdout = open(os.devnull, "w")
    #sys.stderr = open(os.devnull, "w")

    # Number of simulations
    n_sim = numberOfSims

    # 5% max uncertainty in base demands
    eta_bar = perc_uncertainty

    # Specify and implement the base demand uncertainty
    # delta = base_demand * uniform_random[-a, a]
    # base_demand =  base_demand + delta
    class MyBaseDemandUncertainty(UniformUncertainty):
        def __init__(self, **kwds):
            super().__init__(**kwds)

        def apply(self, data: float) -> float:
            z = data * np.random.uniform(low=self.low, high=self.high)
            return data + z
        
    # Specify uncertainty
    base_demand_uncertainty = MyBaseDemandUncertainty(low=-eta_bar, high=eta_bar)

    # Run Monte Carlo simulation
    mcs_results_pressure = []
    mcs_results_quality = []

    inp_file = inp_output_path#"C:\\temp\\test_export.inp"
    alb.RunWadisoCommand("ExportINPTimeSim|"+inp_file)

    #print('Start')
    for i in range(n_sim):
        print('Analysis ' + str(i) + ' of ' + str(n_sim))
        # Create scenario based on Net2
        with ScenarioSimulator(f_inp_in=inp_file) as sim:
            """
            # TODO: Do it without the model uncertainty class
            # Compute and set new base demands
            base_demands = sim.epanet_api.getNodeBaseDemands()[1]
            delta_bd = (2*np.random.rand(len(base_demands))-1) * eta_bar * base_demands
            new_base_demands = base_demands + delta_bd
            #print(base_demands)
            #print(new_base_demands)

            sim.epanet_api.setNodeBaseDemands(new_base_demands)
            #"""
            sim.set_model_uncertainty(ModelUncertainty(base_demand_uncertainty=base_demand_uncertainty))

            # Place pressure sensors at each node
            sim.set_pressure_sensors(sim.sensor_config.nodes)

            # Place quality sensors at each node
            sim.set_node_quality_sensors(sim.sensor_config.nodes)

            # Run simulation and retrieve pressures and quality at each node
            scada_data = sim.run_simulation()

            #plot_timeseries_data(scada_data.get_data_pressures(["5"]).T)
            mcs_results_pressure.append(scada_data.get_data_pressures().T)  # Transpose: Each row contains one tim series! 
            mcs_results_quality.append(scada_data.get_data_nodes_quality().T)

    # Create NumPy array
    mcs_results_pressure = np.array(mcs_results_pressure)
    mcs_results_quality = np.array(mcs_results_quality)
    
    return mcs_results_pressure, mcs_results_quality
    
    #model = WadisoModel()
    #pressures = []
    #for data in mcs_results_pressure:
    #    pressures.append(np.max(data, axis=0))
    #model.Update_Node_Data('Average_Head', pressures)
    
def PlotBoundsPerNode(inp_output_path, node_id, pressure_results):
    node_idx = node_id   # Investigate the pressure at the fifth node -- refers to node "5", recall that indicies start at zero!
    pressure_at_node = pressure_results[:, node_idx]
    

    plot_timeseries_data(pressure_at_node,
                        x_axis_label="Time steps (1min)",
                        y_axis_label="Pressure in $psi$")

    upper_bound = np.max(pressure_at_node, axis=0)
    lower_bound = np.min(pressure_at_node, axis=0)
    average, var = np.mean(pressure_at_node, axis=0), np.var(pressure_at_node, axis=0)

    _, ax = plt.subplots()
    ax.plot(upper_bound, label="Upper bound")
    ax.plot(lower_bound, label="Lower bound")
    ax.plot(average, label="Average")
    ax.legend()
    ax.set_xlabel("Time steps (1min)")
    ax.set_ylabel("Pressure in $psi$")
    
    pre, ext = os.path.splitext(inp_output_path)
    plt.savefig(pre + '.png')
