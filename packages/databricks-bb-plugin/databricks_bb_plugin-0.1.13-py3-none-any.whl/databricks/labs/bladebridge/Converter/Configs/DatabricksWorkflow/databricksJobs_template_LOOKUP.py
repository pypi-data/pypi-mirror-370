from pyspark.sql import SparkSession
import os
spark = SparkSession.builder.appName("LookupWorkflow").getOrCreate()

%COMPONENT_NAME% = spark.sql(f"""%SQL%""")
dbutils.jobs.taskValues.set(key = "%COMPONENT_NAME%", value = %COMPONENT_NAME%)