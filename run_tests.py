import unittest

def test():
    unittest.TextTestRunner().run(unittest.defaultTestLoader.discover("tests"))
