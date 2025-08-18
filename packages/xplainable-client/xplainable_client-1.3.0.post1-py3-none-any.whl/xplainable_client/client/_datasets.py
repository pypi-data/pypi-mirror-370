from ._client_cog_base import *

import requests
import pandas as pd


class Datasets(Client_Cog):

    # upload_dataset

    def list_datasets(self):

        response = requests.get('https://api.xplainable.io/v1/public-datasets')
        
        if response.status_code != 200:
            raise ValueError(f'Unable to list datasets. Check your connection and try again.')
        
        return response.json()

    def _get_url_path(self, name):
        _base = 'xplainablepublic'
        _type = 'blob.core.windows.net'
        _loc = 'asset-repository/datasets'

        return f'https://{_base}.{_type}/{_loc}/{name}/data.csv'

    def load_dataset(self, name):

        datasets = self.list_datasets()

        if name not in datasets:
            raise ValueError(f'{name} is not available. Run xp.list_datasets() to see available datasets.')
        
        try:
            url = self._get_url_path(name)
            df = pd.read_csv(url)

            return df
        
        except Exception as e:
            raise ValueError(f'Unable to load dataset {name}. Check your connection and try again.')
        
    # update_dataset

    # detele_dataset

    # list_dataset_children

    # preview_dataset

    # list_pub_datasets