# coding: utf-8

# Copyright 2020,2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
from typing import Dict
from ibm_aigov_facts_client.utils import cp4d_utils
import jwt
import time
import json
#import requests
import pandas as pd
import hashlib
from ibm_aigov_facts_client.utils.constants import *

import ibm_aigov_facts_client._wrappers.requests as requests

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator,CloudPakForDataAuthenticator
from ibm_aigov_facts_client.client import fact_trace
from ibm_aigov_facts_client.utils.client_errors import *
from ibm_aigov_facts_client.utils.enums import ContainerType,Provider
from ibm_cloud_sdk_core.utils import convert_model
from ibm_aigov_facts_client.supporting_classes.factsheet_utils import ExternalModelSchemas,TrainingDataReference,DeploymentDetails,ModelEntryProps,ModelDetails
from .factsheet_utility import FactSheetElements
from ibm_aigov_facts_client.utils.doc_annotations import deprecated, deprecated_param
from typing import BinaryIO, Dict, List, TextIO, Union
from ibm_aigov_facts_client.factsheet.assets import Assets
from ibm_aigov_facts_client.factsheet.asset_utils_model import ModelAssetUtilities
from ibm_aigov_facts_client.utils.utils import validate_enum,validate_type,STR_TYPE

from ..utils.config import *


_logger = logging.getLogger(__name__)


class ExternalModelFactsElements:

    def __init__(self,facts_client: 'fact_trace.FactsClientAdapter'):

        self._facts_client=facts_client
        self.api_key=self._facts_client._api_key
        self.experiment_name = self._facts_client.experiment_name
        self.model_asset_id=None
        self.model_catalog_id=None
        self.is_cpd=self._facts_client._is_cp4d
        self._external_model=self._facts_client._external
        

        if self.is_cpd:
            self.cpd_configs=convert_model(self._facts_client.cp4d_configs)
            self._cp4d_version=self._facts_client._cp4d_version

    def _encode_model_id(self,model_id):
        encoded_id=hashlib.md5(model_id.encode("utf-8")).hexdigest()
        return encoded_id

    def _encode_deployment_id(self,deployment_id):
        encoded_deployment_id=hashlib.md5(deployment_id.encode("utf-8")).hexdigest()
        return encoded_deployment_id

    def _validate_payload(self, payload):
        if not payload["model_id"] or not payload["name"]:
            raise ClientError("model_identifier or name is missing")
        else:
            payload["model_id"]= self._encode_model_id(payload["model_id"])
        if payload.get("deployment_details"):
            payload["deployment_details"]["id"]= self._encode_deployment_id(payload["deployment_details"]["id"])

        return payload

    def _validate_payload_new(self, payload):
        if not payload["model_id"] or not payload["name"]:
            raise ClientError("model_identifier or name is missing")
        else:
            modelVal = payload["model_id"]
            payload["model_id"]= self._encode_model_id(modelVal)
            payload["external_model_identifier"]= modelVal
        if payload.get("deployment_details"):
            deploymentVal = payload["deployment_details"]["id"]
            payload["deployment_details"]["id"]= self._encode_deployment_id(deploymentVal)
            payload["deployment_details"]["external_identifier"]= deploymentVal

        return payload

    @deprecated_param(alternative="save_external_model_asset().add_tracking_model_usecase() to create/link to model usecase",deprecated_args="model_entry_props") 
    def save_external_model_asset(self, model_identifier:str, name:str, description:str=None, model_details:'ModelDetails'=None, schemas:'ExternalModelSchemas'=None, training_data_reference:'TrainingDataReference'=None,deployment_details:'DeploymentDetails'=None,model_entry_props:'ModelEntryProps'=None,catalog_id:str=None)->ModelAssetUtilities:

        """
        Save External model assets in catalog and (Optional) link to model usecase. By default external model is goig to save in Platform Asset Catalog ( PAC ), if user wants to save it to different catalog user has to pass catalog_id parameter.

        :param str model_identifier: Identifier specific to ML providers (i.e., Azure ML service: `service_id`, AWS Sagemaker:`model_name`)
        :param str name: Name of the model
        :param str description: (Optional) description of the model
        :param ModelDetails model_details: (Optional) Model details.   Supported only after CP4D >= 4.7.0
        :param ExternalModelSchemas schemas: (Optional) Input and Output schema of the model
        :param TrainingDataReference training_data_reference: (Optional) Training data schema
        :param DeploymentDetails deployment_details: (Optional) Model deployment details
        :param ModelEntryProps model_entry_props: (Optional) Properties about model usecase and model usecase catalog.
        :param str catalog_id: (Optional) catalog id as external model can be saved in catalog itslef..

        :rtype: ModelAssetUtilities
        
        If using external models with manual log option, initiate client as:
        
        .. code-block:: python

            from ibm_aigov_facts_client import AIGovFactsClient
            client= AIGovFactsClient(api_key=API_KEY,experiment_name="external",enable_autolog=False,external_model=True)
            
        If using external models with Autolog, initiate client as:

        .. code-block:: python

            from ibm_aigov_facts_client import AIGovFactsClient
            client= AIGovFactsClient(api_key=API_KEY,experiment_name="external",external_model=True)

        If using external models with no tracing, initiate client as:

        .. code-block:: python

            from ibm_aigov_facts_client import AIGovFactsClient
            client= AIGovFactsClient(api_key=API_KEY,external_model=True,disable_tracing=True)

            
        If using Cloud pak for Data:

        .. code-block:: python

            creds=CloudPakforDataConfig(service_url="<HOST URL>",
                                        username="<username>",
                                        password="<password>")
            
            client = AIGovFactsClient(experiment_name=<experiment_name>,external_model=True,cloud_pak_for_data_configs=creds)
        
        Payload example by supported external providers:

        Azure ML Service:

        .. code-block:: python

            from ibm_aigov_facts_client.supporting_classes.factsheet_utils import DeploymentDetails,TrainingDataReference,ExternalModelSchemas

            external_schemas=ExternalModelSchemas(input=input_schema,output=output_schema)
            trainingdataref=TrainingDataReference(schema=training_ref)
            deployment=DeploymentDetails(identifier=<service_url in Azure>,name="deploymentname",deployment_type="online",scoring_endpoint="test/score")

            client.external_model_facts.save_external_model_asset(model_identifier=<service_id in Azure>
                                                                        ,name=<model_name>
                                                                        ,model_details=<model_stub_details>
                                                                        ,deployment_details=deployment
                                                                        ,schemas=external_schemas
                                                                        ,training_data_reference=tdataref)

            client.external_model_facts.save_external_model_asset(model_identifier=<service_id in Azure>
                                                                        ,name=<model_name>
                                                                        ,model_details=<model_stub_details>
                                                                        ,deployment_details=deployment
                                                                        ,schemas=external_schemas
                                                                        ,training_data_reference=tdataref,
                                                                        ,catalog_id=<catalog_id>) Different catalog_id other than Platform Asset Catalog (PAC)

        AWS Sagemaker:

        .. code-block:: python

            external_schemas=ExternalModelSchemas(input=input_schema,output=output_schema)
            trainingdataref=TrainingDataReference(schema=training_ref)
            deployment=DeploymentDetails(identifier=<endpoint_name in Sagemaker>,name="deploymentname",deployment_type="online",scoring_endpoint="test/score")

            client.external_model_facts.save_external_model_asset(model_identifier=<model_name in Sagemaker>
                                                                        ,name=<model_name>
                                                                        ,model_details=<model_stub_details>
                                                                        ,deployment_details=deployment
                                                                        ,schemas=external_schemas
                                                                        ,training_data_reference=tdataref)


            client.external_model_facts.save_external_model_asset(model_identifier=<model_name in Sagemaker>
                                                                        ,name=<model_name>
                                                                        ,model_details=<model_stub_details>
                                                                        ,deployment_details=deployment
                                                                        ,schemas=external_schemas
                                                                        ,training_data_reference=tdataref,
                                                                        ,catalog_id=<catalog_id>) Different catalog_id other than Platform Asset Catalog (PAC)

        NOTE: 

        If you are are using Watson OpenScale to monitor this external model the evaluation results will automatically become available in the external model. 
        
        - To enable that automatic sync of evaluation results for Sagemaker model make sure to use the Sagemaker endpoint name when creating the external model in the notebook 
        - To enable that for Azure ML model make sure to use the scoring URL. 
        
        Example format: 
        ``https://southcentralus.modelmanagement.azureml.net/api/subscriptions/{az_subscription_id}/resourceGroups/{az_resource_group}/
        providers/Microsoft.MachineLearningServices/workspaces/{az_workspace_name}/services/{az_service_name}?api-version=2018-03-01-preview``


    
        model usecase props example, IBM Cloud and CPD:

        >>> from ibm_aigov_facts_client.supporting_classes.factsheet_utils import ModelEntryProps,DeploymentDetails,TrainingDataReference,ExternalModelSchemas
        
        Older way:

        For new model usecase:

        >>> props=ModelEntryProps(
                    model_entry_catalog_id=<catalog_id>,
                    model_entry_name=<name>,
                    model_entry_desc=<description>
                    )
        
        
        For linking to existing model usecase:

        >>> props=ModelEntryProps(
                    model_entry_catalog_id=<catalog_id>,
                    model_entry_id=<model_entry_id to link>
                    )

        >>> client.external_model_facts.save_external_model_asset(model_identifier=<model_name in Sagemaker>
                                                                        ,name=<model_name>
                                                                        ,model_details=<model_stub_details>
                                                                        ,deployment_details=deployment
                                                                        ,schemas=external_schemas
                                                                        ,training_data_reference=tdataref
                                                                        ,model_entry_props= props)

        Current and go forward suggested way:

        .. code-block:: python

            external_model=client.external_model_facts.save_external_model_asset(model_identifier=<service_id in Azure>
                                                                ,name=<model_name>
                                                                ,model_details=<model_stub_details>
                                                                ,deployment_details=deployment
                                                                ,schemas=external_schemas
                                                                ,training_data_reference=tdataref)
            
        
        Create and link to new model usecase:

        >>> external_model.add_tracking_model_usecase(model_usecase_name=<entry name>, model_usecase_catalog_id=<catalog id>)
        
        Link to existing model usecase:
        
        >>> external_model.add_tracking_model_usecase(model_usecase_id=<model_usecase_id>, model_usecase_catalog_id=<catalog id>)

        To remove model usecase:

        >>> external_model.remove_tracking_model_usecase()
        
        """

        if catalog_id is not None and self.is_cpd and self._cp4d_version < "4.6.4":
            raise ClientError("Version mismatch: Saving external model to a catalog other than platform asset catalog (PAC) is only supported in CP4D version 4.6.4 or higher. Please remove catalog_id value to save in PAC. Current version of CP4D is "+self._cp4d_version)
        
        if self.is_cpd and self._cp4d_version < "4.7.0":
            if deployment_details:
                deployment_details=convert_model(deployment_details)
            if schemas:
                schemas=convert_model(schemas)
            if training_data_reference:
                training_data_reference=convert_model(training_data_reference)
            if model_entry_props:
                model_entry_props=convert_model(model_entry_props)

            data = {
                'model_id': model_identifier,
                'name': name,
                'description': description,
                'schemas': schemas,
                'training_data_references': training_data_reference,
                'deployment_details': deployment_details,
                'catalog_id': catalog_id
            }

            data = {k: v for (k, v) in data.items() if v is not None}
            _validated_payload= self._validate_payload(data)

        if (self.is_cpd and self._cp4d_version >= "4.7.0") or (not self.is_cpd):
            training_list = []
            if model_details:
                model_details=convert_model(model_details)
            if deployment_details:
                deployment_details=convert_model(deployment_details)
            if schemas:
                schemas=convert_model(schemas)
            if training_data_reference:
                training_data_reference=convert_model(training_data_reference)
                                
                if (training_data_reference.get('connection') is not None) or (training_data_reference.get('location') is not None):
                    if (training_data_reference.get('type') is None) or (training_data_reference.get('id') is None):
                        raise ClientError("As connection or location is specified type and ID are mandatory for training data reference")

                training_list.append(training_data_reference)
            if model_entry_props:
                model_entry_props=convert_model(model_entry_props)
        
            if model_details:
                if model_details.get('provider'):
                    validate_enum(model_details.get('provider'),"Provider", Provider, False)
                data = {
                    'model_id': model_identifier,
                    'name': name,
                    'description': description,
                    'model_type': model_details.get('model_type'),
                    'input_type': model_details.get('input_type'),
                    'algorithm': model_details.get('algorithm'),
                    'label_type': model_details.get('label_type'),
                    'label_column': model_details.get('label_column'),
                    'prediction_type': model_details.get('prediction_type'),
                    'software_spec': model_details.get('software_spec'),
                    'software_spec_id': model_details.get('software_spec_id'),
                    'external_model_provider': model_details.get('provider'),
                    'schemas': schemas,
                    'training_data_references': training_list,
                    'deployment_details': deployment_details,
                    'catalog_id': catalog_id
                }
            else:
                data = {
                    'model_id': model_identifier,
                    'name': name,
                    'description': description,
                    'schemas': schemas,
                    'training_data_references': training_list,
                    'deployment_details': deployment_details,
                    'catalog_id': catalog_id
                }

            data = {k: v for (k, v) in data.items() if v is not None}
            _validated_payload= self._validate_payload_new(data)

        self._publish(_validated_payload)
        
        if model_entry_props:
            if 'project_id' in model_entry_props or 'space_id' in model_entry_props:
                raise WrongProps("project or space is not expected for external models")

            if 'asset_id' not in model_entry_props:
                model_entry_props['asset_id']=self.model_asset_id
            
            model_entry_props['model_catalog_id']=self.model_catalog_id
            
            self._add_tracking_model_entry(model_entry_props)

        return Assets(self._facts_client).get_model(model_id=self.model_asset_id,container_type=ContainerType.CATALOG,container_id=self.model_catalog_id)
    
    
    def list_external_models(self, inventory_id:str=None,start_index: int = None, max_results: int = None):
        """
        **Lists external models available to the user or within a specific inventory**.

        This method retrieves external models accessible to the account. Optionally, you can filter the models by a specific inventory ID and control pagination using `start_index` and `max_results`.

        Parameters:
            - inventory_id (str, optional): The unique identifier of the inventory to filter models by.If not provided, models from the entire account are listed.
            - start_index (int, optional): The index at which to begin listing models. Useful for pagination.Should be used with `max_results` to define the range of models to retrieve.
            - max_results (int, optional): The maximum number of models to return in a single request.Must be used with `start_index`. The maximum allowed value is 150 models per request.

        Returns:
            list[str]: A list of strings, each representing the identifier or name of an external model.

        Default Behavior

        +--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | **Scenario**                         | **Result**                                                                                                                  |
        +--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | No Parameters                        | Returns up to 100 models from the specified or default inventory.                                                           |
        +--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
        | With `start_index` and `max_results` | Returns models within the specified range. For example, `start_index=51` and `max_results=50` returns models 51 through 100.|
        +--------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+

        Example:
            >>> # List all external models
            >>> models = client.external_model_facts.list_external_models()
            
            >>> # List external models for a specific inventory with pagination
            >>> models = client.external_model_facts.list_external_models(inventory_id="12345", start_index=0, max_results=10)
        """
        print("-" * OUTPUT_WIDTH)
        print(" External Models Retrieval Started ".center(OUTPUT_WIDTH))
        print("-" * OUTPUT_WIDTH)
        try:
            # Set default values if parameters are None
            from_size = start_index if start_index is not None else 0
            size = max_results if max_results is not None else 100

            # Ensure that parameters are valid
            if (start_index is None) != (max_results is None):
                raise ValueError("Both 'start_index' and 'max_results' must be provided together if either is provided")

            if from_size < 0:
                raise ValueError("'start_index' must be 0 or greater")
            if size <= 0:
                raise ValueError("'max_results' must be greater than 0")
            if size > 150:  # Adjust the maximum limit as needed
                raise ValueError("'max_results' must not exceed 150")


                    
            bss_id = self._get_bss_id_cpd() if self.is_cpd else self._get_bss_id()

            query = {
                "size": size,
                "from": from_size,
                "query": {
                    "bool": {
                        "must": [{"query_string": {"query": "*"}}],
                        "filter": [{"term": {"metadata.artifact_type": "model_stub"}}]
                    }
                },
                "sort": [
                    {
                    "metadata.modified_on": {
                        "order": "desc",
                        "unmapped_type": "date"
                    }
                    }
                ]
            }

            # Add catalog_id filter if inventory_id is provided
            if inventory_id:
                query["query"]["bool"]["filter"].append({"term": {"entity.assets.catalog_id": inventory_id}})

            url = self._list_external_model_url()
            headers = self._get_headers()
            headers["Run-as-Tenant"] = bss_id

            response = requests.post(url, headers=headers, data=json.dumps(query))
            if response.status_code == 200:
                data = response.json()
                total_size = data.get('size', 0)
                rows = data.get('rows', [])

                if total_size == 0:
                    _logger.error("No external models were found for the specified inventory ID or account.")
                    return []
            
    


                # if from_size >= total_size:
                #     _logger.info(f"Displaying external models from range {from_size} to {total_size} out of {total_size} total models.")
                #     raise ValueError("The starting index exceeds the total number of models.")
                # else:
                #     end_index = from_size + size
                #     if end_index > total_size:
                #         end_index = total_size  

                #     _logger.info(f"Displaying models {from_size} to {end_index} out of {total_size} total models.")

                # # Notify user if more results are available
                # if total_size > from_size + size:
                #     _logger.info(f"By Default, retrieved {len(rows)} external models out of {total_size}. {total_size - (from_size + len(rows))} external models are still available. Adjust the 'from_size' and 'size' parameters to fetch additional models.")
                                # Check if from_size and size are provided and handle accordingly
           
                if from_size >= total_size:
                        _logger.info(f"A total of {total_size} external models have been fetched.")
                        _logger.info(f"Displaying external models from range {from_size} to {total_size} out of {total_size} total external models.")
                        raise ValueError("The starting index exceeds the total number of models.")

                else:
                        end_index = from_size + size
                        if end_index > total_size:
                            end_index = total_size  
                        _logger.info(f"A total of {total_size} external models have been fetched.")
                        _logger.info(f"Displaying external models from range {from_size} to {end_index} out of {total_size} total external models.")

                if total_size > from_size + size:
                        _logger.info(f"By Default, retrieved {len(rows)} external models out of {total_size}. {total_size - (from_size + len(rows))} external models are still available. Adjust the 'start_index' and 'max_results' parameters to fetch additional models.")
                transformed_rows = self._process_external_models(rows)
                return transformed_rows

            else:
                # Raise ClientError with detailed response
                error_message = response.json().get('message', 'Unknown error occurred')
                raise ClientError(f"Failed to fetch inventory details. Status code: {response.status_code}, Error: {error_message}")
        
        except Exception as e:
            _logger.error(f"An error occurred: {e}")
            raise
    
    def _process_external_models(self, rows):
        catalog_ids = set()
        user_ids = set()
        processed_rows = []

        # Process rows to extract necessary information and populate sets for unique catalog_ids and user_ids
        for item in rows:
            entity = item.get('entity', {}).get('assets', {})
            catalog_id = entity.get('catalog_id', '')
            owner_ids = entity.get('rov', {}).get('owners', [])
            owner_id = owner_ids[0] if owner_ids else ''

            if catalog_id:
                catalog_ids.add(catalog_id)
            if owner_id:
                user_ids.add(owner_id)

            # Store catalog_id and owner_id within each item for later use
            item['catalog_id'] = catalog_id
            item['owner_id'] = owner_id
            processed_rows.append(item)

        # Fetch inventory names
        _logger.info("Retrieving Inventory names...")
        inventory_names = {
            catalog_id: self._get_inventory_name(catalog_id)
            for catalog_id in catalog_ids
            if catalog_id
        }
        for idx in range(len(catalog_ids)):
            sys.stdout.write(f"\rRetrieving Inventory names: {idx + 1}/{len(catalog_ids)} " + "." * ((idx % 3) + 1))
            sys.stdout.flush()
            time.sleep(0.5)
        sys.stdout.write("\r")
        sys.stdout.flush()
        _logger.info("Inventory names retrieval completed.")

        # Fetch user names
        _logger.info("Retrieving Creator names...")
        user_names = {
            user_id: self._fetch_user_name(user_id)
            for user_id in user_ids
            if user_id
        }
        for idx in range(len(user_ids)):
            sys.stdout.write(f"\rRetrieving Creator names: {idx + 1}/{len(user_ids)} " + "." * ((idx % 3) + 1))
            sys.stdout.flush()
            time.sleep(0.5)
        sys.stdout.write("\r")
        sys.stdout.flush()
        _logger.info("Creator names retrieval completed.")

        # Build the transformed list using the stored catalog_id and owner_id
        transformed_rows = [
            {
                "name": item.get('metadata', {}).get('name', ''),
                "inventory_id": item['catalog_id'],
                "inventory_name": inventory_names.get(item['catalog_id'], ''),
                "asset_id": item.get('artifact_id', ''),
                "creator_name": user_names.get(item['owner_id'], '')
            }
            for item in processed_rows
        ]

        _logger.info("External models retrieval completed successfully.")
        return transformed_rows
    
    def _list_external_model_url(self):
        if self.is_cpd:
            base_url = self.cpd_configs['url']

        else:    
            if get_env() == 'dev':
                base_url = dev_config['DEFAULT_DEV_SERVICE_URL']
            elif get_env() == 'test':
                base_url = test_config['DEFAULT_TEST_SERVICE_URL']
            else:
                base_url = prod_config['DEFAULT_SERVICE_URL']

        url = f"{base_url}/v3/search?auth_cache=false&auth_scope=ibm_watsonx_governance_catalog%2Ccatalog"
         
        return url
    

    def _get_inventory_name(self, inventory_id: str) -> str:
        url = self._retrieve_inventory_url(inventory_id)
        
        try:
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                # Directly access 'entity' for the inventory name
                return data['entity'].get('name', 'Unknown Inventory')
            else:
                raise ClientError(f"Failed to fetch inventory details. Status code: {response.status_code}, "
                            f"Error: {response.json().get('message', 'Unknown error occurred')}")
            
        except Exception as e:
            raise ClientError(f"An error occurred while fetching inventory details: {e}")
    
    def _retrieve_inventory_url(self, inventory_id=None):
        if self.is_cpd:
            bss_id = self._get_bss_id_cpd()
        else:
            bss_id = self._get_bss_id()
        
        if self.is_cpd:
            base_url = self.cpd_configs['url']

        else:    
            if get_env() == 'dev':
                base_url = dev_config['DEFAULT_DEV_SERVICE_URL']
            elif get_env() == 'test':
                base_url = test_config['DEFAULT_TEST_SERVICE_URL']
            else:
                base_url = prod_config['DEFAULT_SERVICE_URL']

        if inventory_id:
            url = f"{base_url}/v1/aigov/inventories/{inventory_id}"
        else:
            url = f"{base_url}/v1/aigov/inventories?bss_account_id={bss_id}&limit=25&skip=0"
         
        return url
    

    def _fetch_user_name(self, user_id: str) -> str:
        try:
            user_profile_url = self._retrieve_user_profile_url(user_id)
            response = requests.get(user_profile_url, headers=self._get_headers())

            if response.status_code == 200:
                user_data = response.json()
                user_names = [
                    resource['entity'].get('name', 'N/A')
                    for resource in user_data.get('resources', [])
                    if resource.get('entity', {}).get('iam_id') == user_id
                ] or ['N/A']
                return user_names[0]
            else:
                _logger.error(f"Failed to fetch user profile for user ID '{user_id}'. "
                              f"Status code: {response.status_code}")
                return 'N/A'
        except Exception as e:
            _logger.error(f"An error occurred while fetching user profile: {e}")
            return 'N/A'
    
    def _retrieve_user_profile_url(self, external_model_admin: str) -> str:
        if self.is_cpd:
            url = self.cpd_configs['url'] + \
                '/v2/user_profiles?q=iam_id%20IN%20'+external_model_admin
        else:
            if get_env() == 'dev':
                url = dev_config['DEFAULT_DEV_SERVICE_URL'] + \
                    '/v2/user_profiles?q=iam_id%20IN%20'+external_model_admin
            elif get_env() == 'test':
                url = test_config['DEFAULT_TEST_SERVICE_URL'] + \
                    '/v2/user_profiles?q=iam_id%20IN%20'+external_model_admin
            else:
                url = prod_config['DEFAULT_SERVICE_URL'] + \
                    '/v2/user_profiles?q=iam_id%20IN%20'+external_model_admin

        return url

    def _add_tracking_model_entry(self,model_entry_props):
        
        """
            Link external model to Model usecase. 
        """

        model_entry_name=model_entry_props.get("model_entry_name")
        model_entry_desc=model_entry_props.get("model_entry_desc")

        model_entry_catalog_id=model_entry_props.get("model_entry_catalog_id")
        model_entry_id=model_entry_props.get("model_entry_id")

        grc_model_id=model_entry_props.get("grc_model_id")

        
        model_asset_id=model_entry_props['asset_id']
        container_type=ContainerType.CATALOG
        container_id= model_entry_props['model_catalog_id']
    
        
        params={}
        payload={}
        
        params[container_type +'_id']=container_id


        if grc_model_id and not self._is_cp4d:
            raise WrongParams ("grc_model_id is only applicable for Openpages enabled CPD platform")

        payload['model_entry_catalog_id']=model_entry_catalog_id
        
        if model_entry_name or (model_entry_name and model_entry_desc):
            if model_entry_id:
                raise WrongParams("Please provide either NAME and DESCRIPTION or MODEL_ENTRY_ID and MODEL_ENTRY_CATALOG_ID")
            payload['model_entry_name']=model_entry_name
            if model_entry_desc:
                payload['model_entry_description']=model_entry_desc        
            
        elif model_entry_id:
            if model_entry_name and model_entry_desc:
                raise WrongParams("Please provide either NAME and DESCRIPTION or MODEL_ENTRY_ID and MODEL_ENTRY_CATALOG_ID")
            payload['model_entry_asset_id']=model_entry_id 
            
            
        else:
            raise WrongParams("Please provide either NAME and DESCRIPTION or MODEL_ENTRY_ID and MODEL_ENTRY_CATALOG_ID")

        wkc_register_url=WKC_MODEL_REGISTER.format(model_asset_id)

        if self.is_cpd:
    
            if grc_model_id:
                payload['grc_model_id']=grc_model_id
            url = self.cpd_configs["url"] + \
                 wkc_register_url
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                wkc_register_url
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    wkc_register_url
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    wkc_register_url
        
        if model_entry_id:
            _logger.info("Initiate linking model to existing model usecase {}".format(model_entry_id))
        else:
            _logger.info("Initiate linking model to new model usecase......")
        
        response = requests.post(url,
                                headers=self._get_headers(),
                                params=params,
                                data=json.dumps(payload))

        
        if response.status_code == 200:
            _logger.info("Successfully finished linking Model {} to Model usecase".format(model_asset_id))
        else:
            error_msg = u'Model registration failed'
            reason = response.text
            _logger.info(error_msg)
            raise ClientError(error_msg + '. Error: ' + str(response.status_code) + '. ' + reason)

        return response.json()
    
    def _publish(self, data):

        if data.get('catalog_id'):
            catalog_url = '/v1/aigov/model_inventory/model_stub?catalog_id='+data.get('catalog_id')
        else:
            catalog_url = '/v1/aigov/model_inventory/model_stub'

        if self.is_cpd:
            url = self.cpd_configs["url"] + catalog_url
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + catalog_url
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + catalog_url
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + catalog_url

        params=None
        if self.experiment_name:
            params = {"experiment_name": self.experiment_name}

        if params:
            response = requests.put(url=url,
                                    headers=self._get_headers(),
                                    params=params,
                                    data=json.dumps(data))
        else:
            response = requests.put(url=url,
                        headers=self._get_headers(),
                        data=json.dumps(data))

        if response.status_code == 401:
            _logger.exception("Expired token found.")
            
        elif response.status_code==403:
            _logger.exception("Access Forbidden")
            
        elif response.status_code == 200:
            if response.json()['metadata']['asset_id'] and response.json()['metadata']['catalog_id']:
                self.model_asset_id=response.json()['metadata']['asset_id']
                self.model_catalog_id=response.json()['metadata']['catalog_id']
            _logger.info("External model asset saved successfully under asset_id {} and catalog {}".format(self.model_asset_id,self.model_catalog_id))
        else:
            _logger.exception(
                "Error updating properties..{}".format(response.json()))


    @deprecated(alternative="save_external_model_asset().remove_tracking_model_usecase()")
    def unregister_model_entry(self, asset_id, catalog_id):
        """
            Unregister WKC Model usecase

            :param str asset_id: WKC model usecase id
            :param str catalog_id: Catalog ID where asset is stored


            Example for IBM Cloud or CPD:

            >>> client.external_model_facts.unregister_model_entry(asset_id=<model asset id>,catalog_id=<catalog_id>)

        """


        wkc_unregister_url=WKC_MODEL_REGISTER.format(asset_id)

        params={}
        params[ContainerType.CATALOG +'_id']=catalog_id

        if self.is_cpd:
            url = self.cp4d_configs["url"] + \
                 wkc_unregister_url
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                wkc_unregister_url
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    wkc_unregister_url
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    wkc_unregister_url
        
        response = requests.delete(url,
                                headers=self._get_headers(),
                                params=params,
                                )
    
        if response.status_code == 204:
            _logger.info("Successfully finished unregistering WKC Model {} from Model usecase.".format(asset_id))
        else:
            error_msg = u'WKC Model usecase unregistering failed'
            reason = response.text
            _logger.info(error_msg)
            raise ClientError(error_msg + '. Error: ' + str(response.status_code) + '. ' + reason)

    
    @deprecated(alternative="client.assets.list_model_usecases()")
    def list_model_entries(self, catalog_id=None)-> list:
        """
            Returns all WKC Model usecase assets for a catalog

            :param str catalog_id: (Optional) Catalog ID where you want to register model, if None list from all catalogs
            
            :return: All WKC Model usecase assets for a catalog
            :rtype: list

            Example:

            >>> client.external_model_facts.list_model_entries()
            >>> client.external_model_facts.list_model_entries(catalog_id=<catalog_id>)

        """
        
        if catalog_id:
            list_url=WKC_MODEL_LIST_FROM_CATALOG.format(catalog_id)
        else:
            list_url=WKC_MODEL_LIST_ALL

        if self.is_cpd:
            url = self.cpd_configs["url"] + \
                 list_url
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                list_url
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    list_url
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    list_url
        
        response = requests.get(url,
                                headers=self._get_headers(),
                                #params=params,
                                )


        if response.status_code == 200:
            return response.json()["results"]

        else:
            error_msg = u'WKC Models listing failed'
            reason = response.text
            _logger.info(error_msg)
            raise ClientError(error_msg + '. Error: ' + str(response.status_code) + '. ' + reason)

    def _get_headers(self):
        token = self._facts_client._authenticator.token_manager.get_token() if  ( isinstance(self._facts_client._authenticator, IAMAuthenticator) or (isinstance(self._facts_client.authenticator, CloudPakForDataAuthenticator))) else self._facts_client.authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        return iam_headers 
    

    def _get_bss_id(self):
        try:
            token = self._facts_client._authenticator.token_manager.get_token() if (isinstance(self._facts_client._authenticator, IAMAuthenticator) or (
                isinstance(self._facts_client.authenticator, CloudPakForDataAuthenticator))) else self._facts_client.authenticator.bearer_token
            decoded_bss_id = jwt.decode(token, options={"verify_signature": False})[
                "account"]["bss"]
        except jwt.ExpiredSignatureError:
            raise
        return decoded_bss_id
    
    def _get_bss_id_cpd(self):
        decoded_bss_id = "999"
        return decoded_bss_id


