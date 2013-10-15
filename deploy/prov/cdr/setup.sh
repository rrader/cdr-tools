#!/bin/bash

wget -O /etc/yum.repos.d/hdp.repo http://s3.amazonaws.com/dev.hortonworks.com/HDP-2.0.6.0/repos/centos6/hdp.repo

yum install -y flume
