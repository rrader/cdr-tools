#!/bin/bash

# Creating data folder
su - hdfs -c "hdfs dfs -mkdir /data"
su - hdfs -c "hdfs dfs -mkdir /data/cdr"
su - hdfs -c "hdfs dfs -chmod -R 777 /data"

echo -e "Hortonworks Sandbox 2.0 GA\nlogin with root:hadoop\n\n" > /etc/issue

