import ast
import functools



class VariableAccess:
    def __init__(self, reads, writes):
        self.reads = frozenset(reads)
        self.writes = frozenset(writes)
    

    @classmethod
    def from_code(cls, code):
        return cls.from_ast(ast.parse(code))
    

    @classmethod
    def from_ast(cls, ast_node):
        if isinstance(ast_node, ast.Name):
            return cls(reads=[ast_node.id], writes=[])

        if isinstance(ast_node, ast.Assign):
            targets = cls.from_ast(ast_node.targets)
            value = cls.from_ast(ast_node.value)
            return cls(reads=value.reads, writes=targets.reads | targets.writes | value.writes)
        if isinstance(ast_node, ast.AugAssign): # x += 3, for example
            target = cls.from_ast(ast_node.target)
            value = cls.from_ast(ast_node.value)
            return cls(reads=value.reads, writes=target.reads | target.writes | value.writes)
        
        if isinstance(ast_node, ast.ImportFrom):
            if ast_node.names[0].name == '*':
                raise NotImplementedError('"import *" is not supported yet!')
            return cls.from_ast(ast_node.names)
        if isinstance(ast_node, ast.alias):
            return cls(reads=[], writes=[ast_node.asname or ast_node.name])
        
        if isinstance(ast_node, ast.ClassDef):
            bases = cls.from_ast(ast_node.bases)
            keywords = cls.from_ast(ast_node.keywords)
            decorators = cls.from_ast(ast_node.decorator_list)
            body = cls.from_ast(ast_node.body) # TODO: name shadowing
            return cls(
                reads=bases.reads | keywords.reads | decorators.reads | body.reads,
                writes=[ast_node.name]
            )
        
        if isinstance(ast_node, ast.Lambda):
            return cls.from_ast(ast_node.body) # TODO: name shadowing
        if isinstance(ast_node, ast.FunctionDef):
            decorators = cls.from_ast(ast_node.decorator_list)
            args = cls.from_ast(ast_node.args) # can read variables via default values
            body = cls.from_ast(ast_node.body)
            # TODO: name shadowing - some reads and writes in body refer to local, not global variables
            return cls(reads=decorators.reads | args.reads | body.reads, writes=[ast_node.name])

        if isinstance(ast_node, ast.For):
            target = cls.from_ast(ast_node.target) # no name shadowing - target is actually written to
            iterable = cls.from_ast(ast_node.iter)
            body = cls.from_ast(ast_node.body)
            else_body = cls.from_ast(ast_node.orelse)
            return cls(
                reads=iterable.reads | body.reads | else_body.reads,
                writes=target.reads | target.writes | iterable.writes | body.writes | else_body.writes
            )
        
        if isinstance(ast_node, ast.ListComp):
            element = cls.from_ast(ast_node.elt)
            generators = cls.from_ast(ast_node.generators)
            return element | generators # TODO: name shadowing
        if isinstance(ast_node, ast.SetComp):
            element = cls.from_ast(ast_node.elt)
            generators = cls.from_ast(ast_node.generators)
            return element | generators # TODO: name shadowing
        if isinstance(ast_node, ast.DictComp):
            key = cls.from_ast(ast_node.key)
            value = cls.from_ast(ast_node.value)
            generators = cls.from_ast(ast_node.generators)
            return key | value | generators # TODO: name shadowing
        if isinstance(ast_node, ast.comprehension):
            target = cls.from_ast(ast_node.target)
            iterable = cls.from_ast(ast_node.iter)
            conditions = cls.from_ast(ast_node.ifs)
            return target | iterable | conditions # TODO: name shadowing
        
        if isinstance(ast_node, list):
            return functools.reduce(
                cls.__or__,
                [cls.from_ast(sub_ast) for sub_ast in ast_node],
                cls(reads=[], writes=[])
            )
        
        for node_type, children in node_children.items():
            if isinstance(ast_node, node_type):
                return cls.from_ast([getattr(ast_node, child) for child in children])
        
        raise NotImplementedError(f'Cannot parse {type(ast_node)} yet!')


    def __eq__(self, other):
        return self.reads == other.reads and self.writes == other.writes


    def __or__(self, other):
        return type(self)(reads=self.reads | other.reads, writes=self.writes | other.writes)
    

    def __repr__(self):
        return f'{type(self).__name__}(reads={list(self.reads)}, writes={list(self.writes)})'


node_children = {
    ast.Constant: [],
    ast.Pass: [],
    type(None): [],
    ast.Expr: ['value'],
    ast.Module: ['body'],
    ast.Import: ['names'],
    ast.Attribute: ['value'],
    ast.arguments: ['defaults', 'kw_defaults'],
    ast.Return: ['value'],
    ast.Call: ['func', 'args', 'keywords'],
    ast.keyword: ['value'],
    ast.If: ['test', 'body', 'orelse'],
    ast.IfExp: ['test', 'body', 'orelse'],
    ast.While: ['test', 'body', 'orelse'],
    ast.Tuple: ['elts'],
    ast.List: ['elts'],
    ast.Set: ['elts'],
    ast.Dict: ['keys', 'values'],
    ast.Subscript: ['value', 'slice'],
    ast.Index: ['value'],
    ast.Slice: ['lower', 'upper', 'step'],
    ast.UnaryOp: ['operand'],
    ast.BinOp: ['left', 'right'],
    ast.BoolOp: ['values'],
    ast.Compare: ['left', 'comparators']
}