import re

from bs4 import BeautifulSoup


def getLink(r):
    soup = BeautifulSoup(r, 'html.parser')
    links = []
    for a in soup.find_all('a'):
        temp = a['href']
        if temp.startswith("/documentation/docs/en/2.4/api/paddle/") and not temp.endswith("index_en.html") and not temp.endswith("Overview_en.html"):
            links.append("https://www.paddlepaddle.org.cn" + temp)
    return links


def getInformation(r):
    soup = BeautifulSoup(r, 'html.parser')
    params = []

    api_dt = soup.find('dt', {'class': 'sig sig-object py'})
    api = api_dt.text.replace('\n', '').replace('\t', '').replace(' ', '')
    api_name = api.split('(')[0].replace('class', '')
    p = api_dt.findNext('dd').find('p')
    desc = ''
    while p:
        desc += p.text
        if p.findNext().name == 'p':
            p = p.findNext()
        else:
            p = None
    desc = desc.replace('\n', '').replace('\t', '').replace(';', ',').split('.')[0].strip()

    pars = api[api.find('(') + 1: api.rfind(')')].split(',')
    pars_dict = {}
    for par in pars:
        if '=' in par:
            name, default = par.split('=', 1)
        else:
            name = par
            default = ''
        pars_dict[name] = default

    dd = soup.find('dd', {'class': 'field-odd'})
    if dd and "Parameters" in dd.findPrevious().text:
        lis = dd.find_all('li')
        for i in range(len(lis)):
            li = lis[i]
            if li.parent.parent.name != 'dd':
                continue
            p = li.find('p')
            if p is None:
                continue
            name = p.find('strong')
            if not name:
                print(i)
                continue
            name = name.text
            if name not in pars_dict.keys():
                print(api_name, name)
                continue
            type = p.find('em')
            if not type:
                type = p.find('cite')
            if not type:
                type = ''
            else:
                type = type.text
            description = li.text.split('–')[1].replace('\n', '').replace('\t', '').replace(';', ',').strip().split('.')[0].strip()
            default = pars_dict[name]
            if default == '':
                optional = False
            else:
                optional = True
            params.append((name, type, optional, default, description))

    returnType = []
    if dd:
        dd_return = dd.findNext('dd', {'class': 'field-odd'})
        if dd_return and "Return type" in dd_return.findPrevious().text:
            returnType.append(dd_return.text.strip())

    return api_name, params, returnType, desc


def getApiName(link):
    temp = link.split('/')
    temp[-1] = temp[-1].split('_')[0]
    # 找到temp里面“api”下标
    index = temp.index('api')
    temp = temp[index + 1:]
    # 类似paddle.nn.functional
    return '.'.join(temp)


def specialDeal(link):
    if link == "https://www.paddlepaddle.org.cn/documentation/docs/zh/api/paddle/broadcast_tensors_cn.html":
        params = [('input', 'list(Tensor)|tuple(Tensor)', 'False', ['']), ('name', 'str', 'True', ['None'])]
        inputs = []
        outputs = ['list(Tensor)']
        return params, inputs, outputs
    elif link == "https://www.paddlepaddle.org.cn/documentation/docs/zh/api/paddle/DataParallel_cn.html":
        params = [('layer', 'layer', 'False', ['']), ('strategy', 'ParallelStrategy', 'True', ['None']), ('comm_buffer_size', 'int', 'True', ['25']), ('last_comm_buffer_size', 'float', 'True', ['1']), ("find_unused_parameters", 'bool', 'True', ['False'])]
        inputs = []
        outputs = ['layer']
        return params, inputs, outputs
    return None