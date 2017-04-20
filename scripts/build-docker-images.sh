#!/bin/sh

cd ~/

sudo docker build --tag=eliafengar/mongodb:v1 --file=./dockerfiles/mongodb .
sudo docker build --tag=eliafengar/flask:v1 --file=./dockerfiles/flask .
sudo docker build --tag=eliafengar/tiger_adapter:v1 --file=./dockerfiles/adapter .
sudo docker build --tag=eliafengar/maps-portal:v1 --file=./dockerfiles/maps-portal .
