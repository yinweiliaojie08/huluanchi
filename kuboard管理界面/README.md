# 编辑 kuboard-v3.yaml 文件中的配置，该部署文件中，有两处配置必须修改：
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kuboard-v3-config
  namespace: kuboard
data:
  KUBOARD_ENDPOINT: 'http://your-node-ip-address:30080'           ### 访问地址 nodeport

storageClassName
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      # 请填写一个有效的 StorageClass name
      storageClassName: please-provide-a-valid-StorageClass-name-here
      accessModes: [ "ReadWriteMany" ]
      resources:
        requests:
          storage: 5Gi
