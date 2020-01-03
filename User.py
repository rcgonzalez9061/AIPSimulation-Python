class User:
    
    def __init__(self, id):
        self.id = id
        self.friends = set()
        
    def add_friends(self, friends):
        self.friends.update(friends)
        
    def getFriends():
        return self.friends
