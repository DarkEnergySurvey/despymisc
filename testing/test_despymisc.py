#!/usr/bin/env python2
import unittest
from contextlib import contextmanager
import sys

@contextmanager
def capture_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class TestXmlslurper(unittest.TestCase):
    def test_xx(self):
        pass


if __name__ == '__main__':
    unittest.main()
