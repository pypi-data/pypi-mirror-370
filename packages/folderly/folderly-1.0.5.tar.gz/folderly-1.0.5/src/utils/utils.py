import os 
import tempfile
import json

#Getting the path for the temp json file
def get_temp_json_path():
    temp_dir=tempfile.gettempdir()
    return os.path.join(temp_dir,"folderly_undo.json")

#Getting the path of temp first and then creating the backup directory and returning the path
def get_backup_dir():
    temp_dir=tempfile.gettempdir()
    backup_dir=os.path.join(temp_dir,"folderly_backup")
    os.makedirs(backup_dir,exist_ok=True)
    return backup_dir

def write_operation_metadata(data):
    path=get_temp_json_path()
    with open(path,'w',encoding='utf-8') as f: #opening the file for writing
        json.dump(data,f,indent=2) #dump is the funcion that writes the python dict to a file in json format

def read_operation_metadata():
    path=get_temp_json_path()
    if not os.path.exists(path):
        return None
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)
    
def delete_operation_metadata():
    path=get_temp_json_path()
    if os.path.exists(path):
        os.remove(path)
        
