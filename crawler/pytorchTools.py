from bs4 import BeautifulSoup
import re
from mindsporeTools import jsonDumps

specialName = {"torch.torch.dtype": "torch.dtype", "torch.torch.device": "torch.device", "torch.torch.layout": "torch.layout", "torch.torch.memory_format": "torch.memory_format"}


def print_hit(hit):
    print('------------------------' + hit)


# judge is only one word or not
def isWord(string):
    if string.find(' ') == -1 and string.find('-') == -1:
        return True
    else:
        return False


def getRef(req):
    soup = BeautifulSoup(req, 'html.parser')
    ref = soup.find_all('tr', class_=['row-odd', 'row-even'])
    links = []
    for i in ref:
        if i.find('a', class_='reference internal'):
            links.append('https://pytorch.org/docs/1.8.1/' + i.find('a', class_='reference internal')['href'])
    return links


def getInformation(req, type):
    soup = BeautifulSoup(req, 'html.parser')
    params = []
    outputs = []
    desc = ""
    if type == 'class':
        for dl in soup.find_all('dl', {'class': 'method'}):
            dl.extract()
    dt = soup.find_all('dt')
    for i in dt:
        if i.string == 'Parameters':
            dl = i.parent
            dd = dl.find('dd')
            p = dd.find_all('p')
            for j in p:
                if j.parent.parent.parent.parent.name == 'ul':
                    continue
                strong = j.find_all('strong')
                # js is the name of the parameter
                if strong:
                    js = strong[0]
                else:
                    continue
                # temp is the description and type of the parameter
                temp = j.text
                if temp.startswith(js.text):
                    temp = temp[len(js.text):]
                # get type and description
                if '–' in temp:
                    type = temp.split('–')[0]
                    if "e-" not in temp:
                        description = temp.split('–')[1]
                    else:
                        description = temp
                else:
                    type = temp.split(':')[0]
                    description = temp.split(':')[1]
                type = type.replace('\n', '').replace(')', '').replace('(', '')
                description = description.replace('\n', '').replace('\t', '').replace('"', '').replace(';', ',').strip()
                default = ''
                optional = False
                pattern = '.+default:.+'
                if re.match(pattern, description):
                    default = description.split('default:')[1]
                    default = default.split('。')[0]
                    optional = True
                pattern = '.+Default:.+'
                if re.match(pattern, description):
                    default = description.split('Default:')[1]
                    default = default.split('。')[0]
                    optional = True
                if default != '' and (default[-1] == ')' or default[-1] == '.'):
                    default = default[:-1].strip()
                if 'optional' in type:
                    type = type.split('optional')[0]
                    type = type.replace(',', '').strip()
                params.append((js.text, type, optional, default, description))
            break
    for i in dt:
        if i.string == 'Keyword Arguments':
            dl = i.parent
            flag = False
            for dl_son in dl:
                if dl_son == i:
                    flag = True
                if flag and dl_son.name == 'dd':
                    p = dl_son.find_all('p')
                    for j in p:
                        if j.parent.parent.parent.parent.name == 'ul':
                            continue
                        strong = j.find_all('strong')
                        # js is the name of the parameter
                        if strong:
                            js = strong[0]
                        else:
                            continue
                        # temp is the description and type of the parameter
                        temp = j.text
                        if temp.startswith(js.text):
                            temp = temp[len(js.text):]
                        # get type and description
                        if '–' in temp:
                            type = temp.split('–')[0]
                            if "e-" not in temp:
                                description = temp.split('–')[1]
                            else:
                                description = temp
                        else:
                            type = temp.split(':')[0]
                            description = temp.split(':')[1]
                        type = type.replace('\n', '').replace(')', '').replace('(', '')
                        description = description.replace('\n', '').replace('\t', '').replace('"', '').replace(';', ',').strip()
                        default = ''
                        optional = False
                        pattern = '.+default:.+'
                        if re.match(pattern, description):
                            default = description.split('default:')[1]
                            default = default.split('。')[0]
                            optional = True
                        pattern = '.+Default:.+'
                        if re.match(pattern, description):
                            default = description.split('Default:')[1]
                            default = default.split('。')[0]
                            optional = True
                        if default != '' and (default[-1] == ')' or default[-1] == '.'):
                            default = default[:-1].strip()
                        if 'optional' in type:
                            type = type.split('optional')[0]
                            type = type.replace(',', '').strip()
                        params.append((js.text, type, optional, default, description))
                    break
            break
    for i in dt:
        if i.string == 'Returns':
            dl = i.parent
            flag = False
            for dlSon in dl.children:
                if dlSon == i:
                    flag = True
                elif dlSon.name == 'dd' and flag:
                    returnType = dlSon.text.split('。')[0].split('，')[0]
                    if isWord(returnType):
                        outputs.append(returnType)
                    break
            break

    dd = soup.find_all('dd')
    for i in dd:
        if "class" in i.parent.attrs['class'] or "function" in i.parent.attrs['class']:
            p = i.find('p')
            if p is not None:
                desc = p.text.split('.')[0]
                desc = desc.replace('\n', '').replace('\t', '').replace('"', '').replace(';', ',').strip()
            break
    return params, outputs, desc


def getDl(req, path, version='1.8.1'):
    soup = BeautifulSoup(req, 'html.parser')
    for dl in soup.find_all('dl', class_='function'):
        if dl.parent.name == 'dd':
            continue
        dlStr = str(dl)
        dt = dl.find_all('dt')[0]
        # name is the id of dt
        if dt.has_attr('id'):
            apiName = dt['id']
            if apiName in specialName.keys():
                apiName = specialName[apiName]
            params, returnType, desc = getInformation(dlStr, 'function')
            jsonDumps(apiName, params, returnType, desc, path=path, version=version)
    for dl in soup.find_all('dl', class_='class'):
        dlStr = str(dl)
        dt = dl.find_all('dt')[0]
        # name is the id of dt
        if dt.has_attr('id'):
            apiName = dt['id']
            if apiName in specialName.keys():
                apiName = specialName[apiName]
            params, returnType, desc = getInformation(dlStr, 'class')
            jsonDumps(apiName, params, returnType, desc, path=path, version=version)