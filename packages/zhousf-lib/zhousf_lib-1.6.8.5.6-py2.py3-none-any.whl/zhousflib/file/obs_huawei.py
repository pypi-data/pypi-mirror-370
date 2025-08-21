# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:
"""
pip install huaweicloud-sdk-python-obs
"""
import traceback

from obs import ObsClient


class OBSHuaWei:
    def __init__(self, key_id, key_secret, endpoint, bucket):
        self.bucketName = bucket
        self.obsClient = ObsClient(access_key_id=key_id, secret_access_key=key_secret, server=endpoint)

    def obs2local(self, obs_path, local_path):
        return self.obsClient.getObject(self.bucketName, obs_path, downloadPath=local_path)

    def local2obs(self, obs_path, local_path):
        try:
            resp = self.obsClient.putFile(self.bucketName, obs_path, local_path)
            if resp.status < 300:
                return True, "successful"
            else:
                return False, "{0}: {1}".format(resp.errorCode, resp.errorMessage)
        except Exception as e:
            return False, "{0}".format(e)
        finally:
            self.obsClient.close()

    def local2obs_return_url(self, obs_path, local_path, expires=2592000):
        success, msg = self.local2obs(obs_path=obs_path, local_path=local_path)
        if not success:
            return success, msg
        try:
            resp = self.obsClient.createSignedUrl('GET', self.bucketName, obs_path, expires=expires)
            return True, resp.signedUrl
        except Exception as e:
            return False, "{0}".format(traceback.print_exc())


