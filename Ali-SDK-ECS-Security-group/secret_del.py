#!/usr/bin/python
# -*- coding: utf-8 -*-

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import RevokeSecurityGroupRequest
import sys
import json

class AliGroup:
    def __init__(self, AccessKey, AccessSecret, RegionId):
        self.AccessKey = AccessKey
        self.AccessSecret = AccessSecret
        self.RegionId = RegionId

    def client(self):
        """用于创建AcsClient的实例
        """
        client = AcsClient(self.AccessKey, self.AccessSecret, self.RegionId)
        return client

    def revokeSecurityGroupRequest(self, PortRange, SourceCidrIp, Priority=1, IpProtocol='tcp', SecurityGroupId='your-securitygroup-id'):
        """删除安全组规则
        """
        request = RevokeSecurityGroupRequest.RevokeSecurityGroupRequest()
        request.set_SecurityGroupId(SecurityGroupId)
        request.set_IpProtocol(IpProtocol)
        request.set_PortRange(PortRange)
        if SourceCidrIp:
            request.set_SourceCidrIp(SourceCidrIp)
        request.set_Policy('accept')
        request.set_accept_format('json')
        return request


if __name__ == '__main__':
    ali = AliGroup("your-access-key-id", "your-access-key-secret", "your-region-id")
    clt = ali.client()
    rem = ali.revokeSecurityGroupRequest(sys.argv[1], sys.argv[2])
    res = clt.do_action(rem)
    print res
