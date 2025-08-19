from __future__ import annotations
import ast
import operator as op
from typing import Any, Dict, Union
from .base import ToolBase

_ALLOWED_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
    ast.UAdd: op.pos, ast.USub: op.neg,
}

def _eval_expr(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Num):  # py<3.8
        return node.n  # type: ignore
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        return _ALLOWED_OPS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp):
        return _ALLOWED_OPS[type(node.op)](_eval_expr(node.operand))
    if isinstance(node, ast.Expression):
        return _eval_expr(node.body)  # type: ignore
    raise ValueError("Unsupported expression")

def safe_eval(expr: str) -> Union[int, float]:
    tree = ast.parse(expr, mode="eval")
    return _eval_expr(tree)

class Calculator(ToolBase):
    name = "calculator"
    description = "Evaluate a math expression with 'expr', or compute using a,b,op (+,-,*,/,%)."
    schema = {
        "type": "object",
        "properties": {
            "expr": {"type": "string", "description": "Math expression, e.g., (2+3)*4"},
            "a": {"type": "number"},
            "b": {"type": "number"},
            "op": {"type": "string", "enum": ["+", "-", "*", "/", "%"]},
        },
        "required": [],
        "additionalProperties": True
    }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        expr = kwargs.get("expr")
        if expr:
            val = safe_eval(str(expr))
            return {"ok": True, "expr": expr, "value": val}
        a = float(kwargs.get("a", 0))
        b = float(kwargs.get("b", 0))
        opn = str(kwargs.get("op", "+"))
        result = {
            "+": a + b, "-": a - b, "*": a * b, "/": a / b if b else float("inf"),
            "%": a % b if b else float("nan")
        }.get(opn)
        if result is None:
            raise ValueError("Unsupported op; use one of + - * / % or provide expr")
        return {"ok": True, "a": a, "b": b, "op": opn, "value": result}
