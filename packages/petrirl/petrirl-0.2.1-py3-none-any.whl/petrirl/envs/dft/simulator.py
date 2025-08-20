import numpy as np
from petrirl.envs.dft.petri_build import Petri_build
from petrirl.render.graph import  Graph
from petrirl.utils.obs import get_obs_dft
from petrirl.utils.twin import create_twin
from petrirl.utils.time_gen import Times_manage
from petrirl.utils.firing_log import FiringLogger
import random 
import copy


import warnings
warnings.filterwarnings("ignore", message=".*env.action_masks to get variables from other wrappers is deprecated.*")


class Simulator(Petri_build):
    """
        Class representing the core logic of a Job Shop Scheduling Problem (JSSP) simulation using a Petri net.
        
        Attributes:
            clock (int): The internal clock of the simulation.
            interaction_counter (int): Counter for interactions in the simulation.
            delivery_history (dict): Dictionary storing the delivery history.
            action_map (dict): Mapping for actions in the simulation from discrete to multidiscrete.
    
        Methods:
            __init__(...): Initializes the JSSP simulator with optional parameters.
            petri_reset(): Resets the internal state of the Petri net, including places and tokens.
            action_mapping(): Maps multidiscrete actions to a dictionary for use with reinforcement learning.
            is_terminal(): Checks if the simulation has reached a terminal state.
            sort_tokens(): Processes tokens in sorting places based on their roles.
            refresh_state(): Updates the state of the Petri net after sorting tokens and checking transitions.
            fire_timed(): Advances simulation time and fires timed transitions based on elapsed times.
            action_masks(): Checks which transitions are enabled for action selection.
            fire_controlled(action): Fires a controlled transition based on the provided action.
            time_tick(): Increments the internal simulation clock and updates token logging.
            interact(action, screenshot=False): Performs Petri net interactions based on the action and updates internal state.
    """

    def __init__(self, 
                 label="main",
                 benchmark='Raj',
                 instance_id="ra01", 
                 layout=1,
                 n_agv=0,
                 n_tt=0,
                 
                 dynamic=False,
                 size=(None,None,None,None),
                 
                 observation_depth=1,
                 
                 lookup=False,
                 random_arrival= False,
                 machine_down=False,
                 standby=False

                  ):
        """
    Initializes the JSSP simulator with the given parameters.

    Parameters:
        instance_id (str): Identifier for the JSSP instance.
        dynamic (bool): If True, allows appending new operations; termination condition is all queues empty.
        size (tuple): Size parameters for simulation only if dynamic  (default: (None, None)).
        n_agv (int): Number of AGVs (default: 2).
        n_tt (int): Number of tool transports (default: 1).
    """
    
        super().__init__(instance_id, 
                         layout= layout,
                         benchmark=benchmark,
                         n_agv=n_agv,
                         n_tt=n_tt,
                         dynamic=dynamic,
                         size=size,
                         random_arrival = random_arrival,
                         machine_down = machine_down,
                         stand_by= standby
                         )
        
        self.label=label
        self.create_petri(show_flags=True,show_develop=False) 
        self.cache =self.cache_nodes()

        self.test_mode=False 
        self.clock = 0
        self.episodes=0
        self.interaction_counter = 0
        self.observation_depth=observation_depth
        
        self.action_map = self.action_mapping()
        self.graph=Graph(self)
        
        self.lookup=lookup
        if self.lookup :
            self.twin=create_twin(self)
            
        self.seeds=None
        

        self.random_arrival = random_arrival
        self.machine_down = machine_down
        
        self.time_gen= Times_manage()
        self.machines_down_times={}
        self.job_arrival_times={}
        
        
        self.delivery_history = {}
        self.events_history={"machines_down":{},
                             "job_arrivals":{}}

        self.print_instance_info()
        self.petri_reset()
        

    def set_seeds(self,seeds=None):  
        self.seeds= seeds
        if seeds :
           print(f"seeds loaded numbre of samples seeds :{len (self.seeds)}")
        else :
            print ("No seeds provided  , a random seed will be utilized !")
        

    def set_times(self,seed=None) :
        
        if self.seeds:  # aka a lit of seeds is given  else  None
            seed=self.seeds.pop(0)
            self.time_gen.set_seeds(seed)

        self.machines_down_times=self.time_gen.gen_machines_down(self.instance)
        self.job_arrival_times=self.time_gen.gen_jobs_arrivals(self.instance)
            
            
    def print_instance_info (self):  
        if self.label=="main":
            print(f"{self.benchmark} Instance '{self.instance_id}' ,Layout: '{self.layout}' is loaded.")
            print(f"Random Job Arrival : {self.random_arrival} ,  Random Machines Down : {self.machine_down} ")
            print(f"JSSP {self.instance_id}: {self.n_jobs} jobs X {self.n_machines} machines X  {self.n_tools} Tools, AGVs: {self.n_agv}, TT: {self.n_tt}, Dynamic Mode: {self.dynamic} , Lookup: {self.lookup}")
            
    def get_state(self):
         """Returns the current state of the simulation."""
         return get_obs_dft(self.cache ["places"],self.guard_function(),self.observation_depth)
     

    def  error_check(self): 
        """Checks for any errors in the simulation."""
        ...

    def petri_reset(self):
        """Resets the internal state of the Petri net."""

        self.clock = 0
        self.clear_petri()    
        self.add_tokens()
        self.set_times ()
        
    def save_state(self):
        """Save the full Petri net state."""
        return {
            "tokens": self.save_token_state(),
            "clock": copy.deepcopy(self.clock)
        }

    def load_state(self, saved_state):
        """Restore the full Petri net state."""
        self.load_token_state(saved_state["tokens"])
        self.clock = saved_state["clock"]
        
        

    def action_mapping(self):
         """Maps multidiscrete actions to a more versatile Discrete format for reinforcement learning."""
         return dict(enumerate([t for t in self.transitions.values() if t.type == "c"]))


    def is_terminal(self):
        """Checks if the simulation has reached a terminal state."""
        done = sum(len(p.token_container) for p in self.cache["delivery_places"]) >= self.number_of_ops

        
        #done = np.all([len(p.token_container) == 0 for p in self.cache["flow_places"]])
        return  done 

    
    def job_arrival(self):
        arrivals = self.job_arrival_times
        #print(arrivals)
        
        for transition in self.cache["job_feed"]:
            next_arrival = arrivals[transition.color-1][0]
            if self.clock >= next_arrival:
                if transition.check_state():
                    transition.fire()
                    arrivals[transition.color-1].pop(0)
                
        
    def machines_down(self):
        """Simulates machines going down based on failure times and repair durations."""
    
        machine_starts_transitions = self.cache["machine_start"]
        failure_times = np.array(self.machines_down_times["failure_times"])
        repair_end_durations = np.array(self.machines_down_times["repair_end_times"])
        conditions = (self.clock >= failure_times) & (self.clock < repair_end_durations)

        forced_values = np.where(conditions, False, None)
        
        for machine, forced_value in zip(machine_starts_transitions, forced_values):
            machine.forced = forced_value
            

    def get_utilization(self):
         utilization = 0
         busy_machines= np.array( [bool(machine.token_container) for machine in self.cache["machine_processing"]])
         utilization =  sum(busy_machines)/self.n_machines
         
         return utilization   
     
    def get_consumption(self):
        consumption = 0
        busy_machines= np.array( [bool(machine.token_container) for machine in self.cache["machine_processing"]])
        consumption =  np.dot(busy_machines , self.machines_powers)
        return consumption
     
                    
    def get_deadheadings(self,place,role_dict):
        """Handles deadheading for certain places (e.g., transport)."""
        ...
    
    def time_tick(self):
        """Advances the internal clock and updates token logging."""
    
        self.clock += 1
        process_places = self.cache["process_places"]
        for p in process_places:
            
            transition = next((parent for parent in p.parents if parent.type != "f"), None)
            if transition is None:
                continue
        
            if transition.forced is False:
                p.tick(faulty=True)
            else:
                p.tick()
                
        #self.error_check()  #  useful in safe mode mode 
        
    def fire_auto(self):
        """Fires automatic transitions."""
        
        for transition in self.cache["auto_transitions"]: 
            if transition.check_state():
                transition.fire(self.clock)
            
            
    def sort_tokens(self):
        """Sorts tokens in sorting places based on their roles."""
        
        
        def process_tokens(place, color_criterion_index):
            
            tokens = place.token_container
            if not tokens:
                return
            
            for token in tokens.copy():
                for transition in place.children:
                    if token.color[color_criterion_index] == transition.color:
                        transition.fire(self.clock)
                        break
                else:
                    tokens.remove(token)
                    print(f"Token color: {token.color} destroyed in {place.role} - No compatible destination found!")

        role_to_index = {
            "job_sorting": 0,
            "machine_sorting": 1,
            "machine_sorting_T": 1,
            "request_sorting": 2,
            "tools_sorting": 2,
        }
    
        for place in self.cache.get("sorting_places", []):
                process_tokens(place, role_to_index[place.role])
                
                
    def refresh_state(self):
        """Refreshes the state of the Petri net after sorting tokens and checking enabled transitions."""
        if self.random_arrival:
            self.job_arrival()
            
        if self.machine_down:
            self.machines_down()
        
        self.sort_tokens()
        self.fire_auto()
        
        
    def is_valid(self,action):
        """
        checks if an action is valid to fire 
        """
        transition = self.action_map[int(action)] 
        return  transition.check_state()
        
        
    def guard_function(self):
        """Refreshes the state of the Petri net after sorting tokens and checking enabled transitions."""

        self.refresh_state()
        mask =[t.check_state()  for t in self.transitions.values() if t.type == "c"]
        return mask  
     

    def fire_timed(self):
        """Advances the simulation time, fires timed transitions, and updates the state of the Petri net."""
        
        completed_ops=0
        role_dict={"machine_processing":0,
                   "agv_transporting":1,
                   "agv_relocating":2,
                   "tt_transporting":3,
                   "tt_relocating":4,
                   }
       
        fired_transitions = []
        for place in  self.cache["process_places"]: 
            if place.token_container:
                transition = place.children[0]
                token = place.token_container[0]   
                
                elapsed_time = token.logging[place.uid][2]
                reference_time = token.time_features[role_dict[place.role]]

                if elapsed_time >= reference_time :
                    
                    if place.role in ["agv_transporting", "tt_transporting"]:
                        self.get_deadheadings(place,role_dict)
                        
                    transition.fire(self.clock)
                    fired_transitions.append(transition.uid)
           
                    if transition.role=="machine_finish":
                        completed_ops+=1
            
        self.refresh_state()
        self.delivery_history[self.clock] = [ token for place in self.places.values() if place.type == "d" for token in place.token_container]
           
        return fired_transitions,completed_ops


    def fire_controlled(self, action):
        
        """Fires a controlled transition based on the action."""
        fired_transitions=[]  
        transition = self.action_map[int(action)] 
        
        if transition.role=="standby":
            self.time_tick()
        
        if all(parent.token_container for parent in transition.parents):
            transition.fire(self.clock)
            fired_transitions.append(transition.uid)

        
        self.interaction_counter += 1 
        return fired_transitions
    

    def interact(self, action ,screenshot):
        """Handles the interaction logic for each step in the simulation."""
        
        feedbacks={}

            
        fired_controlled = self.fire_controlled(action)  
        self.graph.plot_net(fired_controlled) if screenshot else None
        
        while sum(self.guard_function()) == self.standby:  
            fired_time,completed_ops_1 = self.fire_timed()
            fired_timed,completed_ops_2 = self.fire_timed()
            self.time_tick()
            
            self.graph.plot_net(fired_timed) if screenshot else None
            if self.is_terminal():
               break
        
        #feedbacks['energy_consumption']=self.get_consumption()
        feedbacks['machine_utilisation']= self.get_utilization()
        
        return feedbacks
           

if __name__ == "__main__":
    
    benchmark='Solax'
    instance = "sl00"
    layout =1
    n_agv=2
    n_tt=0
    
    dynamic=False
    # Job,machines,n_agvs,n_tools,ntt
    size=(100,20,10,0,0)
    
    petri = Simulator(benchmark=benchmark,
                      instance_id= instance ,
                      layout=layout,
                      n_agv=n_agv,
                      n_tt=n_tt,
                      dynamic=dynamic , 
                      size= size,
                      ) 
                
    petri.graph.plot_net()
    petri.print_instance_info()
  



    
    
 
    
  
    
    

  
    
    
 
    
  
    
    

  
    
    
    

    
   
    
    
 

    
    
    
    
    
    
    
    
    
   
    
    

    
    

    
    
    

        


    