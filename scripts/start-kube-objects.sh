sudo kubectl create -f /home/demouser/kubernetesfiles/mongodb-service.json
sudo kubectl create -f /home/demouser/kubernetesfiles/flask-service.json
echo Printing Services List
sudo kubectl get services

sudo kubectl create -f /home/demouser/kubernetesfiles/mongodb-pod.json
sudo kubectl create -f /home/demouser/kubernetesfiles/flask-pod.json
sudo kubectl create -f /home/demouser/kubernetesfiles/tiger_adapter-pod.json
echo Printing Pods List
sudo kubectl get pods
