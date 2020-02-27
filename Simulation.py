import json
import pandas as pd
import numpy as np
import sys

class User:

    def __init__(self, id):
        self.id = id
        self.friends = set()

    def add_friends(self, friends):
        if self.id in friends:
            friends.remove(self.id)
        self.friends.update(friends)

    def getFriends(self):
        return self.friends

def IPC_const(diff):
    """
    Simply returns one, simulates posts that influence all opinions of a topic equally.
    """
    return 1

def IPC_sin(diff):
    """
    Takes a difference vector, derived from the difference of a Series of a
    user's friends' values and a user's value on a topic.

    Returns the vector with an function meant to simulate Identity Protected
    Cognition.
    """
    return np.sin(np.pi * ((diff/25) + 0.5))

def IPC_linear(diff):
    """
    Takes a difference vector, derived from the difference of a Series of a
    user's friends' values and a user's value on a topic.

    Returns the vector with an function meant to simulate Identity Protected
    Cognition.
    """
    diff = abs(diff)
    return (diff / -10) + 1

def IPC_quadratic(diff):
    """
    Takes a difference vector, derived from the difference of a Series of a
    user's friends' values and a user's value on a topic.

    Returns the vector with an function meant to simulate Identity Protected
    Cognition.
    """
    return -(diff/15)**2 + 1

def IPC_log(diff):
    """
    Takes a difference vector, derived from the difference of a Series of a
    user's friends' values and a user's value on a topic.

    Returns the vector with an function meant to simulate Identity Protected
    Cognition.
    """
    diff = abs(diff)
    return np.log(-diff + 20.3) - np.log(20.3) + 1

class Simulation:
    DEFAULT_POST_CHANCE = 0.1
    DEFAULT_NUM_USERS = 100
    DEFAULT_TICK_LIMIT = -1  # no limit default
    DEFAULT_NUM_FRIENDS = 5
    DEFAULT_INITIAL_TICK = -1
    DEFAULT_POST_INFLUENCE = 0.1
    MIN_VALUE = -10
    MAX_VALUE = 10
    VALUE_RANGE = MAX_VALUE - MIN_VALUE
    DEFAULT_VALUES_PATH = "values record.csv"
    DEFAULT_POSTS_PATH = "post record.csv"
    DEFAULT_IPC_FUNC = 'sin'

    IPC_map = {"sin": IPC_sin,
                "linear": IPC_linear,
                "quadratic": IPC_quadratic,
                "log": IPC_log,
                "const": IPC_const
    }

    def __init__(self, parameters):
        # Defaults
        self.tick_count = Simulation.DEFAULT_INITIAL_TICK
        self.tick_limit = Simulation.DEFAULT_TICK_LIMIT
        self.post_chance = Simulation.DEFAULT_POST_CHANCE
        self.num_users = Simulation.DEFAULT_NUM_USERS
        self.num_friends = Simulation.DEFAULT_NUM_FRIENDS
        self.post_influence = Simulation.DEFAULT_POST_INFLUENCE
        self.values_path = Simulation.DEFAULT_VALUES_PATH
        self.posts_path = Simulation.DEFAULT_POSTS_PATH
        self.IPC_func = self.IPC_map[self.DEFAULT_IPC_FUNC]
        self.users = None
        self.seed =  None

        self.parse_parameters(parameters)

        if self.users is None: # if users and friends haven't already been generated
            # Initialize users
            self.users = pd.Series([User(i) for i in range(self.num_users)])
            # Add random friends
            for i in range(self.users.size):
                user = self.users[i]
                user.add_friends(set(pd.Series(self.users.index).sample(self.num_friends)))

            # reset random seed for consistency
            if self.seed is not None:
                np.random.seed(self.seed)

        # Initiate values df
        self.values = (
            pd.DataFrame(np.random.uniform(
                            Simulation.MIN_VALUE,
                            Simulation.MAX_VALUE,
                            (self.num_users, len(self.topics))),
                         index=self.users.index,
                         columns=self.topics)
        )


    def run(self):
        # Initiate deltas df
        self.deltas = self.values.copy()

        # write intial empty record
        pd.DataFrame(columns=["user", "topic", "tick"]).to_csv(self.posts_path, index=False)

        # Initialize values record with initial state
        values_record = self.values.copy()
        values_record['tick'] = np.full(self.num_users, self.tick_count)
        values_record['user'] = self.values.index
        values_record = values_record.astype({'user': int,
                                              'tick': int})
        values_record.to_csv(self.values_path, index=False)

        # If no limit, continue until interrupted
        if (self.tick_limit == -1):
            while True:
                try:
                    self.tick_count += 1
                    print("\rBeginning tick {}".format(self.tick_count), end="")
                    self.tick()
                    self.update_record()
                except (KeyboardInterrupt, SystemExit):
                    print("Exiting simulation...")
                    break

        else:  # run until limit reached
            while self.tick_count < self.tick_limit:
                try:
                    self.tick_count += 1
                    print("\rBeginning tick {}, {}% complete.".format(
                        self.tick_count,
                        round(((self.tick_count) / self.tick_limit) * 100, 2)
                    ), end="")
                    self.tick()
                    self.update_record()
                except (KeyboardInterrupt, SystemExit):
                    print("Exiting simulation...")
                    break
        print("\nFinshed.")

    def tick(self):
        # reset deltas
        self.deltas = self.deltas * 0.0
        posts = pd.DataFrame(columns=["user", "topic", "tick"])

        for user in self.users:
            # check if users posts
            if (np.random.uniform(0, 1) <= self.post_chance):
                # Add post
                topic = self.pick_topic(user)
                posts.loc[posts.shape[0]] = {'user': user.id, "topic": topic, "tick": self.tick_count}

                # update deltas
                diff = (self.values.loc[user.friends, topic] - self.values.loc[user.id, topic])
                magnitude = self.values.loc[user.id, topic] * self.post_influence
                self.deltas.loc[user.friends, topic] += (
                        self.IPC_func(diff) * magnitude
                )

        # add deltas
        self.values += self.deltas
        self.values = self.values.clip(Simulation.MIN_VALUE, Simulation.MAX_VALUE)

        # write posts
        posts.to_csv(self.posts_path, mode='a',index=False, header=False)

    def pick_topic(self, user):
        """Picks a topic, may consider user's preference in future"""
        return self.topics[np.random.randint(0, len(self.topics))]

    def update_record(self):
        record = self.values.copy()
        record['tick'] = np.full(self.num_users, self.tick_count)
        record['user'] = record.index
        record = record.astype({'user': int,
                                'tick': int})
        record.to_csv(self.values_path, mode='a', header=False, index=False)

    def save_adjacency_matrix(self, path="adj_matrix.csv"):
        adj_mat = pd.DataFrame(
                    np.zeros((self.users.size, self.users.size))
                ).astype(int)
        for user in self.users:
            adj_mat.loc[user.id, user.friends] = 1
        adj_mat.to_csv(path, header=False, index=False)

    def init_users_graph(self, matrix_path):
        adj_matrix = pd.read_csv(matrix_path, header=None).astype(int)
        # assert num_users aligns with the matrix provided
        if self.num_users != adj_matrix.shape[0]:
            raise ValueError("""num_users parameter does not match length of adjacency
            # num_users: {}, length: {}""".format(self.num_users, adj_matrix.shape[0]))

        # Initialize users
        self.users = pd.Series([User(i) for i in range(self.num_users)])

        for user in self.users:
            user.add_friends(set(adj_matrix.columns[adj_matrix.loc[user.id] == 1]))
        # for i in adj_matrix.index:
        #     user = self.users[i]
        #     user.add_friends(set(adj_matrix.columns[adj_matrix.loc[i] == 1]))

    def parse_parameters(self, parameters):
        with open(parameters, 'r') as text:
            parameters_dict = json.loads(text.read())

        if "tick_limit" in parameters_dict:
            self.tick_limit = parameters_dict["tick_limit"]

        if "post_chance" in parameters_dict:
            self.post_chance = parameters_dict["post_chance"]

        if "num_users" in parameters_dict:
            self.num_users = parameters_dict["num_users"]

        if "num_friends" in parameters_dict:
            self.num_friends = parameters_dict["num_friends"]

        if "post_influence" in parameters_dict:
            self.post_influence = parameters_dict["post_influence"]

        if "values_path" in parameters_dict:
            self.values_path = parameters_dict["values_path"]

        if "posts_path" in parameters_dict:
            self.posts_path = parameters_dict["posts_path"]

        if "IPC_func" in parameters_dict:
            self.IPC_func = self.IPC_map[parameters_dict["IPC_func"]]

        if "seed" in parameters_dict:
            self.seed = parameters_dict["seed"]
            np.random.seed(parameters_dict["seed"])

        if "friend_matrix" in parameters_dict:
            self.init_users_graph(parameters_dict["friend_matrix"])

        try:
            self.topics = parameters_dict["topics"]
        except:
            sys.exit("No topics provided. Please review your parameters!")
