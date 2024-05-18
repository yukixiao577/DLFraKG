import markdown

from paddleRelationTools import *
url = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/X2Paddle-develop/docs/pytorch_project_convertor/API_docs/"
root_path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/node/1.8.1_r2.2/"
save_path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/relation/1.8.1_r2.2/"

list = []
for dirs in os.listdir(url):
    print(dirs)
    if os.path.isdir(os.path.join(url, dirs)):
        print(1)
        with open(os.path.join(url, dirs + "/README.md"), 'r', encoding='utf-8') as f:
            md_content = f.read()
        # 创建Markdown对象
        md = markdown.Markdown(extensions=['extra'])
        # 将Markdown转换为HTML格式的字符串
        html_output = md.convert(md_content)
        name = getPaddleTorchRelation(html_output, root_path, os.path.join(url, dirs))
        list.extend(name)
        print(list)

paddleJsonDumps(list, save_path)
