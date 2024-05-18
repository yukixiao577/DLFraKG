import json
import os

def fix(path):
    print(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    desc = data['description'].split('.')[0].replace('"', '').replace('\n', '').replace(';', ',').strip()
    data['description'] = desc
    params = []
    for param in data['params']:
        param['description'] = param['description'].split('.')[0].replace('"', '').replace('\n', '').replace(';', ',').strip()
        params.append(param)
    data['params'] = params
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def process_project(path):
    if os.path.exists(path):
        file_list = os.listdir(path)
        for f in file_list:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                process_project(f)
            else:
                file_name, extension = os.path.splitext(f)
                if extension == '.json':
                    fix(f)



if __name__ == "__main__":
    path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/node/1.8.1_r2.2"
    process_project(path)
