import unittest
import numpy as np
from numpy_allocation_tracking.decorators import assert_mem_usage_factor

def dumb_function(x, y, z, input_array):
    ## As of numpy-1.13, the following line of code has no extra memory
    # overhead for intermediate values, thanks to a new inlining feature in numpy. 
    # return x * (input_array + y + z)
    
    # Therefore, we must explicitly break it up to force extra memory usage.
    intermediate = input_array + y + z
    return x * intermediate    

class Test(unittest.TestCase):

    def test_assert_mem_usage_factor(self):
        a = np.ones( (1000,1000), dtype=np.uint8 )

        checked_dumb_function = assert_mem_usage_factor(100.0, comparison_input_arg='input_array')(dumb_function)
        result = checked_dumb_function(2, 3, 4, input_array=a)
        
        checked_dumb_function = assert_mem_usage_factor(1.0, comparison_input_arg=3)(dumb_function)
        try:
            result = checked_dumb_function(2, 3, 4, a)
        except AssertionError as ex:
            if 'memory' not in ex.args[0]:
                raise
        except:
            raise
        else:
            assert False, "Expected assertion wasn't raised."

        checked_dumb_function = assert_mem_usage_factor(1.0, comparison_input_arg='input_array')(dumb_function)
        try:
            result = checked_dumb_function(2, 3, 4, input_array=a)
        except AssertionError as ex:
            if 'memory' not in ex.args[0]:
                raise
        except:
            raise
        else:
            assert False, "Expected assertion wasn't raised."
    
if __name__ == "__main__":
    import sys
    import logging
    decorators_logger = logging.getLogger('numpy_allocation_tracking.decorators')
    decorators_logger.addHandler(logging.StreamHandler(sys.stdout))
    decorators_logger.setLevel(logging.DEBUG)
    unittest.main()
