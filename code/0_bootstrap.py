# ###########################################################################
#
#  CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
#  (C) Cloudera, Inc. 2022
#  All rights reserved.
#
#  Applicable Open Source License: Apache 2.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#
# ###########################################################################

## Part 0: Bootstrap File
# You need to execute this at the start of the project. This will install the
# requirements and if it's running in local mode it unpacks the preprocessed 
# dataset included in the repo.

# Install the requirements
!pip install --progress-bar off -r requirements.txt

import os
import json
import requests

# Install cmlapi package
try:
    import cmlapi
except ModuleNotFoundError:
    import os
    cluster = os.getenv("CDSW_API_URL")[:-1]+"2"
    !pip3 install {cluster}/python.tar.gz
    import cmlapi 
from cmlapi.rest import ApiException


if os.getenv("STORAGE_MODE") == "external":
    try:
        import cml.data_v1 as cmldata
        SPARK_CONNECTION_NAME = os.getenv("SPARK_CONNECTION_NAME")
        conn = cmldata.get_connection(SPARK_CONNECTION_NAME)
    except: 
        print("Spark connection failed. Continuing in local mode.") 
        # Update project STORAGE_MODE to local
        os.environ["STORAGE_MODE"] = "local"

        client = cmlapi.default_client()
        project_id = os.getenv("CDSW_PROJECT_ID")
        try:
            project = client.get_project(project_id)
            if project.environment == '':
                env = {}
            else:
                env = json.loads(project.environment)

            env["STORAGE_MODE"] = "local"
            project.environment = json.dumps(env)
            client.update_project(project,project_id)
        except ApiException as e:
            print("Exception when calling cmlapi->update_project: %s\n" % e)


if os.getenv("STORAGE_MODE") == "local":
    !cd data && tar xzvf preprocessed_flight_data.tgz
else:
    pass


# Start Exploratory Data Science and Visualization experience
# https://blog.cloudera.com/the-power-of-exploratory-data-analysis-for-ml/
API_KEY = os.getenv("CDSW_API_KEY")
CREATE_CDV_ENDPOINT = os.getenv("CDSW_PROJECT_URL") + "/create-cdv-app?"

response = requests.post(CREATE_CDV_ENDPOINT, 
                         json = {}, 
                         headers={"Content-Type": "application/json"},
                         auth=(API_KEY, "")
                        )
print(response.text)
