$ kubectl create secret generic db-user-pass  --from-file=./password
secret "db-user-pass" created

$ kubectl apply -f  pvc.yaml
$ kubectl apply -f  redis.yaml
$ kubectl apply -f  postgresql.yaml
$ kubectl apply -f  gitlab.yaml
