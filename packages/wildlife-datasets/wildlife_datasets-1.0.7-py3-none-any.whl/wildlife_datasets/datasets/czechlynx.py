import os
import json
import numpy as np
import pandas as pd
from . import utils
from .datasets import DatasetFactory
from .summary import summary


class CzechLynx(DatasetFactory):
    summary = summary['CzechLynx']
    archive = 'czechlynx.zip'

    @classmethod
    def _download(cls):
        command = f"datasets download -d picekl/czechlynx --force"
        exception_text = '''Kaggle must be setup.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#czechlynx'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=cls.archive)

    @classmethod
    def _extract(cls):
        utils.extract_archive(cls.archive, delete=True)

    def create_catalogue(self, split: str = 'split-geo_aware') -> pd.DataFrame:
        """
        Creates a comprehensive catalogue DataFrame for the CzechLynx dataset.

        This method reads the dataset's metadata file, processes essential fields required
        by the framework, and returns a detailed dataframe containing information about
        each animal observation and its associated metadata.

        Args:
            split (str): One of the following options:
                - 'split-geo_aware': Split based on spatial location.
                - 'split-time_open': Time-aware split (open-world).
                - 'split-time_closed': Time-aware split (closed-world).
                Default is 'split-geo_aware'.

        Returns:
            pd.DataFrame: A dataframe including the following columns:

                - image_id (str): Unique identifier for each row.
                - identity (str): Identity of the depicted individual animal.
                                  If unknown, standardized to the framework’s unknown label.
                - path (str): Relative path to the image file.
                - source (str): Dataset partition or region (e.g., 'beskydy').
                - date (datetime): Observation date. Converted to `datetime`.
                - relative_age (float): Age estimate relative to first appearance.
                - encounter (int): Unique encounter identifier.
                - coat_pattern (str): Coat pattern or marking description.
                - location (str): Specific trap or site location.
                - cell_code (str): Grid cell reference (e.g., 10km spatial cell).
                - latitude (float): Latitude of the observation point.
                - longitude (float): Longitude of the observation point.
                - trap_id (str): Unique identifier for the camera trap.
                - split-geo_aware (str): Spatial split category.
                - split-time_open (str): Time-aware open-world split.
                - split-time_closed (str): Time-aware closed-world split.

        Notes:
            - The `unique_name` column is renamed to `identity` and then dropped.
            - No filtering is applied to the split; the selected column is kept for downstream use.
            - All metadata columns are retained except explicitly replaced ones.
        """

        # Load metadata
        metadata_path = os.path.join(self.root, 'metadata.csv')
        df = pd.read_csv(metadata_path)

        # Add required columns
        df['image_id'] = df.index.astype(str)
        df['identity'] = df['unique_name']
        idx = ~df['date'].isnull()
        df.loc[idx, 'date'] = df.loc[idx, 'date'].apply(lambda x: str(x)[6:10] + '-' + str(x)[3:5] + '-' + str(x)[:2])
        df.drop(columns=['unique_name'], inplace=True)

        # Keep only selected split column, rename it
        df['original_split'] = df[split]
        df.drop(columns=['unique_name', 'split-geo_aware', 'split-time_open', 'split-time_closed'],
                errors='ignore', inplace=True)

        return self.finalize_catalogue(df)


