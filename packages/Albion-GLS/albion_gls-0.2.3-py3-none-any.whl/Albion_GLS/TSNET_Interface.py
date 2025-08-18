import Albion_GLS.Albion_int as alb
import Albion_GLS.Wadiso as wadiso

import tsnet
from tsnet.network.model import TransientModel

import matplotlib.pyplot as plt
import pandas as pd

class TsnetInterface:
    
    # Constructor
    def __init__(self, iFileName: str = "default", iIsTimeSime: bool = True, wavespeed:float= 1200., dt:float=0.01, tf:int=25):
        self._filename = iFileName + '.inp'
        self._isTimeSim = iIsTimeSime
        self._results_obj = None
        
        # Export INP from Wadiso
        if self._isTimeSim:
            alb.RunWadisoCommand("ExportINPTimeSim|" + self._filename)
        else:
            alb.RunWadisoCommand("ExportINPSteadyState|" + self._filename)  

        # Load TSNet model
        self._tm = tsnet.network.TransientModel(self._filename) 
        self._tm.set_wavespeed(wavespeed) 
        self._tm.set_time(tf, dt)

        
    # --- Property to access underlying TmNetwork ---
    @property
    def tm(self):
        """Get the underlying TmNetwork object."""
        return self._tm
        
    # -----------------------------------------------------
    # Event API
    # -----------------------------------------------------

    def Event_Valve_Closure(self, valve_code: str, tc=0, ts=0, se=0, m=0, curve=None):
        rule = [tc, ts, se, m]
        self._tm.valve_closure(valve_code, rule, curve)

    def Event_Valve_Opening(self, valve_code: str, tc=0, ts=0, se=0, m=0, curve=None):
        rule = [tc, ts, se, m]
        self._tm.valve_opening(valve_code, rule, curve)

    def Event_Pump_Shut_Off(self, name, tc=1, ts=1, se=0, m=1):
        rule = [tc, ts, se, m]
        self._tm.pump_shut_off(name, rule)

    def Event_Pump_Start_Up(self, name, tc=1, ts=1, se=0, m=1):
        rule = [tc, ts, se, m]
        self._tm.pump_start_up(name, rule)

    def Event_Add_Demand_Pulse(self, name, tc=1, ts=1, stay=0, dp=1, m=1):
        rule = [tc, ts, stay, dp, m]
        self._tm.add_demand_pulse(name, rule)

    def Event_Add_Open_Surge_Tank(self, name, As):
        shape = [As]
        self._tm.add_surge_tank(name, shape, 'open')

    def Event_Add_Closed_SurgeTank(self, name, As, Ht, Hs):
        shape = [As, Ht, Hs]
        self._tm.add_surge_tank(name, shape, 'closed')

    def Event_Add_Burst(self, name, ts=1, tc=1, final_burst_coeff=0.01):
        self._tm.add_burst(name, ts, tc, final_burst_coeff)

    def Event_Add_Leak(self, name, coeff=0.01):
        self._tm.add_leak(name, coeff)

    def Event_Add_Blockage(self, name, percentage):
        self._tm.add_blockage(name, percentage)

    def Event_Remove_Leak(self, name):  # NEW
        """Remove an existing leak at the given node(s)."""
        self._tm.remove_leak(name)

    def Event_Remove_Burst(self, name):  # NEW
        """Remove a burst at the given node(s)."""
        self._tm.remove_burst(name)

    def Event_Remove_Blockage(self, name):  # NEW
        """Remove blockage at the given link(s)."""
        self._tm.remove_blockage(name)

    def Event_Add_Pressure_Valve(self, name, setting, coeff=1.0):  # NEW
        """Add a pressure valve (pressure relief or control)."""
        self._tm.add_pressure_valve(name, setting, coeff)

    def Event_Add_Pressure_Wave_Generator(self, name, magnitude, ts=0):  # NEW
        """Inject a pressure wave at a given time (idealized event)."""
        self._tm.add_pressure_wave(name, magnitude, ts)

    # -----------------------------------------------------
    # Simulation Controls
    # -----------------------------------------------------

    def Initialize(self, t0=0.0, engine='PDD'): 
        self._tm = tsnet.simulation.Initializer(self._tm, t0, engine)
        return self._tm

    def Transient_Simulation_Steady(self, results_obj='TnetSteady'): 
        self._results_obj = results_obj
        return tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'steady')

    def Transient_Simulation_Quasi(self, results_obj='TnetQuasi'): 
        self._results_obj = results_obj
        return tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'quasi-steady')

    def Transient_Simulation_Unsteady(self, results_obj='TnetUnsteady'): 
        self._results_obj = results_obj
        return tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'unsteady')

    # -----------------------------------------------------
    # Node/Link Access & Modification
    # -----------------------------------------------------

    def GetNode(self, code):
        return self._tm.get_node(code)

    def GetLink(self, code):
        return self._tm.get_link(code)

    # --- NEW: direct getters ---
    def GetNodeHead(self, code):  # NEW
        return self._tm.get_node(code).head

    def GetNodePressure(self, code):  # NEW
        return self._tm.get_node(code).pressure

    def GetNodeDemand(self, code):  # NEW
        return self._tm.get_node(code).demand_discharge

    def GetLinkFlow(self, code):  # NEW
        return self._tm.get_link(code).flow

    def GetLinkVelocity(self, code):  # NEW
        return self._tm.get_link(code).velocity

    # --- NEW: setters ---
    def SetNodeHead(self, code, value):  # NEW
        self._tm.get_node(code).head = value

    def SetNodeDemand(self, code, value):  # NEW
        self._tm.get_node(code).demand_discharge = value

    def SetLinkFlow(self, code, value):  # NEW
        self._tm.get_link(code).flow = value

    def SetLinkRoughness(self, code, value):  # NEW
        self._tm.get_link(code).roughness = value

    def SetLinkDiameter(self, code, value):  # NEW
        self._tm.get_link(code).diameter = value

    # --- NEW: bulk utilities ---
    def ListAllNodes(self):  # NEW
        return list(self._tm.nodes.keys())

    def ListAllLinks(self):  # NEW
        return list(self._tm.links.keys())

    def GetSimulationTimes(self):  # NEW
        return self._tm.simulation_timestamps      
        
    def Initialize(self, t0:float=0.0, engine: str = 'PDD'): 
        # Initialize steady state simulation
        t0 = t0 # initialize the simulation at 0 [s]
        engine = engine # demand driven simulator
        self._tm = tsnet.simulation.Initializer(self._tm, t0, engine)
        
    def Transient_Simulation_Steady(self, results_obj:str='TnetSteady'): 
        # Transient simulation
        self._results_obj = results_obj # name of the object for saving simulation results
        result = tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'steady')
        return result
        
    def Transient_Simulation_Quasi(self, results_obj:str='TnetQuasi'): 
        # Transient simulation
        self._results_obj = results_obj # name of the object for saving simulation results
        result = tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'quasi-steady')
        return result
        
    def Transient_Simulation_Unsteady(self, results_obj:str='TnetUnsteady'): 
        # Transient simulation
        self._results_obj = results_obj # name of the object for saving simulation results
        result = tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'unsteady')
        return result
    
    def TransientModel(self) -> TransientModel:
        return self._tm
    
    def GetNode(self, iNodeCode):
        return self._tm.get_node(iNodeCode)
    
    def GetLink(self, iLinkCode):
        return self._tm.get_link(iLinkCode)
    
    # -----------------------------------------------------
    # Integrated Plotting
    # -----------------------------------------------------

    def PlotNodeHead(self, node_code, outfile, label=None):
        label = label or node_code
        t = self._tm.simulation_timestamps
        h = self._tm.get_node(node_code).head
        plt.figure(figsize=(8,5))
        plt.plot(t, h, label=label, linewidth=2)
        plt.xlabel("Time [s]"); plt.ylabel("Pressure Head [m]")
        plt.legend(); plt.grid(True)
        plt.savefig(outfile + '.pdf', dpi=500)
        plt.close()

    def PlotLinkFlow(self, link_code, outfile, label=None):
        label = label or link_code
        t = self._tm.simulation_timestamps
        q = self._tm.get_link(link_code).flow
        plt.figure(figsize=(8,5))
        plt.plot(t, q, label=label, linewidth=2)
        plt.xlabel("Time [s]"); plt.ylabel("Flow Rate [m³/s]")
        plt.legend(); plt.grid(True)
        plt.savefig(outfile + '.pdf', dpi=500)
        plt.close()

    def PlotNodeDemand(self, node_code, outfile, label=None):
        label = label or node_code
        t = self._tm.simulation_timestamps
        d = getattr(self._tm.get_node(node_code), 'demand_discharge', None)
        if d is None:
            raise AttributeError(f"Node {node_code} has no demand_discharge data")
        plt.figure(figsize=(8,5))
        plt.plot(t, d, label=label, linewidth=2)
        plt.xlabel("Time [s]"); plt.ylabel("Demand [m³/s]")
        plt.legend(); plt.grid(True)
        plt.savefig(outfile + '.pdf', dpi=500)
        plt.close()

    def CompareNodeHead(self, tm2, node_code, outfile, labels=('TM1', 'TM2')):
        t = self._tm.simulation_timestamps
        h1 = self._tm.get_node(node_code).head
        h2 = tm2.get_node(node_code).head
        plt.figure(figsize=(8,5))
        plt.plot(t, h1, 'k', label=labels[0], linewidth=2)
        plt.plot(t, h2, 'b', label=labels[1], linewidth=2)
        plt.xlabel("Time [s]"); plt.ylabel("Pressure Head [m]")
        plt.legend(); plt.grid(True)
        plt.savefig(outfile + '.pdf', dpi=500)
        plt.close()

    # -----------------------------------------------------
    # Integrated CSV Export
    # -----------------------------------------------------

    def ExportResultsCSV(self, filename_prefix):
        data = {'time_s': self._tm.simulation_timestamps}
        for code, node in self._tm.nodes.items():
            data[f'head_{code}'] = node.head
            if hasattr(node, 'pressure'):
                data[f'pressure_{code}'] = node.pressure
            if hasattr(node, 'demand_discharge'):
                data[f'demand_{code}'] = node.demand_discharge
        for code, link in self._tm.links.items():
            data[f'flow_{code}'] = link.flow
            if hasattr(link, 'velocity'):
                data[f'velocity_{code}'] = link.velocity
        df = pd.DataFrame(data)
        df.to_csv(filename_prefix + '.csv', index=False)