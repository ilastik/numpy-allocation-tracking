import unittest
import tempfile
import shutil

import numpy as np

from numpy_allocation_tracking import PrettyAllocationTracker

class TestPrettyAllocationTracker(unittest.TestCase):
    def test_basic(self):
        """
        This test doesn't actually verify the output,
        but at least it verifies that the code runs at all.
        """
        def f():
            a = np.zeros((1000000000,), dtype=np.uint8)
            g()
        
        def g():
            b = np.zeros((2000000000,), dtype=np.uint8)
        
        with PrettyAllocationTracker(threshold=1000) as tracker:
            f()
        
        tmpdir = tempfile.mkdtemp()
        try:
            tracker.write_html(tmpdir + '/hello.html')
        finally:
            shutil.rmtree(tmpdir)

if __name__ == "__main__":
    unittest.main()
