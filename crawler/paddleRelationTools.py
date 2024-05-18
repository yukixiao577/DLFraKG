import os

import markdown
import requests
from bs4 import BeautifulSoup
import json

unusualName = []
noJsonName = []
proxy = {'http': '127.0.0.1:33210', 'https': '127.0.0.1:33210'}

def getPaddleTorchRelation(req, root_path, url):
    soup = BeautifulSoup(req, 'html.parser')
    tbody = soup.find('tbody')  # the first tbody isn't needed
    nameRelation = []

    trList = tbody.find_all('tr')
    for tr in trList:
        tdList = tr.find_all('td')
        if len(tdList) == 4:
            torchName = tdList[1].text
            paddleName = tdList[2].text
            if tdList[3].text == '差异对比' or '参数不一致' in tdList[3].text:
                link = tdList[3].find('a')['href'].split('/')[-1]
                link = os.path.join(url, link)
                with open(link, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                # 创建Markdown对象
                md = markdown.Markdown(extensions=['extra'])
                # 将Markdown转换为HTML格式的字符串
                html_output = md.convert(md_content)
                params_equal = getPaddleFromJson(torchName, paddleName, root_path)
                temp = getPaddleDifferencePage(html_output)
                params_equal.update(temp)
                nameRelation.append((tdList[1].text, tdList[2].text, params_equal))
            elif "功能一致" == tdList[3].text:
                params = getPaddleFromJson(torchName, paddleName, root_path)
                nameRelation.append((torchName, paddleName, params))

    return nameRelation


def getPaddleDifferencePage(req):
    soup = BeautifulSoup(req,  'html.parser')
    tbodyList = soup.find_all('tbody')
    params = {}
    if len(tbodyList) == 0:
        return {}
    table = tbodyList[-1]
    trList = table.find_all('tr')
    for tr in trList:
        tdList = tr.find_all('td')
        if "-" not in tdList[0].text and "-" not in tdList[1].text:
            params[tdList[0].text] = tdList[1].text
    # print(params)
    return params


def getPaddleFromJson(torchName, paddleName, root_path):
    torchParam = []
    result = {}
    flag = False
    # first get torch
    for file in os.listdir(root_path + 'pytorch'):
        for secondFile in os.listdir(root_path + 'pytorch/' + file):
            if secondFile.lower() == torchName.lower() + '.json':
                with open(root_path + 'pytorch/' + file + '/' + secondFile, 'r', encoding='utf-8') as f:
                    torchFile = json.load(f)
                    for dic in torchFile['params']:
                        torchParam.append(dic['name'])
                flag = True
    # then get mind
    if not flag:
        print('not found: ', torchName)
    flag = False
    paddleParam = []
    for file in os.listdir(root_path + 'paddle'):
        if file.lower() == paddleName.lower() + '.json':
            with open(root_path + 'paddle/' + file, 'r', encoding='utf-8') as f:
                paddleFile = json.load(f)
                for dic in paddleFile['params']:
                    paddleParam.append(dic['name'])
                    if dic['name'] in torchParam:
                        result[dic['name']] = dic['name']
            flag = True

    if not flag:
        print('not found: ', paddleName)
    return result


def paddleJsonDumps(nameRelation, path):
    jsDict = {}
    jsDict['torchVersion'] = '1.8.1'
    jsDict['paddleVersion'] = '2.4'
    relationShip = []
    for relation in nameRelation:
        print(relation)
        relationShip.append({'pytorch': relation[0], 'paddle': relation[1], 'params': relation[2], 'typeJudgement': False})
    jsDict['relationship'] = relationShip
    with open(path + 'relationship_paddle.json', 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, indent=4)