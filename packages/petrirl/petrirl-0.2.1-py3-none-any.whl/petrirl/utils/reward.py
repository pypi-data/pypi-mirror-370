
class RewardCalculator:
    def __init__(self, env):
        """
        Initialize the reward calculator with the environment.
        """
        self.env = env
        self.reward_function = self.get_reward_function()

    def get_reward_function(self):
        reward_functions = {
            "G": self.general_reward,
            "GS": self.general_soft_reward,
            "A":self.advancement_reward,
            "J": self.jit_reward,
            "E": self.energy_reward,
            "M": self.machine_utilization,
            "C": self.mix_rewards,
            "T": self.test_reward,
        }
        return reward_functions.get(self.env.reward_f, lambda f, t: 0)
    
    
    
    def advancement_reward(self,feedback,terminal):
        
        in_process = sum(len(place.token_container) for place in self.env.sim.cache["flow_places"] if place.token_container)
        delivered = sum(len(place.token_container) for place in self.env.sim.cache["delivery_places"] if place.token_container)
        advancement = delivered /(in_process+delivered)
        return  advancement 
    

    
    def machine_utilization(self, feedback, terminal):
        

        
        if terminal :
            return 100
        elif  feedback['valid_move']==False:
            return 0
        else :
            return feedback['machine_utilisation']
        



    def energy_reward(self, feedback, terminal):
        
        consumption = feedback["energy_consumption"]

        if  terminal  :
            return 100
        
        elif   consumption ==0 :
            return 0
        
        else :
 
            deviation = (consumption - self.env.sim.target_consumption) / self.env.sim.machines_powers.sum()  
            target =  1 - abs (deviation)
    
            return target 
        
    def mix_rewards (self, feedback, terminal):
        
        o1= self.energy_reward(feedback, terminal)
        o2= self.machine_utilization(feedback, terminal)
    
        
        return  0.8*o1 +0.2*o2
    
    
    def jit_reward(self, feedback, terminal):
        total_tokens_in_buffer = sum(
            len(buffer.token_container)
            for buffer in self.env.sim.places.values()
            if buffer.uid in self.env.sim.filter_nodes("machine_buffer")
        )
        return -total_tokens_in_buffer
        
        
        

    def general_soft_reward (self, feedback, terminal):
    
        if terminal:
            return -self.env.sim.clock
        
        elif  feedback['valid_move']==False:
            return -0.5
        else :
            return 0.1
        

    def general_reward (self, feedback, terminal):
        if terminal:
            return -self.env.sim.clock
        else :
            return 0


    def test_reward(self, feedback, terminal):
        

        if terminal:
            return -self.env.sim.clock
        
        else :
            
            reward =0
            reward-=0.01* (1-feedback['machine_utilisation'])
            reward+=0.05* feedback['completed_ops']
            return reward
            
        

    def calculate(self, feedback=None, terminal=False):
        """
        Compute the reward using the predefined reward function.
        """
        return self.reward_function(feedback, terminal)
