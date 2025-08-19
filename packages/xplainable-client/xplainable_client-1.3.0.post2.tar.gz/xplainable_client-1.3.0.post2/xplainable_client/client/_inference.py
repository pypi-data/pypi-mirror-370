from ._client_cog_base import *


class Inference(Client_Cog):
    
    def predict(self, filename: str, model_id: str, version_id: str, threshold: float = 0.5, delimiter: str = ","):
        """ Predicts the target column of a dataset.
        Args:
            filename (str): The name of the file.
            model_id (str): The model id.
            version_id (str): The version id.
            threshold (float): The threshold for classification models.
            delimiter (str): The delimiter of the file.
        Returns:
            dict: The prediction results.
        """
        url = f"{self.session.hostname}/v1/predict"
        try:
            files = {'file': open(filename, 'rb')}
        except Exception:
            raise ValueError(f'Unable to open file {filename}. Check the file path and try again.')
        form = {'model_id': model_id, 'version_id': version_id, 'threshold': threshold, 'delimiter': delimiter}
        
        try:
            response = self.session._session.post(url, files=files, form=form)
        except Exception as e:
            raise ValueError(f'{e}. Please contact us if this problem persists.')
        data = self.session.get_response_content(response)
        return data

