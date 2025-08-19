from __future__ import annotations
from typing import List, Optional, Tuple
import requests
import tqdm
import threading
from dataset_up.config.constants import SERVER_URL, UPLOAD_TIMEOUT

from dataset_up.utils.concurrent_utils import concurrent_submit
from dataset_up.utils.concurrent_utils import error_event,parse_filelist_to_tasklist_event,upload_files_event,interrupt_event
from dataset_up.utils.retryable import retry_with_backoff


lock = threading.Lock()
update_lock = threading.Lock()

def parse_filelist_to_tasklist(file_list: List[UploadingFile], # type: ignore
                               task_list: List,
                               dataset_id:str,
                               version:str,
                               progress: tqdm = None,
                               worker_num:int = None):
    concurrent_submit(to_upload_tasks, worker_num, parse_filelist_to_tasklist_event,file_list, task_list, progress)
    return task_list

def to_upload_tasks(
    file_list: List[UploadingFile], # type: ignore
    task_list: List[Tuple[UploadingFile, int, int]], # type: ignore
    progress: tqdm = None,
):
    while len(file_list) > 0: 
        if(error_event.is_set() or interrupt_event.is_set()):
            raise Exception("upload interrupted or error happened")
        with lock:
            try:
                file = file_list.pop(0)
            except Exception:
                return
        file.get_pre_upload_info()
        if file.upload_id and not file.pre_upload["resume"]: #完整的文件从0开始上传，不是断点续传
            for filePart in file.pre_upload["fileParts"]:
                part_number = filePart["partNum"]
                size = min(file.pre_upload["partSize"],
                           file.size - (part_number -1) * file.pre_upload["partSize"])
                with lock:
                    task_list.append((file, part_number, size))
        elif not file.upload_id: #文件已经存在了不用再传
            task = (file, 0, 0)
            with lock:
                task_list.append(task)
        elif file.upload_id and file.pre_upload["resume"]: #断点续传
            for filePart in file.pre_upload["fileParts"]:
                part_number = filePart["partNum"]
                size = min(file.pre_upload["partSize"],
                           file.size - (part_number -1) * file.pre_upload["partSize"])
                with lock:
                    task_list.append((file, part_number, size))
        else: 
            pass
        update_progress(1, progress)
        
        

def upload_files(
    task_list: List[Tuple[UploadingFile, int, int]], progress: Optional[tqdm] = None, workers: int = 8 # type: ignore
):
    concurrent_submit(upload_files_worker, workers,upload_files_event, task_list, progress)        
        
  

def upload_files_worker(
    task_list: List[Tuple[UploadingFile, int, int]], progress: Optional[tqdm] = None # type: ignore
):
    while len(task_list) > 0:
        if(error_event.is_set() or interrupt_event.is_set()):
            raise Exception("upload interrupted or error happened")
        with lock:
            try:
                task = task_list.pop(0)
            except Exception:
                # task_list 为空，表示已完成
                return
        file = task[0]
        part_number = task[1]
        part_size = task[2]
        if file.upload_id is None and not error_event.is_set():
            update_progress(file.size, progress)
        else:
            if part_number not in file.uploaded_part_numbers:
                file.upload_part(part_number)
            if len(file.pre_upload["fileParts"]) == len(file.uploaded_part_infos):#上传完成
                with lock:
                    if file.post_upload_in_progress:
                        return
                    file.post_upload_in_progress = True
                    try:
                        file.get_post_upload_info()
                    except Exception as e:
                        raise Exception(f"post upload failed. Error:{e}")
            if not error_event.is_set():
                update_progress(part_size, progress)


@retry_with_backoff(max_retries=3,base_delay=1,max_delay=5)
def put_file(url: str, data):
    if not error_event.is_set() and not interrupt_event.is_set():
        put_resp = requests.put(url=url, data=data, timeout=UPLOAD_TIMEOUT)
        return put_resp
    return None

  
def update_progress(update_value: int, progress: tqdm = None):
    if progress:
        with update_lock:
            progress.update(update_value)
