alias python3=/usr/bin/python3
alias python=/usr/bin/python
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
#export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin
export SPARL_HOME=/opt/spark

export HADOOP_HOME=/opt/hadoop
#export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=${HADOOP_HOME}
export HADOOP_COMMON_HOME=${HADOOP_HOME}
export HADOOP_HDFS_HOME=${HADOOP_HOME}
export YARN_HOME=${HADOOP_HOME}
#export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
#export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib"
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop


export SPARK_HOME=/opt/spark
export SPARK_MASTER_HOST=master
export PYSPARK_PYTHON=python3
#export PYSPARK_DRIVER_PYTHON=python3
export PYSPARK_DRIVER_PYTHON="jupyter"
export PYSPARK_DRIVER_PYTHON_OPTS="notebook"
export PATH=$PATH:$SPARK_HOME/bin
export PATH=$PATH:$SPARK_HOME/sbin
export AIRFLOW_HOME=/home/lohrasp/airflow
