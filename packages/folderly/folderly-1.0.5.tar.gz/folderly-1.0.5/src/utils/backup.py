import os
import shutil
from .utils import get_backup_dir

def backup_file_or_folder(original_path):
    backup_dir=get_backup_dir()
    name=os.path.basename(original_path)
    backup_path=os.path.join(backup_dir,name)
    if os.path.isdir(original_path):
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        shutil.copytree(original_path,backup_path)
    else:
        shutil.copy2(original_path,backup_path)
    return backup_path


def restore_file_or_folder(backup_path,restore_path):
    if os.path.isdir(backup_path):
        if os.path.exists(restore_path):
            shutil.rmtree(restore_path)
        shutil.copytree(backup_path,restore_path)
    else:
        shutil.copy2(backup_path,restore_path)

def delete_backup_file_or_folder(backup_path):
    if os.path.isdir(backup_path):
        shutil.rmtree(backup_path,ignore_errors=True)
    elif os.path.exists(backup_path):
        os.remove(backup_path)