import json
import pandas as pd

class Simulation:
    DEFAULT_POST_CHANCE = 0.1
    DEFAULT_NUM_USERS = 100
    DEFAULT_TICK_LIMIT = -1 # no limit default
    DEFAULT_NUM_FRIENDS = 5
    DEFAULT_INITIAL_TICK = 0
    
    def __init__(self, parameters):
        # Set defaults
        self.tick = DEFAULT_INITIAL_TICK
        self.tick_limit = DEFAULT_TICK_LIMIT
        self.post_chance = DEFAULT_POST_CHANCE
        self.num_users = DEFAULT_NUM_USERS
        self.num_friends = DEFAULT_NUM_FRIENDS
        
        self.parse_parameters(parameters)
        
        # Intiate users
        self.users = pd.Series([User(i) for i in range(self.num_users)])
        # Add random friends
        for i in range(self.users.size):
            user = self.users[i]
            user.add_friends(set(self.users.sample(self.num_friends)))
            
        # Initiate values df
        self.values = pd.DataFram(columns = self.topics,
                                  index = self.users.index)
    
    def run():
        # If no limit, continue until interrupted
        if (self.tick_limit == -1):
            while (true):
                self.tick()
                self.record()
        else: # run until limit reached
            while (tick <= tickLimit):
                self.tick()
                self.record()
                self.tick += 1
    
    def tick():
        self.posts = pd.DataFrame(columns = ["user", "topic"])
        # Add post
        df.loc[df.shape[0]] = {'user': user, "topic": topic}
    
    def record():
        return ...
    
    def parse_parameters(self, parameters):
        parameters_dict = json.loads(parameters)
        
        if ("tickLimit" in parameters_dict):
            self.tick_limit = parameters_dict["tickLimit"]
            
        if ("postChance" in parameters_dict):
            self.post_chance = parameters_dict["postChance"]
            
        if ("numUsers" in parameters_dict):
            self.num_users = parameters_dict["numUsers"]
                
        if ("numFriends" in parameters_dict):
            self.num_friends = parameters_dict["numFriends"]
        
        try:
            self.topics = parameters_dict["topics"]
        except:
            print("No topics provided. Please review your parameters!")
