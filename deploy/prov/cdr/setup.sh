#!/bin/bash

echo "root:42" | chpasswd

test -f /etc/yum.repos.d/hdp.repo || wget -O /etc/yum.repos.d/hdp.repo http://s3.amazonaws.com/dev.hortonworks.com/HDP-2.0.6.0/repos/centos6/hdp.repo

yum install -y flume java-1.6.0-openjdk
grep namenode /etc/hosts || echo "192.168.42.101	namenode" >> /etc/hosts
grep sandbox /etc/hosts || echo "192.168.42.101	sandbox" >> /etc/hosts
grep JAVA_HOME /etc/bashrc || echo "export JAVA_HOME=/usr/lib/jvm/jre" >> /etc/bashrc

mkdir -p /root/cdr
cp /vagrant/prov/cdr/gen/flume-cdr-source*.jar /root/cdr

cp -f /vagrant/prov/cdr/flume/flume-env.sh /etc/flume/conf/flume-env.sh
cp -f /vagrant/prov/cdr/flume/flume.conf /etc/flume/conf/flume.conf

cp /vagrant/prov/cdr/flume/flume-cdr.init /etc/init.d/flume-cdr
chmod +x /etc/init.d/flume-cdr
chkconfig --add flume-cdr
chkconfig flume-cdr on
