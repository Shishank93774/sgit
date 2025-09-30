import pytest
import os
import tempfile


class TestRepositoryStructure:
    def test_repo_structure(self, repo_dir):
        """Test that repository has correct structure."""
        git_dir = os.path.join(repo_dir, ".git")

        assert os.path.exists(git_dir)
        assert os.path.exists(os.path.join(git_dir, "objects"))
        assert os.path.exists(os.path.join(git_dir, "refs"))
        assert os.path.exists(os.path.join(git_dir, "refs", "heads"))
        assert os.path.exists(os.path.join(git_dir, "refs", "tags"))
        assert os.path.exists(os.path.join(git_dir, "HEAD"))
        assert os.path.exists(os.path.join(git_dir, "config"))
        assert os.path.exists(os.path.join(git_dir, "description"))

    def test_head_file(self, repo_dir):
        """Test HEAD file content."""
        head_path = os.path.join(repo_dir, ".git", "HEAD")
        with open(head_path, "r") as f:
            content = f.read().strip()
        assert content == "ref: refs/heads/master"

    def test_config_file(self, repo_dir):
        """Test default configuration."""
        config_path = os.path.join(repo_dir, ".git", "config")
        assert os.path.exists(config_path)

        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)

        assert "core" in config.sections()
        assert config.get("core", "repositoryformatversion") == "0"
        assert config.get("core", "filemode") == "false"
        assert config.get("core", "bare") == "false"

    def test_repo_find(self, repo_dir):
        """Test repository discovery."""
        from sgit.utils.file_io import repo_find

        # Should find repo from subdirectory
        subdir = os.path.join(repo_dir, "subdir")
        os.makedirs(subdir)

        repo = repo_find(subdir)
        assert repo is not None
        assert repo.worktree == repo_dir

    def test_repo_find_failure(self, temp_dir):
        """Test repository discovery failure."""
        from sgit.utils.file_io import repo_find

        # Should raise exception when required
        with pytest.raises(Exception):
            repo_find(temp_dir, required=True)

        # Should return None when not required
        repo = repo_find(temp_dir, required=False)
        assert repo is None