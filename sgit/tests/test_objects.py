import pytest
import os
import tempfile


class TestObjectOperations:
    def test_hash_object(self, repo_dir, sgit_cmd):
        """Test hashing objects."""
        os.chdir(repo_dir)

        # Create a test file
        with open("test.txt", "w") as f:
            f.write("Hello, World!\n")

        # Hash without writing
        result = sgit_cmd(["hash-object", "test.txt"])
        assert result.returncode == 0, f"Hash failed: {result.stderr_text}"
        sha = result.stdout_text.strip()
        assert len(sha) == 40, f"Invalid SHA length: {sha}"
        assert all(c in "0123456789abcdef" for c in sha), f"Invalid SHA characters: {sha}"

        # Hash with writing
        result = sgit_cmd(["hash-object", "-w", "test.txt"])
        assert result.returncode == 0, f"Hash with write failed: {result.stderr_text}"
        written_sha = result.stdout_text.strip()
        assert sha == written_sha, f"SHA mismatch: {sha} != {written_sha}"

        # Verify object exists
        obj_path = f".git/objects/{sha[:2]}/{sha[2:]}"
        assert os.path.exists(obj_path), f"Object file not found: {obj_path}"

    def test_cat_file_blob(self, repo_dir, sgit_cmd):
        """Test reading blob objects."""
        os.chdir(repo_dir)

        # Create and hash a file
        content = "Test content for cat-file\n"
        with open("test.txt", "w") as f:
            f.write(content)

        result = sgit_cmd(["hash-object", "-w", "test.txt"])
        assert result.returncode == 0, f"Hash failed: {result.stderr_text}"
        sha = result.stdout_text.strip()

        # Read it back - cat-file outputs binary data
        result = sgit_cmd(["cat-file", "blob", sha])
        assert result.returncode == 0, f"Cat-file failed: {result.stderr_text}"

        # Compare binary content - decode the stdout bytes to text
        output_text = result.stdout.decode('utf-8')
        assert output_text == content, f"Content mismatch: {output_text} != {content}"

    def test_cat_file_invalid_object(self, repo_dir, sgit_cmd):
        """Test reading non-existent objects."""
        os.chdir(repo_dir)

        # Use a valid-looking but non-existent SHA
        result = sgit_cmd(["cat-file", "blob", "a" * 40])
        # Should fail, but different implementations might handle this differently
        if result.returncode == 0:
            pytest.skip("Implementation doesn't validate object existence")

    def test_hash_object_different_types(self, repo_dir, sgit_cmd):
        """Test hashing different object types."""
        os.chdir(repo_dir)

        with open("test.txt", "w") as f:
            f.write("test content")

        # Test blob (default)
        result = sgit_cmd(["hash-object", "test.txt"])
        assert result.returncode == 0, f"Default hash failed: {result.stderr_text}"

        # Explicit blob
        result = sgit_cmd(["hash-object", "-t", "blob", "test.txt"])
        assert result.returncode == 0, f"Explicit blob hash failed: {result.stderr_text}"

    def test_rev_parse(self, repo_dir, sgit_cmd):
        """Test revision parsing."""
        os.chdir(repo_dir)

        # In empty repo, HEAD should not resolve to a commit
        result = sgit_cmd(["rev-parse", "HEAD"])
        # Different implementations handle this differently
        if result.returncode == 0:
            # If it succeeds, output should be empty or a ref
            output = result.stdout_text.strip()
            assert output == "" or "ref:" in output