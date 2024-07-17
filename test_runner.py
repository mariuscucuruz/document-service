import unittest
import sys
import os

loader = unittest.TestLoader()
start_dir = os.getcwd()
suite = loader.discover(start_dir=f"{start_dir}/tests/", pattern="test_*.py")
runner = unittest.TextTestRunner()
errors = runner.run(suite).errors

if __name__ == "__main__":
    unittest.main()

if len(errors) > 0:
    sys.exit(1)
