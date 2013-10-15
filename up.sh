#!/bin/bash

# ========= Flume source build ==========

cd flume-source
mvn package
cd ..

mkdir -p deploy/prov/cdr/gen
cp flume-source/target/flume-cdr-source-*.jar deploy/prov/cdr/gen/
cp flume-source/setup/* deploy/prov/cdr/gen/