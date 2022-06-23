#!/usr/bin/python
# -*- coding: utf-8 -*-

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import AuthorizeSecurityGroupRequest
import sys
import json

class AliGroup:

    def __init__(self, AccessKey, AccessSecret, RegionId):
        self.AccessKey = AccessKey
        self.AccessSecret = AccessSecret
        self.RegionId = RegionId

    def client(self):
        """用于创建AcsClient实例
        """
        client = AcsClient(self.AccessKey, self.AccessSecret, self.RegionId)
        return client

    def authorizeSecurityGroupRequest(self, PortRange, SourceCidrIp, Priority=1, IpProtocol='tcp', SecurityGroupId='your-securitygroup-id'):
        """用于添加安全组规则
        """
        #创建AuthorizeSecurityGroupRequest实例
        request = AuthorizeSecurityGroupRequest.AuthorizeSecurityGroupRequest()
        #设置安全组ID
        request.set_SecurityGroupId(SecurityGroupId)
        #设置协议，比如TCP或者UDP
        request.set_IpProtocol(IpProtocol)
        #设置端口范围
        request.set_PortRange(PortRange)
        #如果存在源ip，则设置源ip
        if SourceCidrIp:
            request.set_SourceCidrIp(SourceCidrIp)
        #设置优先级
        request.set_Priority(Priority)
        #设置规则的动作为接受
        request.set_Policy('accept')
        #设置接收数据格式为json
        request.set_accept_format('json')
        return request


if __name__ == '__main__':
    #AliGroup类实例化
    ali = AliGroup("your-access-key-id", "your-access-key-secret", "your-region-id")
    #创建AcsClient实例
    clt = ali.client()
    #添加安全组规则，由于优先级、协议和安全组ID已经设置默认参数，所以只需要在运行脚本时输入端口范围和源ip两个参数
    add = ali.authorizeSecurityGroupRequest(sys.argv[1], sys.argv[2])
    #打印输出
    res = clt.do_action(add)
    print res
