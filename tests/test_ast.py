"""
tests/test_ast.py — Unit tests for ast_parser.py

Covers:
- Simple variable assignments
- Multiple targets on one line
- AugAssign (+=, -=, etc.)
- Loop body assignments
- Nested function assignments
- JSON-serializable output shape from analyze()
"""

import ast
import os

import pytest

from ast_parser import find_assignments, analyze


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(source: str) -> ast.Module:
    """Parse a source string and return its AST module."""
    return ast.parse(source)


# ---------------------------------------------------------------------------
# find_assignments tests
# ---------------------------------------------------------------------------

class TestFindAssignments:

    def test_simple_assignment(self):
        source = "\nx = 10\ny = 20\n"
        tree = _parse(source)
        result = find_assignments(tree)
        assert result == [(2, "x"), (3, "y")]

    def test_multi_target_assignment(self):
        """a = b = 5 should detect both names."""
        source = "\na = b = 5\n"
        tree = _parse(source)
        result = find_assignments(tree)
        assert (2, "a") in result
        assert (2, "b") in result

    def test_aug_assign(self):
        """AugAssign (+=) should be detected."""
        source = "\ntotal = 0\nfor i in range(5):\n    total += i\n"
        tree = _parse(source)
        result = find_assignments(tree)
        # total appears twice: initial assign + augmented assign
        names = [name for _, name in result]
        assert names.count("total") == 2

    def test_loop_variable(self):
        source = "\ntotal = 0\nfor i in range(5):\n    total += i\n"
        tree = _parse(source)
        result = find_assignments(tree)
        assert (2, "total") in result
        assert (4, "total") in result

    def test_nested_function(self):
        source = (
            "\ndef outer():\n"
            "    x = 10\n"
            "    def inner():\n"
            "        y = 20\n"
            "    return x\n"
        )
        tree = _parse(source)
        result = find_assignments(tree)
        assert (3, "x") in result
        assert (5, "y") in result

    def test_empty_source(self):
        tree = _parse("")
        result = find_assignments(tree)
        assert result == []

    def test_no_assignments(self):
        source = "print('hello')\n"
        tree = _parse(source)
        result = find_assignments(tree)
        assert result == []

    def test_tuple_unpack(self):
        source = "\na, b = 1, 2\n"
        tree = _parse(source)
        result = find_assignments(tree)
        names = [name for _, name in result]
        assert "a" in names
        assert "b" in names

    def test_sorted_by_line(self):
        source = "\nz = 3\na = 1\nm = 2\n"
        tree = _parse(source)
        result = find_assignments(tree)
        lines = [line for line, _ in result]
        assert lines == sorted(lines)


# ---------------------------------------------------------------------------
# analyze() tests (JSON-serializable output)
# ---------------------------------------------------------------------------

class TestAnalyze:

    def test_returns_list_of_dicts(self, sample_script_path):
        result = analyze(sample_script_path)
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_dict_keys(self, sample_script_path):
        result = analyze(sample_script_path)
        for item in result:
            assert "line_number" in item
            assert "variable_name" in item

    def test_line_numbers_are_ints(self, sample_script_path):
        result = analyze(sample_script_path)
        for item in result:
            assert isinstance(item["line_number"], int)
            assert item["line_number"] > 0

    def test_variable_names_are_strings(self, sample_script_path):
        result = analyze(sample_script_path)
        for item in result:
            assert isinstance(item["variable_name"], str)
            assert len(item["variable_name"]) > 0

    def test_known_variables_detected(self, sample_script_path):
        """The sample script defines x, name, flag, total, average, result, done."""
        result = analyze(sample_script_path)
        detected_names = {item["variable_name"] for item in result}
        expected = {"x", "name", "flag", "total", "average", "result", "done"}
        assert expected.issubset(detected_names), (
            f"Missing variables: {expected - detected_names}"
        )

    def test_file_not_found_raises(self, tmp_path):
        missing = str(tmp_path / "does_not_exist.py")
        with pytest.raises((FileNotFoundError, OSError)):
            analyze(missing)
