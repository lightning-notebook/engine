import ast
import functools



class VariableAccess:
    def __init__(self, reads, writes):
        self.reads = reads
        self.writes = writes
    

    @classmethod
    def from_code(cls, code):
        return cls.from_ast(ast.parse(code))
    

    @classmethod
    def from_ast(cls, ast_node):
        if isinstance(ast_node, ast.Name):
            return cls(reads=[ast_node.id], writes=[])
        if isinstance(ast_node, ast.Constant):
            return cls(reads=[], writes=[])
        if ast_node is None:
            return cls(reads=[], writes=[])
        if isinstance(ast_node, ast.Pass):
            return cls(reads=[], writes=[])
        
        if isinstance(ast_node, list):
            return functools.reduce(
                cls.__add__,
                [cls.from_ast(sub_ast) for sub_ast in ast_node],
                cls(reads=[], writes=[])
            )

        if isinstance(ast_node, ast.Expr):
            return cls.from_ast(ast_node.value)
        if isinstance(ast_node, ast.Assign):
            targets = cls.from_ast(ast_node.targets)
            value = cls.from_ast(ast_node.value)
            return cls(reads=value.reads, writes=targets.reads + targets.writes + value.writes)
        if isinstance(ast_node, ast.AugAssign): # x += 3, for example
            target = cls.from_ast(ast_node.target)
            value = cls.from_ast(ast_node.value)
            return cls(reads=value.reads, writes=target.reads + targets.writes + value.writes)
        
        if isinstance(ast_node, ast.Module):
            return cls.from_ast(ast_node.body)
        if isinstance(ast_node, ast.Import):
            return cls.from_ast(ast_node.names)
        if isinstance(ast_node, ast.ImportFrom):
            return cls.from_ast(ast_node.names)
        if isinstance(ast_node, ast.alias):
            return cls(reads=[], writes=[ast_node.asname])
        
        if isinstance(ast_node, ast.ClassDef):
            bases = cls.from_ast(ast_node.bases)
            keywords = cls.from_ast(ast_node.keywords)
            decorators = cls.from_ast(ast_node.decorator_list)
            body = cls.from_ast(ast_node.body) # TODO: name shadowing
            return cls(
                reads=bases.reads + keywords.reads + decorators.reads + body.reads,
                writes=[ast_node.name]
            )
        if isinstance(ast_node, ast.Attribute):
            return cls.from_ast(ast_node.value)
        
        if isinstance(ast_node, ast.Lambda):
            return cls.from_ast(ast_node.body)
        if isinstance(ast_node, ast.FunctionDef):
            decorators = cls.from_ast(ast_node.decorator_list)
            args = cls.from_ast(ast_node.args) # can read variables via default values
            body = cls.from_ast(ast_node.body)
            # TODO: name shadowing - some reads and writes in body refer to local, not global variables
            return cls(reads=decorators.reads + args.reads + body.reads, writes=[ast_node.name])
        if isinstance(ast_node, ast.arguments):
            return cls.from_ast(ast_node.defaults) + cls.from_ast(ast_node.kw_defaults)
        if isinstance(ast_node, ast.Return):
            return cls.from_ast(ast_node.value)

        if isinstance(ast_node, ast.Call):
            function = cls.from_ast(ast_node.func)
            arguments = cls.from_ast(ast_node.args)
            keyword_arguments = cls.from_ast(ast_node.keywords)
            return function + arguments + keyword_arguments
        if isinstance(ast_node, ast.keyword):
            return cls.from_ast(ast_node.value)
        
        if isinstance(ast_node, ast.If):
            condition = cls.from_ast(ast_node.test)
            body = cls.from_ast(ast_node.body)
            else_body = cls.from_ast(ast_node.orelse) # elif is syntax sugar for else (if ...)
            return condition + body + else_body
        if isinstance(ast_node, ast.For):
            target = cls.from_ast(ast_node.target) # no name shadowing - target is actually written to
            iterable = cls.from_ast(ast_node.iter)
            body = cls.from_ast(ast_node.body)
            else_body = cls.from_ast(ast_node.orelse)
            return cls(
                reads=iterable.reads + body.reads + else_body.reads,
                writes=target.reads + target.writes + iterable.writes + body.writes + else_body.writes
            )
        if isinstance(ast_node, ast.While):
            condition = cls.from_ast(ast_node.test)
            body = cls.from_ast(ast_node.body)
            else_body = cls.from_ast(ast_node.orelse)
            return condition + body + else_body
        
        if isinstance(ast_node, ast.Tuple):
            return cls.from_ast(ast_node.elts)
        if isinstance(ast_node, ast.List):
            return cls.from_ast(ast_node.elts)
        if isinstance(ast_node, ast.Dict):
            keys = cls.from_ast(ast_node.keys)
            values = cls.from_ast(ast_node.values)
            return keys + values
        
        if isinstance(ast_node, ast.ListComp):
            element = cls.from_ast(ast_node.elt)
            generators = cls.from_ast(ast_node.generators)
            return element + generators # TODO: name shadowing
        if isinstance(ast_node, ast.DictComp):
            key = cls.from_ast(ast_node.key)
            value = cls.from_ast(ast_node.value)
            generators = cls.from_ast(ast_node.generators)
            return key + value + generators # TODO: name shadowing
        if isinstance(ast_node, ast.comprehension):
            target = cls.from_ast(ast_node.target)
            iterable = cls.from_ast(ast_node.iter)
            conditions = cls.from_ast(ast_node.ifs)
            return iterable + conditions # TODO: name shadowing
        
        if isinstance(ast_node, ast.Subscript):
            indexed = cls.from_ast(ast_node.value)
            index = cls.from_ast(ast_node.slice)
            return indexed + index
        if isinstance(ast_node, ast.Index):
            return cls.from_ast(ast_node.value)
        if isinstance(ast_node, ast.Slice):
            lower = cls.from_ast(ast_node.lower)
            upper = cls.from_ast(ast_node.upper)
            step = cls.from_ast(ast_node.step)
            return lower + upper + step

        if isinstance(ast_node, ast.UnaryOp):
            return cls.from_ast(ast_node.operand)
        if isinstance(ast_node, ast.BinOp):
            left = cls.from_ast(ast_node.left)
            right = cls.from_ast(ast_node.right)
            return left + right
        if isinstance(ast_node, ast.Compare):
            left = cls.from_ast(ast_node.left)
            comparators = cls.from_ast(ast_node.comparators)
            return left + comparators
        
        raise NotImplementedError(f'Cannot parse {type(ast_node)} yet!')



    def __add__(self, other):
        return type(self)(reads=self.reads + other.reads, writes=self.writes + other.writes)
    

    def __repr__(self):
        return f'{type(self).__name__}(reads={self.reads}, writes={self.writes})'