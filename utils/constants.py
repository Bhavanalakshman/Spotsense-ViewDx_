import os
import json
import requests
from pathlib import Path

class AppPath():
    APP_PATH = None
    def __init__(self):
        self.APP_PATH = os.path.sep.join(os.path.dirname(__file__).split(os.path.sep)[0:-1])
        pass
    def set(self, path):
        self.APP_PATH = path
        pass
    def get(self):
        return self.APP_PATH

AP = AppPath()

def set_app_path(path):
    AP.set(Path(Path(path).parent))

def get_path(file=""):
    return str(Path(AP.get()) / file)

def read_json_file(file_path):
    _file = open(os.path.expanduser(file_path) if file_path[0] == "~" else get_path(file_path))
    return json.load(_file)

def is_online(url = 'https://google.com'):
    # CHECK WHETHER INTERNET IS AVAILABLE OR NOT
    try:
        response = requests.get(url).status_code
        return response == 200
    except:
        return False

_device_info = read_json_file('~/.device')
DEVICE_ID = _device_info['device_id']
DEVICE_PSK = _device_info['device_psk']
DEVICE_INSTALL = _device_info['install_date']

_aws_creds = read_json_file(get_path('.aws'))
AWS_ACCESS_KEY = _aws_creds['access_key']
AWS_SECRET_KEY = _aws_creds['secret_key']
AWS_REGION = _aws_creds['region']
