from pluto.notebook import Notebook
from pluto.cell import Cell
from pluto.errors import CycleError



class TestNotebook:
    def test_empty(self):
        notebook = Notebook(cells=[])
        notebook.run() # we're just testing if this doesn't error
    

    def test_simple(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='b = a + 1')
        ])
        notebook.run()
        assert notebook.cells[0].output == {'a': 0}
        assert notebook.cells[1].output == {'b': 1}
    

    def test_reverse(self):
        notebook = Notebook(cells=[
            Cell(code='b = a * 0'),
            Cell(code='a = 1')
        ])
        notebook.run()
        assert notebook.cells[0].output == {'b': 0}
        assert notebook.cells[1].output == {'a': 1}
    

    def test_cycle(self):
        notebook = Notebook(cells=[
            Cell(code='a = b + 0'),
            Cell(code='b = a - 1')
        ])
        notebook.run()
        assert notebook.cells[0].output == CycleError(notebook.cells)
        assert notebook.cells[1].output == CycleError(notebook.cells)
    

    def test_cycle(self):
        notebook = Notebook(cells=[
            Cell(code='a = b + 0'),
            Cell(code='b = a - 1')
        ])
        notebook.run()
        assert notebook.cells[0].output == CycleError(notebook.cells)
        assert notebook.cells[1].output == CycleError(notebook.cells)
    

    def test_rerun(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='b = a + 1')
        ])
        notebook.run()
        notebook.run(cells={notebook.cells[0]: 'a = 17'})
        assert notebook.cells[0].output == {'a': 17}
        assert notebook.cells[1].output == {'b': 18}
    

    def test_error_propagation(self):
        notebook = Notebook(cells=[
            Cell(code='a = b + 0'),
            Cell(code='b = a - 1'),
            Cell(code='c = a + b')
        ])
        notebook.run()
        assert notebook.cells[0].output == CycleError(notebook.cells[:2])
        assert notebook.cells[1].output == CycleError(notebook.cells[:2])
        assert isinstance(notebook.cells[2].output, NameError)