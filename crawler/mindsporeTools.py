import os

from bs4 import BeautifulSoup
import re
import json

specialName = {"torch.torch.dtype": "torch.dtype", "torch.torch.device": "torch.device",
               "torch.torch.layout": "torch.layout", "torch.torch.memory_format": "torch.memory_format"}


def isWord(string):
    if string.find(' ') == -1 and string.find('-') == -1:
        return True
    else:
        return False


def print_hit(hit):
    print('------------------------' + hit)


def getRef(root, req):
    soup = BeautifulSoup(req, 'html.parser')
    ref = soup.find_all(class_='xref py py-obj docutils literal notranslate')
    link = []
    for i in ref:
        link.append(root + i.parent['href'])
    return link


def isClassOrFunction(req):
    soup = BeautifulSoup(req, 'html.parser')
    dl = soup.find('dl')
    if dl:
        dl_class = dl['class']
        if "class" in dl_class:
            return 'class'
        elif "function" in dl_class:
            return 'function'
    return 'error'


def solve_params(soup):
    dl = soup.parent
    dd = dl.find('dd')
    params = []
    if dd:
        # must be the p under li not ul
        p = dd.find_all('p')
        for j in p:
            if j.parent.parent.parent.parent.name == 'ul':
                continue
            strong = j.find_all('strong')
            if strong:
                js = strong[0]
            else:
                continue
            temp = j.text
            if temp.startswith(js.text):
                temp = temp[len(js.text):].strip()
            info = temp.replace('\n', '').split('–', 1)
            type = info[0]
            if len(info) == 1:
                description = info[0]
            else:
                description = info[1]
            description = description.replace("\t", '').replace('"', '').replace(";", ',').strip()
            # delete the （ and ）
            type = type.replace('(', '')
            type = type.replace(')', '').strip()

            default = ''
            optional = False
            if "Default:" in temp:
                temp = temp.replace("\n", " ")
                default = temp.split('Default:')[1].strip()
                default = default.split(" ")[0].strip()
                if default[-1] == '.':
                    default = default[:-1].strip()
                optional = True
            # if "eps" in js.text:
            #     print(temp, default)

            params.append((js.text, type, optional, default, description))
    return params


def solve_input(soup):
    inputs = []
    flag = False
    dl = soup.parent
    for dl_son in dl.children:
        if dl_son == soup:
            flag = True
        if flag and dl_son.name == 'dd':
            # must be the p under li not ul
            p = dl_son.find_all('p')
            for j in p:
                if j.parent.parent.parent.parent.name == 'ul':
                    continue
                strong = j.find_all('strong')
                if strong:
                    js = strong[0]
                else:
                    continue
                temp = j.text
                if temp.startswith(js.text):
                    temp = temp[len(js.text):]
                type = temp.replace('\n', '').split('–')[0]
                # delete the （ and ）
                type = type.replace('(', '')
                type = type.replace(')', '')

                default = ''
                optional = False
                if "Default:" in temp:
                    temp = temp.replace("\n", " ")
                    default = temp.split('Default:')[1].strip()
                    default = default.split(" ")[0].strip()
                    if default[-1] == '.':
                        default = default[:-1].strip()
                    optional = True

                inputs.append((js.text, type, optional, default))
            break
    return inputs


def solve_output(soup):
    outputs = []
    dl = soup.parent
    flag = False
    for dlSon in dl.children:
        if dlSon == soup:
            flag = True
        elif dlSon.name == 'dd' and flag:
            returnType = dlSon.text.split('。')[0].split('，')[0]
            if isWord(returnType):
                outputs.append(returnType)
            break
    return outputs


def getOperatorInformation(req):
    soup = BeautifulSoup(req, 'html.parser')
    dt = soup.find_all('dt')
    params = []
    inputs = []
    outputs = []
    for i in dt:
        if i.string == 'Parameters':
            params = solve_params(i)
            break
    dt = soup.find_all('dt')
    for i in dt:
        if i.string == 'Outputs:':
            outputs = solve_output(i)
            break
    dd = soup.find_all('dd')
    desc = ''
    for i in dd:
        if "function" in i.parent.attrs['class']:
            p = i.find('p')
            desc = p.text.split('.')[0]
            desc = desc.replace("\n", "").replace(";", ",").replace('"', "").replace("\\", " ").strip()
            break
    return params, outputs, desc


def getClassInformation(req):
    soup = BeautifulSoup(req, 'html.parser')
    for dl in soup.find_all('dl', {'class': 'method'}):
        dl.extract()
    params = []
    outputs = []
    dt = soup.find_all('dt')
    for i in dt:
        if i.string == 'Parameters':
            params = solve_params(i)
            break
    dt = soup.find_all('dt')
    for i in dt:
        if i.string == 'Outputs:':
            outputs = solve_output(i)
            break

    dd = soup.find_all('dd')
    desc = ''
    for i in dd:
        if "class" in i.parent.attrs['class']:
            p = i.find('p')
            desc = p.text.split('.')[0]
            desc = desc.replace("\n", "").replace('"', "").replace(";", ",").strip()
            break
    return params, outputs, desc


def getDl(req, path, version):
    soup = BeautifulSoup(req, 'html.parser')
    for dl in soup.find_all('dl', class_='py function'):
        dlStr = str(dl)
        dt = dl.find_all('dt')[0]
        # name is the id of dt
        apiName = dt['id']
        params, returnType, desc = getOperatorInformation(dlStr)
        jsonDumps(apiName, params, returnType, desc, version=version, path=path)
    for dl in soup.find_all('dl', class_='class'):
        dlStr = str(dl)
        dt = dl.find_all('dt')[0]
        # name is the id of dt
        apiName = dt['id']
        if apiName in specialName.keys():
            apiName = specialName[apiName]
        params, returnType, desc = getClassInformation(dlStr)
        jsonDumps(apiName, params, returnType, desc, version=version, path=path)


def dealDefault(default):
    #default = default.encode('utf-8')
    default = default.replace("mstype", "mindspore")
    i = default.strip()
    if len(i) == 0:
        i = ""
    else:
        i = i.replace("\"", "")
        i = i.replace("\'", "")
        i = i.replace("‘", "")
        i = i.replace("’", "")
        i = i.replace("“", "")
        i = i.replace("”", "")
    return i


def jsonDumps(api, params, returnType, desc='', version='2.2', path='./'):
    jsDict = {}
    myParams = []
    for i in params:
        temp = {}
        temp['name'] = i[0]
        temp['type'] = [i[1]]
        temp['optional'] = i[2]
        # change the " to '
        temp['default'] = dealDefault(i[3])
        temp['description'] = dealDefault(i[4])
        myParams.append(temp)
    # myInputs = []
    # for i in inputs:
    #     temp = {}
    #     temp['name'] = i[0]
    #     temp['type'] = [i[1]]
    #     temp['optional'] = i[2]
    #     temp['default'] = dealDefault(i[3])
    #     myInputs.append(temp)
    jsDict['api'] = api
    jsDict['version'] = version
    jsDict['description'] = desc
    jsDict['params'] = myParams
    #jsDict['inputs'] = myInputs
    jsDict['returnType'] = returnType
    fileName = api + '.json'
    filePath = path + fileName
    if os.path.exists(filePath):
        filePath = filePath.replace(".json", "_2.json")
    if not os.path.exists(path):
        os.makedirs(path)
    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(jsDict, f, ensure_ascii=False, indent=4, default=str)
        f.close()
