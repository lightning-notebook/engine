from .identified import Identified
from .run_order import RunOrder
from .errors import MultipleReactivityErrors


class Notebook(Identified):
    '''Represents a single .py file - can consist of multiple cells.'''
    def __init__(self, *, id=None, cells=[]):
        super().__init__(id=id)
        self.cells = cells
        self.workspace = {}
    

    def run(self, cells=None):
        '''
        Run some cells and their dependencies, optionally changing their code.
        `cells` can be either [cell1, cell2, ...] or {cell1: new_code1, ...}
        '''
        old_run_order = RunOrder.from_notebook(self, cells)

        if isinstance(cells, dict):
            for cell, new_code in cells.items():
                cell.code = new_code

        new_run_order = RunOrder.from_notebook(self, cells)
        run_order = RunOrder(
            order=new_run_order.order + [c for c in old_run_order.order if c not in new_run_order.order],
            errors=new_run_order.errors
        )

        for cell in run_order.order + list(run_order.errors):
            for variable in cell.variable_access.writes:
                if variable in self.workspace:
                    del self.workspace[variable]
        for cell in run_order.order:
            cell.run(workspace=self.workspace)
        for cell, errors in run_order.errors.items():
            cell.mode = 'error'
            cell.output = MultipleReactivityErrors.pack(errors)