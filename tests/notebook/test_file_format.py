from pluto.notebook import Notebook
from pluto.cell import Cell



class TestFileFormat:
    def test_empty(self):
        notebook = Notebook()
        remake = Notebook.from_file_format(notebook.to_file_format())
        assert len(remake.cells) == 0
    

    def test_one_cell(self):
        notebook = Notebook(cells=[
            Cell(code='2 ** 5')
        ])
        remake = Notebook.from_file_format(notebook.to_file_format())
        assert remake.cells == notebook.cells
    

    def test_ordered(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='b = a + 1')
        ])
        remake = Notebook.from_file_format(notebook.to_file_format())
        assert remake.cells == notebook.cells
    

    def test_unordered(self):
        notebook = Notebook(cells=[
            Cell(code='b = a + 1'),
            Cell(code='a = 0')
        ])
        remake = Notebook.from_file_format(notebook.to_file_format())
        assert remake.cells == notebook.cells
    

    def test_format_stability(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='b = a + 1')
        ])
        remake = Notebook.from_file_format(notebook.to_file_format())
        assert remake.to_file_format() == notebook.to_file_format()
    

    def test_cycle(self):
        notebook = Notebook(cells=[
            Cell(code='a = b - 0'),
            Cell(code='b = a + 1')
        ])
        remake = Notebook.from_file_format(notebook.to_file_format())
        assert remake.cells == notebook.cells
    

    def test_multiple_definition(self):
        notebook = Notebook(cells=[
            Cell(code='a = 0'),
            Cell(code='a = 1')
        ])
        remake = Notebook.from_file_format(notebook.to_file_format())
        assert remake.cells == notebook.cells
    