import os
import sys
from dotenv import load_dotenv
import ee.imagecollection
from typing import List
import rasterio
from rasterio.windows import from_bounds
from rasterio.plot import show
import numpy as np

load_dotenv()

# EE authentication
sys.path.insert(0, os.getenv('PROJECT_PATH'))
earth_engine_project = os.getenv('GOOGLE_PROJECT')
ee.Authenticate()
ee.Initialize(project=earth_engine_project)


class GetCorrectProdesMask:
    def __init__(self,
                 prodes_path,
                 limits,
                 ref_date: str,
                 ):
        self.prodes_path = prodes_path
        self.limits = limits
        self.ref_date = ref_date

    def _read_filtered_prodes_raster(self, shape):
        with rasterio.open(self.prodes_path) as dataset:
            window = from_bounds(*self.limits, transform=dataset.transform)
            windowed_data = dataset.read(1, window=window, out_shape=shape)  # Nearest Neighbors
            return windowed_data

    def _get_raster_pixels(self) -> List[int]:
        # "Ano Prodes" ends at YYYY-07-31 see:
        # http://mtc-m21d.sid.inpe.br/col/sid.inpe.br/mtc-m21d/2022/08.25.11.46/doc/thisInformationItemHomePage.html
        # Page 16

        # See PDDigital.txt file
        # 32 = Clouds, 91 = Rivers, 101 = Not-forest
        raster_pixels = [32, 91, 101]

        if self.ref_date > '2007-07-31':
            raster_pixels.append(7)  # d2007
        if self.ref_date > '2008-07-31':
            raster_pixels.append(8)  # d2008
        if self.ref_date > '2009-07-31':
            raster_pixels.append(9)  # d2009
        if self.ref_date > '2010-07-31':
            raster_pixels.append(50)  # r2010
            raster_pixels.append(10)  # d2010
        if self.ref_date > '2011-07-31':
            raster_pixels.append(51)  # r2011
            raster_pixels.append(11)  # d2011
        if self.ref_date > '2012-07-31':
            raster_pixels.append(52)  # r2012
            raster_pixels.append(12)  # d2012
        if self.ref_date > '2013-07-31':
            raster_pixels.append(53)  # r2013
            raster_pixels.append(13)  # d2013
        if self.ref_date > '2014-07-31':
            raster_pixels.append(54)  # r2014
            raster_pixels.append(14)  # d2014
        if self.ref_date > '2015-07-31':
            raster_pixels.append(55)  # r2015
            raster_pixels.append(15)  # d2015
        if self.ref_date > '2016-07-31':
            raster_pixels.append(56)  # r2016
            raster_pixels.append(16)  # d2016
        if self.ref_date > '2017-07-31':
            raster_pixels.append(57)  # r2017
            raster_pixels.append(17)  # d2017
        if self.ref_date > '2018-07-31':
            raster_pixels.append(58)  # r2018
            raster_pixels.append(18)  # d2018
        if self.ref_date > '2019-07-31':
            raster_pixels.append(59)  # r2019
            raster_pixels.append(19)  # d2019
        if self.ref_date > '2020-07-31':
            raster_pixels.append(60)  # r2020
            raster_pixels.append(20)  # d2020
        if self.ref_date > '2021-07-31':
            raster_pixels.append(61)  # r2021
            raster_pixels.append(21)  # d2021
        if self.ref_date > '2022-07-31':
            raster_pixels.append(22)  # d2022

        return raster_pixels

    def get_mask(self, shape) -> ee.image.Image:
        clipped_prodes = self._read_filtered_prodes_raster(shape)
        pixels_to_enter_mask = self._get_raster_pixels()

        combined_mask = np.zeros_like(clipped_prodes)
        mask = np.isin(clipped_prodes, pixels_to_enter_mask)

        return mask
