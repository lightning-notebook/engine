class Notebook:
    def __init__(self, cells=[]):
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