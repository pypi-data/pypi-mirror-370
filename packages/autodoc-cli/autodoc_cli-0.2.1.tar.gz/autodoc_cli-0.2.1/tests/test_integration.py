"""Integration test to verify tree-sitter refactoring works correctly."""

from autodoc.adapters.c_adapter import CAdapter
from autodoc.scanner import find_comment_nodes_in_tree, get_indentation_from_tree_sitter


def test_tree_sitter_comment_detection_integration():
    """Test that comment detection works with real tree-sitter parsing."""
    adapter = CAdapter()
    source = b"""
    /* This is a test comment */
    int test_function() {
        return 0;
    }
    """

    tree = adapter.parser.parse(source)
    comments = find_comment_nodes_in_tree(tree, source)

    # Should find one comment
    assert len(comments) == 1
    start_byte, end_byte, comment_text = comments[0]

    # Verify the comment content
    assert b"/* This is a test comment */" in comment_text.encode("utf-8")
    assert start_byte < end_byte


def test_tree_sitter_indentation_detection_integration():
    """Test that indentation detection works with real tree-sitter parsing."""
    adapter = CAdapter()
    source = b"    int test_function() {\n        return 0;\n    }\n"

    tree = adapter.parser.parse(source)

    # Find the function definition node
    function_node = None
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "function_definition":
            function_node = node
            break
        for child in node.children:
            stack.append(child)

    assert function_node is not None

    # Test indentation detection
    indentation = get_indentation_from_tree_sitter(source, function_node, adapter)

    # Should detect the 4-space indentation
    assert indentation == "    "


def test_tree_sitter_function_analysis_integration():
    """Test that function analysis works with real tree-sitter parsing."""
    adapter = CAdapter()
    source = b"""
    /**
     * Test function documentation
     */
    int test_function(int param) {
        return param * 2;
    }
    """

    functions = list(adapter.iter_functions(source))

    # Should find one function
    assert len(functions) == 1
    func = functions[0]

    # Verify function information
    assert func.name == "test_function"
    assert func.has_doc()  # Should have documentation
    assert func.doc_range is not None

    # Verify ranges are valid
    assert func.full_range.start < func.full_range.end
    assert func.signature_range.start < func.signature_range.end
    assert func.body_range.start < func.body_range.end

    # Verify the function signature contains the parameter
    signature = source[func.signature_range.start : func.signature_range.end].decode(
        "utf-8"
    )
    assert "int param" in signature
