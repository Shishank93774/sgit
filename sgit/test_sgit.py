#!/usr/bin/env python3
"""
Quick test script for sgit functionality.
Run with: python test_sgit.py
"""

import os
import tempfile
import shutil
import subprocess
import sys


def run_test():
    """Run a quick smoke test of sgit functionality."""
    print("🚀 Testing sgit implementation...")

    # Create temporary directory
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()

    try:
        os.chdir(test_dir)
        print(f"📁 Testing in: {test_dir}")

        # Test 1: Initialize repository
        print("1. Testing 'sgit init'...")
        result = subprocess.run([sys.executable, "-m", "sgit.cli.main", "init", "."],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Init failed: {result.stderr}")
            return False
        print("✅ Repository initialized")

        # Test 2: Create and add file
        print("2. Testing file operations...")
        with open("test.txt", "w") as f:
            f.write("Hello, sgit!\n")

        result = subprocess.run([sys.executable, "-m", "sgit.cli.main", "add", "test.txt"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Add failed: {result.stderr}")
            return False
        print("✅ File added to index")

        # Test 3: Check status
        print("3. Testing 'sgit status'...")
        result = subprocess.run([sys.executable, "-m", "sgit.cli.main", "status"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Status failed: {result.stderr}")
            return False
        print("✅ Status command works")

        # Test 4: Hash object
        print("4. Testing 'sgit hash-object'...")
        result = subprocess.run([sys.executable, "-m", "sgit.cli.main", "hash-object", "test.txt"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Hash-object failed: {result.stderr}")
            return False
        sha = result.stdout.strip()
        if len(sha) == 40 and all(c in '0123456789abcdef' for c in sha):
            print("✅ Hash-object works correctly")
        else:
            print(f"❌ Invalid SHA: {sha}")
            return False

        # Test 5: List files
        print("5. Testing 'sgit ls-files'...")
        result = subprocess.run([sys.executable, "-m", "sgit.cli.main", "ls-files"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ ls-files failed: {result.stderr}")
            return False
        if "test.txt" in result.stdout:
            print("✅ ls-files shows correct files")
        else:
            print("❌ ls-files missing test.txt")
            return False

        print("\n🎉 All tests passed! sgit is working correctly.")
        return True

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)