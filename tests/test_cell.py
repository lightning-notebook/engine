from pluto.cell import Cell



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