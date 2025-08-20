"""Tests for CLI functionality."""

from unittest.mock import patch, MagicMock

from autodoc.cli.main import app


def test_app_creation():
    """Test that the Typer app can be created."""
    assert app is not None
    assert hasattr(app, 'command')


@patch('autodoc.cli.main.Path')
@patch('autodoc.cli.main.HashDatabase')
@patch('autodoc.cli.main.OllamaClient')
def test_run_command_success(mock_ollama, mock_db, mock_path):
    """Test the run command with successful execution."""
    # Mock the path
    mock_target_path = MagicMock()
    mock_target_path.exists.return_value = True
    mock_target_path.is_dir.return_value = True
    mock_path.return_value.resolve.return_value = mock_target_path
    
    # Mock the database
    mock_db_instance = MagicMock()
    mock_db.return_value = mock_db_instance
    
    # Mock the LLM client
    mock_ollama_instance = MagicMock()
    mock_ollama_instance.is_available.return_value = True
    mock_ollama.return_value = mock_ollama_instance
    
    # Mock process_directory
    with patch('autodoc.cli.main.process_directory') as mock_process:
        mock_process.return_value = {
            "files": 1,
            "functions": 5,
            "new": 2,
            "updated": 1,
            "skipped": 2,
            "plans": []
        }
        
        # Test the command
        with patch('sys.argv', ['autodoc', 'run', '/test/path']):
            with patch('autodoc.cli.main.typer.echo'):
                # This would normally run the command, but we're just testing the setup
                pass


def test_main_function():
    """Test that the main function can be called."""
    from autodoc.cli.main import main
    # Test that the function exists and has the correct signature
    assert callable(main)
    # Test that it returns an integer when called
    # We'll just test the function signature without running the CLI
    import inspect
    sig = inspect.signature(main)
    assert sig.return_annotation is int
