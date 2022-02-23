# Apache Spark
While I was preparing for Databricks Certified Associate Developer for Apache exam, I found some information and links. Here are some of list of topics assessed in the exam by each category and some links:
## Spark Architecture — Conceptual
- Cluster architecture: nodes, drivers, workers, executors, slots, etc.
- Spark execution hierarchy: applications, jobs, stages, tasks, etc.
- Shuffling
- Partitioning
- Lazy evaluation
- Transformations vs Actions
- Narrow vs Wide transformations
## Spark Architecture — Applied
- Execution deployment modes
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

There are three modes to run Apache Spark Applications:
</br>
| Deploy Mode    | Driver Location  | Task Scheduler|
| -------------- | ---------------- |--------------- |
| Local          | local            |      local     |
| Client         | client machine   | Spark Driver   |
| Cluster        | Worker Nodes     | cluster manager|

