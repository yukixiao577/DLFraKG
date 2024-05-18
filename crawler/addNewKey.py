import json
import os
import openpyxl

"""
1. addKeysInRelation 现在将所有文件添加了字段 processProject 为false，需要：
    a. 从映射表中找到所有两边类型不同的项，保存到一个 .xls 中，如     torch.abs mindspore.ops.Abs
    b. 读取新的relation文件，将在表格中存在的映射的 processProject 置为 true
2. 同上写一个 addKeysInNode 函数，使得可以一次在所有 node.json 文件中添加新字段，注意 node.json 与 relation.json 文件格式不同
"""

def getTypeDiff(filePath_xlsx):
    workbook = openpyxl.load_workbook(filePath_xlsx)
    worksheet = workbook['Sheet']
    string_list = []
    for row in worksheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                string_list.append(cell.value)
    print(string_list)
    return string_list


def addKeysInRelation(filePath, dict):
    """
    往 relation.json文件里添加新字段
    Parameters
    ----------
    filePath
    dict
    """
    with open(filePath, 'r', encoding='utf8') as jsonF:
        print(filePath)
        jsonData = json.load(jsonF)
        for datas in jsonData["relationship"]:
            for k, v in dict.items():
                datas[k] = v
        with open(filePath, 'w', encoding='utf8') as f:
            f.write(json.dumps(jsonData, indent=4, ensure_ascii=False))


def addKeysInNode(filePath, dict):
    with open(filePath, 'r', encoding='utf8') as jsonF:
        print(filePath)
        jsonData = json.load(jsonF)
        for datas in jsonData:
            for k, v in dict.items():
                datas[k] = v
        with open(filePath, 'w', encoding='utf8') as f:
            f.write(json.dumps(jsonData, indent=4, ensure_ascii=False))


def changeTypeJudgement(filePath_rela):
    with open(filePath_rela, 'r', encoding='utf8') as jsonF:
        jsonData = json.load(jsonF)
        for datas in jsonData["relationship"]:
            torch_api = datas["pytorch"].split('.')[-1]
            ms_api = datas["mindspore"].split('.')[-1]
            if torch_api[:1].isupper() and not ms_api[:1].isupper() or not torch_api[:1].isupper() and ms_api[:1].isupper():
                datas["typeJudgement"] = True
            else:
                datas["typeJudgement"] = False
        with open(filePath_rela, 'w', encoding='utf8') as f:
            f.write(json.dumps(jsonData, indent=4, ensure_ascii=False))


def goback(filePath_rela):
    with open(filePath_rela, 'r', encoding='utf8') as jsonF:
        jsonData = json.load(jsonF)
        for datas in jsonData["relationship"]:
            datas["typeJudgement"] = False
        with open(filePath_rela, 'w', encoding='utf8') as f:
            f.write(json.dumps(jsonData, indent=4, ensure_ascii=False))


def processProject(path, dict):
    """
    处理项目，根据dict,像API 关系 json 文件中添加 key
    Parameters
    ----------
    path
    dict
    """
    if os.path.exists(path):
        fileList = os.listdir(path)
        for f in fileList:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                processProject(f)
            else:
                file_name, extension = os.path.splitext(f)
                if extension == '.json':
                    #addKeysInRelation(f, dict)
                    changeTypeJudgement(f)


def fix_node(path):
    if os.path.exists(path):
        fileList = os.listdir(path)
        for f in fileList:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                fix_node(f)
            else:
                file_name, extension = os.path.splitext(f)
                if extension == '.json':
                    with open(f, 'r', encoding='utf8') as jsonF:
                        jsonData = json.load(jsonF)
                        jsonData["version"] = "1.8.1"
                        with open(f, 'w', encoding='utf8') as f:
                            f.write(json.dumps(jsonData, indent=4, ensure_ascii=False))


def fix_relation(path):
    if os.path.exists(path):
        fileList = os.listdir(path)
        for f in fileList:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                fix_relation(f)
            else:
                file_name, extension = os.path.splitext(f)
                if extension == '.json':
                    with open(f, 'r', encoding='utf8') as jsonF:
                        jsonData = json.load(jsonF)
                        jsonData["mindsporeVersion"] = "2.0"
                        with open(f, 'w', encoding='utf8') as f:
                            f.write(json.dumps(jsonData, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    '''
    读取写入 result/**/**.txt
    '''
    path = "../../../dao/relation/1.8.1_r2.2"
    # dict = {"typeJudgement": "false"}
    processProject(path, dict)
    # path = "../../../dao/node/1.8.1_r2.0/Pytorch"
    # fix_node(path)
