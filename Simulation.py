import json
import pandas as pd
import random
from User import User
import numpy as np

class Simulation:
    DEFAULT_POST_CHANCE = 0.1
    DEFAULT_NUM_USERS = 100
    DEFAULT_TICK_LIMIT = -1 # no limit default
    DEFAULT_NUM_FRIENDS = 5
    DEFAULT_INITIAL_TICK = 0
    DEFAULT_POST_INFLUENCE = 0.1
    MIN_VALUE = -10
    MAX_VALUE = 10
    VALUE_RANGE = MAX_VALUE - MIN_VALUE
    
    def __init__(self, parameters):
        # Set defaults
        self.tick_count = Simulation.DEFAULT_INITIAL_TICK
        self.tick_limit = Simulation.DEFAULT_TICK_LIMIT
        self.post_chance = Simulation.DEFAULT_POST_CHANCE
        self.num_users = Simulation.DEFAULT_NUM_USERS
        self.num_friends = Simulation.DEFAULT_NUM_FRIENDS
        self.post_influence = Simulation.DEFAULT_POST_INFLUENCE
        
        self.parse_parameters(parameters)
        
        # Intiate users
        self.users = pd.Series([User(i) for i in range(self.num_users)])
        # Add random friends
        for i in range(self.users.size):
            user = self.users[i]
            user.add_friends(pd.Series(self.users.index).sample(self.num_friends))
            
        # Initiate values df
        self.values = (
            pd.DataFrame(np.random.rand(self.users.size, len(self.topics)) * Simulation.VALUE_RANGE - (Simulation.VALUE_RANGE/2),
                         index = self.users.index,
                         columns = self.topics)
        )
        # Initiate deltas df
        self.deltas = self.values.copy()
    
    def run(self):
        # If no limit, continue until interrupted
        if (self.tick_limit == -1):
            while True:
                print("Beginning tick ".format(self.tick_count))
                self.tick()
#                 self.record()
        else: # run until limit reached
            while self.tick_count <= self.tick_limit:
                print("Beginning tick {}".format(self.tick_count))
                self.tick()
#                 self.record()
                self.tick_count += 1
        print("Finshed.")
    
    def tick(self):
        # reset deltas
        self.deltas = self.deltas * 0.0
        
        # Init posts df
        self.posts = pd.DataFrame(columns = ["user", "topic"])
        
        for user in self.users:
            # check if users posts
            if (random.uniform(0,1) < self.post_chance):
                # Add post
                topic = self.pick_topic(user)
                self.posts.loc[self.posts.shape[0]] = {'user': user.id, "topic": topic}
                
                # update deltas
                self.deltas.loc[user.friends, topic] += (
                    (self.values.loc[user.friends, topic] - self.values.loc[user.id, topic]) * self.post_influence
                )
            
            # consolidate deltas
        self.values += self.deltas
        self.values.clip(Simulation.MIN_VALUE, Simulation.MAX_VALUE)
                
    def pick_topic(self, user):
        """Picks a topic, may consider user's preference in future""" 
        return self.topics[random.randint(0, len(self.topics)-1)]
    
    def record(self):
        return ...
    
    def parse_parameters(self, parameters):
        with open(parameters, 'r') as text:
            parameters_dict = json.loads(text.read())
        
        if "tickLimit" in parameters_dict:
            self.tick_limit = parameters_dict["tickLimit"]
            
        if "postChance" in parameters_dict:
            self.post_chance = parameters_dict["postChance"]
            
        if "numUsers" in parameters_dict:
            self.num_users = parameters_dict["numUsers"]
                
        if "numFriends" in parameters_dict:
            self.num_friends = parameters_dict["numFriends"]
        
        if "postInfluence" in parameters_dict:
            self.post_influence = parameters_dict["postInfluence"]
        
        try:
            self.topics = parameters_dict["topics"]
        except:
            print("No topics provided. Please review your parameters!")
