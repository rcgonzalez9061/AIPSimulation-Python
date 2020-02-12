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
