#!/bin/bash

echo "root:42" | chpasswd

test -f /etc/yum.repos.d/hdp.repo || wget -O /etc/yum.repos.d/hdp.repo http://s3.amazonaws.com/dev.hortonworks.com/HDP-2.0.6.0/repos/centos6/hdp.repo

yum install -y flume
grep namenode /etc/hosts || echo "192.168.42.101	namenode" >> /etc/hosts
grep sandbox /etc/hosts || echo "192.168.42.101	sandbox" >> /etc/hosts
