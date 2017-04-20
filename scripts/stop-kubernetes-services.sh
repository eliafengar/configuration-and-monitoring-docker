#!/bin/sh

for SERVICES in kube-proxy kubelet docker flanneld; do
        sudo systemctl stop $SERVICES
        sudo systemctl status $SERVICES
done


for SERVICES in etcd kube-apiserver kube-controller-manager kube-scheduler; do 
	sudo systemctl stop $SERVICES
	sudo systemctl status $SERVICES 
done
