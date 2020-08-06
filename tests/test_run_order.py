from pluto.notebook import Notebook
from pluto.run_order import RunOrder
from pluto.cell import Cell
from pluto.errors import NameConflictError, CycleError



class TestRunOrder:
    def test_independent(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='b = 1')
        ])
        run_order = RunOrder.from_notebook(notebook)
        assert run_order.order == notebook.cells
        assert run_order.errors == {}


    def test_basic_ordered(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='b = a + 1')
        ])
        run_order = RunOrder.from_notebook(notebook)
        assert run_order.order == notebook.cells
        assert run_order.errors == {}


    def test_basic_unordered(self):
        notebook = Notebook(cells=[
            Cell(code='b = a + 0'),
            Cell(code='a = 1')
        ])
        run_order = RunOrder.from_notebook(notebook)
        assert run_order.order == list(reversed(notebook.cells))
        assert run_order.errors == {}


    def test_name_conflict(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='a = 1')
        ])
        run_order = RunOrder.from_notebook(notebook)
        assert run_order.order == []
        assert run_order.errors == {
            notebook.cells[0]: [NameConflictError('a')],
            notebook.cells[1]: [NameConflictError('a')]
        }


    def test_name_conflict_consequence(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='a = 1\nb = 1'),
            Cell(code='b * 2')
        ])
        run_order = RunOrder.from_notebook(notebook)
        assert run_order.order == [notebook.cells[2]]
        assert run_order.errors == {
            notebook.cells[0]: [NameConflictError('a')],
            notebook.cells[1]: [NameConflictError('a')]
        }


    def test_cycle(self):
        notebook = Notebook(cells=[
            Cell(code='a = b - 0'),
            Cell(code='b = a + 1')
        ])
        run_order = RunOrder.from_notebook(notebook)
        assert run_order.order == []
        assert run_order.errors == {
            notebook.cells[0]: [CycleError(notebook.cells)],
            notebook.cells[1]: [CycleError(notebook.cells)]
        }


    def test_cycle_consequence(self):
        notebook = Notebook(cells=[
            Cell(code='a = b - 0'),
            Cell(code='b = a + 1\nc = -1'),
            Cell(code='c // 2')
        ])
        run_order = RunOrder.from_notebook(notebook)
        assert run_order.order == [notebook.cells[2]]
        assert run_order.errors == {
            notebook.cells[0]: [CycleError(notebook.cells[:2])],
            notebook.cells[1]: [CycleError(notebook.cells[:2])]
        }