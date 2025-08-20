"""Basic tests for autodoc-cli."""



from autodoc.adapters.c_adapter import CAdapter
from autodoc.adapters.base import ByteRange, FunctionInfo


def test_c_adapter_initialization():
    """Test that CAdapter can be initialized."""
    adapter = CAdapter()
    assert adapter.language_name == "c"
    assert adapter.language is not None
    assert adapter.parser is not None


def test_byte_range():
    """Test ByteRange dataclass."""
    byte_range = ByteRange(start=0, end=10)
    assert byte_range.start == 0
    assert byte_range.end == 10


def test_function_info():
    """Test FunctionInfo dataclass."""
    byte_range = ByteRange(start=0, end=10)
    func_info = FunctionInfo(
        name="test_function",
        signature_range=byte_range,
        body_range=byte_range,
        full_range=byte_range,
        doc_range=None,
    )
    assert func_info.name == "test_function"
    assert func_info.signature_range == byte_range
    assert func_info.body_range == byte_range
    assert func_info.full_range == byte_range
    assert func_info.doc_range is None


def test_function_info_with_doc():
    """Test FunctionInfo with documentation range."""
    byte_range = ByteRange(start=0, end=10)
    doc_range = ByteRange(start=0, end=5)
    func_info = FunctionInfo(
        name="test_function",
        signature_range=byte_range,
        body_range=byte_range,
        full_range=byte_range,
        doc_range=doc_range,
    )
    assert func_info.has_doc() is True


def test_function_info_without_doc():
    """Test FunctionInfo without documentation range."""
    byte_range = ByteRange(start=0, end=10)
    func_info = FunctionInfo(
        name="test_function",
        signature_range=byte_range,
        body_range=byte_range,
        full_range=byte_range,
        doc_range=None,
    )
    assert func_info.has_doc() is False


def test_c_adapter_walk_method():
    """Test the _walk method of CAdapter."""
    adapter = CAdapter()
    # Create a mock node-like object for testing
    class MockNode:
        def __init__(self, children=None):
            self.children = children or []
    
    root = MockNode([
        MockNode([MockNode()]),
        MockNode()
    ])
    
    nodes = list(adapter._walk(root))
    assert len(nodes) == 4  # root + 2 children + 1 grandchild


def test_imports():
    """Test that all main modules can be imported."""
    import autodoc
    import autodoc.adapters
    import autodoc.cli
    import autodoc.db
    import autodoc.editing
    import autodoc.llm
    import autodoc.scanner
    
    # Test that the modules exist
    assert autodoc is not None
    assert autodoc.adapters is not None
    assert autodoc.cli is not None
    assert autodoc.db is not None
    assert autodoc.editing is not None
    assert autodoc.llm is not None
    assert autodoc.scanner is not None
