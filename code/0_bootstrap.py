# ###########################################################################
#
#  CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
#  (C) Cloudera, Inc. 2021
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
# You need to at the start of the project. It will install the requirements, creates the
# STORAGE environment variable and copy the data to the STORAGE location.

# The STORAGE environment variable is the Cloud Storage location used by the DataLake
# to store hive data. On AWS it will s3a://[something], on Azure it will be
# abfs://[something] and on CDSW cluster, it will be hdfs://[something]

# Install the requirements
!pip install --progress-bar off -r requirements.txt

# Create the directories and upload data
# from cmlbootstrap import CMLBootstrap
# import os
# import xml.etree.ElementTree as ET
# import subprocess

# # Set the setup variables needed by CMLBootstrap
# HOST = os.getenv("CDSW_API_URL").split(":")[0] + "://" + os.getenv("CDSW_DOMAIN")
# USERNAME = os.getenv("CDSW_PROJECT_URL").split("/")[6]  # args.username  # "vdibia"
# API_KEY = os.getenv("CDSW_API_KEY")
# PROJECT_NAME = os.getenv("CDSW_PROJECT")

# # Instantiate API Wrapper
# cml = CMLBootstrap(HOST, USERNAME, API_KEY, PROJECT_NAME)

# # Set the STORAGE environment variable
# try:
#     storage = os.environ["STORAGE"]
# except:
#     if os.path.exists("/etc/hadoop/conf/hive-site.xml"):
#         tree = ET.parse("/etc/hadoop/conf/hive-site.xml")
#         root = tree.getroot()
#         for prop in root.findall("property"):
#             if prop.find("name").text == "hive.metastore.warehouse.dir":
#                 storage = (
#                     prop.find("value").text.split("/")[0]
#                     + "//"
#                     + prop.find("value").text.split("/")[2]
#                 )
#     else:
#         storage = "/user/" + os.getenv("HADOOP_USER_NAME")
#     storage_environment_params = {"STORAGE": storage}
#     storage_environment = cml.create_environment_variable(storage_environment_params)
#     os.environ["STORAGE"] = storage

# # define a function to run commands on HDFS
# def run_cmd(cmd, raise_err=True):

#     """
#     Run Linux commands using Python's subprocess module

#     Args:
#         cmd (str) - Linux command to run
#     Returns:
#         process
#     """
#     print("Running system command: {0}".format(cmd))

#     proc = subprocess.run(
#         cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
#     )

#     if proc.returncode != 0 and raise_err == True:
#         raise RuntimeError(
#             "Error running command: {}. Return code: {}, Output: {}, Error: {}".format(
#                 cmd, proc.returncode, proc.stdout, proc.stderr
#             )
#         )

#     return proc


# if os.environ["STORAGE_MODE"] == "local":
#     !cd data && tar xzvf preprocessed_flight_data.tgz
# else:
#     # Check if data already exists in external storage, if not, attempt to download the full
#     # datasets to cloud storage, if error, set environment variable indicating the use of local
#     # storage for project build
#     try:
#         dataset_1_check = run_cmd(
#             f'hdfs dfs -test -f {os.environ["STORAGE"]}/{os.environ["DATA_LOCATION"]}/set_1/flight_data_1.csv',
#             raise_err=False,
#         )
#         dataset_2_check = run_cmd(
#             f'hdfs dfs -test -f {os.environ["STORAGE"]}/{os.environ["DATA_LOCATION"]}/set_2/2018.csv',
#             raise_err=False,
#         )

#         if dataset_1_check.returncode != 0:
#             run_cmd(
#                 f'hdfs dfs -mkdir -p {os.environ["STORAGE"]}/{os.environ["DATA_LOCATION"]}/set_1'
#             )
#             run_cmd(
#                 f'curl https://cdp-demo-data.s3-us-west-2.amazonaws.com/all_flight_data.zip | zcat | hadoop fs -put - {os.environ["STORAGE"]}/{os.environ["DATA_LOCATION"]}/set_1/flight_data_1.csv'
#             )

#         if dataset_2_check.returncode != 0:
#             run_cmd(
#                 f'hdfs dfs -mkdir -p {os.environ["STORAGE"]}/{os.environ["DATA_LOCATION"]}/set_2'
#             )
#             run_cmd(
#                 f'for i in $(seq 2009 2018); do curl https://cdp-demo-data.s3-us-west-2.amazonaws.com/$i.csv | hadoop fs -put - {os.environ["STORAGE"]}/{os.environ["DATA_LOCATION"]}/set_2/$i.csv; done'
#             )

#     except RuntimeError as error:
#         cml.create_environment_variable({"STORAGE_MODE": "local"})
#         !cd data && tar xzvf preprocessed_flight_data.tgz
#         print(
#             "Could not interact with external data store so local project storage will be used. HDFS DFS command failed with the following error:"
#         )
#         print(error)