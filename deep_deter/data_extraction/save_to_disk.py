# Std.Lib.
import os
import sys
from typing import Union

# Data Science and Earth Engine
import geopandas.geodataframe
import ee
import geemap

# Custom functions
from deep_deter.data_extraction.custom_error import NoImagesError
from deep_deter.data_extraction.fetch_sentinel_img import FetchSentinelImg
from deep_deter.data_extraction.utils import get_rectangle_around_polygon

# Environment variables
# Reads .env file. You need to create a .env file and add:
# GOOGLE_PROJECT=your_project_name
# PROJECT_PATH=/your/path/to/project
from dotenv import load_dotenv
load_dotenv()
EE_PROJECT = os.getenv('GOOGLE_PROJECT')
PROJECT_PATH = os.getenv('PROJECT_PATH')
sys.path.insert(0, PROJECT_PATH)

# EE authentication
ee.Authenticate()
ee.Initialize(project=EE_PROJECT)


class SaveToDisk:
    """
    This class receives the DETER_gdf dataset and extracts the RGB + NIR bands of a polygon defined
    in the ./data/external dataset.

    It can be a random polygon or deterministic.
    """
    deter_gdf: geopandas.geodataframe.GeoDataFrame
    curr_polygon: geopandas.geodataframe.GeoDataFrame

    def __init__(self, deter_gdf: geopandas.geodataframe.GeoDataFrame):
        """
        :param deter_gdf: The gdf from the Deter dataset
        """
        self.deter_gdf = deter_gdf

        # Initial random row to instantiate fetch_sentinel_img
        self.curr_polygon = self._get_random_row()
        self.fetch_sentinel_img = FetchSentinelImg(
            max_allowed_cloud_percentage=20,
            max_allowed_lookback_days=14,
        )

    def _get_random_row(self) -> geopandas.geodataframe.GeoDataFrame:
        return self.deter_gdf.sample(1)

    def main(self, n_iterations: int = 10, deterministic_id: Union[str, None] = None) -> None:
        """
        Main is the public method responsible
        for fetching all data saving to disk

        :param n_iterations: Number of polygons to sample from
        :param deterministic_id: An ID that can be used to pull a single geometry
        :return: None, all channels are saved to disk instead
        """
        for i in range(n_iterations):
            print('**********')

            if deterministic_id is not None:
                current_deter_alert = self.deter_gdf[self.deter_gdf['FID'] == deterministic_id]
            else:
                print(f'Running iteration {i + 1} out of {n_iterations} total iterations')
                current_deter_alert = self._get_random_row()
            
            alert_id = current_deter_alert.FID.values[0]
            print(f'Fetching images for polygon with FID: {alert_id}')

            try:
                curr_img = self.fetch_sentinel_img.get_sentinel_img(current_deter_alert)

                # Get limits of the img that will be pulled to local disk
                rectangle_pull_limits = get_rectangle_around_polygon(current_deter_alert)

                all_bands = dict()
                all_bands['blue'] = curr_img.select('B2')   # Blue
                all_bands['green'] = curr_img.select('B3')  # Green
                all_bands['red'] = curr_img.select('B4')    # Red
                all_bands['nir'] = curr_img.select('B8')    # NIR (Near Infrared)

                for band, band_data in all_bands.items():
                    print(f'Getting data for {band}...')
                    geemap.ee_export_image(
                        band_data,
                        filename=f'data/raw/{alert_id}_{band}_band.tif',
                        scale=10,
                        region=rectangle_pull_limits,
                        file_per_band=False,
                    )

            except NoImagesError:
                # This can happen if no images match the constraints of FetchSentinelImg
                # (Too many clouds the last X days, etc.)
                # Could also be caused by data not being available on those dates as well.
                print('No images were returned for this polygon, skipping...')
            except AttributeError:
                # We are ignoring multipolygons as they are rare (<1% of all alerts) and
                # could introduce more difficulties in the data processing, we have enough
                # data as it is.
                print('An image was a MultiPolygon and was ignored, skipping...')

            if deterministic_id is not None:
                # End the loop as this method only supports a single deterministic_id
                break
