from typing import Optional
from datetime import datetime
from getpass import getpass
import json, os

FSINFO_MUST_INCLUDE_FILES_BACKUP_JSON: str = r"C:\Users\kevin\Desktop\data\datasets\fsinfo\must_include_files.backup.json"

backup_data: Optional[str] = None
archive_name: Optional[str] = None


## get file information from the json data file

with open(FSINFO_MUST_INCLUDE_FILES_BACKUP_JSON) as file:
  file_content = file.read()
  backup_data = json.loads(file_content)["windows"]
  archive_name = datetime.now().strftime(backup_data["prefix"]) + backup_data["sufix"]

backup_data["target"] = list(map(lambda t: os.path.join(t, archive_name),  #include the archive name for each path
                                 filter(lambda t: os.path.isdir(t),
                                        backup_data["target"])))


## create the base target directory with windows system commands

for target in backup_data["target"]:
  os.system(f'MKDIR "{target}"')


## iterate for each group and copy every file/folder to the target

for group, sources in backup_data["files"].items():
  for target in backup_data["target"]:
    for source in sources:

      if os.path.isfile(source):
        os.system(f'COPY "{source}" "{target}"')

      elif os.path.isdir(source):
        source_name = os.path.basename(source)
        os.system(f'XCOPY "{source}" "{target}\\{group}\\{source_name}" /E /I')

      else:
        print(f"[ERRO]: this script only works with files/dirs, the file {source} type is invalid")


## Use the 7zip program to compress the generated snapshot

for target in backup_data["target"]:
  os.system(f'7z a -t7z -mx=9 -m0=lzma2 "{target}.7z" "{target}"')
  os.system(f'RMDIR "{target}" /S /Q')