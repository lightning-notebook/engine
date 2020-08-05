from collections import defaultdict
from .errors import MultipleAssignmentError, CycleError


class RunOrder:
    def __init__(self, order, errors):
        self.order = order
        self.errors = errors
    

    @classmethod
    def from_notebook(cls, notebook, roots=None):
        if roots is None:
            roots = notebook.cells
        
        discovered_cells = []
        errors = defaultdict(list)

        def discover_cells(starting_cell):
            if starting_cell in discovered_cells:
                return
            discovered_cells.append(cell)
            dependencies = cls.direct_dependencies(notebook, starting_cell)
            conflicts = cls.conflicts(notebook, starting_cell)
            for conflict in conflicts | {starting_cell}:
                errors[conflict] += [MultipleAssignmentError(var) for var in cell.pulled_variables(conflict)]
            for next_cell in dependencies | conflicts:
                dfs(next_cell)
        
        for root in roots:
            discover_cells(root)

        entries = []
        exits = []

        def topological_scan(cell):
            if cell in exits:
                return
            if cell in entries:
                currently_in = [c for c in entries if c not in exits]
                cycle = currently_in[currently_in.index(cell):]
                for cycle_member in cycle:
                    errors[cycle_member].append(CycleError(cycle))
                return
            entries.append(cell)
            for next_cell in cls.direct_dependencies(notebook, cell):
                topological_scan(next_cell)
            exits.append(cell)
        
        for cell in discovered_cells:
            topological_scan(cell)
        return cls(order=[c for c in reversed(exits) if c not in errors], errors=errors)
    

    @staticmethod
    def direct_dependencies(notebook, cell):
        return frozenset(c for c in notebook.cells if c.depends_on(cell))
    

    @staticmethod
    def conflicts(notebook, cell):
        return frozenset(c for c in notebook.cells if variable in c.conflicts_wth(cell))