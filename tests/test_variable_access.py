import pytest
from pluto.variable_access import VariableAccess



def test_import():
    assert VariableAccess.from_code('import somemodule') == VariableAccess(reads=[], writes=['somemodule'])
    assert VariableAccess.from_code('import m as alias') == VariableAccess(reads=[], writes=['alias'])
    assert VariableAccess.from_code('from a import b') == VariableAccess(reads=[], writes=['b'])
    assert VariableAccess.from_code('from a import b as c') == VariableAccess(reads=[], writes=['c'])
    with pytest.raises(NotImplementedError):
        VariableAccess.from_code('from somemodule import *')


def test_arithmetic():
    assert VariableAccess.from_code('x + 3') == VariableAccess(reads=['x'], writes=[])
    assert VariableAccess.from_code('-x') == VariableAccess(reads=['x'], writes=[])
    assert VariableAccess.from_code('x // y') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('x < 3 < y') == VariableAccess(reads=['x', 'y'], writes=[])


def test_boolean():
    assert VariableAccess.from_code('x or y') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('x and y') == VariableAccess(reads=['x', 'y'], writes=[])


def test_assign():
    assert VariableAccess.from_code('var = 11') == VariableAccess(reads=[], writes=['var'])
    assert VariableAccess.from_code('var = e ^ x - pi ^ 2 / 6') == VariableAccess(reads=['e', 'x', 'pi'], writes=['var'])
    assert VariableAccess.from_code('a, b = x, y') == VariableAccess(reads=['x', 'y'], writes=['a', 'b'])
    assert VariableAccess.from_code('a, b = sometuple') == VariableAccess(reads=['sometuple'], writes=['a', 'b'])
    assert VariableAccess.from_code('var += "zzz"') == VariableAccess(reads=[], writes=['var'])
    assert VariableAccess.from_code('var = var * 2') == VariableAccess(reads=['var'], writes=['var'])


def test_if():
    assert VariableAccess.from_code('if x < 3:\n\ty += z') == VariableAccess(reads=['x', 'z'], writes=['y'])
    assert VariableAccess.from_code('if a or b:\n\tw += x\nelse:\n\ty /= z') == VariableAccess(reads=['a', 'b', 'x', 'z'], writes=['w', 'y'])
    assert VariableAccess.from_code('if a or b:\n\tx += y\nelse:\n\ty -= z') == VariableAccess(reads=['a', 'b', 'y', 'z'], writes=['x', 'y'])
    assert VariableAccess.from_code('a if b < c else d') == VariableAccess(reads=['a', 'b', 'c', 'd'], writes=[])


def test_loops():
    assert VariableAccess.from_code('while x < 3:\n\tx += y') == VariableAccess(reads=['x', 'y'], writes=['x'])
    assert VariableAccess.from_code('while x < 3:\n\ty += z') == VariableAccess(reads=['x', 'z'], writes=['y'])
    assert VariableAccess.from_code('for x in range(3):\n\tprint(x)') == VariableAccess(reads=['x', 'print', 'range'], writes=['x'])
    assert VariableAccess.from_code('for x in range(3):\n\tprint(y)') == VariableAccess(reads=['y', 'print', 'range'], writes=['x'])
    assert VariableAccess.from_code('for x in range(z):\n\tprint(y)') == VariableAccess(reads=['y', 'z', 'print', 'range'], writes=['x'])


def test_functions():
    assert VariableAccess.from_code('lambda x: 2') == VariableAccess(reads=[], writes=[])
    # the following tests fail because shadowing is not implemented yet
    # assert VariableAccess.from_code('lambda x: x ** 2') == VariableAccess(reads=[], writes=[])
    # assert VariableAccess.from_code('square = lambda x: x ** 2') == VariableAccess(reads=[], writes=['square'])
    # assert VariableAccess.from_code('square = lambda x=x: x ** 2') == VariableAccess(reads=['x'], writes=['square'])
    # assert VariableAccess.from_code('add = lambda x: x + y') == VariableAccess(reads=['y'], writes=['add'])
    # assert VariableAccess.from_code('add = lambda x=x: x + y') == VariableAccess(reads=['x', 'y'], writes=['add'])
    # assert VariableAccess.from_code('add = lambda x, y: x + y') == VariableAccess(reads=[], writes=['add'])
    # assert VariableAccess.from_code('add = lambda x, y=z: x + y') == VariableAccess(reads=['z'], writes=['add'])

    assert VariableAccess.from_code('def f(): return') == VariableAccess(reads=[], writes=['f'])
    # assert VariableAccess.from_code('def square(x):\n\treturn x ** 2') == VariableAccess(reads=[], writes=['square'])
    # assert VariableAccess.from_code('def square(x=x):\n\treturn x ** 2') == VariableAccess(reads=['x'], writes=['square'])
    # assert VariableAccess.from_code('def square(x=y):\n\treturn x ** 2') == VariableAccess(reads=['y'], writes=['square'])
    # assert VariableAccess.from_code('def thing(x):\n\treturn x + y') == VariableAccess(reads=['y'], writes=['thing'])
    # assert VariableAccess.from_code('def thing(x=x):\n\treturn x + y') == VariableAccess(reads=['x', 'y'], writes=['thing'])
    # assert VariableAccess.from_code('def thing(x, y=z):\n\treturn x + y') == VariableAccess(reads=['z'], writes=['thing'])


def test_classes():
    assert VariableAccess.from_code('class Test:\n\tpass') == VariableAccess(reads=[], writes=['Test'])
    # the following tests fail because shadowing is not implemented yet
    # assert VariableAccess.from_code('class Test:\n\tdef method(self):\n\t\treturn 3') == VariableAccess(reads=[], writes=['Test'])
    # assert VariableAccess.from_code('class Test:\n\tdef method(self, x):\n\t\treturn x') == VariableAccess(reads=[], writes=['Test'])
    # assert VariableAccess.from_code('class Test:\n\tdef method(self, x):\n\t\treturn y') == VariableAccess(reads=['y'], writes=['Test'])
    # assert VariableAccess.from_code('class Test:\n\ty=7\n\tdef method(self):\n\t\treturn y') == VariableAccess(reads=['y'], writes=['Test'])
    # assert VariableAccess.from_code('class Test:\n\ty=7\n\tdef method(self):\n\t\treturn self.y') == VariableAccess(reads=[], writes=['Test'])
    # assert VariableAccess.from_code('class Test:\n\ty=x') == VariableAccess(reads=['x'], writes=['Test'])
    # assert VariableAccess.from_code('class Test:\n\tx=7\n\ty=x') == VariableAccess(reads=[], writes=['Test'])
    assert VariableAccess.from_code('a.b') == VariableAccess(reads=['a'], writes=[])
    assert VariableAccess.from_code('f(a + 3).b') == VariableAccess(reads=['a', 'f'], writes=[])


def test_base_types():
    assert VariableAccess.from_code('') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('4') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('3.4') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('"asdf"') == VariableAccess(reads=[], writes=[])
    # assert VariableAccess.from_code('f"{varname}"') == VariableAccess(reads=['varname'], writes=[])

    assert VariableAccess.from_code('()') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('(1, 2, 3)') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('(1, 2, x)') == VariableAccess(reads=['x'], writes=[])
    
    assert VariableAccess.from_code('[]') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('[1, 2, 3]') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('[1, 2, x]') == VariableAccess(reads=['x'], writes=[])

    assert VariableAccess.from_code('set()') == VariableAccess(reads=['set'], writes=[])
    assert VariableAccess.from_code('{1, 2, 3}') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('{1, 2, x}') == VariableAccess(reads=['x'], writes=[])
    
    assert VariableAccess.from_code('{}') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('{1: 2}') == VariableAccess(reads=[], writes=[])
    assert VariableAccess.from_code('{1: x}') == VariableAccess(reads=['x'], writes=[])
    assert VariableAccess.from_code('{x: 1}') == VariableAccess(reads=['x'], writes=[])
    assert VariableAccess.from_code('{x: y}') == VariableAccess(reads=['x', 'y'], writes=[])


def test_syntax_errors():
    with pytest.raises(SyntaxError):
        VariableAccess.from_code('x = ')
    with pytest.raises(SyntaxError):
        VariableAccess.from_code('[')
    with pytest.raises(SyntaxError):
        VariableAccess.from_code('x =+ ')
    with pytest.raises(SyntaxError):
        VariableAccess.from_code('2:1:3:1')
    with pytest.raises(SyntaxError):
        VariableAccess.from_code('f x')


def test_comprehensions():
    assert VariableAccess.from_code('[x for x in y]') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('[x ** 2 for x in y]') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('[x for y in z for x in y]') == VariableAccess(reads=['x', 'y', 'z'], writes=[])
    assert VariableAccess.from_code('[x for x in y if x < 3]') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('[x + y for y in z]') == VariableAccess(reads=['x', 'y', 'z'], writes=[])

    assert VariableAccess.from_code('{x for x in y}') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('{x ** 2 for x in y}') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('{x for y in z for x in y}') == VariableAccess(reads=['x', 'y', 'z'], writes=[])
    assert VariableAccess.from_code('{x for x in y if x < 3}') == VariableAccess(reads=['x', 'y'], writes=[])

    assert VariableAccess.from_code('{x: z for x in y}') == VariableAccess(reads=['x', 'y', 'z'], writes=[])
    assert VariableAccess.from_code('{x: x ** 2 for x in y}') == VariableAccess(reads=['x', 'y'], writes=[])
    assert VariableAccess.from_code('{y: x for y in z for x in y}') == VariableAccess(reads=['x', 'y', 'z'], writes=[])
    assert VariableAccess.from_code('{x: -x for x in y if x < 3}') == VariableAccess(reads=['x', 'y'], writes=[])


def test_indexing():
    assert VariableAccess.from_code('a[b]') == VariableAccess(reads=['a', 'b'], writes=[])
    assert VariableAccess.from_code('(a + b)[c]') == VariableAccess(reads=['a', 'b', 'c'], writes=[])
    assert VariableAccess.from_code('(a + b)[c + d]') == VariableAccess(reads=['a', 'b', 'c', 'd'], writes=[])
    assert VariableAccess.from_code('a[b:c]') == VariableAccess(reads=['a', 'b', 'c'], writes=[])
    assert VariableAccess.from_code('a[b:c:d]') == VariableAccess(reads=['a', 'b', 'c', 'd'], writes=[])