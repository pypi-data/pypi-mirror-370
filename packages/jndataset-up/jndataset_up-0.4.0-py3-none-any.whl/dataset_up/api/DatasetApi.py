import json
import requests
import sys
from dataset_up.config.constants import TIMEOUT,UPLOAD_URL,OPERATE_URL
from dataset_up.utils.retryable import retry_with_backoff
from dataset_up.utils.http_utils import http_common_header
from dataset_up.client.AuthClient import auth_client

class DatasetApi(object):
    def __init__(self, host: str):
        self.host = host
    
    
    def http_authorization_header(self) -> dict:
        try:
            header_dict = http_common_header()
            token = auth_client.get_token()
            header_dict['Authorization'] = token
        except Exception as e:
            print(f"{e}")
            sys.exit(-1)
        return header_dict
    
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def pre_object_upload(self, req: dict) -> dict:
        
        headers = self.http_authorization_header()
        resp = requests.post(
            url=f"{self.host}{UPLOAD_URL}preUpload",
            data=json.dumps(req),
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise Exception(f"failed to pre_object_upload,req:{req},resp:{resp.json()}")
        resp_json = resp.json()
        if resp_json['code'] != 0:
            raise Exception(f"failed to pre_object_upload,req:{req},resp:{resp_json}")
        data = resp_json['data']
        return data
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def post_object_upload(self,  req: dict) -> dict:
        headers = self.http_authorization_header()

        resp = requests.post(
            url=f"{self.host}{UPLOAD_URL}complete",
            data=json.dumps(req),
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise Exception(f"post_object_upload failed, req: {req}, message: {resp.text}")
        resp_json = resp.json()
        if resp_json["code"] != 0:
            raise Exception(f"post_object_upload failed, req: {req}, message: {resp_json}")
        data = resp_json["data"]
        return data
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def report_part_uploaded(self, req: dict) ->dict:
        headers = self.http_authorization_header()
        resp = requests.post(
            url=f"{self.host}{UPLOAD_URL}partUploadReport",
            data=json.dumps(req),
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise Exception(f"report_part_uploaded failed, req: {req}, message: {resp.text}")
        resp_json = resp.json()
        if resp_json["code"] != 0:
            raise Exception(f"report_part_uploaded failed, req: {req}, message: {resp_json}")
        data = resp_json["data"]
        return data
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def mkdir(self,req: dict) -> dict:
        headers = self.http_authorization_header()
        resp = requests.post(
            url=f"{self.host}{OPERATE_URL}createDir",
            data=json.dumps(req),
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise Exception(f"mkdir failed, req: {req}, message: {resp.text}")
        resp_json = resp.json()
        if resp_json["code"] != 0:
            raise Exception(f"mkdir failed, req: {req}, message: {resp_json}")
        data = resp_json["data"]
        return data
    
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def deleteDir(self,req: dict) -> dict:
        headers = self.http_authorization_header()
        resp = requests.post(
            url=f"{self.host}{OPERATE_URL}deleteDir",
            data=json.dumps(req),
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise Exception(f"deleteDir failed, req: {req}, message: {resp.text}")
        resp_json = resp.json()
        if resp_json["code"] != 0:
            raise Exception(f"deleteDir failed, req: {req}, message: {resp_json}")
        data = resp_json["data"]
        return data
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def deleteFile(self,req: dict) -> dict:
        headers = self.http_authorization_header()
        resp = requests.post(
            url=f"{self.host}{OPERATE_URL}deleteKey",
            data=json.dumps(req),
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise Exception(f"deleteFile failed, req: {req}, message: {resp.text}")
        resp_json = resp.json()
        if resp_json["code"] != 0:
            raise Exception(f"deleteFile failed, req: {req}, message: {resp_json}")
        data = resp_json["data"]
        return data
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def list(self, req: dict) -> dict:
        headers = self.http_authorization_header()
        resp = requests.post(
            url=f"{self.host}{OPERATE_URL}list",
            data=json.dumps(req),
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        if resp.status_code != 200:
            raise Exception(f"list error: {resp.status_code}")
        resp_json = resp.json()
        data = resp_json["data"]
        return data
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def create_task(self,req: dict) -> dict:
        headers = self.http_authorization_header()
        response = requests.post(
            url=f"{self.host}{OPERATE_URL}createTask", 
            data=json.dumps(req), 
            headers=headers, 
            timeout=TIMEOUT
        )
        response.raise_for_status()
        if response.status_code == 200:
            ret_code = response.json()["code"]
            if ret_code == 0:
                return response.json()["data"]
            else:
                msg = response.json()["message"]
                if msg:
                    raise Exception(f"create task failed, error_msg:{msg}")
        raise Exception("create task failed,error message: %s" % response.text)
    
    
    @retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
    def report(self,req: dict):
        report_url = f"{self.host}{OPERATE_URL}report"  
        response = requests.post(report_url, data=json.dumps(req),headers=self.http_authorization_header(),timeout=3)
        response.raise_for_status()
        if response.status_code == 200:
            ret_code = response.json()["code"]
            if ret_code == 0:
                data = response.json()["data"]
                return data
            else:
                raise Exception(f"failed to report upload progress, ret_code: {ret_code}")
        else:
            raise Exception(f"failed to report upload progress. status_code: {response.status}, reason: {response.reason}")
        