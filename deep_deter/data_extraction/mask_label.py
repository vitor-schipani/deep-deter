import rasterio
from rasterio.features import geometry_mask
import geopandas.geodataframe
from deep_deter.data_extraction.mask_sentinel_img import GetCorrectProdesMask
from PIL import Image
import numpy as np


class MaskLabel:
    def __init__(self, gdf: geopandas.geodataframe.GeoDataFrame):
        self.gdf = gdf

    def write_label_to_disk(self, polygon_id: str):
        # for name in current_ids:
        # Path to your raster file
        raster_path = f'./data/processed/masked_feature_bands/{polygon_id}_bands.tif'

        # Open the raster file
        with rasterio.open(raster_path) as src:
            # Read the raster data
            raster_data = src.read(1)  # Read the first band
            raster_data[:] = 0  # Set all values to zero
            bounds = src.bounds

        filtered_gdf = self.gdf.cx[bounds.left:bounds.right, bounds.bottom:bounds.top]
        target_date = filtered_gdf[filtered_gdf['FID'] == polygon_id]['VIEW_DATE'].values[0]
        filtered_gdf = filtered_gdf[filtered_gdf['VIEW_DATE'] <= target_date]

        # Create a mask where geometries intersect
        mask = rasterio.features.geometry_mask(
            [geom for geom in filtered_gdf.geometry],
            out_shape=raster_data.shape,
            transform=src.transform,
            invert=True
        )

        # Set those locations to one
        raster_data[mask] = 1

        # Define the output path for the modified raster
        output_raster_path = f'./data/processed/labels/{polygon_id}.tif'

        limits = (bounds.left, bounds.bottom, bounds.right, bounds.top)

        get_correct_prodes_mask = GetCorrectProdesMask(
            './data/external/PDigital2000_2022_AMZ_raster.tif',
            limits,
            target_date,
        )
        prodes_mask = get_correct_prodes_mask.get_mask(raster_data.shape)
        raster_data[prodes_mask] = 1

        # Save as image
        raster_image = raster_data.copy()
        raster_image[raster_image == 1] = 255
        raster_image[raster_image == 0] = 0
        raster_image = raster_image.astype(np.uint8)
        image = Image.fromarray(raster_image, 'L')
        image.save(f'./data/images/labels/{polygon_id}.png')

        # Save the raster
        with rasterio.open(
                output_raster_path, 'w',
                driver='GTiff',
                height=raster_data.shape[0],
                width=raster_data.shape[1],
                count=1,  # number of bands
                dtype=raster_data.dtype,
                crs=src.crs,
                transform=src.transform,
        ) as dst:
            dst.write(raster_data, 1)
