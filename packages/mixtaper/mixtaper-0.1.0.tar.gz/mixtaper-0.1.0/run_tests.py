#!/usr/bin/env python3
"""
Test runner for the mixtape organizer
"""

import subprocess
import sys


def run_tests():
    """Run all tests using pytest"""
    try:
        # Run pytest with verbose output and coverage
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], check=True
        )

        print("\n✅ All tests passed!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: uv sync --dev")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
