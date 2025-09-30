import pytest
import os
import tempfile
import shutil


class TestBasicCommands:
    def test_init_command(self, temp_dir, sgit_cmd):
        """Test repository initialization."""
        os.chdir(temp_dir)

        result = sgit_cmd(["init", "."])
        assert result.returncode == 0, f"Init failed: {result.stderr_text}"
        assert os.path.exists(".git")
        assert os.path.exists(".git/objects")
        assert os.path.exists(".git/refs")
        assert os.path.exists(".git/HEAD")

        # Test init message - use stdout_text instead of stdout
        assert "Initialized empty sgit repository" in result.stdout_text

    def test_init_custom_path(self, temp_dir, sgit_cmd):
        """Test initializing repository in custom path."""
        repo_path = os.path.join(temp_dir, "myrepo")
        os.makedirs(repo_path)

        result = sgit_cmd(["init", repo_path])
        assert result.returncode == 0, f"Init failed: {result.stderr_text}"
        assert os.path.exists(os.path.join(repo_path, ".git"))

    def test_init_already_exists(self, temp_dir, sgit_cmd):
        """Test initializing where repository already exists."""
        os.chdir(temp_dir)
        sgit_cmd(["init", "."])

        # Try to init again
        result = sgit_cmd(["init", "."])
        # Should fail or handle gracefully
        assert result.returncode != 0 or "exists" in result.stderr_text.lower()

    def test_help_command(self, sgit_cmd):
        """Test help command."""
        result = sgit_cmd(["--help"])
        assert result.returncode == 0, f"Help failed: {result.stderr_text}"
        assert "usage:" in result.stdout_text.lower()
        assert "commands:" in result.stdout_text.lower()

    def test_unknown_command(self, sgit_cmd):
        """Test handling of unknown commands."""
        result = sgit_cmd(["unknown-command"])
        assert result.returncode != 0
        assert "unknown" in result.stderr_text.lower() or "bad command" in result.stderr_text.lower()

    def test_no_command(self, sgit_cmd):
        """Test behavior when no command is provided."""
        result = sgit_cmd([])
        # Should show help or error
        assert result.returncode != 0 or "usage:" in result.stdout_text.lower()