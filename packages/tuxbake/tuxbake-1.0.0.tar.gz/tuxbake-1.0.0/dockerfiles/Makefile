# variables
PROJECT_DIR := tuxbake
DATE = date +%Y%m%d
REPOSITORY := docker.io

##  docker commad to build containers with two different tags \
	tag - 1 = project-dir/container-dir:latest \
	tag - 2 = project-dir/container-dir:yyyymmdd \

list := centos-8 \
       debian-buster debian-bullseye debian-bookworm \
       fedora-33 fedora-34 \
       opensuse-leap-15.2 \
       ubuntu-18.04 ubuntu-20.04 ubuntu-22.04 ubuntu-24.04

help:
	@echo "Makefile arguments:"
	@echo ""
	@echo "list=$(list)"
	@echo "specify one target by add that to the list."
	@echo ""
	@echo ""
	@echo "Make commands:"
	@echo ""
	@echo "build"
	@echo "publish"
	@echo "all"
	@echo ""
	@echo "Example command:"
	@echo ""
	@echo "make all"
	@echo "make list=ubuntu-20.04 build"

.DEFAULT_GOAL := all

build:
	for os in $(list); do echo $$os ; docker build -t $(PROJECT_DIR)/$$os:latest -t $(PROJECT_DIR)/$$os:$$($(DATE)) $$os/. ; done

publish: build
	for os in $(list); do echo $$os ; docker push $(REPOSITORY)/$(PROJECT_DIR)/$$os ; done

all: build
