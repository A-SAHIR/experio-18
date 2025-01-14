THIS_FILE := $(lastword $(MAKEFILE_LIST))
include .env

ifndef DIR
override DIR = .
endif
ifndef DOCKER_COMMAND
override DOCKER_COMMAND = docker-compose
endif

image ?= myregistry.experioservices.com/experio
docker ?= $(DOCKER_COMMAND)


.PHONY: help build up start stop restart logs ps reload tests update pylint

help:
	make -pRrq  -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
build:
	$(docker) -f docker-compose.yml build $(c)
up:
	$(docker) -f docker-compose.yml up -d $(c)
start:
	$(docker) -f docker-compose.yml start $(c)
stop:
	$(docker) -f docker-compose.yml stop $(c)
restart:
	$(docker) -f docker-compose.yml stop $(c)
	$(docker) -f docker-compose.yml up -d $(c)
logs:
	$(docker) -f docker-compose.yml logs --tail=100 -f $(c)
ps:
	$(docker) -f docker-compose.yml ps
reload:
	sudo service nginx reload
tests:
	$(docker) -f docker-compose.yml run --rm odoo --test-enable --stop-after-init -d $(db) -i $(m)

wintests:
	python odoo-bin --test-enable -c odoo.conf --stop-after-init -d $(db) -i $(m)

upgrade:
	$(docker) -f docker-compose.yml run --rm odoo python3 /mnt/scripts/upgrade.py \
	--dbname $(dbname) --host $(POSTGRES_HOST) --user $(POSTGRES_USER) --passwd $(POSTGRES_PASS) \
	--range_min $(min) --range_max $(max) --option $(option) --modules $(modules) --databases $(databases) \
	--client $(CLIENT_HANDLE) --timeout $(timeout) --command $(command)

update:
	git checkout $(b)
	git pull upstream $(b)
	git submodule update --init --recursive

pylint:
	pylint --rcfile=$(DIR)/.pylintrc $(DIR)/*

ci:
	docker build -t $(image):$(t) -f docker/odoo/Dockerfile .
	docker push $(image):$(t)
	cd exp-cognitive && git tag v$(t) && git push upstream v$(t)
	cd exp-accounting && git tag v$(t) && git push upstream v$(t)
	cd exp-base && git tag v$(t) && git push upstream v$(t)
	cd odoo && git tag v$(t) && git push upstream v$(t)

preci:
	docker build -t $(image):$(t) -f docker/odoo/Dockerfile .
	docker push $(image):$(t)

prepare:
	git checkout $(b)
	git pull upstream $(b)
	cd exp-cognitive && make update
	cd exp-accounting && make update
	cd exp-base && make update
	cd odoo && make update

clean:
	cd exp-cognitive && make clean
	cd exp-accounting && make clean
	cd exp-base && make clean
	cd odoo && make clean

checkout:
	cd exp-cognitive && git checkout $(b)
	cd exp-accounting && git checkout $(b)
	cd exp-base && git checkout $(b)
	cd odoo && git checkout $(b)
