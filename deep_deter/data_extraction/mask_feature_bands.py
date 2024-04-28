# Std.Lib.
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Data Science and Earth Engine
import numpy as np
import rasterio
import ee.geometry
import geopandas.geodataframe
from PIL import Image

# Environment variables
# Reads .env file. You need to create a .env file and add:
# GOOGLE_PROJECT=your_project_name
# PROJECT_PATH=/your/path/to/project
from dotenv import load_dotenv
load_dotenv()
EE_PROJECT = os.getenv('GOOGLE_PROJECT')
PRODES_FILE = os.getenv('PRODES_FILE')
PROJECT_PATH = os.getenv('PROJECT_PATH')
sys.path.insert(0, PROJECT_PATH)

# EE authentication
ee.Authenticate()
ee.Initialize(project=EE_PROJECT)


class MaskFeatureBands:
    """
    Take the bands from ./data/raw_bands/ and mask where PRODES
    already declared degraded areas.
    """
    gdf: geopandas.geodataframe.GeoDataFrame
    path_raw_bands: Path
    gdf_slice: int

    def __init__(self,
                 gdf: geopandas.geodataframe.GeoDataFrame,
                 path_raw_bands: str,
                 ):
        """
        The ID from the degradation.
        """
        self.gdf = gdf
        self.path_raw_bands = Path(path_raw_bands)
        self.gdf_slice = None  # Placeholder until it gets defined

    @property
    def gdf_slice(self) -> geopandas.geodataframe.GeoSeries:
        return self._gdf_slice

    @gdf_slice.setter
    def gdf_slice(self, id_polygon: str) -> None:
        self._gdf_slice = self.gdf[self.gdf['FID'] == id_polygon]

    def _get_relevant_tif_files(self, id_polygon: str) -> List[Path]:
        """
        This gets all *.tif files from that example that are relevant
        """
        target_files = []
        for file in self.path_raw_bands.glob('*.tif'):
            file_root = file.name.split('_')[0] + '_' + file.name.split('_')[1]
            if file_root == id_polygon:
                target_files.append(self.path_raw_bands/Path(file_root+'_red_band.tif'))
                target_files.append(self.path_raw_bands/Path(file_root+'_green_band.tif'))
                target_files.append(self.path_raw_bands/Path(file_root+'_blue_band.tif'))
                target_files.append(self.path_raw_bands/Path(file_root+'_nir_band.tif'))

        # This is not exactly efficient, but let's go with it
        target_files = list(set(target_files))
        target_files = sorted(target_files)
        return target_files

    @staticmethod
    def _get_raster_limits(raster_path: Path) -> Tuple:
        with rasterio.open(raster_path) as src:
            bounds = src.bounds

        bounds_rect = (bounds.left, bounds.bottom, bounds.right, bounds.top)
        return bounds_rect

    @staticmethod
    def _mask_raw_bands(raster_paths: List[Path],
                        # prodes_mask: np.ndarray,
                        ) -> List[np.ndarray]:
        masked_bands = []

        for raster_file in raster_paths:
            with rasterio.open(raster_file) as src:
                band = src.read(1)
            masked_bands.append(band)
        return masked_bands

    @staticmethod
    def _merge_masked_raw_bands_and_write_to_disk(
            masked_bands: List[np.ndarray],
            polygon_id: str,
            target_files: List[Path],
    ) -> None:
        # This is just to obtain the metadata about the raster files
        # All should have the same metadata
        with rasterio.open(target_files[0]) as src:
            out_meta = src.meta.copy()
        out_meta.update(count=4)

        with rasterio.open(
                Path('./data/processed/masked_feature_bands')/f'{polygon_id}_bands.tif',
                'w',
                **out_meta,
        ) as dest:
            for i, ds in enumerate(masked_bands, 1):
                dest.write_band(i, ds)

    @staticmethod
    def _merge_masked_raw_bands_and_write_image(
            bands: List[np.ndarray],
            polygon_id: str,
    ) -> None:
        for i in range(len(bands)):
            band = bands[i]
            band = (band - np.min(band)) / (np.max(band) - np.min(band)) * 255.0
            bands[i] = band.astype(np.uint8)

        # Check shapes and ensure all are the same; this step is important to avoid shape mismatches
        if not all(b.shape == bands[0].shape for b in bands):
            raise ValueError("All bands must have the same dimensions")

        rgb = np.dstack((bands[3], bands[1], bands[0]))

        image = Image.fromarray(rgb)
        image.save(f'./data/images/features/{polygon_id}.png')

    def process_raw_raster_files(self, id_polygon: str):
        """
        This method masks all polygons specified in a PRODES mask with zeroes
        and saves all bands to a single *.tif file.
        """
        target_files = self._get_relevant_tif_files(id_polygon)
        limits = self._get_raster_limits(target_files[0])  # Files have the same limits so we can use any
        self.gdf_slice = id_polygon
        ref_date = self.gdf_slice['VIEW_DATE'].values[0]

        #prodes_mask_builder = GetCorrectProdesMask(
        #    './data/external/PDigital2000_2022_AMZ_raster.tif',
        #    limits,
        #    ref_date,
        #)
        #prodes_mask = prodes_mask_builder.get_mask()

        masked_bands = self._mask_raw_bands(raster_paths=target_files)
        self._merge_masked_raw_bands_and_write_to_disk(masked_bands, id_polygon, target_files)
        self._merge_masked_raw_bands_and_write_image(masked_bands, id_polygon)
