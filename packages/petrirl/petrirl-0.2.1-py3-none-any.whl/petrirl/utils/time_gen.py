
import os
import pickle
import uuid
import numpy as np
import math




def save_seeds(nsamples=100):
    " Generate a list of random integer seeds and save them to a pickle file with a unique ID."""
    
    directory = os.getcwd()
    os.makedirs(os.path.join(directory, "time_seeds"), exist_ok=True)
    
    unique_id = str(uuid.uuid4())[-4:]  
    file_path = f"time_seeds//{unique_id}{nsamples}.pkl"  
    
    # Generate a list of random integer seeds (e.g., between 0 and 2^32-1)
    random_seeds = [np.random.randint(0, 2**32 - 1) for _ in range(nsamples)]

    # Save the random seeds list to the uniquely named pickle file
    with open(file_path, "wb") as pickle_file:
        pickle.dump(random_seeds, pickle_file)
        
    print(f"seeds with id {unique_id}{nsamples} generated and saved in {file_path} ")

    return unique_id


def load_seeds(unique_id):
    "Load the list of random integer seeds from a pickle file given a unique ID."""
    
    
    file_path = f"time_seeds//{unique_id}.pkl"
    
    try:
        with open(file_path, "rb") as pickle_file:
            random_seeds = pickle.load(pickle_file)
        return random_seeds
    except FileNotFoundError:
        print(f"Error: No file found with unique ID {unique_id}.")
        return None


class Times_manage():
    
    def __init__(self):
        self.seed = None
        self.rng = np.random.default_rng(self.seed)

        self.mtbf_factors = (0.5, 1)  # MTBF range as factor of max processing time
        self.weibull_param = 1.5      # Weibull shape parameter
        self.repair_factors = (0.2, 0.5)  # Repair duration as fraction of max processing time


        self.arrival_schedule = []    # Stores all generated operation arrivals
    
    def set_seeds(self, seed=None):
        self.seed = seed
        self.rng = np.random.default_rng(self.seed)

    def gen_machines_down(self, instance):
        n_jobs, n_machines, n_tools, max_bound, max_op = instance.specs
        
        # Generate MTBF (Mean Time Between Failures) for each machine
        breakdown_time_lookup = {
            "machines_mtbf": [int(self.rng.uniform(self.mtbf_factors[0] * max_bound, 
                                                   self.mtbf_factors[1] * max_bound)) for _ in range(n_machines)]
        }

        # Use Weibull distribution for failure times (based on MTBF and Weibull parameter)
        breakdown_time_lookup["failure_times"] = [
            int(self.rng.weibull(self.weibull_param) * mtbf) for mtbf in breakdown_time_lookup["machines_mtbf"]
        ]
        
        # Generate repair durations as a uniform distribution between repair factors
        breakdown_time_lookup["repair_durations"] = [
            int(self.rng.uniform(self.repair_factors[0] * max_bound, 
                                 self.repair_factors[1] * max_bound)) for _ in range(n_machines)
        ]

        # Calculate repair end times based on failure time and repair durations
        breakdown_time_lookup["repair_end_times"] = [
            failure_time + repair for failure_time, repair in 
            zip(breakdown_time_lookup["failure_times"], breakdown_time_lookup["repair_durations"])
        ]
        
        return breakdown_time_lookup

    def gen_jobs_arrivals(self, instance):
        """
        Generate per-job operation arrival times using a mixed Poisson process.
        The rate (lambda) for the Poisson process is drawn from a Gamma distribution.
        """
        n_jobs, _, _, max_bound, max_op = instance.specs
        horizon = max_bound * max_op
        arrival_time_lookup = []
    
        for _ in range(n_jobs):
            job_arrivals = [0]  # First operation always arrives at time 0
    
            job_skewness = self.rng.uniform(0, 1)
            alpha = 10 * job_skewness
            beta = 0.1 * horizon
    
            raw_arrivals = self.rng.gamma(alpha, beta, size=max_op)
            clipped_arrivals = [
                int(np.clip(x, 1, horizon - 1)) for x in raw_arrivals
            ]
    
            job_arrivals.extend(sorted(clipped_arrivals))
            arrival_time_lookup.append(job_arrivals)
    
        return arrival_time_lookup
    
        
            
 
if __name__=="__main__":
    
    
    T= Times_manage()
    T.set_seeds(101)
   
    

   
    



    
 
    
    
    
    
    
    
  

