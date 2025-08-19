from ._client_cog_base import *

class GPT(Client_Cog):

    def _gpt_report(
            self, model_id, version_id, target_description='',
            project_objective='', max_features=15, temperature=0.5):
        """ Generates a report using Open-AI GPT.
        Args:
            model_id (int): The model id
            version_id (int): The version id
            target_description (str): The target description
            project_objective (str): The project objective
            max_features (int): The maximum number of features
            temperature (float): The temperature
        Return:
            dict: The report
        """

        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/versions/'
            f'{version_id}/generate-report'
        )
        params = {
            'target_description': target_description,
            'project_objective': project_objective,
            'max_features': max_features,
            'temperature': temperature
        }
        response = self.session._session.put(
            url=url,
            json=params,
            )

        content = self.session.get_response_content(response)
        return content
