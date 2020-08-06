from .identified import Identified


class Notebook(Identified):
    '''Represents a single .py file - can consist of multiple cells.'''
    def __init__(self, *, id=None, cells=[]):
        super().__init__(id=id)
        self.cells = cells
    

    def commit(self, cell, code=None):
        '''
        Run a cell and its dependencies, optionally changing its code.
        '''
        code = code if code is not None else cell.code

        old_dependencies = all_dependencies(self, cell)
        cell.code = code
        new_dependencies = all_dependencies(self, cell)
        # TODO