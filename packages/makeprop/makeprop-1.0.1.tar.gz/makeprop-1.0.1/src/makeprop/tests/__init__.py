import unittest

__all__ = ["test"]


def test() -> unittest.TextTestRunner:
    loader: unittest.TestLoader = unittest.TestLoader()
    tests: unittest.TestSuite = loader.discover(start_dir="makeprop.tests")
    runner: unittest.TextTestRunner = unittest.TextTestRunner()
    result: unittest.TextTestRunner = runner.run(tests)
    return result
