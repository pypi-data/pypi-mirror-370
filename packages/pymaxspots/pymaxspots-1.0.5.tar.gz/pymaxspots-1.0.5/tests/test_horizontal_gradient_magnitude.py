import numpy as np
import rasterio
import pathlib
import pymaxspots
import unittest

def get_array(dataset):
    masked_img = dataset.read(1, masked=True)
    return masked_img.filled(np.nan)

class TestHGM(unittest.TestCase):

    def test_hgm_umatilla(self):
        pseudograv_raster_path = pathlib.Path("data/Umatilla_final_220308/Magnetics/Umatilla_aeromag_Pseudogravity.tif")
        hgm_raster_path = pathlib.Path("data/Umatilla_final_220308/Magnetics/Umatilla_aeromag_HGM.tif")

        pseudograv_dataset = rasterio.open(pseudograv_raster_path)
        ulx, dx, rr, uly, cr, dy = pseudograv_dataset.get_transform()

        hgm_dataset = rasterio.open(hgm_raster_path)

        pseudograv = get_array(pseudograv_dataset)
        hgm_true = get_array(hgm_dataset)

        hgm_test = pymaxspots.horizontal_gradient_magnitude(pseudograv, dx, dy)

        np.testing.assert_allclose(hgm_test[1:-1,1:-1], hgm_true[1:-1,1:-1], atol=1.e-05)

    def test_hgm_x(self):
        ncol = nrow = 5
        X = np.vstack([np.arange(ncol)] * nrow)

        X_hgm = pymaxspots.horizontal_gradient_magnitude(X, 1, 1)

        np.testing.assert_array_equal(X_hgm, 1)

    def test_hgm_y(self):
        ncol = nrow = 5
        Y = np.hstack([np.c_[np.arange(nrow)]] * ncol)

        Y_hgm = pymaxspots.horizontal_gradient_magnitude(Y, 1, 1)

        np.testing.assert_array_equal(Y_hgm, 1)

    def test_hgm_xy(self):
        ncol = nrow = 5
        X, Y = np.meshgrid(np.arange(ncol), np.arange(nrow))

        XY_hgm = pymaxspots.horizontal_gradient_magnitude(X+Y, 1, 1)

        np.testing.assert_array_equal(XY_hgm, np.sqrt(2))

    def test_hgm_zero(self):
        ncol = nrow = 5
        Z = np.ones((ncol, nrow))

        Z_hgm = pymaxspots.horizontal_gradient_magnitude(Z, 1, 1)

        np.testing.assert_array_equal(Z_hgm, 0)

if __name__ == "__main__":
    unittest.main()
