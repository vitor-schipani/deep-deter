# Std. Lib.
import os
import sys
from datetime import datetime, timedelta

# Data Science and Earth Engine
import geopandas.geodataframe
from pandas.core.series import Series
import ee

# Custom functions
from deep_deter.data_extraction.custom_error import NoImagesError
from deep_deter.data_extraction.utils import mask_s2_clouds

# Environment variables
# Reads .env file. You need to create a .env file and add:
# GOOGLE_PROJECT=your_project_name
# PROJECT_PATH=/your/path/to/project
from dotenv import load_dotenv
load_dotenv()
PROJECT_PATH = os.getenv('PROJECT_PATH')
EE_PROJECT = os.getenv('GOOGLE_PROJECT')
SENTINEL_COLLECTION = os.getenv('EE_COLLECTION')
sys.path.insert(0, PROJECT_PATH)

# EE authentication
ee.Authenticate()
ee.Initialize(project=EE_PROJECT)


class FetchSentinelImg:
    """
    This class receives 1 row from the DETER alerts dataset in a dataframe format.
    It also receives how much % of clouds is acceptable and how many lookback days to scan for images
    """
    cloud_pct: int
    max_lookback: int

    def __init__(self,
                 max_allowed_cloud_percentage: int,
                 max_allowed_lookback_days: int,
                 ):
        self.cloud_pct = max_allowed_cloud_percentage
        self.max_lookback = max_allowed_lookback_days

    @property
    def ee_polygon(self) -> ee.geometry.Geometry:
        return self._ee_polygon

    @ee_polygon.setter
    def ee_polygon(self, new_polygon_series: Series) -> None:
        # Need to transform from geometry to ee.Geometry.Polygon
        new_polygon_series = new_polygon_series.squeeze()
        coordinates = list(new_polygon_series['geometry'].exterior.coords)
        self._ee_polygon = ee.Geometry.Polygon(coordinates)

    @staticmethod
    def _get_date_n_days_before(view_date: str, lookback_days: int) -> str:
        """
        Returns a date string 'N' days before the given 'date_str'.

        Parameters:
        view_date (str): The initial date in the format 'YYYY-MM-DD'.
        lookback_days (int): The number of days to subtract from the date.

        Returns:
        str: A date string 'N' days before the given date, in the format 'YYYY-MM-DD'.
        """
        initial_date = datetime.strptime(view_date, '%Y-%m-%d')
        new_date = initial_date - timedelta(days=lookback_days)
        return new_date.strftime('%Y-%m-%d')

    def _fetch_sentinel_img(self,
                            ee_polygon: ee.geometry.Geometry,
                            first_date: str,
                            last_date: str,
                            ) -> ee.imagecollection.ImageCollection:
        """
        Obtains an image_collection from the Sentinel-2 satellite collection
        :return: Gets a handle to the image collection from Earth Engine
        """
        img_collection = (
            ee.ImageCollection(SENTINEL_COLLECTION)
            .filterDate(first_date, last_date)
            .filterBounds(ee_polygon)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.cloud_pct))
            .map(mask_s2_clouds)
        )
        return img_collection

    @staticmethod
    def _get_sentinel_limits(img_collection: ee.imagecollection.ImageCollection) -> ee.geometry.Geometry:
        """
        Not in use
        Gets the limits of the sentinel image as a complex geometry (in the range of 20-25 points)
        :param img_collection: the
        :return: The geometry with the geometry
        """
        first_img = img_collection.first()  # We get the first image and access its geometry
        return first_img.geometry()

    @staticmethod
    def _get_first_img(img_collection: ee.imagecollection.ImageCollection) -> ee.image.Image:
        """
        Not in use
        Get the first image from the collection with all its properties intact
        :return: First image from current ImageCollection
        """
        return img_collection.first()

    def get_sentinel_img(self,
                         polygon_series: geopandas.geodataframe.GeoDataFrame,
                         ) -> ee.image.Image:
        """
        Fetches the sentinel image.
        :return: A single image using the composition of all images in the period
        """
        print('Fetching img...')
        new_polygon_series = polygon_series.squeeze()  # Transform GeoDataFrame into GeoSeries
        coordinates = list(new_polygon_series['geometry'].exterior.coords)
        ee_polygon = ee.Geometry.Polygon(coordinates)

        # Redefining pull dates
        ref_date = polygon_series['VIEW_DATE'].values[0]
        first_date = self._get_date_n_days_before(ref_date, self.max_lookback)
        last_date = ref_date

        img_collection = self._fetch_sentinel_img(ee_polygon, first_date, last_date)
        n_images = img_collection.size().getInfo()
        print(f'Earth Engine API returned {n_images} images')

        if n_images == 0:
            # This lets other objects know that they should skip this polygon due to lack of data
            raise NoImagesError
        else:
            # https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED#bands
            bands = ['B4', 'B3', 'B2', 'B8']  # R, G, B, NIR
            return img_collection.select(bands).median()  # Median helps mitigate clouds masked in some images
