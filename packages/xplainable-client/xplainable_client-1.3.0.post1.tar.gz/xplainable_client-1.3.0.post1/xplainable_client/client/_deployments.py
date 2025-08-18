import inspect
import pandas as pd
from xplainable.utils.encoders import force_json_compliant
from ._client_cog_base import *


class Deployments(Client_Cog):

    #TODO: Add the ability to chose the hostname for users that want to use the client in a different environment
    def deploy(
        self, model_version_id: str,
    ) -> dict:

        payload = {
            "model_version_id": model_version_id
        }

        url = f'{self.session.hostname}/v1/client/deployments/create'
        response = self.session._session.post(url=url, json=force_json_compliant(payload))
        content = self.session.get_response_content(response)

        return content

    def generate_deploy_key(
        self, 
        deployment_id: str, 
        description: str = "",
        days_until_expiry: float = 90
    ) -> str:
        """ Generates a deploy key for a model deployment.
        Args:
            description (str): Description of the deploy key use case.
            deployment_id (str): The deployment id.
            days_until_expiry (float): The number of days until the key expires.
        Returns:
            str: The deploy key.
        """

        payload = {
            "deployment_id": deployment_id,
            "description": description,
            "days_until_expiry": days_until_expiry
        }

        url = f'{self.session.hostname}/v1/client/deployments/create-deploy-key'
        response = self.session._session.post(url=url, json=force_json_compliant(payload))
        content = self.session.get_response_content(response)

        return content

    # TODO everything below here needs to be updated

    def list_deployments(self):
        """ Lists all deployments of the active user's team.
        Returns:
            dict: Dictionary of deployments.
        """
        response = self.session._session.get(
            url=f'{self.session.hostname}/v1/{self.session._ext}/deployments'
            )
        deployments = self.session.get_response_content(response)
        return deployments
        
    def list_deploy_keys(self, deployment_id: str):
        """ Lists all deploy keys for a deployment.
        Args:
            deployment_id (str): The deployment id.
        Returns:
            dict: Dictionary of deploy keys.
        """
        url = f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/deploy-keys'
        response = self.session._session.get(url)
        deploy_keys = self.session.get_response_content(response)
        return deploy_keys

    def list_active_team_deploy_keys(self, team_id: str):
        """ Lists all active team deploy keys.
        Args:
            team_id (str): The team id.
        Returns:
            dict: Dictionary of deploy keys.
        """
        url = f'{self.session.hostname}/deployments/active-team-deploy-keys/{team_id}'
        response = self.session._session.get(url)
        deploy_keys = self.session.get_response_content(response)
        return deploy_keys

    def revoke_deploy_key(self, deployment_id: str, deploy_key_id: str):
        """ Revokes a deploy key for a deployment.
        Args:
            deployment_id (str): The deployment id.
            deploy_key_id (str): The deploy key id.
        Returns:
            dict: Dictionary of deploy keys.
        """
        url = f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/revoke-deploy-key/{deploy_key_id}'
        response = self.session._session.patch(url)
        return response.json()

    def delete_deployment(self, deployment_id: str):
        """ Deletes a model deployment.
        Args:
            deployment_id (str): The deployment id
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}'
        )
        response = self.session._session.delete(url)
        return response.json()
    

    def add_allowed_ip_address(self, deployment_id: str):
        """ Add allowed ip address to a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            json: The json response if the ip is added.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/add-allowed-ip'

        )
        response = self.session._session.put(url)
        return response.json()

    def list_allowed_ip_addresses(self, deployment_id: str):
        """ List allowed ip addresses for a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            json: The json response of the allowed ip addresses.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/get-firewall'
        )
        response = self.session._session.get(url)
        firewall = self.session.get_response_content(response)
        return firewall['allowed_ips']

    def list_allowed_ip_address_and_description(self, deployment_id: str):
        """ List allowed ip addresses and their descriptions for a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            json: The json response of the allowed ip addresses and descriptions.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/get-firewall-descriptions'
        )
        response = self.session._session.get(url)
        firewall = self.session.get_response_content(response)
        return firewall

    def delete_allowed_ip_address(self, deployment_id: str, ip_id: str):
        """ Delete an allowed ip address from a deployment.
        Args:
            deployment_id (str): The deployment id
            ip_id (str): The ip id
        Return:
            json: The json response if the ip is deleted.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/ips/{ip_id}'
        )
        response = self.session._session.delete(url)
        message = self.session.get_response_content(response)
        return message.get('message')

    #Update: complete and is working
    def activate_deployment(self, deployment_id):
        """ Activates a model deployment.
        Args:
            deployment_id (str): The deployment id
        """
        url = (
            f'{self.session.hostname}/v1/client/deployments/{deployment_id}/activate'
        )
        response = self.session._session.patch(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "message": f"Failed with status code {response.status_code}"}

    #Update: complete and is working
    def deactivate_deployment(self, deployment_id):
        """ Deactivates a model deployment.
        Args:
            deployment_id (str): The deployment id
        """
        url = (
            f'{self.session.hostname}/v1/client/deployments/{deployment_id}/deactivate'
        )
        response = self.session._session.patch(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "message": f"Failed with status code {response.status_code}"}
        
    def enable_explain(self, deployment_id: str):
        """ Enables explain for a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            str: The message if explain is enabled.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/enable-explain'
        )
        response = self.session._session.patch(url)
        try:
            message = self.session.get_response_content(response)
            return message.get('message')
        except:
            return {"Explain for this deployment could not be enabled. Status code: ", response.status_code}

        
    def disable_explain(self, deployment_id: str):
        """ Disables explain for a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            str: The message if explain is disabled.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/disable-explain'
        )
        response = self.session._session.patch(url)
        try:
            message = self.session.get_response_content(response)
            return message.get('message')
        except:
            return {"Explain for this deployment could not be disabled. Status code: ", response.status_code}

    def activate_deployment_ip_blocking(self, deployment_id: str):
        """ Activates ip blocking for a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            str: The message if ip blocking is activated.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/activate-deployment-ip-blocking'
        )
        response = self.session._session.patch(url)
        try:
            message = self.session.get_response_content(response)
            return message.get('message')
        except:
            return {"Ip blocking for this deployment could not be activated. Status code: ", response.status_code}

    def deactivate_deployment_ip_blocking(self, deployment_id: str):
        """ Deactivates ip blocking for a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            str: The message if ip blocking is deactivated.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/deactivate-deployment-ip-blocking'
        )
        response = self.session._session.patch(url)
        try:
            message = self.session.get_response_content(response)
            return message.get('message')
        except:
            return {"Ip blocking for this deployment could not be deactivated. Status code: ", response.status_code}

    def revoke_all_deploy_keys(self, deployment_id: str):
        """ Revokes all deploy keys for a deployment.
        Args:
            deployment_id (str): The deployment id
        Return:
            str: The message if all deploy keys are revoked.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/revoke-all-user-deploy-keys'
        )
        response = self.session._session.patch(url)
        try:
            message = self.session.get_response_content(response)
            return message.get('message')
        except:
            return {"All deploy keys for this deployment could not be revoked. Status code: ", response.status_code}

    def delete_deploy_key(self, deployment_id: str, key_id: str):
        """ Deletes a deploy key for a deployment.
        Args:
            deployment_id (str): The deployment id
            key_id (str): The key id
        Return:
            str: The message if the key is deleted.
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/deploy-keys/{key_id}'
        )
        response = self.session._session.delete(url)
        try:
            message = self.session.get_response_content(response)
            return message.get('message')
        except:
            return {"Deploy key could not be deleted. Status code: ", response.status_code}


    def generate_example_deployment_payload(self, deployment_id):
        """ Generates an example deployment payload for a deployment.
        Args:
            deployment_id (str): The deployment id.
        """
        url = f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/payload'
        response = self.session._session.get(url)
        return response.json()
    

    def add_deployment_middleware(
        self, deployment_id, func, name, description=None):
        """ Adds or replaces a middleware function to a deployment.
        Args:
            deployment_id (str): The deployment id
            func (function): The middleware function
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/add-middleware'
        )
        # Convert function to expected name
        if func.__name__ != 'middleware':
            func = self.__parse_function(func)
            source_code = func.source

        else:
            source_code = inspect.getsource(func)
        body = {
            "code_block": source_code,
            "name": name,
            "description": description
        }
        response = self.session._session.put(
            url=url,
            json=body
            )
        return response.json()
    
    def get_middleware(self, deployment_id):
        """ Gets the middleware function from a deployment.
        Args:
            deployment_id (str): The deployment id
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/middleware'
        )
        response = self.session._session.get(url)
        return self.session.get_response_content(response)

    def delete_deployment_middleware(self, deployment_id):
        """ Deletes a middleware function from a deployment.
        Args:
            deployment_id (str): The deployment id
        """
        url = (
            f'{self.session.hostname}/v1/{self.session._ext}/deployments/{deployment_id}/middleware'
        )
        response = self.session._session.delete(url)
        return {"status_code": response.status_code}
