import requests
from mindsporeTools import *

root = "https://www.mindspore.cn/docs/en/r2.2/api_python/"


def solve_ms(save_path):
    modules = ['mindspore', 'mindspore.nn', 'mindspore.ops', 'mindspore.ops.primitive', 'mindspore.amp', 'mindspore.train',
           'mindspore.dataset', 'mindspore.dataset.transforms', 'mindspore.nn.probability', 'mindspore.numpy',
           'mindspore.scipy', 'mindspore.experimental']
    direct_api = ['mindspore.communication', 'mindspore.common.initializer', 'mindspore.mindrecord',
                  'mindspore.rewrite', 'mindspore.boost']
    for i in modules:
        url = root + i + '.html'
        r = requests.get(url)
        links = getRef(root, r.text)
        for link in links:
            print_hit(link)
            r = requests.get(link)
            apiName = link.split('#')[1]
            type = isClassOrFunction(r.text)
            if type == 'function':
                params, returnType, desc = getOperatorInformation(r.text)
                jsonDumps(apiName, params, returnType, desc, version="2.2", path=save_path + i + '/')
            elif type == 'class':
                params, returnType, desc = getClassInformation(r.text)
                jsonDumps(apiName, params, returnType, desc, version="2.2", path=save_path + i + '/')
            else:
                print('error')

    for i in direct_api:
        url = root + i + '.html'
        r = requests.get(url)
        getDl(r.text, save_path + i + '/', version="2.2")


if __name__ == "__main__":
    save_path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/node/1.8.1_r2.2/mindspore/"
    solve_ms(save_path)






