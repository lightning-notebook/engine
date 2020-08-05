from collections import defaultdict
from .errors import MultipleAssignmentError, CycleError


class RunOrder:
    def __init__(self, order, errors):
        self.order = order
        self.errors = errors
    

    @classmethod
    def from_notebook(cls, notebook, roots=None):
        entries = []
        exits = []
        errors = defaultdict(list)

        def dfs(cell):
            if cell in exits:
                return
            if cell in entries:
                currently_in = [c for c in entries if c not in exits]
                cycle = currently_in[currently_in.index(cell):]
                for cycle_member in cycle:
                    errors[cycle_member].append(CycleError(cycle))
                return

            entries.append(cell)
            dependencies = cls.direct_dependencies(notebook, cell)
            conflicts = cls.conflicts(notebook, cell)
            for conflict in conflicts | {cell}:
                errors[conflict] += [MultipleAssignmentError(var) for var in cell.pulled_variables(conflict)]
            for next_cell in dependencies | conflicts:
                dfs(next_cell)
            exits.append(cell)
        
        for root in roots:
            dfs(root)
        return cls(order=[c for c in reversed(exits) if c not in errors], errors=errors)
    

    @staticmethod
    def direct_dependencies(notebook, cell):
        return frozenset(c for c in notebook.cells if c.depends_on(cell))
    

    @staticmethod
    def conflicts(notebook, cell):
        return frozenset(c for c in notebook.cells if variable in c.conflicts_wth(cell))