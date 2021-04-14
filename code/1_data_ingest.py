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


# Part 1: Data Ingest
# A data scientist should never be blocked in getting data into their environment,
# so CML is able to ingest data from many sources.
# Whether you have data in .csv files, modern formats like parquet or feather,
# in cloud storage or a SQL database, CML will let you work with it in a data
# scientist-friendly environment.

# Access local data on your computer
#
# Accessing data stored on your computer is a matter of [uploading a file to the CML filesystem and
# referencing from there](https://docs.cloudera.com/machine-learning/cloud/import-data/topics/ml-accessing-local-data-from-your-computer.html).
#
# > Go to the project's **Overview** page. Under the **Files** section, click **Upload**, select the relevant data files to be uploaded and a destination folder.
#
# If, for example, you upload a file called, `mydata.csv` to a folder called `data`, the
# following example code would work.

# ```
# import pandas as pd
#
# df = pd.read_csv('data/mydata.csv')
#
# # Or:
# df = pd.read_csv('/home/cdsw/data/mydata.csv')
# ```

# Access data in S3
#
# Accessing [data in Amazon S3](https://docs.cloudera.com/machine-learning/cloud/import-data/topics/ml-accessing-data-in-amazon-s3-buckets.html)
# follows a familiar procedure of fetching and storing in the CML filesystem.
# > Add your Amazon Web Services access keys to your project's
# > [environment variables](https://docs.cloudera.com/machine-learning/cloud/import-data/topics/ml-environment-variables.html)
# > as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
#
# To get the the access keys that are used for your in the CDP DataLake, you can follow
# [this Cloudera Community Tutorial](https://community.cloudera.com/t5/Community-Articles/How-to-get-AWS-access-keys-via-IDBroker-in-CDP/ta-p/295485)

#
# The following sample code would fetch a file called `myfile.csv` from the S3 bucket, `data_bucket`, and store it in the CML home folder.
# ```
# # Create the Boto S3 connection object.
# from boto.s3.connection import S3Connection
# aws_connection = S3Connection()
#
# # Download the dataset to file 'myfile.csv'.
# bucket = aws_connection.get_bucket('data_bucket')
# key = bucket.get_key('myfile.csv')
# key.get_contents_to_filename('/home/cdsw/myfile.csv')
# ```


# Access data from Cloud Storage or the Hive metastore
#
# Accessing data from [the Hive metastore](https://docs.cloudera.com/machine-learning/cloud/import-data/topics/ml-accessing-data-from-apache-hive.html)
# that comes with CML only takes a few more steps.
# But first we need to fetch the data from Cloud Storage and save it as a Hive table.
#
# > Specify `STORAGE` as an
# > [environment variable](https://docs.cloudera.com/machine-learning/cloud/import-data/topics/ml-environment-variables.html)
# > in your project settings containing the Cloud Storage location used by the DataLake to store
# > Hive data. On AWS it will `s3a://[something]`, on Azure it will be `abfs://[something]` and on
# > on prem CDSW cluster, it will be `hdfs://[something]`
#
# This was done for you when you ran `0_bootstrap.py`, so the following code is set up to run as is.
# It begins with imports and creating a `SparkSession`.


# The following data ingestion script uses Spark to read in two large datasets from external storage,
# cleans and unions them together into one cohesive dataset. This script accesses data that was copied
# to external storage in 0_bootstrap.py and is only executed if the project is run with STORAGE_MODE=='external'.
#
# The two datasets are:
#     1. set_1/flight_data_1.csv - one large .csv file (~8GB) of historical airline delay data for years
#        prior to 2009.
#     2. set_2/* - 10 separate .csv files (~8GB in total) of airline delay data corresponding to years 2009 - 2018


import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *


def main():

    spark = (
        SparkSession.builder.appName("PythonSQL")
        .config("spark.executor.memory", "8g")
        .config("spark.executor.cores", "2")
        .config("spark.driver.memory", "6g")
        .config("spark.executor.instances", "4")
        .config("spark.yarn.access.hadoopFileSystems", os.environ["STORAGE"])
        .getOrCreate()
    )

    # First, lets load in the first dataset
    # Since we know the data already, we can add schema upfront. This is good practice as Spark will
    # read *all* the Data if you try infer the schema.

    set_1_schema = StructType(
        [
            StructField("month", DoubleType(), True),
            StructField("dayofmonth", DoubleType(), True),
            StructField("dayofweek", DoubleType(), True),
            StructField("deptime", DoubleType(), True),
            StructField("crsdeptime", DoubleType(), True),
            StructField("arrtime", DoubleType(), True),
            StructField("crsarrtime", DoubleType(), True),
            StructField("uniquecarrier", StringType(), True),
            StructField("flightnum", DoubleType(), True),
            StructField("tailnum", StringType(), True),
            StructField("actualelapsedtime", DoubleType(), True),
            StructField("crselapsedtime", DoubleType(), True),
            StructField("airtime", DoubleType(), True),
            StructField("arrdelay", DoubleType(), True),
            StructField("depdelay", DoubleType(), True),
            StructField("origin", StringType(), True),
            StructField("dest", StringType(), True),
            StructField("distance", DoubleType(), True),
            StructField("taxiin", DoubleType(), True),
            StructField("taxiout", DoubleType(), True),
            StructField("cancelled", DoubleType(), True),
            StructField("cancellationcode", StringType(), True),
            StructField("diverted", DoubleType(), True),
            StructField("carrierdelay", DoubleType(), True),
            StructField("weatherdelay", DoubleType(), True),
            StructField("nasdelay", DoubleType(), True),
            StructField("securitydelay", DoubleType(), True),
            StructField("lateaircraftdelay", DoubleType(), True),
            StructField("year", DoubleType(), True),
        ]
    )

    path_1 = (
        f"{os.environ['STORAGE']}/{os.environ['DATA_LOCATION']}/set_1/flight_data_1.csv"
    )
    flights_data_1 = spark.read.csv(path_1, header=True, schema=set_1_schema, sep=",")

    # Let's inspect the data
    flights_data_1.show()
    flights_data_1.printSchema()

    # Now we can load in the second, fragmented dataset
    set_2_schema = StructType(
        [
            StructField("FL_DATE", DateType(), True),
            StructField("OP_CARRIER", StringType(), True),
            StructField("OP_CARRIER_FL_NUM", StringType(), True),
            StructField("ORIGIN", StringType(), True),
            StructField("DEST", StringType(), True),
            StructField("CRS_DEP_TIME", StringType(), True),
            StructField("DEP_TIME", StringType(), True),
            StructField("DEP_DELAY", DoubleType(), True),
            StructField("TAXI_OUT", DoubleType(), True),
            StructField("WHEELS_OFF", StringType(), True),
            StructField("WHEELS_ON", StringType(), True),
            StructField("TAXI_IN", DoubleType(), True),
            StructField("CRS_ARR_TIME", StringType(), True),
            StructField("ARR_TIME", StringType(), True),
            StructField("ARR_DELAY", DoubleType(), True),
            StructField("CANCELLED", DoubleType(), True),
            StructField("CANCELLATION_CODE", StringType(), True),
            StructField("DIVERTED", DoubleType(), True),
            StructField("CRS_ELAPSED_TIME", DoubleType(), True),
            StructField("ACTUAL_ELAPSED_TIME", DoubleType(), True),
            StructField("AIR_TIME", DoubleType(), True),
            StructField("DISTANCE", DoubleType(), True),
            StructField("CARRIER_DELAY", DoubleType(), True),
            StructField("WEATHER_DELAY", DoubleType(), True),
            StructField("NAS_DELAY", DoubleType(), True),
            StructField("SECURITY_DELAY", DoubleType(), True),
            StructField("LATE_AIRCRAFT_DELAY", DoubleType(), True),
        ]
    )

    path_2 = f"{os.environ['STORAGE']}/{os.environ['DATA_LOCATION']}/set_2/"
    flights_data_2 = spark.read.csv(
        path_2, schema=set_2_schema, header=True, sep=",", nullValue="NA"
    )
    flights_data_2.show()

    # Now we can clean up the schema of flights_data_1 so it is consistent with flights_data_2,
    # downselect to columns of interest, and then union all the data together

    flights_data_1 = flights_data_1.withColumn(
        "FL_DATE",
        to_date(
            concat_ws("-", col("year"), col("month"), col("dayofmonth")),
            "yyyy.0-MM.0-dd.0",
        ),
    )

    flights_data_1 = (
        flights_data_1.withColumnRenamed("deptime", "DEP_TIME")
        .withColumnRenamed("crsdeptime", "CRS_DEP_TIME")
        .withColumnRenamed("arrtime", "ARR_TIME")
        .withColumnRenamed("crsarrtime", "CRS_ARR_TIME")
        .withColumnRenamed("uniquecarrier", "OP_CARRIER")
        .withColumnRenamed("flightnum", "OP_CARRIER_FL_NUM")
        .withColumnRenamed("actualelapsedtime", "ACTUAL_ELAPSED_TIME")
        .withColumnRenamed("crselapsedtime", "CRS_ELAPSED_TIME")
        .withColumnRenamed("airtime", "AIR_TIME")
        .withColumnRenamed("arrdelay", "ARR_DELAY")
        .withColumnRenamed("depdelay", "DEP_DELAY")
        .withColumnRenamed("origin", "ORIGIN")
        .withColumnRenamed("dest", "DEST")
        .withColumnRenamed("distance", "DISTANCE")
        .withColumnRenamed("taxiin", "TAXI_IN")
        .withColumnRenamed("taxiout", "TAXI_OUT")
        .withColumnRenamed("cancelled", "CANCELLED")
        .withColumnRenamed("cancellationcode", "CANCELLATION_CODE")
        .withColumnRenamed("diverted", "DIVERTED")
        .withColumnRenamed("carrierdelay", "CARRIER_DELAY")
        .withColumnRenamed("weatherdelay", "WEATHER_DELAY")
        .withColumnRenamed("nasdelay", "NAS_DELAY")
        .withColumnRenamed("securitydelay", "SECURITY_DELAY")
        .withColumnRenamed("lateaircraftdelay", "LATE_AIRCRAFT_DELAY")
    )

    flights_data_1 = flights_data_1.select(
        [
            "FL_DATE",
            "DEP_TIME",
            "CRS_DEP_TIME",
            "ARR_TIME",
            "CRS_ARR_TIME",
            "OP_CARRIER",
            "OP_CARRIER_FL_NUM",
            "ACTUAL_ELAPSED_TIME",
            "CRS_ELAPSED_TIME",
            "AIR_TIME",
            "ARR_DELAY",
            "DEP_DELAY",
            "ORIGIN",
            "DEST",
            "DISTANCE",
            "TAXI_IN",
            "TAXI_OUT",
            "CANCELLED",
            "CANCELLATION_CODE",
            "DIVERTED",
            "CARRIER_DELAY",
            "WEATHER_DELAY",
            "NAS_DELAY",
            "SECURITY_DELAY",
            "LATE_AIRCRAFT_DELAY",
        ]
    )

    flights_data_2 = flights_data_2.select(
        [
            "FL_DATE",
            "DEP_TIME",
            "CRS_DEP_TIME",
            "ARR_TIME",
            "CRS_ARR_TIME",
            "OP_CARRIER",
            "OP_CARRIER_FL_NUM",
            "ACTUAL_ELAPSED_TIME",
            "CRS_ELAPSED_TIME",
            "AIR_TIME",
            "ARR_DELAY",
            "DEP_DELAY",
            "ORIGIN",
            "DEST",
            "DISTANCE",
            "TAXI_IN",
            "TAXI_OUT",
            "CANCELLED",
            "CANCELLATION_CODE",
            "DIVERTED",
            "CARRIER_DELAY",
            "WEATHER_DELAY",
            "NAS_DELAY",
            "SECURITY_DELAY",
            "LATE_AIRCRAFT_DELAY",
        ]
    )

    flights_data_all = flights_data_1.unionByName(flights_data_2)

    # Now we can store the Spark DataFrame as a file in the local CML file system
    # *and* as a table in Hive used by the other parts of the project.

    # flights_data.coalesce(1).write.csv(
    #    "file:/home/cdsw/raw/telco-data/",
    #    mode='overwrite',
    #    header=True
    # )

    spark.sql("show databases").show()
    spark.sql("show tables in default").show()

    # Create the Hive table
    # This is here to create the table in Hive used be the other parts of the project, if it
    # does not already exist.

    hive_database = os.environ["HIVE_DATABASE"]
    hive_table = os.environ["HIVE_TABLE"]
    hive_table_fq = hive_database + "." + hive_table

    if hive_table not in list(
        spark.sql("show tables in default").toPandas()["tableName"]
    ):
        print(f"Creating the {hive_table} table in {hive_database}")
        flights_data_all.write.format("parquet").mode("overwrite").saveAsTable(
            f"{hive_table_fq}"
        )

    # Show the data in the hive table
    spark.sql(f"select * from {hive_table_fq}").show()

    # To get more detailed information about the hive table you can run this:
    spark.sql(f"describe formatted {hive_table_fq}").toPandas()

    spark.stop()
    # Other ways to access data

    # To access data from other locations, refer to the
    # [CML documentation](https://docs.cloudera.com/machine-learning/cloud/import-data/index.html).

    # Scheduled Jobs
    #
    # One of the features of CML is the ability to schedule code to run at regular intervals,
    # similar to cron jobs. This is useful for **data pipelines**, **ETL**, and **regular reporting**
    # among other use cases. If new data files are created regularly, e.g. hourly log files, you could
    # schedule a Job to run a data loading script with code like the above.

    # > Any script [can be scheduled as a Job](https://docs.cloudera.com/machine-learning/cloud/jobs-pipelines/topics/ml-creating-a-job.html).
    # > You can create a Job with specified command line arguments or environment variables.
    # > Jobs can be triggered by the completion of other jobs, forming a
    # > [Pipeline](https://docs.cloudera.com/machine-learning/cloud/jobs-pipelines/topics/ml-creating-a-pipeline.html)
    # > You can configure the job to email individuals with an attachment, e.g. a csv report which your
    # > script saves at: `/home/cdsw/job1/output.csv`.

    # Try running this script `1_data_ingest.py` for use in such a Job.


if __name__ == "__main__":

    if os.environ["STORAGE_MODE"] == "external":
        main()
    else:
        print(
            "Skipping 1_data_ingest.py because excution is limited to local storage only."
        )
        pass