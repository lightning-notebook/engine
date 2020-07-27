from .variable_access import VariableAccess


class Cell:
    def __init__(self, code=''):
        self.code = code
    

    @property
    def code(self):
        return self._code
    

    @code.setter
    def code(self, value):
        self._code = value
        self.variable_access = VariableAccess.from_code(value)
    

    def __repr__(self):
        return f'{type(self).__name__} with id {id(self)}:\n{self.code}'