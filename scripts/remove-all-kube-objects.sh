sudo kubectl delete pod mongodb-pod
sudo kubectl delete pod	flask-pod
sudo kubectl delete pod	tiger-adapter-pod
sudo kubectl delete pod mysql-pod
echo Printing Pods List
sudo kubectl get pods

sudo kubectl delete service mongodb-service
sudo kubectl delete service flask-service
echo Printing Services List
sudo kubectl get services
