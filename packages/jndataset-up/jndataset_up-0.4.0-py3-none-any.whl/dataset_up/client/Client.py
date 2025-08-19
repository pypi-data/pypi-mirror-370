from dataset_up.api.DatasetApi import DatasetApi
from dataset_up.config.constants import SERVER_URL

class Client(object):
    def __init__(self, host :str):
        self.host = host
        self.api = DatasetApi(self.host)
    
    def pre_object_upload(self, req: dict) -> dict:
        return self.api.pre_object_upload(req)
    
    def post_object_upload(self, req: dict) -> dict:
        return self.api.post_object_upload(req)
    
    def report_part_uploaded(self, req: dict) -> dict:
        return self.api.report_part_uploaded(req)
    
    def mkdir(self, req: dict) -> dict:
        return self.api.mkdir(req)
    
    def deleteDir(self, req: dict) -> dict:
        return self.api.deleteDir(req)
    
    def deleteFile(self, req: dict) -> dict:
        return self.api.deleteFile(req)
    
    def list(self, req: dict) -> dict:
        return self.api.list(req)
    
    def create_task(self,req: dict):
        return self.api.create_task(req)
    
    def report(self,req: dict):
        return self.api.report(req)

api_client = Client(SERVER_URL)