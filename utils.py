import ast

# Thank you stack overflow
def safe_eval(s):
    whitelist = (
        ast.Expression,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.BinOp,
        ast.UnaryOp,
        ast.operator,
        ast.unaryop,
        ast.cmpop,
        ast.Num,
    )
    tree = ast.parse(s, mode="eval")
    safe_dict = {}
    valid = all(isinstance(node, whitelist) for node in ast.walk(tree))
    if valid:
        result = eval(
            compile(tree, filename="", mode="eval"), {"__builtins__": None}, safe_dict
        )
        return result
    return 0
