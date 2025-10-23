
import subprocess

def test_basic_generation():
    """Check that the script returns non-empty output for a normal phrase"""
    result = subprocess.run(
        ["python3", "continue_phrase.py", "Hello world"],
        capture_output=True,
        text=True,
        check=True
    )
    output = result.stdout.strip()
    assert "Hello world" in output
    assert len(output) > len("Hello world")

def test_markov_mode():
    """Check that the script works with --use-markov flag"""
    result = subprocess.run(
        ["python3", "continue_phrase.py", "Test phrase", "--use-markov"],
        capture_output=True,
        text=True,
        check=True
    )
    output = result.stdout.strip()
    assert "Test phrase" in output
    assert len(output) > len("Test phrase")

def test_verbose_mode():
    """Check that the script works with --verbose flag"""
    result = subprocess.run(
        ["python3", "continue_phrase.py", "Verbose test", "--verbose"],
        capture_output=True,
        text=True,
        check=True
    )
    output = result.stdout.strip()
    assert "Verbose test" in output
    assert len(output) > len("Verbose test")

def test_empty_input():
    """Check that the script handles empty input gracefully"""
    result = subprocess.run(
        ["python3", "continue_phrase.py", ""],
        capture_output=True,
        text=True,
        check=True
    )
    output = result.stdout.strip()
    assert len(output) > 0

def test_markov_empty_input():
    """Check that --use-markov does not fail with empty input"""
    result = subprocess.run(
        ["python3", "continue_phrase.py", "", "--use-markov"],
        capture_output=True,
        text=True,
        check=True
    )
    output = result.stdout.strip()
    assert len(output) > 0

