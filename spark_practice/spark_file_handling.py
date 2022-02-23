import os
import subprocess

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("regression").getOrCreate()
sc = spark.sparkContext

server_file = "hdfs:///192.168.0.233:9000"
file_uri = "hdfs:///user/hadoop/OntheOriginofSpecies.txt"
# text = sc.textFile("hdfs:///testdata/stockdata2.csv")

URI           = sc._gateway.jvm.java.net.URI
Path          = sc._gateway.jvm.org.apache.hadoop.fs.Path
FileSystem    = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
Configuration = sc._gateway.jvm.org.apache.hadoop.conf.Configuration

log4jLogger = sc._jvm.org.apache.log4j
LOGGER = log4jLogger.LogManager.getLogger(__name__)
LOGGER.info("pyspark script logger initialized")

fs = FileSystem.get(URI(server_file), Configuration())
status = fs.listStatus(Path('movies/'))

df = spark.read.csv("hdfs:///user/hadoop/OntheOriginofSpecies.txt")
print('\033[92m')
print("test is done ***************************************")
for fileStatus in status:
    print(fileStatus.getPath())
# print(text.take(2))

print('\033[0m')



cmd = 'hdfs dfs -ls movies/'
files = subprocess.check_output(cmd, shell=True).strip().split('\n')
for pat in files:
  print (pat)
