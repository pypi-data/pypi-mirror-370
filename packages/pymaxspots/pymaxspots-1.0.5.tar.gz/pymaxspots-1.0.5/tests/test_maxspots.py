import numpy as np
import pandas as pd
import rasterio
import pathlib
import pymaxspots
from scipy import spatial
import unittest

def get_array(dataset):
    masked_img = dataset.read(1, masked=True)
    return masked_img.filled(np.nan)

class TestMaxspots(unittest.TestCase):

    def test_maxspots_umatilla_aeromag(self):

        max_spots_csv_path = pathlib.Path("data/Umatilla_final_220308/Magnetics/Umatilla_aeromag_max_spots.csv")
        hgm_raster_path = pathlib.Path("data/Umatilla_final_220308/Magnetics/Umatilla_aeromag_HGM.tif")

        max_spots_validation_df = pd.read_csv(max_spots_csv_path)

        hgm_dataset = rasterio.open(hgm_raster_path)

        ulx, dx, rr, uly, cr, dy = hgm_dataset.get_transform()
        dy_abs = np.abs(dy)

        hgm = get_array(hgm_dataset)
        nrow, ncol = hgm.shape
        urx = ulx + (ncol-1)*dx
        lly = uly - (nrow-1)*dy_abs

        max_spots_test = pymaxspots.maxspots(hgm, ulx, uly, dx, dy_abs)

        max_spots_test_df = pd.DataFrame(max_spots_test)

        max_spots_validation_df = max_spots_validation_df[(max_spots_validation_df['X'] > ulx + dx) &
                                                          (max_spots_validation_df['X'] < urx) &
                                                          (max_spots_validation_df['Y'] < uly - dy_abs) &
                                                          (max_spots_validation_df['Y'] > lly) &
                                                          ((max_spots_validation_df["ID"]=="ridge") | (max_spots_validation_df["ID"]=="saddle"))
                                                          ]

        max_spots_test_df = max_spots_test_df[(max_spots_test_df['X'] > ulx + dx) &
                                              (max_spots_test_df['X'] < urx) &
                                              (max_spots_test_df['Y'] < uly - dy_abs) &
                                              (max_spots_test_df['Y'] > lly) &
                                              ((max_spots_test_df["ID"]=="ridge") | (max_spots_test_df["ID"]=="saddle"))
                                              ]

        xy_tol = 2.5

        vtree = spatial.KDTree(max_spots_validation_df[['X','Y']].values)
        dist, ix = vtree.query(max_spots_test_df[['X','Y']].values)

        if not np.all(dist < xy_tol):
            raise AssertionError("Not all points are within the tolerance")
        

    def test_maxspots_ridge(self):
        N = 3
        X, Y = np.meshgrid(np.arange(N), np.arange(N))
        Z = - (X - Y)**2

        max_spots = pymaxspots.maxspots(Z, 0, 0, 1, 1)

        max_spots_true = np.array([('ridge', 1.5, -1.5, 0., 0., -45., 0., -4., 1)],
                                    dtype=max_spots.dtype)

        assert(max_spots_true == max_spots)

    def test_maxspots_trough(self):
        N = 3
        X, Y = np.meshgrid(np.arange(N), np.arange(N))
        Z = (X - Y)**2

        max_spots = pymaxspots.maxspots(Z, 0, 0, 1, 1)

        max_spots_true = np.array([('trough', 1.5, -1.5, 0., np.inf, -45., 4., 0., 2)],
                                    dtype=max_spots.dtype)

        assert(max_spots_true == max_spots)

    def test_maxspots_saddle(self):
        N = 3
        X, Y = np.meshgrid(np.arange(N), np.arange(N))
        Z = (X-1)**2 - (Y-1)**2

        max_spots = pymaxspots.maxspots(Z, 0, 0, 1, 1)

        max_spots_true = np.array([('saddle', 1.5, -1.5, 0., 1., 90., 2., -2., 5)],
                                    dtype=max_spots.dtype)

        assert(max_spots_true == max_spots)

    def test_maxspots_high(self):
        N = 3
        X, Y = np.meshgrid(np.arange(N), np.arange(N))
        Z = - (X-1)**2 - (Y-1)**2

        max_spots = pymaxspots.maxspots(Z, 0, 0, 1, 1)

        max_spots_true = np.array([('high', 1.5, -1.5, 0., 1., np.inf, -2., -2., 3)],
                                    dtype=max_spots.dtype)

        assert(max_spots_true == max_spots)

    def test_maxspots_low(self):
        N = 3
        X, Y = np.meshgrid(np.arange(N), np.arange(N))
        Z = (X-1)**2 + (Y-1)**2

        max_spots = pymaxspots.maxspots(Z, 0, 0, 1, 1)

        max_spots_true = np.array([('low', 1.5, -1.5, 0., 1., np.inf, 2., 2., 4)],
                                    dtype=max_spots.dtype)

        assert(max_spots_true == max_spots)
        
if __name__ == "__main__":
    unittest.main(argv=['ignored'], exit=False)
