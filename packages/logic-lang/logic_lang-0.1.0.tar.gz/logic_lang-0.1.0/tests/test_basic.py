"""Basic tests for the logic_lang package."""

import pytest
from logic_lang import RuleParser, RuleInterpreter


def test_import():
    """Test that the package can be imported."""
    from logic_lang import RuleParser, RuleInterpreter

    assert RuleParser is not None
    assert RuleInterpreter is not None


def test_basic_parsing():
    """Test basic rule parsing."""
    parser = RuleParser()

    # Test simple rule
    script = """
    expect var1
    define test = var1
    """

    ast = parser.parse(script)
    assert ast is not None
    assert len(ast.statements) == 2


def test_interpreter_creation():
    """Test that interpreter can be created."""
    interpreter = RuleInterpreter()
    assert interpreter is not None


if __name__ == "__main__":
    test_import()
    test_basic_parsing()
    test_interpreter_creation()
    print("All tests passed!")
