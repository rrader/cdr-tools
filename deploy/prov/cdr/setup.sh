#!/bin/bash

echo "root:42" | chpasswd

test -f /etc/yum.repos.d/hdp.repo || wget -O /etc/yum.repos.d/hdp.repo http://s3.amazonaws.com/dev.hortonworks.com/HDP-2.0.6.0/repos/centos6/hdp.repo

# ======== Flume ==========

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
chkconfig flume-cdr off

# ======== PBX ==========

yum install -y make wget openssl-devel ncurses-devel newt-devel libxml2-devel kernel-devel gcc gcc-c++ sqlite-devel
cd /usr/src/

# DAHDI
wget http://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
tar zxvf dahdi-linux-complete*
cd /usr/src/dahdi-linux-complete*
make && make install && make config

cd /usr/src
# LibPRI
wget http://downloads.asterisk.org/pub/telephony/libpri/libpri-1.4-current.tar.gz
tar zxvf libpri*
cd /usr/src/libpri*
make && make install

cd /usr/src
# Asterisk
yum -y install uuid-devel libuuid libuuid-devel # for rtp resource module
wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-11-current.tar.gz
tar zxvf asterisk*
cd /usr/src/asterisk*
#for x86: ./configure && make menuselect && make && make install
./configure --libdir=/usr/lib64

# make menuselect # ?? can we skip this?
make menuselect.makeopts

make && make install

make samples
make config

chkconfig dahdi on
chkconfig asterisk on
service dahdi start
service asterisk start

iptables -F
