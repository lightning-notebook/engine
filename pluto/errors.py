class ReactivityError:
    '''Base class for all reactivity-related errors.'''



class MultipleAssignmentError(ReactivityError):
    def __init__(self, errored_variable):
        super().__init__()
        self.errored_variable = errored_variable
    

    def __repr__(self):
        return f'{type(self).__name__}: {self.errored_variable}'



class CycleError(ReactivityError):
    def __init__(self, cells_in_cycle):
        super().__init__()
        self.cells_in_cycle = cells_in_cycle
    

    def __repr__(self):
        return f'{type(self).__name__}: {self.cells_in_cycle}'
