import requests
from paddleTools import *
from mindsporeTools import print_hit, jsonDumps

flag = False
specialLinks = ["https://www.paddlepaddle.org.cn/documentation/docs/zh/api/paddle/broadcast_tensors_cn.html", "https://www.paddlepaddle.org.cn/documentation/docs/zh/api/paddle/DataParallel_cn.html"]
specialLinks = []
url = "https://www.paddlepaddle.org.cn/documentation/docs/en/2.4/api/index_en.html"   # "https://www.paddlepaddle.org.cn/documentation/docs/zh/api/index_cn.html"

def solve_paddle(save_path):
    r = requests.get(url)
    links = getLink(r.text)
    for link in links:
        print_hit(link)
        # if link == "https://www.paddlepaddle.org.cn/documentation/docs/zh/api/paddle/text/viterbi_decode_cn.html":
        #     flag = True
        # if not flag:
        #     continue

        if link in specialLinks:
            params, inputs, outputs, returnType, desc = specialDeal(link)
        else:
            r = requests.get(link)
            apiName, params, returnType, desc = getInformation(r.text)
        jsonDumps(apiName, params, returnType, desc, version="2.4", path=save_path)


if __name__ == "__main__":
    save_path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/node/1.8.1_r2.2/paddle/"
    solve_paddle(save_path)
