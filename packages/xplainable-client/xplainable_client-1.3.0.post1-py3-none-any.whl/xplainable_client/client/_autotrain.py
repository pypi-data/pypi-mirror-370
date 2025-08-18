"""
Autotrain functionality for the Xplainable client.

This module provides methods for automated training workflows including
dataset summarization, goal generation, feature engineering, and model training.
"""

import json
import pandas as pd
from typing import Dict, Any, Optional, List, Union
from xplainable.utils.encoders import force_json_compliant
from ._client_cog_base import Client_Cog


class Autotrain(Client_Cog):
    """Autotrain functionality for automated ML workflows."""

    def summarize_dataset(
        self,
        file_path: str,
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Summarize a dataset by uploading a file.
        
        Args:
            file_path (str): Path to the dataset file
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Dataset summary and metadata
        """
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    'team_id': team_id,
                    'textgen_config': json.dumps(textgen_config) if textgen_config else None
                }
                
                url = f'{self.session.hostname}/v1/client/autotrain/summarize'
                response = self.session._session.post(
                    url=url,
                    files=files,
                    data=data
                )
                
            return self.session.get_response_content(response)
            
        except Exception as e:
            raise Exception(f"Failed to summarize dataset: {str(e)}")

    def generate_goals(
        self,
        summary: Dict[str, Any],
        team_id: str,
        n: int = 5,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate training goals based on dataset summary.
        
        Args:
            summary (dict): Dataset summary from summarize_dataset
            team_id (str): Team ID
            n (int): Number of goals to generate
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Generated goals and metadata
        """
        payload = {
            "team_id": team_id,
            "req": {
                "summary": summary,
                "n": n,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/goal'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def generate_labels(
        self,
        summary: Dict[str, Any],
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate label recommendations for training.
        
        Args:
            summary (dict): Dataset summary from summarize_dataset
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Label recommendations and metadata
        """
        payload = {
            "team_id": team_id,
            "req": {
                "summary": summary,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/labels'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def generate_feature_engineering(
        self,
        summary: Dict[str, Any],
        team_id: str,
        n: int = 5,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate feature engineering recommendations.
        
        Args:
            summary (dict): Dataset summary from summarize_dataset
            team_id (str): Team ID
            n (int): Number of recommendations to generate
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Feature engineering recommendations and metadata
        """
        payload = {
            "team_id": team_id,
            "req": {
                "summary": summary,
                "n": n,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/feature_engineering'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def start_autotrain(
        self,
        model_name: str,
        model_description: str,
        summary: Dict[str, Any],
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start the autotrain process.
        
        Args:
            model_name (str): Name for the model
            model_description (str): Description of the model
            summary (dict): Dataset summary from summarize_dataset
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Training job information including training_id
        """
        payload = {
            "team_id": team_id,
            "req": {
                "model_name": model_name,
                "model_description": model_description,
                "summary": summary,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/autotrain'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def check_training_status(
        self,
        training_id: str,
        team_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of a training job.
        
        Args:
            training_id (str): Training job ID from start_autotrain
            team_id (str): Team ID
            
        Returns:
            dict: Training status and progress information
        """
        url = f'{self.session.hostname}/v1/client/autotrain/train/status/{training_id}'
        response = self.session._session.get(
            url=url,
            params={'team_id': team_id}
        )
        
        return self.session.get_response_content(response)

    def train_manual(
        self,
        label: str,
        model_name: str,
        model_description: str,
        preprocessor_id: str,
        version_id: str,
        team_id: str,
        drop_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Train a model manually with specific parameters.
        
        Args:
            label (str): Target label column
            model_name (str): Name for the model
            model_description (str): Description of the model
            preprocessor_id (str): Preprocessor ID
            version_id (str): Preprocessor version ID
            team_id (str): Team ID
            drop_columns (list, optional): Columns to drop
            
        Returns:
            dict: Training job information
        """
        payload = {
            "team_id": team_id,
            "req": {
                "label": label,
                "drop_columns": drop_columns or [],
                "model_name": model_name,
                "model_description": model_description,
                "preprocessor_id": preprocessor_id,
                "version_id": version_id
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/train'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def cleanup_autotrain(self) -> Dict[str, Any]:
        """
        Clean up autotrain resources and cache.
        
        Returns:
            dict: Cleanup status
        """
        url = f'{self.session.hostname}/v1/client/autotrain/autotrain/cleanup'
        response = self.session._session.delete(url=url)
        
        return self.session.get_response_content(response)

    def query_dataset(
        self,
        goal: Dict[str, Any],
        summary: Dict[str, Any],
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query dataset using natural language.
        
        Args:
            goal (dict): Query goal/question
            summary (dict): Dataset summary
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Query results and insights
        """
        payload = {
            "team_id": team_id,
            "req": {
                "goal": goal,
                "summary": summary,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/query'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def visualize_data(
        self,
        summary: Dict[str, Any],
        goal: Dict[str, Any],
        team_id: str,
        library: str = "plotly",
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate data visualizations.
        
        Args:
            summary (dict): Dataset summary
            goal (dict): Visualization goal
            team_id (str): Team ID
            library (str): Visualization library (plotly, matplotlib, etc.)
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Visualization code and metadata
        """
        payload = {
            "team_id": team_id,
            "req": {
                "summary": summary,
                "goal": goal,
                "library": library,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/visualize'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def edit_visualization(
        self,
        summary: Dict[str, Any],
        code: str,
        instructions: Union[str, List[str]],
        team_id: str,
        library: str = "plotly",
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Edit existing visualization code.
        
        Args:
            summary (dict): Dataset summary
            code (str): Existing visualization code
            instructions (str or list): Edit instructions
            team_id (str): Team ID
            library (str): Visualization library
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Updated visualization code and metadata
        """
        payload = {
            "team_id": team_id,
            "req": {
                "summary": summary,
                "code": code,
                "instructions": instructions,
                "library": library,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/visualize/edit'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def generate_insights(
        self,
        goal: Dict[str, Any],
        summary: Dict[str, Any],
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate insights about the dataset.
        
        Args:
            goal (dict): Analysis goal
            summary (dict): Dataset summary
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Generated insights and analysis
        """
        payload = {
            "team_id": team_id,
            "req": {
                "goal": goal,
                "summary": summary,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/insights'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def recommend_dataprep(
        self,
        summary: Dict[str, Any],
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get data preprocessing recommendations.
        
        Args:
            summary (dict): Dataset summary
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Data preprocessing recommendations
        """
        payload = {
            "team_id": team_id,
            "req": {
                "summary": summary,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/dataprep/recommend'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def apply_dataprep(
        self,
        preprocessor_id: str,
        version_id: str,
        apply: str,
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply data preprocessing steps.
        
        Args:
            preprocessor_id (str): Preprocessor ID
            version_id (str): Version ID
            apply (str): Preprocessing operation to apply
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Applied preprocessing results
        """
        payload = {
            "team_id": team_id,
            "req": {
                "preprocessor_id": preprocessor_id,
                "version_id": version_id,
                "apply": apply,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/dataprep/apply'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def download_dataprep(
        self,
        preprocessor_id: str,
        version_id: str,
        team_id: str
    ) -> Dict[str, Any]:
        """
        Download processed data.
        
        Args:
            preprocessor_id (str): Preprocessor ID
            version_id (str): Version ID
            team_id (str): Team ID
            
        Returns:
            dict: Download information or processed data
        """
        payload = {
            "team_id": team_id,
            "req": {
                "preprocessor_id": preprocessor_id,
                "version_id": version_id
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/dataprep/download'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response)

    def generate_text(
        self,
        prompt: str,
        team_id: str,
        textgen_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate text using LLM.
        
        Args:
            prompt (str): Text prompt
            team_id (str): Team ID
            textgen_config (dict, optional): Text generation configuration
            
        Returns:
            dict: Generated text and metadata
        """
        payload = {
            "team_id": team_id,
            "req": {
                "prompt": prompt,
                "textgen_config": textgen_config or {}
            }
        }
        
        url = f'{self.session.hostname}/v1/client/autotrain/text/generate'
        response = self.session._session.post(
            url=url,
            json=force_json_compliant(payload)
        )
        
        return self.session.get_response_content(response) 