from collections import defaultdict
from .errors import NameConflictError, CycleError


class RunOrder:
    def __init__(self, order, errors):
        self.errors = {cell: cell_errors for cell, cell_errors in errors.items() if len(cell_errors) > 0}
        self.order = [c for c in order if c not in self.errors]
    

    @classmethod
    def from_notebook(cls, notebook, roots=None):
        if roots is None:
            roots = notebook.cells
        
        discovered_cells = []
        errors = defaultdict(list)

        def discover_cells(starting_cell):
            if starting_cell in discovered_cells:
                return
            discovered_cells.append(starting_cell)
            dependencies = cls.direct_dependencies(notebook, starting_cell)
            conflicts = cls.conflicts(notebook, starting_cell)
            conflict_vars = frozenset(var for conflict in conflicts for var in starting_cell.common_writes(conflict))
            errors[starting_cell] += [NameConflictError(var) for var in conflict_vars]
            for next_cell in dependencies | conflicts:
                discover_cells(next_cell)
        
        for root in roots:
            discover_cells(root)
         # this helps stay as close to notebook order as possible:
        discovered_cells.sort(key=lambda cell: notebook.cells.index(cell), reverse=True)

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
        return cls(order=reversed(exits), errors=errors)
    

    @staticmethod
    def direct_dependencies(notebook, cell):
        return frozenset(c for c in notebook.cells if c.depends_on(cell))
    

    @staticmethod
    def conflicts(notebook, cell):
        return frozenset(c for c in notebook.cells if c.conflicts_with(cell))