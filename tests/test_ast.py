import ast

from ast_parser import find_assignments



def parse_source(source):
    """
    Convert source code string into AST.
    """
    return ast.parse(source)


def test_simple_assignment():

    source = """
x = 10
y = 20
"""

    tree = parse_source(source)

    result = find_assignments(tree)

    assert result == [
        (2, "x"),
        (3, "y")
    ]


def test_multi_assignment():

    source = """
a = b = 5
"""

    tree = parse_source(source)

    result = find_assignments(tree)

    assert result == [
        (2, "a"),
        (2, "b")
    ]


def test_loop_assignment():

    source = """
total = 0

for i in range(5):
    total += i
"""

    tree = parse_source(source)

    result = find_assignments(tree)

    assert result == [
        (2, "total"),
        (5, "total")
    ]


def test_nested_function():

    source = """
def outer():

    x = 10

    def inner():
        y = 20

    return x
"""

    tree = parse_source(source)

    result = find_assignments(tree)

    assert result == [
        (4, "x"),
        (7, "y")
    ]