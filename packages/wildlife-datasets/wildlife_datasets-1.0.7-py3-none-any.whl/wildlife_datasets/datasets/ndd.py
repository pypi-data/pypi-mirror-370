import os
import json
import numpy as np
import pandas as pd
from . import utils
from .datasets import DatasetFactory
from .summary import summary

class NDD20(DatasetFactory):
    outdated_dataset = True
    summary = summary['NDD20']
    url = 'https://data.ncl.ac.uk/ndownloader/files/22774175'
    archive = 'NDD20.zip'

    @classmethod
    def _download(cls):
        utils.download_url(cls.url, cls.archive)

    @classmethod
    def _extract(cls):
        utils.extract_archive(cls.archive, delete=True)    

    def create_catalogue(self) -> pd.DataFrame:
        # Load information about the above-water dataset
        with open(os.path.join(self.root, 'ABOVE_LABELS.json')) as file:
            data = json.load(file)
        
        # Analyze the information about the above-water dataset
        entries = []
        for key in data.keys():
            regions = data[key]['regions']
            for region in regions:
                if 'id' in region['region_attributes']:
                    identity = region['region_attributes']['id']
                else:
                    identity = self.unknown_name
                segmentation = np.zeros(2*len(region['shape_attributes']['all_points_x']))
                segmentation[0::2] = region['shape_attributes']['all_points_x']
                segmentation[1::2] = region['shape_attributes']['all_points_y']
                entries.append({
                    'identity': identity,
                    'species': region['region_attributes']['species'],
                    'out_of_focus': np.nan,
                    'file_name': data[key]['filename'],
                    'reg_type': region['shape_attributes']['name'],
                    'segmentation': segmentation,
                    'orientation': 'above'
                })
        
        # Load information about the below-water dataset
        with open(os.path.join(self.root, 'BELOW_LABELS.json')) as file:
            data = json.load(file)
            
        # Analyze the information about the below-water dataset
        for key in data.keys():
            regions = data[key]['regions']
            for region in regions:
                if 'id' in region['region_attributes']:
                    identity = region['region_attributes']['id']
                else:
                    identity = self.unknown_name
                segmentation = np.zeros(2*len(region['shape_attributes']['all_points_x']))
                segmentation[0::2] = region['shape_attributes']['all_points_x']
                segmentation[1::2] = region['shape_attributes']['all_points_y']
                entries.append({
                    'identity': identity,
                    'species': 'WBD',
                    'out_of_focus': region['region_attributes']['out of focus'] == 'true',
                    'file_name': data[key]['filename'],
                    'reg_type': region['shape_attributes']['name'],
                    'segmentation': segmentation,
                    'orientation': 'below'
                })

        # Create the dataframe from entries 
        df = pd.DataFrame(entries)
        if len(df.reg_type.unique()) != 1:
            raise(Exception('Multiple segmentation types'))

        # Finalize the dataframe
        df['image_id'] = range(len(df))
        df['path'] = df['orientation'].str.upper() + os.path.sep + df['file_name']
        df = df.drop(['reg_type', 'file_name'], axis=1)
        return self.finalize_catalogue(df)


class NDD20v2(NDD20):
    outdated_dataset = False

    def fix_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        for i, df_row in df.iterrows():
            # Rewrite wrong segmentations. There is no dolphin -> should be deleted.
            # But that would break compability and the identity is unknown anyway.
            if len(df_row['segmentation']) == 4:
                img = utils.load_image(os.path.join(self.root, df_row['path']))
                w, h = img.size
                df.at[i, 'segmentation'] = np.array(utils.bbox_segmentation([0, 0, w, h]))
        return df
