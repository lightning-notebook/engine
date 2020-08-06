from uuid import uuid4



class Identified:
    '''Base class for objects with a unique identifier.'''
    def __init__(self, id=None):
        self.id = id or uuid4()
    

    def __hash__(self):
        return self.id.int