import os

import requests
from bs4 import BeautifulSoup
import json

unusualName = []
noJsonName = []


def getInformation(req, root_path):
    soup = BeautifulSoup(req, 'html.parser')
    tbodyList = soup.find_all('tbody')[1:] # the first tbody isn't needed
    num = 0
    nameRelation = []
    for tbody in tbodyList:
        trList = tbody.find_all('tr')
        num += len(trList)
        for tr in trList:
            tdList = tr.find_all('td')
            if len(tdList) == 3:
                # print(tdList[0].text, tdList[1].text, tdList[2].text)
                if tdList[2].text == '差异对比':
                    # continue
                    link = tdList[2].find('a')['href']
                    print(link)
                    temp = getDifferencePage(requests.get(link).text)
                    if len(temp) == 0:
                        unusualName.append(link)
                    else:
                        # paramsRelation.append(temp)
                        nameRelation.append((tdList[0].text, tdList[1].text, temp))
                elif tdList[2].text == '一致':
                    # print(link)
                    torchName = tdList[0].text
                    mindName = tdList[1].text
                    #print(torchName, mindName)
                    params, temp = getFromJson(torchName, mindName, root_path)
                    if len(temp) == 0:
                       # print(params)
                        nameRelation.append((tdList[0].text, tdList[1].text, params))
                    # else:
                    #     link1 = tdList[0].find('a')['href']
                    #     link2 = tdList[1].find('a')['href']
                    #     print(link1, link2)
                    #     params = getFromPage(requests.get(link1), requests.get(link2))
            #else:
                #print(tdList[0].text, tdList[1].text)
    with open("noJson.txt", "w") as f:
        f.write(str(noJsonName))
    print(len(noJsonName))
    return nameRelation


# getInformation from the difference page
def getDifferencePage(req):
    soup = BeautifulSoup(req,  'html.parser')
    tbodyList = soup.find_all('tbody')
    params = []
    if len(tbodyList) == 0:
        return []
    table = tbodyList[-1]
    trList = table.find_all('tr')
    for tr in trList:
        tdList = tr.find_all('td')
        if "参数" in tdList[1].text and "-" not in tdList[2].text and "-" not in tdList[3].text:
            params.append((tdList[2].text, tdList[3].text))
    return params


def getFromJson(torchName, mindName, root_path):
    torchParam = []
    temp = []
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
        temp.append(torchName)
    flag = False
    mindParam = []
    for file in os.listdir(root_path + 'mindspore'):
        for secondFile in os.listdir(root_path + 'mindspore/' + file):
            if secondFile.lower() == mindName.lower() + '.json':
                with open(root_path + 'mindspore/' + file + '/' + secondFile, 'r', encoding='utf-8') as f:
                    mindFile = json.load(f)
                    for dic in mindFile['params']:
                        mindParam.append(dic['name'])
                flag = True
    if not flag:
        print('not found: ', mindName)
        temp.append(mindName)

    result = []
    for param in torchParam:
        if param in mindParam:
            result.append((param, param))
    if len(temp) != 0:
        noJsonName.append(temp)
    return result, temp


def jsonDumps(nameRelation, path):
    jsDict = {}
    jsDict['torchVersion'] = '1.8.1'
    jsDict['mindsporeVersion'] = '2.2'
    relationShip = []
    num = 0
    for name1, name2, params in nameRelation:
        num += 1
        index = num % 10
        tempParams = {}
        for param1, param2 in params:
            tempParams[param1] = param2
        relationShip.append({'pytorch': name1, 'mindspore': name2, 'params': tempParams})
    jsDict['relationship'] = relationShip
    with open(path + 'relationship.json', 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, indent=4)
