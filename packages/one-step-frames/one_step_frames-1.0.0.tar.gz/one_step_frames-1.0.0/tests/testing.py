import unittest

if __name__ == '__main__':
    # Discover all tests named testing.py recursively from current directory
    suite = unittest.defaultTestLoader.discover(start_dir='.', pattern='testing.py')
    runner = unittest.TextTestRunner()
    runner.run(suite)