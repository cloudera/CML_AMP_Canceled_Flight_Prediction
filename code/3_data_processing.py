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

# The following data processing script uses Spark to read in the Hive table that
# was created in 1_data_ingest.py and sample records from it to balance out the
# cancelled and not-cancelled classes. This sampled dataset is then saved to the local
# project to be used for modeling in the 5_model_train.py

import os
import sys

    
def main():
    import cml.data_v1 as cmldata
    from pyspark import SparkContext
    from pyspark.sql import functions as sqlfn   
    
    ### cleanup needed start
    # These should come from the AMP
    os.environ['SPARK_CONNECTION_NAME'] = "go01-aw-dl"
    os.environ['DW_DATABASE'] = "airlines_iceberg"
    os.environ['DW_TABLE'] = "flights"
    
    # These shound't be set after cml.data adds iceberg support
    import glob

    jars = glob.glob("/opt/spark/optional-lib/*.jar")
    jarsList = ",".join(jars)
    SparkContext.setSystemProperty("spark.jars",jarsList)

    SparkContext.setSystemProperty("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
    SparkContext.setSystemProperty("spark.sql.catalog.spark_catalog.type", "hive")
    SparkContext.setSystemProperty("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    ### cleanup needed end


    SparkContext.setSystemProperty('spark.executor.cores', '4')
    SparkContext.setSystemProperty('spark.executor.memory', '8g')

    SPARK_CONNECTION_NAME = os.getenv("SPARK_CONNECTION_NAME")
    conn = cmldata.get_connection(SPARK_CONNECTION_NAME)
    spark = conn.get_spark_session()

    # Lets query the table
    dw_database = os.environ["DW_DATABASE"]
    dw_table = os.environ["DW_TABLE"]

    flight_df = spark.sql(f"select * from {dw_database}.{dw_table}")
    flight_df.printSchema()

    print(f"There are {flight_df.count()} records in {dw_database}.{dw_table}.")

    # Since majority of flights are not cancelled, lets create a more balanced dataset
    # by undersampling from non-cancelled flights
    sample_normal_flights = flight_df.filter("cancelled == 0").sample(
        withReplacement=False, fraction=0.03, seed=3
    )

    cancelled_flights = flight_df.filter("cancelled == 1")

    all_flight_data = cancelled_flights.union(sample_normal_flights)
    all_flight_data.persist()

    all_flight_data = all_flight_data.withColumn(
        "hour",
        sqlfn.substring(
            sqlfn.when(sqlfn.length(sqlfn.col("crsdeptime")) == 4, sqlfn.col("crsdeptime")).otherwise(
                sqlfn.concat(sqlfn.lit("0"), sqlfn.col("crsdeptime"))
            ),
            1,
            2,
        ).cast("integer"),
    ).withColumn(
        "fl_date",
        sqlfn.to_date(
            sqlfn.concat_ws("/", sqlfn.col("year"), sqlfn.col("month"), sqlfn.col("dayofmonth")),
            "yyyy/M/d",
        ),
    ).withColumn("week", sqlfn.weekofyear("fl_date"))

    smaller_all_flight_data = all_flight_data.select(
        "fl_date",
        "uniquecarrier",
        "flightnum",
        "origin",
        "dest",
        "crsdeptime",
        "crsarrtime",
        "cancelled",
        "crselapsedtime",
        "distance",
        "hour",
        "week",
    )

    smaller_all_flight_data.printSchema()

    # Save the sampled dataset as a .csv file to the local project file system
    smaller_all_flight_data_pd = smaller_all_flight_data.toPandas()
    smaller_all_flight_data_pd.to_csv("data/preprocessed_flight_data.csv", index=False)
    spark.stop()


if __name__ == "__main__":

    if os.environ["STORAGE_MODE"] == "external":
        main()
    else:
        print(
            "Skipping 3_data_processing.py because excution is limited to local storage only."
        )
        pass