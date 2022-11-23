FROM registry.cn-hangzhou.aliyuncs.com/zhangjt_shinemo/shinemo:zabbix-server-mysql-centos-5.4.9

# 安装工具并提升权限
USER root
RUN  rm -rf /etc/yum.repos.d/*  \
     && curl  -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-8.repo \
     && sed -i 's/mirrors.cloud.aliyuncs.com/mirrors.aliyun.com/g' /etc/yum.repos.d/CentOS-Base.repo \
     && sed -i 's/$releasever/$releasever-stream/g' /etc/yum.repos.d/CentOS-Base.repo \
     && yum install -y bc openssl-devel  && echo 'zabbix    ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers  \
     && rm -rf /var/cache/yum/* && yum clean all
#CMD ["sleep","12000"]
