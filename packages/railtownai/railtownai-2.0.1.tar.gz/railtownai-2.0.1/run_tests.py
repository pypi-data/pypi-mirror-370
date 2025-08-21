#!/usr/bin/env python3
"""
Test runner script for Railtown AI Python SDK.

This script provides convenient commands to run different types of tests.
"""

import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'=' * 60}\n")

    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Railtown AI SDK tests")
    parser.add_argument("test_type", choices=["unit", "integration", "all", "quick"], help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests with verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--markers", "-m", help="Run tests with specific markers (e.g., 'not slow')")

    args = parser.parse_args()

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if args.verbose:
        cmd.append("-v")

    if args.coverage:
        cmd.extend(["--cov=railtownai", "--cov-report=html", "--cov-report=term"])

    if args.markers:
        cmd.extend(["-m", args.markers])

    # Add test paths based on type
    if args.test_type == "unit":
        cmd.append("tests/unit/")
        description = "Unit Tests"
    elif args.test_type == "integration":
        cmd.append("tests/integration/")
        description = "Integration Tests"
    elif args.test_type == "all":
        cmd.append("tests/")
        description = "All Tests"
    elif args.test_type == "quick":
        cmd.extend(["-m", "not slow"])
        cmd.append("tests/")
        description = "Quick Tests (excluding slow tests)"

    # Check if integration tests are being run
    if args.test_type in ["integration", "all"] and not args.markers:
        api_key = os.getenv("RAILTOWN_API_KEY")
        if not api_key:
            print("\n⚠️  Warning: RAILTOWN_API_KEY environment variable not set.")
            print("Integration tests will be skipped.")
            print("Set the environment variable to run integration tests.")
            print("\nExample:")
            print("  export RAILTOWN_API_KEY='your_api_key_here'")
            print("  python run_tests.py integration\n")

    # Run the tests
    success = run_command(cmd, description)

    if success:
        print(f"\n🎉 All {args.test_type} tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 Some {args.test_type} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
