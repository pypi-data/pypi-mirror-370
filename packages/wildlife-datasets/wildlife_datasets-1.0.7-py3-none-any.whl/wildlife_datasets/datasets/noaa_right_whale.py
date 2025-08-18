import os
import shutil
import pandas as pd
from . import utils
from .datasets import DatasetFactory
from .summary import summary

class NOAARightWhale(DatasetFactory):
    summary = summary['NOAARightWhale']
    archive = 'noaa-right-whale-recognition.zip'

    @classmethod
    def _download(cls):
        command = f"competitions download -c noaa-right-whale-recognition --force"
        exception_text = '''Kaggle terms must be agreed with.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#noaarightwhale'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=cls.archive)

    @classmethod
    def _extract(cls):
        try:
            utils.extract_archive(cls.archive, delete=True)
            utils.extract_archive('imgs.zip', delete=True)
            # Move misplaced image
            shutil.move('w_7489.jpg', 'imgs')
            os.remove('w_7489.jpg.zip')
        except:
            exception_text = '''Extracting failed.
                Either the download was not completed or the Kaggle terms were not agreed with.
                Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#noaarightwhale'''
            raise Exception(exception_text)

    def create_catalogue(self) -> pd.DataFrame:
        # Load information about the training dataset
        data = pd.read_csv(os.path.join(self.root, 'train.csv'))
        df1 = pd.DataFrame({
            'image_id': data['Image'].str.split('.', expand=True)[0].str.strip('w_').astype(int),
            'path': 'imgs' + os.path.sep + data['Image'],
            'identity': data['whaleID'],
            'original_split': 'train'
            })

        # Load information about the testing dataset
        data = pd.read_csv(os.path.join(self.root, 'sample_submission.csv'))
        df2 = pd.DataFrame({
            'image_id': data['Image'].str.split('.', expand=True)[0].str.strip('w_').astype(int),
            'path': 'imgs' + os.path.sep + data['Image'],
            'identity': self.unknown_name,
            'original_split': 'test'
            })
        
        # Finalize the dataframe
        df = pd.concat([df1, df2])
        return self.finalize_catalogue(df)
