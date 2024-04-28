# Std.Lib.
from pathlib import Path

# Data Science and Earth Engine
import geopandas.geodataframe
import ee
import rasterio
import numpy as np
import matplotlib.pyplot as plt


def get_image_limits(input_img):
    input_img = input_img.getInfo()
    
    coordinates = input_img['properties']['system:footprint']['coordinates']

    latitudes = [i[0] for i in coordinates]
    longitudes = [i[1] for i in coordinates]
    
    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lng = min(longitudes)
    max_lng = max(longitudes)

    return min_lat, max_lat, min_lng, max_lng


def mask_s2_clouds(image: ee.image.Image) -> ee.image.Image:
  """Masks clouds in a Sentinel-2 image using the QA band.

  Args:
      image (ee.Image): A Sentinel-2 image.

  Returns:
      ee.Image: A cloud-masked Sentinel-2 image.
  """
  qa = image.select('QA60')

  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloud_bit_mask = 1 << 10
  cirrus_bit_mask = 1 << 11

  # Both flags should be set to zero, indicating clear conditions.
  mask = (
      qa.bitwiseAnd(cloud_bit_mask)
      .eq(0)
      .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
  )

  return image.updateMask(mask).divide(10000)


def convert_to_feature(row):
    geom = row['geometry']  # Accessing the geometry field in the row
    if geom.geom_type == 'Polygon':
        # Create a list of tuples for the exterior coordinates of the polygon
        coords = list(geom.exterior.coords)
        ee_geom = ee.Geometry.Polygon(coords)
    elif geom.geom_type == 'MultiPolygon':
        # Handle each polygon in the MultiPolygon
        polygons = [list(poly.exterior.coords) for poly in geom.geoms]  # Correctly access polygons in a MultiPolygon
        ee_geom = ee.Geometry.MultiPolygon(polygons)
    else:
        raise ValueError(f"Unsupported geometry type: {geom.type}")
    return ee_geom


def get_all_polygons_in_sentinel_img(image, gdf, ref_date, return_as_gdf=False):
    min_lat, max_lat, min_lng, max_lng = get_image_limits(image)
    filtered_gdf = gdf.cx[min_lat:max_lat, min_lng:max_lng]

    if return_as_gdf:
        filtered_gdf_past = filtered_gdf[filtered_gdf['VIEW_DATE'] <= ref_date]
        filtered_gdf_future = filtered_gdf[filtered_gdf['VIEW_DATE'] > ref_date]
        return filtered_gdf_past, filtered_gdf_future
    else:
        filtered_gdf['geometry_ee'] = filtered_gdf.apply(convert_to_feature, axis=1)
        my_list = filtered_gdf['geometry_ee'].to_list()
        feature_collection = ee.FeatureCollection(my_list)
        return feature_collection


def get_rectangle_around_polygon(curr_deter_alert: geopandas.geodataframe.GeoDataFrame,
                                 delta: float = 0.14,
                                 ) -> ee.geometry.Geometry.Rectangle:
    """
    This gets a rectangle around the deter alert to pull from Earth Engine.
    If delta is left at default then there should be no problems with API limits.
    :param curr_deter_alert: The sample we are fetching data for
    :param delta: The change in degrees to get a bounding box
    :return: The rectangle around the area of interest
    """
    centroid = curr_deter_alert.geometry.centroid.values
    centroid_x = centroid.x[0]
    centroid_y = centroid.y[0]

    min_lat = centroid_x - delta
    max_lat = centroid_x + delta

    min_lng = centroid_y - delta
    max_lng = centroid_y + delta

    lower_left = (min_lat, min_lng)
    upper_right = (max_lat, max_lng)

    return ee.Geometry.Rectangle([lower_left, upper_right])


def display_raster_rgb(id_polygon: str, type: str, plot=False) -> None:
    if type == 'feature':
        suffix = '_bands.tif'

        with rasterio.open(Path(f'../data/processed/masked_feature_bands/') / (id_polygon + suffix)) as src:
            # Read the red, green, and blue bands
            # Bands were saved in alphabetical order so 1 = blue, 2 = green, 3 = nir, 4 = red
            blue = src.read(1)
            green = src.read(2)
            red = src.read(4)

        # Stack the bands together
        rgb = np.dstack((red, green, blue))

        if plot:
            # Display the image
            plt.figure(figsize=(10, 10))
            plt.imshow(rgb)
            plt.title('RGB Image')
            plt.axis('off')  # Turn off axis numbers and ticks
            plt.show()

        return rgb

    elif type == 'label':
        dir = 'labels'
        suffix = '.tif'

        with rasterio.open(Path(f'../data/processed/labels') / (id_polygon + suffix)) as src:
            # Read the red, green, and blue bands
            label = src.read(1)

        if plot:
            # Display the image
            plt.figure(figsize=(10, 10))
            plt.imshow(label)
            plt.title('RGB Image')
            plt.axis('off')  # Turn off axis numbers and ticks
            plt.show()

        return label

    else:
        raise ValueError("type must be either 'feature' or 'label'")
