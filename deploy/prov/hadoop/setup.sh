#!/bin/bash

# Creating data folder
su - hdfs -c "hdfs dfs -mkdir /data"
su - hdfs -c "hdfs dfs -mkdir /data/cdr"
su - hdfs -c "hdfs dfs -chmod -R 777 /data"
