from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime
import json
import os
spark = SparkSession.builder.appName("SwitchWorkflow").getOrCreate()

%CASE_CONDITIONS%

%CASE_EXEC%