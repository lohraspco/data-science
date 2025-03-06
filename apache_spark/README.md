# Apache Spark
While I was preparing for Databricks Certified Associate Developer for Apache exam, I found some information and links. Here are some of list of topics assessed in the exam by each category and some links:
## Spark Architecture — Conceptual
- Driver: The process that runs the main() function of your Spark application, coordinates tasks, and manages the execution plan.
- Executors: Worker processes that execute tasks assigned by the driver and store data in memory or disk.
- Cluster Manager: The system responsible for allocating resources (e.g., CPU, memory) to Spark applications (e.g., YARN, Mesos, Standalone, Kubernetes).
- Cluster architecture: nodes, drivers, workers, executors, slots(parallel capacity on executor).
  
  Spark execution hierarchy: 
    - **applications**: an application contains one or more jobs, and it interacts with the driver and cluster manager to execute
    - **jobs**: A job is triggered by an action (like collect() or save() in Spark)
    - **stages**: A stage is a subdivision of a job and consists of tasks that can be executed without shuffling data between nodes. Stages are defined by transformations and are separated whenever a shuffle (data reorganization) occurs.
    - **tasks**: A task processes a single partition of data within a stage. Tasks are executed in parallel across the cluster.
- Partitioning: dividing a dataset into smaller, manageable chunks (partitions) that can be processed independently. The choice of partitioning strategy (e.g., hash or range partitioning) impacts efficiency.
- Shuffling: appens when operations like groupBy, join, or reduceByKey require data to be rearranged
- Transformations: Transformations are operations that create a new dataset from an existing one.
    - Narrow transformations:  No data shuffling between nodes and can be pipelined. map(), filter(), mapPartitions(), coalesce()
    - Wide transformations: data from multiple input partitions may contribute to one or more output partitions (involves data shuffling). groupByKey(), reduceByKey() , join(), repartition(), sortByKey()
- Lazy evaluation

- Execution deployment modes (Local, client, cluster: spark-submit --master spark://<master-host>:7077 --deploy-mode cluster my_app.py).  </br>

| Deploy Mode    | Driver Location  | Task Scheduler|
| -------------- | ---------------- |--------------- |
| Local          | local            |      local     |
| Client         | client machine   | Spark Driver   |
| Cluster        | Worker Nodes     | cluster manager|

- Stability
- Storage levels
- Repartitioning
- Coalescing
 - Broadcasting
## DataFrames
- Spark DataFrame API
- Subsetting DataFrames (select, filter, etc.)
- Column manipulation (casting, creating columns, manipulating existing columns, complex column types)
- String manipulation (Splitting strings, regex)
- Performance-based operations (repartitioning, shuffle partitions, caching)
- Combining DataFrames (joins, broadcasting, unions, etc)
- Reading/writing DataFrames (schemas, overwriting)
- Working with dates (extraction, formatting, etc)
- Aggregations
- Miscellaneous (sorting, missing values, typed UDFs, value extraction, sampling)

## Links 
https://medium.com/data-arena/databricks-certified-associate-developer-for-apache-spark-tips-to-get-prepared-for-the-exam-cf947795065b

https://www.youtube.com/watch?v=639JCua-bQU
<br>set the .bashrc variables as in https://opensource.com/article/18/11/pyspark-jupyter-notebook

## My notes:

# About Apache  
Apache Spark: open source data processing engine,  RDDs are the basic data structure within the Apahe Spark.
- **RDDs**: Immutable, fault-tolerant, distributed datasets for parallel processing.  
- **Spark vs. MapReduce**: Caches data in memory, reducing replication, serialization, and I/O.  

- **MapReduce**, a programming model for “chunking” a large data processing task into smaller parallel tasks.
Spark was developed to address shortcomings in MapReduce.

Key Concepts of Spark Core
1. **RDD** Operations on RDDs fall into:
- **Transformations** (e.g., map, filter) that create a new RDD.
- **Actions** (e.g., count, collect) that compute results or write data.
Lazy Evaluation: Transformations on RDDs are not executed immediately but are "lazy," meaning computation is only triggered when an action is called.
2. **Distributed Computing**
3. **Cluster Management**: It integrates with cluster managers like Apache Hadoop YARN, Apache Mesos, or its own built-in Spark Standalone cluster manager to handle resource allocation.

Use Cases for Spark Core
Log processing: Analyze web server logs for patterns or errors.
Batch data processing: Process large datasets quickly (e.g., ETL workflows).
Iterative computations: Run algorithms that repeatedly process the same data (e.g., PageRank).