import subprocess
import tempfile
import os
import pytest
import time
from pathlib import Path

class TestBasicGeneration:
    """Test basic phrase generation functionality"""
    
    def test_basic_generation(self, continue_phrase_script):
        """Check that the script returns non-empty output for a normal phrase"""
        result = subprocess.run(
            ["python3", continue_phrase_script, "Hello world"],
            capture_output=True,
            text=True,
            timeout=60  # Add timeout to prevent hanging
        )
        assert result.returncode == 0, f"Script failed with stderr: {result.stderr}"
        output = result.stdout.strip()
        assert "Hello world" in output
        assert len(output) > len("Hello world")

    @pytest.mark.parametrize("phrase", [
        "Test phrase",
        "Machine learning",
        "Artificial intelligence"
    ])
    def test_markov_mode(self, continue_phrase_script, phrase):
        """Check that the script works with --use-markov flag"""
        result = subprocess.run(
            ["python3", continue_phrase_script, phrase, "--use-markov"],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Markov mode failed with stderr: {result.stderr}"
        output = result.stdout.strip()
        assert phrase in output
        assert len(output) > len(phrase)

    def test_verbose_mode(self, continue_phrase_script):
        """Check that the script works with --verbose flag"""
        result = subprocess.run(
            ["python3", continue_phrase_script, "Verbose test", "--verbose"],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Verbose mode failed with stderr: {result.stderr}"
        output = result.stdout.strip()
        assert "Verbose test" in output
        assert len(output) > len("Verbose test")
        # Check that verbose output contains timing information
        # Note: verbose info might be in stdout or stderr depending on implementation
        combined_output = (result.stdout + result.stderr).lower()
        assert any(keyword in combined_output for keyword in ["time", "memory", "mb", "markov", "transformers"])
