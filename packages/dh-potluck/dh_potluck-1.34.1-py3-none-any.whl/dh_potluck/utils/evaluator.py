import re
from ast import Add, BinOp, Constant, Div, Mult, Sub, UnaryOp, USub, dump, parse
from re import sub
from typing import Optional


def _safe_addition(x, y):
    return (x or 0) + (y or 0)


def _safe_subtraction(x, y):
    return (x or 0) - (y or 0)


def _safe_multiplication(x, y):
    return None if x is None or y is None else x * y


def _safe_division(x, y):
    if y is None or y == 0:
        raise ZeroDivisionError()
    if x is None:
        return None
    return x / y


def _safe_negative(x):
    return -x if x is not None else 0


PERMITTED_OPERATORS = {
    Add: _safe_addition,
    Sub: _safe_subtraction,
    Mult: _safe_multiplication,
    Div: _safe_division,
    USub: _safe_negative,
}


class MathExpressionEvaluator:
    @staticmethod
    def evaluate_formula(formula: str) -> Optional[float]:
        """Evaluate a string formula using ast functions.

        Note:
            None multiplication, None division, or zero division will result in a None result.
            In None addition and None subtraction, None will be treated as Zero

        Args:
            formula (str): The formula to be parsed and evaluated using ast functions. This function
        should only include numbers and operators inside a string i.e. '6/2*(1/2)'.

        Returns:
            Optional[float]: The value of the evaluated formula.
        """

        def _preprocess_formula(formula: str) -> str:
            formatted_formula = ''.join(formula.split())  # remove whitespace
            formatted_formula = formatted_formula.replace('x', '*')
            return sub(r'(\d)\s*\(', r'\1*(', formatted_formula)

        def _evaluate(node):
            if isinstance(node, Constant):
                return node.n
            elif isinstance(node, BinOp):
                return PERMITTED_OPERATORS[type(node.op)](
                    _evaluate(node.left), _evaluate(node.right)
                )
            elif isinstance(node, UnaryOp):
                return PERMITTED_OPERATORS[type(node.op)](_evaluate(node.operand))
            raise TypeError(f'Unsupported operation: {dump(node)}')

        def _safe_eval(formula):
            try:
                node = parse(formula, mode='eval').body
                return _evaluate(node)
            except ZeroDivisionError:
                return None

        def _evaluate_subexpr(match):
            subexpr = match.group(0)
            return str(_safe_eval(subexpr))

        subexpr_pattern = r'\([^()]*\)'
        processed_formula = _preprocess_formula(formula)
        while '(' in processed_formula:
            processed_formula = re.sub(subexpr_pattern, _evaluate_subexpr, processed_formula)

        return _safe_eval(processed_formula)
