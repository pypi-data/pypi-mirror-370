import numpy as np
import pymaxspots
import unittest

class Test_MeanNNDist(unittest.TestCase):

    def test_mean_nndist_allone(self):
        N = 4
        x = np.arange(N)
        y = np.zeros(N)

        dist = pymaxspots.mean_nearest_neighbor_distance(x, y)

        np.testing.assert_equal(dist, 1)

    def test_mean_nndist_alldiff(self):
        x = np.array([-3, -2, 0, 3, 6])
        y = np.zeros(x.size)

        dist = pymaxspots.mean_nearest_neighbor_distance(x, y)

        np.testing.assert_equal(dist, 2)

    def test_mean_nndist_allzero(self):
        N = 4
        x = np.ones(N)
        y = np.zeros(N)

        dist = pymaxspots.mean_nearest_neighbor_distance(x, y)

        np.testing.assert_equal(dist, 0)

if __name__ == "__main__":
    unittest.main()