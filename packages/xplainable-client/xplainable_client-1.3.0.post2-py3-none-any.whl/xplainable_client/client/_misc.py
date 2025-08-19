""" Copyright Xplainable Pty Ltd"""
import pandas as pd
import inspect
import ast
import xplainable
from xplainable.utils.model_parsers import *
from xplainable.quality.scanner import XScan
import numpy as np

from xplainable.utils.encoders import NpEncoder
from xplainable.metrics.metrics import evaluate_classification, evaluate_regression

from ._client_cog_base import *


class Misc(Client_Cog):

    @staticmethod
    def _get_xplainable_version():
        """Retrieve the installed xplainable package version."""
        try:
            # Access the __version__ attribute from the xplainable package
            return xplainable.__version__
        except AttributeError:
            # Handle the case where __version__ is not defined
            return "Unknown"

    def ping_server(self, hostname):
        response = self.session._session.get(
            f'{hostname}/v1/compute/ping',
            timeout=1
            )
        content = json.loads(response.content)
        if content == True:
            return True
        else:
            return False

    def ping_gateway(self, hostname):
        response = self.session._session.get(
            f'{hostname}/v1/ping',
            timeout=1
            )
        content = json.loads(response.content)
        if content == True:
            return True
        else:
            return False



    def load_classifier(self, model_id: int, version_id: int, model=None):
        """ Loads a binary classification model by model_id
        Args:
            model_id (str): A valid model_id
            version_id (str): A valid version_id
            model (PartitionedClassifier): An existing model to add partitions
        Returns:
            xplainable.PartitionedClassifier: The loaded xplainable classifier
        """
        response = self.__get_model__(model_id, version_id)
        if response['model_type'] != 'binary_classification':
            raise ValueError(f'Model with ID {model_id}:{version_id} is not a binary classification model')
        return parse_classifier_response(response, model)
    

    def load_regressor(self, model_id: int, version_id: int, model=None):
        """ Loads a regression model by model_id and version_id
        Args:
            model_id (str): A valid model_id
            version_id (str): A valid version_id
            model (PartitionedRegressor): An existing model to add partitions to
        Returns:
            xplainable.PartitionedRegressor: The loaded xplainable regressor
        """
        response = self.__get_model__(model_id, version_id)
        if response['model_type'] != 'regression':
            raise ValueError(f'Model with ID {model_id}:{version_id} is not a regression model')
        return parse_regressor_response(response, model)
    

    def _get_partition_data(
            self, model, partition_name: str, x: pd.DataFrame,
            y: pd.Series) -> dict:
        """ Logs a partition to a model version.
        Args:
            model_type (str): The model type
            partition_name (str): The name of the partition column
            model (mixed): The model to log
            model_id (int): The model id
            version_id (int): The version id
            evaluation (dict, optional): Model evaluation data and metrics.
            training_metadata (dict, optional): Model training metadata.
        """
        model_type, _ = self._detect_model_type(model)
        data = {
            "partition": str(partition_name),
            "profile": json.dumps(model._profile, cls=NpEncoder),
            "feature_importances": json.loads(
                json.dumps(model.feature_importances, cls=NpEncoder)),
            "id_columns": json.loads(
                json.dumps(model.id_columns, cls=NpEncoder)),
            "columns": json.loads(
                json.dumps(model.columns, cls=NpEncoder)),
            "parameters": model.params.to_json(),
            "base_value": json.loads(
                json.dumps(model.base_value, cls=NpEncoder)),
            "feature_map": json.loads(
                json.dumps({k: fm.forward for k, fm in model.feature_map.items()}, cls=NpEncoder)),
            "target_map": json.loads(
                json.dumps(model.target_map.reverse, cls=NpEncoder)),
            "category_meta": json.loads(
                json.dumps(model.category_meta, cls=NpEncoder)),
            # "constructs": model.constructs_to_json(),
            "calibration_map": None,
            "support_map": None
        }
        if model_type == 'binary_classification':
            data.update({
                "calibration_map": json.loads(
                    json.dumps(model._calibration_map, cls=NpEncoder)),
                "support_map": json.loads(
                    json.dumps(model._support_map, cls=NpEncoder))
            })
            evaluation = model.metadata.get('evaluation', {})
            if evaluation == {}:
                y_prob = model.predict_score(x)
                if model.target_map:
                    y = y.map(model.target_map)
                evaluation = {
                    'train': evaluate_classification(y, y_prob)
                }

        elif model_type == 'regression':
            evaluation = model.metadata.get('evaluation', {})
            if evaluation == {}:
                y_pred = model.predict(x)
                evaluation = {
                            'train': evaluate_regression(y, y_pred)
                        }

        data["evaluation"] = json.dumps(evaluation, cls=NpEncoder)
        training_metadata = {
            i: v for i, v in model.metadata.items() if i != "evaluation"}

        data["training_metadata"] = json.dumps(training_metadata, cls=NpEncoder)

        if x is not None:
            scanner = XScan()
            scanner.scan(x)  # Assuming scan method doesn't raise exceptions itself now
            results = []
            for i, v in scanner.profile.items():
                # Check if the column 'i' in dataframe 'x' is completely NA
                if x[i].isna().all():
                    # If the column is not all NA, process it
                    feature_info = {
                        "feature": i,
                        "description": '',
                        "type": "All NA",
                        "health_info": json.loads(json.dumps({}, cls=NpEncoder))
                    }
                # If the column is not all NA, process it
                feature_info = {
                    "feature": i,
                    "description": '',
                    "type": v['type'],
                    "health_info": json.loads(json.dumps(v, cls=NpEncoder))
                }
                results.append(feature_info)
            data["health_info"] = json.dumps(results, cls=NpEncoder)
        return data

    @staticmethod
    def __parse_function(func):
        """ Parses a function to a middleware function. """
        if not callable(func):
            raise Exception("Function must be callable")
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if len(params) != 1:
            raise Exception("Function must take one parameter")
        # Parse the source code to an AST
        source = inspect.getsource(func)
        parsed_ast = ast.parse(source)
        # Rename the function in the AST
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                node.name = "middleware"
                break
        # Store the modified source
        modified_source = ast.unparse(parsed_ast)
        # Compile the AST back to code and execute in a new namespace
        local_vars = {}
        exec(compile(
            parsed_ast, filename="<ast>", mode="exec"),
            func.__globals__, local_vars)
        middleware = local_vars['middleware']
        middleware.source = modified_source
        return middleware