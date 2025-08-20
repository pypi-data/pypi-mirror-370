from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql.connect.session import DataFrame as DataFrameRemote
from pyspark.sql.connect.session import SparkSession as SparkRemoteSession

PairCol = tuple[Column, str]
AnyDataFrame = DataFrame | DataFrameRemote
AnySparkSession = SparkSession | SparkRemoteSession
