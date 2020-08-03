from pluto.cell import Cell
from pluto.variable_access import VariableAccess


def test_variable_access():
    cell = Cell('x = y')
    assert cell.variable_access == VariableAccess(reads=['y'], writes=['x'])


def test_expression():
    cell = Cell('[11 + 12, 3]')
    cell.run({})
    assert cell.output == [23, 3]


def test_assignments():
    cell = Cell('x = 11\ny = 12')
    cell.run({})
    assert cell.output['x'] == 11
    assert cell.output['y'] == 12


def test_dependent_internal():
    cell = Cell('x = 11\ny = x + 1')
    cell.run({})
    assert cell.output['x'] == 11
    assert cell.output['y'] == 12


def test_dependent_external():
    cell = Cell('x = 11\ny = x + z')
    cell.run({'z': 7})
    assert cell.output['x'] == 11
    assert cell.output['y'] == 18
    assert 'z' not in cell.output


def test_workspace_change():
    workspace = {'z': 7}
    cell = Cell('x = 11\ny = x + z')
    cell.run(workspace=workspace)
    assert cell.output['x'] == 11
    assert cell.output['y'] == 18
    assert 'z' not in cell.output
    assert set(workspace.keys()) == {'x', 'y', 'z'}
    assert workspace['x'] == 11
    assert workspace['y'] == 18
    assert workspace['z'] == 7


def test_syntax_error():
    cell = Cell('x = +')
    cell.run({})
    assert isinstance(cell.output, SyntaxError)


def test_depend():
    a = Cell('a_var = b_var - 11')
    b = Cell('b_var = 3')
    assert a.depends_on(b)

    a.code = 'a_var = c_var + 12'
    assert not a.depends_on(b)


def test_depend_self():
    a = Cell('x = 11\nx = x + 1')
    assert not a.depends_on(a)