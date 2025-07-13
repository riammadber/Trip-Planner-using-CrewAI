from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import ast
import operator

class CalculationInput(BaseModel):
    operation: str = Field(..., description="The mathematical expression to evaluate")

class CalculatorTools(BaseTool):
    name: str = "Make a calculation"
    description: str = """Useful to perform any mathematical calculations, 
    like sum, minus, multiplication, division, etc.
    The input should be a mathematical expression, e.g. '200*7' or '5000/2*10'"""
    args_schema: type[BaseModel] = CalculationInput

    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate mathematical expressions without using eval()"""
        # Define allowed operators
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
        }
        
        def _eval(node):
            if isinstance(node, ast.Constant):  # Numbers
                return float(node.value)
            elif isinstance(node, ast.BinOp):  # Binary operations
                left = _eval(node.left)
                right = _eval(node.right)
                return operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):  # Unary operations (like negative numbers)
                operand = _eval(node.operand)
                return operators[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported operation: {type(node)}")
        
        try:
            tree = ast.parse(expression, mode='eval')
            return _eval(tree.body)
        except (ValueError, KeyError, SyntaxError, ZeroDivisionError) as e:
            raise ValueError(f"Invalid mathematical expression: {e}")

    def _run(self, operation: str) -> float:
        return self._safe_eval(operation)

    async def _arun(self, operation: str) -> float:
        raise NotImplementedError("Async not implemented")
