from uuid import UUID, uuid4



class Identified:
    '''Base class for objects with a unique identifier.'''
    def __init__(self, id=None):
        if id is None:
            self.id = uuid4()
        elif isinstance(id, UUID):
            self.id = id
        elif isinstance(id, int):
            self.id = UUID(int=id)
        else:
            self.id = UUID(id)
    

    def __eq__(self, other):
        return self.id == other.id
    

    def __hash__(self):
        return self.id.int