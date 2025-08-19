from datetime import timedelta
import datetime
import os 
import json

from dataset_up.config.constants import NAME
from dataset_up.update.sdk_version import LatestVersionInfo, SDKVersion
from dataset_up.utils.file import get_file_content
from dataset_up.utils.time_utils import get_datetime_from_formatted_str
from dataset_up.utils.time_utils import get_current_time
from dataset_up.utils.time_utils import get_current_formatted_time
from dataset_up.config.path_config import get_version_path




def get_now_version():
    return SDKVersion.get_now_version()

def get_version_from_local():
    try:
        version_json = get_file_content(get_version_path())
        version_dict = json.loads(version_json)
        return SDKVersion(**version_dict)
    except Exception as e:
        print(f"failed to get content from {get_version_path()}, error: {e}")
        return None

def get_last_version_update_time():
    try:
        if not os.path.exists(get_version_path()):
            return None
        version_cache_local = get_version_from_local()
        if version_cache_local:
            return version_cache_local.last_version_check_time
    except Exception:
        pass
    return None


def get_version_cache_expiration_time(last_update_time: datetime) -> datetime:
    return last_update_time + timedelta(days=1)




def update_check():
    try:
        last_update_time = get_last_version_update_time()
        if last_update_time is not None:
            last_update_datetime = get_datetime_from_formatted_str(last_update_time)
            expire_time = get_version_cache_expiration_time(last_update_datetime)
            if expire_time > get_current_time():
                return 
        
        latestVersion, isLatestVersion, needUpdate = SDKVersion.check_newest_version()
        if not isLatestVersion and needUpdate:
            print(f'{NAME} sdk latest version is {latestVersion} and need update, now will try "pip install --upgrade {NAME}"')
            SDKVersion.update_sdk_to_latest()
        now = get_current_formatted_time()
        latest_version_data = LatestVersionInfo(
            is_latest_version=isLatestVersion,
            latest_version=latestVersion,
            need_update=needUpdate
        )
        sdk_version = SDKVersion(now, latest_version_data.__dict__)
        sdk_version.store_to_local()
        if not isLatestVersion:
            print(f"当前版本为：{SDKVersion.get_now_version()}，最新版本为：{latestVersion},请及时更新SDK,更新命令 pip install --upgrade {NAME} ")
    except Exception as e:
        raise Exception(f"update sdk version error: {e}")
    
    
    