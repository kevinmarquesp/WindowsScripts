from ftplib import FTP, error_perm
from json import loads
from typing import Any
from time import time
from concurrent.futures import ThreadPoolExecutor
import os

BACKUP_TARGET: str = r"C:\Users\kevin\Desktop\data\backup\mirror\android"
SYNCBAK_CONF_JSON_FILE: str = "syncbak.conf.json"

FTP_SERVER_HOST: str = "192.168.100.16"
FTP_PORT: int = 2121
FTP_LOGIN_USERNAME: str = "kevin"
FTP_LOGIN_PASSWORD: str = "kevinmarquesp"
FTP_TIMEOUT: int = 120

base_ftp: FTP = FTP()
base_ftp.connect(FTP_SERVER_HOST, port=FTP_PORT, timeout=FTP_TIMEOUT)
base_ftp.login(FTP_LOGIN_USERNAME, FTP_LOGIN_PASSWORD)


## make sure that the sever has a config file to make the backup

if SYNCBAK_CONF_JSON_FILE not in base_ftp.nlst():
    raise "Could not find the config file: " + SYNCBAK_CONF_JSON_FILE


## fetch the json data and convert it to a python dictionary

syncbak_config_json_lines: list[str] = []

base_ftp.retrbinary(f"RETR {SYNCBAK_CONF_JSON_FILE}", lambda data: syncbak_config_json_lines.append(data))

syncbak_config_json_data: str = "".join([ data.decode() for data in syncbak_config_json_lines ])
syncbak_config: dict[str: Any] = loads(syncbak_config_json_data)

security_mirror_data_list: list[dict[Any]] = syncbak_config["BackupProfiles"]["SecurityMirror"]["Data"]
security_mirror_exclude_list: list[str] = [ data["Path"]
                                            for data in syncbak_config["BackupProfiles"]["SecurityMirror"]["Exclude"] ]

base_ftp.close()

## mirror each file/directory to the target backup dir

def mirror_directory(ftp_path, local_path):
    ftp: FTP = FTP()

    ftp.connect(FTP_SERVER_HOST, port=FTP_PORT, timeout=FTP_TIMEOUT)
    ftp.login(FTP_LOGIN_USERNAME, FTP_LOGIN_PASSWORD)
    ftp.cwd(ftp_path)

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    items = ftp.nlst()

    for item in items:
        try:
            ftp.cwd(item)
            is_dir = True
            ftp.cwd("..")
        except:
            is_dir = False

        ftp_item_path = f"{ftp_path}/{item}"
        local_item_path = os.path.join(local_path, item)

        if ftp_item_path in security_mirror_exclude_list:
            continue

        if is_dir:
            mirror_directory(ftp_item_path, local_item_path)
        else:
            print(f"{ftp_item_path}  ==>  {local_item_path}")

            with open(local_item_path, 'wb') as f:
                ftp.retrbinary('RETR ' + ftp_item_path, f.write)

    ftp.cwd("..")
    ftp.close()


benchmark_start: float = time()


for mirror_data in security_mirror_data_list:
    item_path: str = mirror_data["Path"]  #todo: sanatize the path, put a / if there is any and replace ./!
    target_subdir: str = os.path.basename(item_path)

    mirror_directory(item_path, os.path.join(BACKUP_TARGET, target_subdir))


benchmark: float = time() - benchmark_start

print("\n\n")
print(benchmark)
input("\n\n")