"""Enhanced AST transformer for emoji operators."""

import ast
from typing import Dict, Any

class EmojiOperatorTransformer(ast.NodeTransformer):
    """Transform emoji operators in Python code."""
    
    # Mapping of emoji operators to AST operator nodes
    EMOJI_TO_OP = {
        '➕': ast.Add,
        '➖': ast.Sub,
        '✖️': ast.Mult,
        '✖': ast.Mult,  # Alternative without variation selector
        '➗': ast.Div,
        '💪': ast.Pow,
        '🔢': ast.Mod,
        '⬇️': ast.FloorDiv,
        '⬇': ast.FloorDiv,  # Alternative
        
        # Comparison operators
        '🟰': ast.Eq,
        '≠': ast.NotEq,
        '⬆️': ast.Gt,
        '⬆': ast.Gt,
        '📈': ast.GtE,
        '📉': ast.LtE,
        
        # Logical operators (need special handling)
        '✅': ast.And,
        '🔀': ast.Or,
        '❌': ast.Not,
    }
    
    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        """Transform binary operations with emoji operators."""
        # First visit child nodes
        self.generic_visit(node)
        
        # Check if we have emoji operator in source
        if hasattr(node, 'emoji_op'):
            op_class = self.EMOJI_TO_OP.get(node.emoji_op)
            if op_class:
                node.op = op_class()
        
        return node
    
    def visit_Compare(self, node: ast.Compare) -> ast.Compare:
        """Transform comparison operations with emoji operators."""
        self.generic_visit(node)
        
        # Transform emoji operators in comparisons
        new_ops = []
        for op in node.ops:
            if hasattr(op, 'emoji_op'):
                op_class = self.EMOJI_TO_OP.get(op.emoji_op)
                if op_class:
                    new_ops.append(op_class())
                else:
                    new_ops.append(op)
            else:
                new_ops.append(op)
        
        node.ops = new_ops
        return node
    
    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.UnaryOp:
        """Transform unary operations with emoji operators."""
        self.generic_visit(node)
        
        if hasattr(node, 'emoji_op') and node.emoji_op == '❌':
            node.op = ast.Not()
        
        return node


def preprocess_emoji_operators(code: str) -> str:
    """Preprocess code to mark emoji operators for transformation."""
    import re
    
    # Clean up variation selectors
    code = code.replace('\uFE0F', '')
    
    # Map of emoji operators to temporary placeholders
    emoji_ops = {
        '➕': '__EMOJI_ADD__',
        '➖': '__EMOJI_SUB__',
        '✖': '__EMOJI_MUL__',
        '➗': '__EMOJI_DIV__',
        '💪': '__EMOJI_POW__',
        '🔢': '__EMOJI_MOD__',
        '⬇': '__EMOJI_FLOORDIV__',
        '🟰': '__EMOJI_EQ__',
        '≠': '__EMOJI_NE__',
        '⬆': '__EMOJI_GT__',
        '📈': '__EMOJI_GE__',
        '📉': '__EMOJI_LE__',
        '✅': '__EMOJI_AND__',
        '🔀': '__EMOJI_OR__',
        '❌': '__EMOJI_NOT__',
    }
    
    # Replace emoji operators with placeholders
    for emoji, placeholder in emoji_ops.items():
        code = code.replace(emoji, f' {placeholder} ')
    
    return code


def transform_emoji_operators(code: str) -> str:
    """Transform code with emoji operators to valid Python."""
    # Preprocess to handle emoji operators
    preprocessed = preprocess_emoji_operators(code)
    
    # Parse the preprocessed code
    try:
        tree = ast.parse(preprocessed)
    except SyntaxError:
        # If preprocessing fails, try original
        tree = ast.parse(code)
    
    # Apply transformations
    transformer = EmojiOperatorTransformer()
    transformed_tree = transformer.visit(tree)
    
    # Fix missing locations
    ast.fix_missing_locations(transformed_tree)
    
    # Compile back to code
    return compile(transformed_tree, '<emoji>', 'exec')


# Make operators available as functions
class EmojiOperators:
    """Emoji operators as callable functions."""
    
    @staticmethod
    def add(a, b):
        """➕ operator"""
        return a + b
    
    @staticmethod
    def sub(a, b):
        """➖ operator"""
        return a - b
    
    @staticmethod
    def mul(a, b):
        """✖️ operator"""
        return a * b
    
    @staticmethod
    def div(a, b):
        """➗ operator"""
        return a / b
    
    @staticmethod
    def pow(a, b):
        """💪 operator"""
        return a ** b
    
    @staticmethod
    def mod(a, b):
        """🔢 operator"""
        return a % b
    
    # Create emoji method aliases
    def __getattr__(self, name):
        emoji_methods = {
            '➕': self.add,
            '➖': self.sub,
            '✖️': self.mul,
            '✖': self.mul,
            '➗': self.div,
            '💪': self.pow,
            '🔢': self.mod,
        }
        return emoji_methods.get(name, lambda *args: None)


# Global instance
emoji_ops = EmojiOperators()