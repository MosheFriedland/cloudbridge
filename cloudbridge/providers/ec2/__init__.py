"""
Provider implementation based on boto library for EC2-compatible clouds.
"""

import boto
from boto.ec2.regioninfo import RegionInfo

from cloudbridge.util import Bunch
from cloudbridge.providers.interfaces import CloudProvider
from cloudbridge.providers.interfaces import SecurityManager
from cloudbridge.providers.interfaces import KeyPair


class EC2CloudProviderV1(CloudProvider):

    def __init__(self, config):
        print "EC2CloudProviderV1; for config: '%s'" % config
        self.config = config
        self.a_key = config.access_key
        self.s_key = config.secret_key
        self.cloud_type = 'ec2'

        # Initialize optional fields
        if type(config) is Bunch:
            self.is_secure = config.get('is_secure', True)
            self.region_name = config.get('region_name', 'us-east-1')
            self.region_endpoint = config.get('region_endpoint', 'ec2.us-east-1.amazonaws.com')
            self.ec2_port = config.get('ec2_port', '')
            self.ec2_conn_path = config.get('ec2_conn_path', '/')
        else:
            if hasattr(config.is_secure):
                self.is_secure = config.is_secure
            else:
                self.is_secure = True
            if hasattr(config.region_name):
                self.region_name = config.region_name
            else:
                self.region_name = 'us-east-1'
            if hasattr(config.region_endpoint):
                self.region_endpoint = config.region_endpoint
            else:
                self.region_endpoint = 'ec2.us-east-1.amazonaws.com'
            if hasattr(config.ec2_port):
                self.ec2_port = config.ec2_port
            else:
                self.ec2_port = ''
            if hasattr(config.ec2_conn_path):
                self.ec2_conn_path = config.ec2_conn_path
            else:
                self.ec2_conn_path = "/"

        self.ec2_conn = self._connect_ec2()

        # self.Compute = EC2ComputeManager(self)
        # self.Images = EC2ImageManager(self)
        self.Security = EC2SecurityManager(self)
        # self.BlockStore = EC2BlockStore(self)
        # self.ObjectStore = EC2ObjectStore(self)

    def _connect_ec2(self):
        """
        Get a boto connection object for the given cloud.
        """
        r = RegionInfo(name=self.region_name, endpoint=self.region_endpoint)
        ec2_conn = boto.connect_ec2(aws_access_key_id=self.a_key,
                                    aws_secret_access_key=self.s_key,
                                    # api_version is needed for availability zone support for EC2
                                    api_version='2012-06-01' if self.cloud_type == 'ec2' else None,
                                    is_secure=self.is_secure,
                                    region=r,
                                    port=self.ec2_port,
                                    path=self.ec2_conn_path,
                                    validate_certs=False)
        return ec2_conn


class EC2SecurityManager(SecurityManager):
    def __init__(self, provider):
        self.provider = provider

    def list_key_pairs(self):
        """
        List all key pairs.

        :rtype: ``list`` of :class:`.KeyPair`
        :return:  list of KeyPair objects
        """
        kps = self.provider.ec2_conn.get_all_key_pairs()
        kpl = []
        for kp in kps:
            kpl.append(KeyPair(kp.name))
        return kpl