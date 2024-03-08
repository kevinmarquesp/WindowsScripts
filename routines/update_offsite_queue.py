from typing import Optional
from getpass import getpass
import json, os, re

OFFSITE_ARCHIVE_INFO: str = r"C:\Users\kevin\Desktop\data\datasets\fsinfo\offsite_archive_info.backup.json"
offsite_info: Optional[dict] = None


## GET THE JSON CONFIGURATION DICTIONARY

with open(OFFSITE_ARCHIVE_INFO) as file:
  file_con = file.read()
  offsite_info = json.loads(file_con)["windows"]  #select the only `windows` config


if offsite_info is None:
  exit(1)


def user_passwd() -> str:
  while True:
    passwd = getpass("Create a encryption password (Ctrl+Shift+V to paste): ")
    passwd_confirm = getpass("Confirm password: ")

    if passwd == passwd_confirm and len(passwd) > 24:
      print("\n[ERRO]: Passwords doesn't match or lessa than 24 characters\n")
      return passwd


password = user_passwd()


for archives_dir in offsite_info["paths"]["archives"]:
  if not os.path.isdir(archives_dir):
    continue

  for archive_name in os.listdir(archives_dir):
    if re.match(offsite_info["exclude"], archive_name):
      continue

    archive = os.path.join(archives_dir, archive_name)
    
    for target_dir in offsite_info["paths"]["offqueue"]:
      if not os.path.isdir(target_dir):
        continue

      target = os.path.join(target_dir, archive_name) + ".7z"

      os.system(f'7z a -t7z -mx=9 -m0=lzma2 -p"{password}" "{target}" "{archive}" && RMDIR {archive} /S /Q')