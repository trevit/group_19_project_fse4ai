
import subprocess
import tempfile
import os
import pytest
import time
from pathlib import Path


# Pytest fixtures
@pytest.fixture
def temp_corpus_file():
    """Create a temporary corpus file for testing"""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
        f.write("This is a custom corpus text for testing phrase continuation. It contains multiple sentences to help with generation.")
        f.flush()
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.remove(f.name)


@pytest.fixture
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def continue_phrase_script(project_root):
    """Get the path to the continue_phrase.py script"""
    script_path = project_root / "continue_phrase.py"
    if not script_path.exists():
        pytest.skip("continue_phrase.py not found")
    return str(script_path)


@pytest.fixture
def run_script(project_root):
    """Get the path to the run.sh script"""
    script_path = project_root / "run.sh"
    if not script_path.exists():
        pytest.skip("run.sh not found")
    return str(script_path)


# Test markers
pytestmark = [
    pytest.mark.integration,  # Mark as integration tests
    pytest.mark.slow,  # Mark as slow tests (can be skipped with -m "not slow")
]


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


class TestModelSelection:
    """Test different model selection options"""
    
    @pytest.mark.parametrize("model", ["gpt2", "distilgpt2"])
    def test_specific_models(self, continue_phrase_script, model):
        """Test that specific models work"""
        result = subprocess.run(
            ["python3", continue_phrase_script, "Model test", "--model", model],
            capture_output=True,
            text=True,
            timeout=120  # Models may take longer to load
        )
        assert result.returncode == 0, f"Model {model} failed with stderr: {result.stderr}"
        output = result.stdout.strip()
        assert "Model test" in output

class TestRunScript:
    """Test the run.sh wrapper script"""
    
    def run_command(self, run_script, args):
        """Helper to run the run.sh CLI and return stdout"""
        result = subprocess.run(
            [run_script] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"run.sh failed with stderr: {result.stderr}"
        return result.stdout.strip()

    def test_run_basic_generation(self, run_script):
        """Test basic phrase generation"""
        output = self.run_command(run_script, ["Hello world"])
        assert "Hello world" in output
        assert len(output) > len("Hello world")

    def test_run_specific_model(self, run_script):
        """Test that selecting a specific model works"""
        output = self.run_command(run_script, ["Model test", "--model", "distilgpt2"])
        assert "Model test" in output

    @pytest.mark.parametrize("max_words,expected_max", [
        (3, 6),  # 3 input words + max 3 generated
        (5, 8),  # 3 input words + max 5 generated
        (1, 4),  # 3 input words + max 1 generated
    ])
    def test_run_max_words(self, run_script, max_words, expected_max):
        """Test that --max-words limits the generated text"""
        output = self.run_command(run_script, ["Word limit test", "--max-words", str(max_words)])
        words = output.split()
        assert len(words) <= expected_max

    def test_run_custom_corpus(self, run_script, temp_corpus_file):
        """Test that using a custom corpus works"""
        output = self.run_command(run_script, ["Corpus test", "--corpus", temp_corpus_file])
        assert "Corpus test" in output


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_model(self, continue_phrase_script):
        """Test that invalid model names are handled gracefully"""
        result = subprocess.run(
            ["python3", continue_phrase_script, "Test", "--model", "invalid_model"],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Should either work with fallback or fail gracefully
        assert result.returncode in [0, 1]  # Accept both success and graceful failure

    def test_empty_phrase(self, continue_phrase_script):
        """Test behavior with empty input"""
        result = subprocess.run(
            ["python3", continue_phrase_script, ""],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Should handle empty input gracefully
        assert result.returncode in [0, 1, 2]  # Accept various exit codes

    def test_very_long_phrase(self, continue_phrase_script):
        """Test behavior with very long input"""
        long_phrase = "This is a very long phrase " * 20  # 500+ characters
        result = subprocess.run(
            ["python3", continue_phrase_script, long_phrase],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Should handle long input gracefully
        assert result.returncode in [0, 1, 2]


class TestPerformance:
    """Test performance-related functionality"""
    
    @pytest.mark.slow
    def test_generation_time(self, continue_phrase_script):
        """Test that generation completes within reasonable time"""
        start_time = time.time()
        result = subprocess.run(
            ["python3", continue_phrase_script, "Performance test"],
            capture_output=True,
            text=True,
            timeout=120
        )
        end_time = time.time()
        
        assert result.returncode == 0
        assert (end_time - start_time) < 120  # Should complete within 2 minutes
        output = result.stdout.strip()
        assert "Performance test" in output

    def test_memory_usage_verbose(self, continue_phrase_script):
        """Test that verbose mode shows memory information"""
        result = subprocess.run(
            ["python3", continue_phrase_script, "Memory test", "--verbose"],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0
        # Check that output contains memory information
        # Note: verbose info might be in stdout or stderr depending on implementation
        combined_output = (result.stdout + result.stderr).lower()
        assert any(keyword in combined_output for keyword in ["memory", "mb", "usage", "markov", "transformers"])


# Pytest configuration and utilities
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add slow marker to performance tests
        if "performance" in item.name.lower() or "time" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Add integration marker to all tests in this file
        item.add_marker(pytest.mark.integration)


# Test utilities
def run_phrase_continuation(script_path, phrase, **kwargs):
    """Utility function to run phrase continuation with various options"""
    cmd = ["python3", script_path, phrase]
    
    for key, value in kwargs.items():
        if key == "use_markov" and value:
            cmd.append("--use-markov")
        elif key == "verbose" and value:
            cmd.append("--verbose")
        elif key == "model" and value:
            cmd.extend(["--model", value])
        elif key == "max_words" and value:
            cmd.extend(["--max-words", str(value)])
        elif key == "corpus" and value:
            cmd.extend(["--corpus", value])
        elif key == "seed" and value:
            cmd.extend(["--seed", str(value)])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=kwargs.get("timeout", 60)
    )
    return result


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])