import ast
from .variable_access import VariableAccess


class Cell:
    def __init__(self, code=''):
        self.code = code
    

    def run(self, workspace, filename='Pluto cell'):
        for mode in ['eval', 'exec']:
            try:
                parsed = ast.parse(self.code, filename=filename, mode=mode)
                compiled = compile(self.code, filename=filename, mode=mode)
            except SyntaxError as err:
                syntax_error = err
            else:
                break
        else:
            self.variable_access = VariableAccess(reads=[], writes=[])
            self.output = syntax_error
            return

        self.variable_access = VariableAccess.from_ast(parsed)
        if mode == 'eval':
            self.output = eval(compiled, workspace)
        elif mode == 'exec':
            exec(compiled, workspace)
            del workspace['__builtins__']
            self.output = VariableValues.from_workspace(workspace, self.variable_access.writes)
    

    def __repr__(self):
        return f'{self.code}'



class VariableValues(dict):
    @classmethod
    def from_workspace(cls, workspace, variable_names):
        return cls({var: workspace[var] for var in variable_names})


    def __repr__(self):
        return '\n'.join(f'{var} = {value}' for var, value in self.items())