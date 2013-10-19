
.PHONY: build

build:
	make -C flume-source build
	mkdir -p ./deploy/prov/cdr/gen
	cp -f flume-source/target/flume-cdr-source-1.0-SNAPSHOT.jar ./deploy/prov/cdr/gen

up: build
	cd deploy; vagrant up

update: build up
	vagrant provision
