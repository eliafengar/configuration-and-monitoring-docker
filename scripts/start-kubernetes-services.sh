#!/bin/sh

for SERVICES in etcd kube-apiserver kube-controller-manager kube-scheduler; do 
	sudo systemctl restart $SERVICES
	sudo systemctl enable $SERVICES
	sudo systemctl status $SERVICES 
done

for SERVICES in kube-proxy kubelet docker flanneld; do 
	sudo systemctl restart $SERVICES
	sudo systemctl enable $SERVICES
	sudo systemctl status $SERVICES 
done
