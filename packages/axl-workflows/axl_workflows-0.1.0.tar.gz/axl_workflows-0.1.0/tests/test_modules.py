"""
Tests for various modules to improve coverage.
"""

from axl import compiler, io, runtime


class TestCompilerModule:
    """Test cases for compiler module."""

    def test_compiler_init(self) -> None:
        """Test that compiler module can be imported."""
        assert compiler is not None
        # Test that __all__ is defined
        assert hasattr(compiler, "__all__")
        assert isinstance(compiler.__all__, list)


class TestIOModule:
    """Test cases for io module."""

    def test_io_init(self) -> None:
        """Test that io module can be imported."""
        assert io is not None
        # Test that __all__ is defined
        assert hasattr(io, "__all__")
        assert isinstance(io.__all__, list)


class TestRuntimeModule:
    """Test cases for runtime module."""

    def test_runtime_init(self) -> None:
        """Test that runtime module can be imported."""
        assert runtime is not None
        # Test that __all__ is defined
        assert hasattr(runtime, "__all__")
        assert isinstance(runtime.__all__, list)
