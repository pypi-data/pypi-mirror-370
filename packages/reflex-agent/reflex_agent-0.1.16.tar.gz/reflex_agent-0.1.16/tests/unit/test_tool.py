from flexai.tool import Tool


def example_function() -> str:
    """A simple test function to use with Tool."""
    return "test result"


def test_tool_from_function():
    tool = Tool.from_function(example_function)
    assert tool.name == "example_function"
    assert tool.description == "A simple test function to use with Tool."
    assert tool.params == ()
    assert tool.return_type == "str"
    assert tool.fn() == "test result"
