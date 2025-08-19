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

import os 


dev_config = {
    'DEFAULT_DEV_SERVICE_URL': 'https://api.dataplatform.dev.cloud.ibm.com',
    'IAM_URL': 'https://iam.stage1.ng.bluemix.net/identity/token',
    'IAM_API_URL':'https://iam.test.cloud.ibm.com/identity/introspect',
    'DEFAULT_DEV_WML_SERVICE_URL':'https://wml-fvt.ml.test.cloud.ibm.com'
}

test_config = {
    'DEFAULT_TEST_SERVICE_URL': 'https://api.dataplatform.test.cloud.ibm.com',
    'IAM_URL': 'https://iam.cloud.ibm.com/identity/token', 
    'IAM_API_URL': 'https://iam.cloud.ibm.com/identity/introspect',
    'DEFAULT_TEST_WML_SERVICE_URL':'https://yp-qa.ml.cloud.ibm.com'
}

sydney_region = {
    "DEFAULT_SERVICE_URL": "https://api.au-syd.dai.cloud.ibm.com",
    'IAM_API_URL':'https://iam.cloud.ibm.com/identity/introspect',
    'DEFAULT_WML_SERVICE_URL':'https://us-south.ml.cloud.ibm.com',
    'UI_SERVICE_URL': 'https://au-syd.dai.cloud.ibm.com'
    
    }

frankfurt_region = {
    "DEFAULT_SERVICE_URL": "https://api.eu-de.dataplatform.cloud.ibm.com",
    'IAM_API_URL':'https://iam.cloud.ibm.com/identity/introspect',
    'DEFAULT_WML_SERVICE_URL':'https://us-south.ml.cloud.ibm.com',
    'UI_SERVICE_URL': 'https://eu-de.dataplatform.cloud.ibm.com',
    
    }

toronto_region = {
    "DEFAULT_SERVICE_URL": "https://api.ca-tor.dai.cloud.ibm.com",
    'IAM_API_URL':'https://iam.cloud.ibm.com/identity/introspect',
    'DEFAULT_WML_SERVICE_URL': "https://ca-tor.ml.cloud.ibm.com",
    'UI_SERVICE_URL': 'https://ca-tor.dai.cloud.ibm.com'

    }

prod_config = {
    "DEFAULT_SERVICE_URL": "https://api.dataplatform.cloud.ibm.com",
    'IAM_API_URL':'https://iam.cloud.ibm.com/identity/introspect',
    'DEFAULT_WML_SERVICE_URL':'https://us-south.ml.cloud.ibm.com'
}

# def ensure_sydney_override():
#     current_env = os.environ.get("FACTS_CLIENT_ENV")
#     if current_env == "sydney":
#         prod_config.update(sydney_region)  
#     else:
#         os.environ["FACTS_CLIENT_ENV"] = os.environ.get("FACTS_CLIENT_ENV", "prod")

# def get_env():
#     ensure_sydney_override()
#     env_value = os.environ.get("FACTS_CLIENT_ENV", "prod")
#     return env_value



def ensure_sydney_override():
    if os.environ.get('FACTS_CLIENT_ENV') == "sydney":
        prod_config.update(sydney_region)  
    elif  os.environ.get('FACTS_CLIENT_ENV') == "frankfurt":
        prod_config.update(frankfurt_region) 
    elif  os.environ.get('FACTS_CLIENT_ENV') == "toronto":
        prod_config.update(toronto_region) 
    else:
        os.environ["FACTS_CLIENT_ENV"] = os.environ.get("FACTS_CLIENT_ENV", "prod")

def get_env():
    ensure_sydney_override()
    return os.environ.get('FACTS_CLIENT_ENV')


WKC_MODEL_REGISTER = u"/v1/aigov/model_inventory/models/{}/model_entry"
WKC_MODEL_LIST_FROM_CATALOG = u"/v1/aigov/model_inventory/{}/model_entries"
WKC_MODEL_LIST_ALL = u"/v1/aigov/model_inventory/model_entries"
