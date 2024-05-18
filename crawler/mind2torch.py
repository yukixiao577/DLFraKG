import requests
from relationTools import *

url = "https://www.mindspore.cn/docs/zh-CN/r2.2/note/api_mapping/pytorch_api_mapping.html"
root_path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/node/1.8.1_r2.2/"
save_path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/relation/1.8.1_r2.2/"

r = requests.get(url)
name = getInformation(r.text, root_path)
jsonDumps(name, save_path)

# print(name)
# print(params)