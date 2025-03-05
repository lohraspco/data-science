
from dataclasses import dataclass
from pyspark.sql.types import StructField, IntegerType, DoubleType, StringType, StructType

class DataModel:
    def __init__(self,spark, movie_case="ml-1m",delimiter="::") -> None:
        if movie_case=="movieLense100k":
            self.movies = spark.read.json("hdfs:///user/hadoop/moviesdb/movieLense100k/movies")
        else:
            schemaMovies = StructType([
                StructField("id", IntegerType(), True),
                StructField("title", StringType(), True),
                StructField("genre", StringType(), True)
            ])
            self.movies = spark.read.schema(schemaMovies).csv(f"hdfs:///user/hadoop/moviesdb/{movie_case}/movies", sep=delimiter)

        self.name_dict = {x.id:x.title for x in self.movies.select(['id','title']).collect()}

        # schema = StructType([
        #     StructField("id", IntegerType(), True),
        #     StructField("gender", StringType(), True),
        #     StructField("age", IntegerType(), True),
        #     StructField("occupation", StringType(), True),
        #     StructField("zip", IntegerType(), True)
        # ])
        # self.user = spark.read.schema(schema=schema).csv(
        #     f"hdfs:///user/hadoop/moviesdb/{movie_case}/users", sep=delimiter)

        self.user = spark.read.csv(
            f"hdfs:///user/hadoop/moviesdb/{movie_case}/users", sep=delimiter,inferSchema=True)
        self.user = self.user.rdd.toDF(["id","gender","age","occupation","zip"])
        schema = StructType([
            StructField("userId", IntegerType(), True),
            StructField("movieId", IntegerType(), True),
            StructField("rating", IntegerType(), True),
            StructField("timestamp", IntegerType(), True),
        ])
        self.rating = spark.read.schema(schema).csv(
            f"hdfs:///user/hadoop/moviesdb/{movie_case}/ratings", sep=delimiter)