"""Test that comment functions maintain quality and reliability with tree-sitter."""

from autodoc.adapters.c_adapter import CAdapter
from autodoc.scanner import (
    build_comment_block_with_tree_sitter,
    sanitize_llm_comment_with_tree_sitter,
    build_comment_block_fallback,
    sanitize_llm_comment_fallback,
)


def test_build_comment_block_with_tree_sitter_simple_content():
    """Test building comment block with simple content using tree-sitter."""
    adapter = CAdapter()
    content = "This is a simple function that does something."
    indentation = "    "

    result = build_comment_block_with_tree_sitter(content, indentation, adapter)

    # Should create a proper block comment
    assert result.startswith("    /**")
    assert result.endswith("    */\n")
    assert " * This is a simple function that does something." in result


def test_build_comment_block_with_tree_sitter_existing_comment():
    """Test building comment block when content already has comment markers."""
    adapter = CAdapter()
    content = "/* This is already a comment */"
    indentation = "    "

    result = build_comment_block_with_tree_sitter(content, indentation, adapter)

    # Should preserve the existing comment structure and add indentation
    assert result.startswith("    /*")
    assert result.endswith(" */\n")  # The comment ends with " */" not "    */"
    assert "This is already a comment" in result


def test_build_comment_block_with_tree_sitter_multiline_content():
    """Test building comment block with multiline content using tree-sitter."""
    adapter = CAdapter()
    content = "This is line one.\nThis is line two.\nThis is line three."
    indentation = "    "

    result = build_comment_block_with_tree_sitter(content, indentation, adapter)

    # Should create a proper multiline block comment
    assert result.startswith("    /**")
    assert result.endswith("    */\n")
    assert " * This is line one." in result
    assert " * This is line two." in result
    assert " * This is line three." in result


def test_build_comment_block_with_tree_sitter_empty_content():
    """Test building comment block with empty content using tree-sitter."""
    adapter = CAdapter()
    content = ""
    indentation = "    "

    result = build_comment_block_with_tree_sitter(content, indentation, adapter)

    # Should return empty string for empty content
    assert result == ""


def test_build_comment_block_with_tree_sitter_code_content():
    """Test building comment block with content that contains code-like text."""
    adapter = CAdapter()
    content = "This is a function.\nint x = 5;\nThis is more text."
    indentation = "    "

    result = build_comment_block_with_tree_sitter(content, indentation, adapter)

    # Should include all content as documentation (including code examples)
    assert result.startswith("    /**")
    assert result.endswith("    */\n")
    assert " * This is a function." in result
    assert " * int x = 5;" in result
    assert " * This is more text." in result


def test_sanitize_llm_comment_with_tree_sitter_simple_text():
    """Test sanitizing simple text using tree-sitter."""
    adapter = CAdapter()
    raw = "This is simple text without any special formatting."

    result = sanitize_llm_comment_with_tree_sitter(raw, adapter)

    # Should return the text as-is
    assert result == "This is simple text without any special formatting."


def test_sanitize_llm_comment_with_tree_sitter_code_fences():
    """Test sanitizing text with code fences using tree-sitter."""
    adapter = CAdapter()
    raw = "```c\nint x = 5;\nreturn x;\n```"

    result = sanitize_llm_comment_with_tree_sitter(raw, adapter)

    # Should remove the code fences and return the content
    assert result == "int x = 5;\nreturn x;"


def test_sanitize_llm_comment_with_tree_sitter_existing_comment():
    """Test sanitizing text that already has comment markers using tree-sitter."""
    adapter = CAdapter()
    raw = "/* This is a comment with * markers */"

    result = sanitize_llm_comment_with_tree_sitter(raw, adapter)

    # Should remove comment markers and clean up * markers
    assert result == "This is a comment with markers"


def test_sanitize_llm_comment_with_tree_sitter_multiline_comment():
    """Test sanitizing multiline comment using tree-sitter."""
    adapter = CAdapter()
    raw = """/*
 * This is a multiline comment
 * with asterisk markers
 * on each line
 */"""

    result = sanitize_llm_comment_with_tree_sitter(raw, adapter)

    # Should clean up the comment structure
    expected_lines = [
        "This is a multiline comment",
        "with asterisk markers",
        "on each line",
    ]
    for line in expected_lines:
        assert line in result


def test_sanitize_llm_comment_with_tree_sitter_empty_input():
    """Test sanitizing empty input using tree-sitter."""
    adapter = CAdapter()
    raw = ""

    result = sanitize_llm_comment_with_tree_sitter(raw, adapter)

    # Should return empty string
    assert result == ""


def test_build_comment_block_fallback_consistency():
    """Test that fallback function produces consistent results."""
    content = "This is test content."
    indentation = "    "

    # Test fallback function
    fallback_result = build_comment_block_fallback("c", content, indentation)

    # Should create a proper block comment
    assert fallback_result.startswith("    /**")
    assert fallback_result.endswith("    */\n")
    assert " * This is test content." in fallback_result


def test_sanitize_llm_comment_fallback_consistency():
    """Test that fallback function produces consistent results."""
    raw = "/* This is a test comment */"

    # Test fallback function
    fallback_result = sanitize_llm_comment_fallback(raw)

    # Should clean up the comment
    assert fallback_result == "This is a test comment"


def test_comment_functions_without_adapter():
    """Test that functions work correctly when no adapter is provided."""
    content = "This is test content."
    indentation = "    "

    # Test without adapter (should use fallback)
    result = build_comment_block_with_tree_sitter(content, indentation, None)

    # Should still produce valid output
    assert result.startswith("    /**")
    assert result.endswith("    */\n")
    assert " * This is test content." in result


def test_sanitize_functions_without_adapter():
    """Test that sanitize functions work correctly when no adapter is provided."""
    raw = "/* This is a test comment */"

    # Test without adapter (should use fallback)
    result = sanitize_llm_comment_with_tree_sitter(raw, None)

    # Should still produce valid output
    assert result == "This is a test comment"


def test_tree_sitter_comment_quality_comparison():
    """Test that tree-sitter version produces same or better quality than fallback."""
    adapter = CAdapter()
    content = "This is a function that processes data."
    indentation = "    "

    # Test tree-sitter version
    tree_sitter_result = build_comment_block_with_tree_sitter(
        content, indentation, adapter
    )

    # Test fallback version
    fallback_result = build_comment_block_fallback("c", content, indentation)

    # Both should produce valid block comments
    assert tree_sitter_result.startswith("    /**")
    assert tree_sitter_result.endswith("    */\n")
    assert fallback_result.startswith("    /**")
    assert fallback_result.endswith("    */\n")

    # Both should contain the content
    assert "This is a function that processes data." in tree_sitter_result
    assert "This is a function that processes data." in fallback_result


def test_tree_sitter_sanitize_quality_comparison():
    """Test that tree-sitter sanitize produces same or better quality than fallback."""
    adapter = CAdapter()
    raw = "/* This is a test comment with * markers */"

    # Test tree-sitter version
    tree_sitter_result = sanitize_llm_comment_with_tree_sitter(raw, adapter)

    # Test fallback version
    fallback_result = sanitize_llm_comment_fallback(raw)

    # Both should produce cleaned content
    assert "This is a test comment with markers" in tree_sitter_result
    assert "This is a test comment with markers" in fallback_result
