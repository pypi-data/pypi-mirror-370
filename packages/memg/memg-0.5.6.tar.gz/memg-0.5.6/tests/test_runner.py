#!/usr/bin/env python3
"""
Test runner script for MEMG test suite.
Provides convenient commands for running different test categories.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and return success status."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def run_unit_tests():
    """Run unit tests only."""
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "-m",
            "unit",
        ]
    )


def run_integration_tests():
    """Run integration tests only."""
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            "-m",
            "integration",
        ]
    )


def run_fast_tests():
    """Run fast tests (excluding slow ones)."""
    return run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-m", "not slow"]
    )


def run_all_tests():
    """Run all tests with coverage."""
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=memg",
            "--cov-report=term-missing",
            "--cov-report=html",
        ]
    )


def run_tests_requiring_api():
    """Run tests that require API access."""
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "-m",
            "requires_api",
        ]
    )


def run_specific_test(test_path):
    """Run a specific test file or function."""
    return run_command([sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"])


def main():
    """Main test runner interface."""
    if len(sys.argv) < 2:
        print("MEMG Test Runner")
        print("Usage: python tests/test_runner.py <command>")
        print("\nCommands:")
        print("  unit        - Run unit tests only")
        print("  integration - Run integration tests only")
        print("  fast        - Run fast tests (exclude slow ones)")
        print("  all         - Run all tests with coverage")
        print("  api         - Run tests requiring API access")
        print("  <path>      - Run specific test file or function")
        print("\nExamples:")
        print("  python tests/test_runner.py unit")
        print("  python tests/test_runner.py tests/unit/test_genai.py")
        print(
            "  python tests/test_runner.py tests/unit/test_genai.py::TestGenAI::test_init_default"
        )
        return False

    command = sys.argv[1]

    # Change to project root
    project_root = Path(__file__).parent.parent
    import os

    os.chdir(project_root)

    if command == "unit":
        success = run_unit_tests()
    elif command == "integration":
        success = run_integration_tests()
    elif command == "fast":
        success = run_fast_tests()
    elif command == "all":
        success = run_all_tests()
    elif command == "api":
        success = run_tests_requiring_api()
    else:
        # Assume it's a specific test path
        success = run_specific_test(command)

    if success:
        print("\n✅ Tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
