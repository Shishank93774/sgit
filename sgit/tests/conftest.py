import pytest
import tempfile
import os
import shutil
import sys
import subprocess
import io

# Add the sgit package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_sgit(cmd_args, cwd=None):
    """Run sgit command and return result."""
    try:
        # Use subprocess for better compatibility with binary output
        result = subprocess.run(
            [sys.executable, "-m", "sgit.cli.main"] + cmd_args,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=False,  # Don't decode to text - handle binary output
            timeout=30
        )

        # Decode stdout/stderr to text for assertions, but keep binary available
        result.stdout_text = result.stdout.decode('utf-8', errors='replace')
        result.stderr_text = result.stderr.decode('utf-8', errors='replace')

        return result
    except subprocess.TimeoutExpired:
        pytest.fail("Command timed out")
    except Exception as e:
        pytest.fail(f"Command failed: {e}")


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    tmpdir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(tmpdir)
    yield tmpdir
    os.chdir(original_cwd)
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def repo_dir(temp_dir):
    """Create and initialize a git repository in temp directory."""
    # Initialize repo
    result = run_sgit(["init", "."])
    assert result.returncode == 0, f"Init failed: {result.stderr_text}"
    return temp_dir


@pytest.fixture
def sgit_cmd():
    """Return a function to run sgit commands."""

    def _run_sgit(args, cwd=None):
        return run_sgit(args, cwd)

    return _run_sgit