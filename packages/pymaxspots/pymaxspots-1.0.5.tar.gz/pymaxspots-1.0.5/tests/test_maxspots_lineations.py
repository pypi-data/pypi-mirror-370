import numpy as np
import pymaxspots
import unittest

class TestLineations(unittest.TestCase):

    def test_lineations(self):
        N = 9
        X, Y = np.meshgrid(np.arange(N), np.arange(N))
        Z = -(X-Y)**2
        maxspots = pymaxspots.maxspots(Z, 0, 0, 1, 1)
        lines = pymaxspots.maxspots_lineations(maxspots["X"], maxspots["Y"])

        assert(len(lines) == 1)

        assert(lines[0] == [6, 5, 4, 3, 2, 1, 0])
        
if __name__ == "__main__":
    unittest.main(argv=['ignored'], exit=False)
