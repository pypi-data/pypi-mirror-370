import os 

VERSION = "0.1.0"
NAME = "dataset-up"

# 默认的配置路径
DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), f".{NAME}")

# 默认配置文件名称
DEFAULT_CLI_CONFIG_FILE_NAME = "config.json"

DEFAULT_CLI_TOKEN_FILE_NAME = "token.json"

# version
DEFAULT_CLI_VERSION_FILE_NAME = "version.json"


AK_ENV_NAME = "DATASET_UP_SDK_AK"
SK_ENV_NAME = "DATASET_UP_SDK_SK"

#SERVER_URL = "http://127.0.0.1:8081/api/data/sdkService/"
#SERVER_URL = "http://120.131.12.160:31815/api/data/sdkService/"
#SERVER_URL = "http://127.0.0.1:8081/sdk-server/api/data/sdkService/"
#SERVER_URL = "http://120.131.12.160:31800/sdk-srv/v5/api/data/sdkService/"
#GET_TOKEN_URL = "http://120.131.12.160:31800/user-srv/userAccessKey/v1/getAccessToken"

#SERVER_URL = "http://120.92.51.36:31801/api/sdk-srv/v5/api/data/sdkService/"
#GET_TOKEN_URL = "http://120.92.51.36:31801/api/user-srv/userAccessKey/v1/getAccessToken"

#SERVER_URL = "http://60.205.59.219:31801/api/sdk-srv/v5/api/data/sdkService/"
#GET_TOKEN_URL = "http://60.205.59.219:31801/api/user-srv/userAccessKey/v1/getAccessToken"

#SERVER_URL = "https://www.beaicloud.com/api/sdk-srv/v5/api/data/sdkService/"
#GET_TOKEN_URL = "https://www.beaicloud.com/api/user-srv/userAccessKey/v1/getAccessToken"

SERVER_URL = "http://10.2.11.101:1800/api/sdk-srv/v5/api/data/sdkService/"
GET_TOKEN_URL = "http://10.2.11.101:1800/api/user-srv/userAccessKey/v1/getAccessToken"


UPLOAD_URL = "upload/"
OPERATE_URL = "operate/"

TIMEOUT = (5, None)
UPLOAD_TIMEOUT = (600, None)

