import Albion_GLS.Albion_int as alb
import Albion_GLS.Wadiso as wadiso
import wntr
import numpy as np

class WntrInterface:
    
    # Constructor
    def __init__(self, iFileName: str = "default.inp", iIsTimeSime: bool = True):
        self.filename = iFileName + '.inp'
        
        self.isTimeSim = iIsTimeSime
        
        if self.isTimeSim:
            alb.RunWadisoCommand("ExportINPTimeSim|"+self.filename)
        else:
            alb.RunWadisoCommand("ExportINPSteadyState|"+self.filename)  
                                       
        self.wn = wntr.network.WaterNetworkModel(self.filename) 
        
        self.EarthQuake = None
        
        self.Results = None
        
    # called in print(obj)
    def __repr__(self):  
        return self.filename 
     
        
    def Simulate(self):
        sim = wntr.sim.EpanetSimulator(self.wn)
        self.Results = sim.run_sim() # by default, this runs EPANET 2.2.0
    
    def Simulate_EarthQuake(self, epicenter_x, epicenter_y, magnitude, depth):
    
        epicenter = (epicenter_x,epicenter_y) # x,y location

        self.EarthQuake = wntr.scenario.Earthquake(epicenter, magnitude, depth)

        #distance = self.EarthQuake.distance_to_epicenter(wn, element_type=wntr.network.Pipe)
        #pga = self.EarthQuake.pga_attenuation_model(distance)
        #pgv = self.EarthQuake.pgv_attenuation_model(distance)
        #repair_rate = self.EarthQuake.repair_rate_model(pgv)
        
    def Add_Break_or_Leak(self, node_code: str, area, start_time, end_time):
        leak_node = self.wn.get_node(node_code)
        if leak_node != None:
            leak_node.add_leak(self.wn, area=area, start_time=start_time, end_time=end_time)
        
    def Add_Power_Outage(self, link_code: str, start_time, end_time):
        pump = self.wn.get_link(link_code)
        if pump != None:
            pump.add_outage(self.wn, start_time=start_time, end_time=end_time)

    def Add_Fire_Flow(self, node_code, fire_flow_demand, fire_start, fire_end):
        node = self.wn.get_node(node_code)
        if node != None:
            node.add_fire_fighting_demand(self.wn, fire_flow_demand, fire_start, fire_end)
            
    def Criticality_Analysis(self, end_time_h, pipe_size_m, req_pressure, pressure_threshold ):
        # Adjust simulation options for criticality analyses
        analysis_end_time = end_time_h*3600 
        self.wn.options.time.duration = analysis_end_time
        self.wn.options.hydraulic.demand_model = 'PDD'
        self.wn.options.hydraulic.required_pressure = req_pressure
        self.wn.options.hydraulic.minimum_pressure = 0

        # Create a list of pipes with large diameter to include in the analysis
        pipes = self.wn.query_link_attribute('diameter', np.greater_equal, pipe_size_m, link_type=wntr.network.model.Pipe)      
        pipes = list(pipes.index)
        #wntr.graphics.plot_network(self.wn, link_attribute=pipes, title='Pipes included in criticality analysis')
        
        # Define the pressure threshold
        pressure_threshold = pressure_threshold

        # Run a preliminary simulation to determine if junctions drop below the 
        # pressure threshold during normal conditions
        sim = wntr.sim.WNTRSimulator(self.wn)
        results = sim.run_sim()
        min_pressure = results.node['pressure'].loc[:,self.wn.junction_name_list].min()
        below_threshold_normal_conditions = set(min_pressure[min_pressure < pressure_threshold].index)

        # Run the criticality analysis, closing one pipe for each simulation
        junctions_impacted = {} 
        for pipe_name in pipes:

            print('Pipe:', pipe_name)     
            
            # Reset the water network model
            self.wn.reset_initial_values()

            # Add a control to close the pipe
            pipe = self.wn.get_link(pipe_name)        
            act = wntr.network.controls.ControlAction(pipe, 'status', 
                                                    wntr.network.LinkStatus.Closed)
            cond = wntr.network.controls.SimTimeCondition(self.wn, '=', '24:00:00')
            ctrl = wntr.network.controls.Control(cond, act)
            self.wn.add_control('close pipe ' + pipe_name, ctrl)
                
            # Run a PDD simulation
            sim = wntr.sim.WNTRSimulator(self.wn)
            results = sim.run_sim()
                
            # Extract the number of junctions that dip below the minimum pressure threshold
            min_pressure = results.node['pressure'].loc[:,self.wn.junction_name_list].min()
            below_threshold = set(min_pressure[min_pressure < pressure_threshold].index)
            
            # Remove the set of junctions that were below the pressure threshold during 
            # normal conditions and store the result
            junctions_impacted[pipe_name] = below_threshold - below_threshold_normal_conditions
                
            # Remove the control
            self.wn.remove_control('close pipe ' + pipe_name)

        # Extract the number of junctions impacted by low pressure conditions for each pipe closure  
        number_of_junctions_impacted = dict([(k,len(v)) for k,v in junctions_impacted.items()])
        print(number_of_junctions_impacted)

# Run the app
if __name__ == '__main__':
    
    inp_file = "disaster"
    
    model = WntrInterface(inp_file, True) 
    
    #model.Criticality_Analysis()
    
    model.Simulate()
    
    #model.Simulate_EarthQuake(32000,15000, 6.5, 10000) # X, Y, Richter Scale, Depth (m)
    
    #distanceTo = model.EarthQuake.distance_to_epicenter(model.wn, element_type=wntr.network.Pipe)
    #pga = model.EarthQuake.pga_attenuation_model(distanceTo)
    
    
    #model.Add_Break_or_Leak('50', 0.05, 2*3600, 12*3600)
    
    #model.Add_Fire_Flow('5', 0.252, 10*3600, 14*3600)