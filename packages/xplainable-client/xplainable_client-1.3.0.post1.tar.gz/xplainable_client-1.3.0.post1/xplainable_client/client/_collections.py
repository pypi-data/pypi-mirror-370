from ._client_cog_base import *


class Collections(Client_Cog):

    def create_collection(self, model_id: str, name: str, description: str):
        """ Creates a new collection.
        Args:
            model_id (str): The model id.
            name (str): The name of the collection.
            description (str): The description of the collection.
        Returns:
            int: The id of the collection created.
        """
        payload = {
            "name": name,
            "description": description
        }
        
        response = self.session._session.put(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/create-collection",
            json=payload
            )
        data = self.session.get_response_content(response)
        return data
    
    
    def get_model_collections(self, model_id: str):
        """ Gets all collections of a model.
        Args:
            model_id (str): The model id.
        Returns:
            dict: Dictionary of collections.
        """
        response = self.session._session.get(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections"
            )
        data = self.session.get_response_content(response)
        return data
    
    def get_team_collections(self):
        """ Gets all collections of a team.
        Returns:
            dict: Dictionary of collections.
        """
        response = self.session._session.get(
            url=f"{self.session.hostname}/v1/{self.session._ext}/collections"
            )
        data = self.session.get_response_content(response)
        return data
    

    def edit_collection_name(self, model_id: str, collections_id: str, name: str):
        """ Edits the name of a collection.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
            name (str): The new name of the collection.
        Returns:
            json: A json payload.
        """
        payload = {
            "name": name
        }

        response = self.session._session.patch(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collections_id}/name",
            json=payload
            )
        return response
    

    def edit_collection_description(self, model_id: str, collections_id: str, description: str):
        """ Edits the description of a collection.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
            description (str): The new description of the collection.
        Returns:
            json: A json payload.
        """
        payload = {
            "description": description
        }

        response = self.session._session.patch(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collections_id}/description",
            json=payload
            )
        return response
    

    def delete_collection(self, model_id: str, collections_id: str):
        """ Deletes a collection.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
        Returns:
            json: A json payload.
        """
        response = self.session._session.delete(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collections_id}"
            )
        return response
    

    def delete_model_collections(self, model_id: str):
        """ Deletes all collections of a model.
        Args:
            model_id (str): The model id.
        Returns:
            json: A json payload.
        """
        response = self.session._session.delete(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections"
            )
        return response
    
    
    def restore_collection(self, model_id: str, collection_id: str):
        """ Restores a collection.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
        Returns:
            json: A json payload.
        """
        response = self.session._session.patch(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collection_id}/restore"
            )
        return response
    

    def get_collection(self, model_id: str, collection_id: str):
        """ Gets a collection.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
        Returns:
            dict: Dictionary of collection.
        """
        response = self.session._session.get(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collection_id}"
            )
        data = self.session.get_response_content(response)
        return data
    

    #TODO: Implement.
    # def add_scenario(self, model_id: str, version_id: str, collection_id: str):
    #     try:
    #         response = self.session._session.get(
    #             url=f'{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/versions/{version_id}'
    #         )
    #         return self.session.get_response_content(response)
    #     except Exception as e:
    #         raise ValueError(f'Model with ID {model_id}:{version_id} does not exist')
    #     return

    # add_scenario


    def edit_scenario_notes(self, model_id: str, collection_id: str, scenario_id: str, notes: str):
        """ Edits the notes of a scenario.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
            scenario_id (str): The scenario id.
            notes (str): The new notes of the scenario.
        Returns:
            json: A json payload.
        """
        payload = {
            "notes": notes
        }

        response = self.session._session.patch(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collection_id}/scenarios/{scenario_id}/notes",
            json=payload
            )
        return response
    

    def delete_scenario(self, model_id: str, collection_id: str, scenario_id: str):
        """" Deletes a scenario.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
            scenario_id (str): The scenario id.
        Returns:
            json: A json payload.
        """

        response = self.session._session.delete(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collection_id}/scenarios/{scenario_id}"
            )
        return response
    

    def restore_scenario(self, model_id: str, collection_id: str, scenario_id: str):
        """ Restores a scenario.
        Args:
            model_id (str): The model id.
            collections_id (str): The collection id.
            scenario_id (str): The scenario id.
        Returns:
            json: A json payload.
        """
        response = self.session._session.patch(
            url=f"{self.session.hostname}/v1/{self.session._ext}/models/{model_id}/collections/{collection_id}/scenarios/{scenario_id}/restore"
            )
        return response