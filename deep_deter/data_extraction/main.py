# Std.Lib.
import os
import sys
import warnings
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

# Data Science and Earth Engine
import geopandas as gpd
import ee

# Environment variables
from dotenv import load_dotenv

# Custom functions
from deep_deter.data_extraction.mask_feature_bands import MaskFeatureBands
from deep_deter.data_extraction.mask_label import MaskLabel
from deep_deter.data_extraction.save_to_disk import SaveToDisk
from deep_deter.data_extraction.train_test_split import assign_files_to_datasets

# Reads .env file. You need to create a .env file and add:
# GOOGLE_PROJECT=your_project_name
# PROJECT_PATH=/your/path/to/project
# DETER_FILE = path to the .shp file
load_dotenv()
DETER_FILE = os.getenv('DETER_FILE')
EE_PROJECT = os.getenv('GOOGLE_PROJECT')
PROJECT_PATH = os.getenv('PROJECT_PATH')
N_ITERATIONS = int(os.getenv('N_ITERATIONS'))
sys.path.insert(0, PROJECT_PATH)

# Earth Engine authentication
ee.Authenticate()
ee.Initialize(project=EE_PROJECT)

# Ignore certain warnings
warnings.filterwarnings("ignore", category=UserWarning)


class ExtractFiles:
    def __init__(self,
                 run_extraction: bool = True,
                 run_feature_processing: bool = True,
                 run_label_processing: bool = True,
                 run_train_test_split: bool = True,
                 ):
        self.run_extraction = run_extraction
        self.run_feature_processing = run_feature_processing
        self.run_label_processing = run_label_processing
        self.run_train_test_split = run_train_test_split

        print('Loading DETER data...')
        print(f'Reading from path: {DETER_FILE}')
        self.gdf = gpd.read_file(DETER_FILE)

    @staticmethod
    def _get_raw_saved_ids() -> Tuple[List[str], int]:
        """
        Gets all .tif files from the ./data/raw/ directory
        :return: A list with all polygon_ids
        """
        # Use a dictionary to count the occurrences of each ID
        id_counts = defaultdict(int)

        # Collect all files and count occurrences of each ID
        for file in Path('./data/raw/').glob('*.tif'):
            id_name = file.name.split('_')[0] + '_' + file.name.split('_')[1]
            id_counts[id_name] += 1

        # Filter IDs to only those with exactly 4 entries (R + G + B + NIR)
        # This avoids errors if one polygon_id was pulled in an incomplete way
        # TODO: function to catch errors here
        current_ids = [id_name for id_name, count in id_counts.items() if count == 4]
        count_polygon_ids = len(current_ids)
        print(f'There are currently {count_polygon_ids} distinct ids saved in ./data/raw')

        return current_ids, count_polygon_ids

    def _run_extraction(self, n_iterations: int = 10):
        save_to_disk = SaveToDisk(self.gdf)
        save_to_disk.main(n_iterations=n_iterations)

    def _run_feature_processing(self, polygon_ids: List[str], count_polygon_ids: int):
        mask_feature_bands = MaskFeatureBands(self.gdf, './data/raw/')
        for i, polygon_id in enumerate(polygon_ids):
            print(f'{i}/{count_polygon_ids} Processing features for polygon id: {polygon_id}...')
            if self.gdf[self.gdf['FID'] == polygon_id].shape[0] > 0:
                mask_feature_bands.process_raw_raster_files(polygon_id)
            else:
                print('Raw image is not in sample dataframe, skipping feature...')

    def _run_label_processing(self, polygon_ids: List[str], count_polygon_ids: int):
        mask_label = MaskLabel(self.gdf)
        for i, polygon_id in enumerate(polygon_ids):
            print(f'{i}/{count_polygon_ids} Processing labels for polygon id: {polygon_id}...')
            if self.gdf[self.gdf['FID'] == polygon_id].shape[0] > 0:
                mask_label.write_label_to_disk(polygon_id)
            else:
                print('Raw image is not in sample dataframe, skipping label...')

    @staticmethod
    def _run_train_test_split():
        base_dir = './data'
        assign_files_to_datasets(base_dir, 80)

    def main(self, n_iterations: int = 10) -> None:
        if self.run_extraction:
            print('Saving polygon images to disk...')
            self._run_extraction(n_iterations=n_iterations)

        polygon_ids, count_polygon_ids = self._get_raw_saved_ids()

        if self.run_feature_processing:
            print('Processing Features...')
            self._run_feature_processing(polygon_ids=polygon_ids,
                                         count_polygon_ids=count_polygon_ids,
                                         )

        if self.run_label_processing:
            print('Processing Labels...')
            self._run_label_processing(polygon_ids=polygon_ids,
                                       count_polygon_ids=count_polygon_ids,
                                       )

        if self.run_train_test_split:
            print('Splitting Train/Test...')
            self._run_train_test_split()


if __name__ == '__main__':
    print('Calling main function...')
    extract_files = ExtractFiles(
        run_extraction=False,
        run_feature_processing=True,
        run_label_processing=True,
        run_train_test_split=True,
    )
    extract_files.main(N_ITERATIONS)
