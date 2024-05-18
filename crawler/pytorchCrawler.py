import requests
from pytorchTools import *
from mindsporeTools import isClassOrFunction, jsonDumps

root = 'https://pytorch.org/docs/1.8.1/'
# 开梯子的代理端口，如果没有开梯子，可以注释掉
#proxy = {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'}
apis = ['torch', 'nn', 'quantization']
directApis = ['nn.functional', 'tensors', 'tensor_attributes', 'autograd', 'cuda', 'amp', 'backends', 'distributed', 'distributions', 'fft', 'futures', 'fx', 'hub', 'jit', 'linalg', 'torch.overrides', 'nn.init', 'onnx', 'optim', 'ddp_comm_hooks', 'pipeline', 'rpc', 'random', 'sparse', 'storage', 'benchmark_utils', 'checkpoint', 'cpp_extension', 'data', 'dlpack', 'mobile_optimizer', 'model_zoo', 'tensorboard']
specialLink = {'https://pytorch.org/docs/1.8.1/torch.nn.intrinsic.qat.html': 'torch.nn.intrinsic.qat', 'https://pytorch.org/docs/1.8.1/torch.nn.intrinsic.quantized.html': 'torch.nn.intrinsic.quantized', 'https://pytorch.org/docs/1.8.1/torch.nn.qat.html': 'torch.nn.qat', 'https://pytorch.org/docs/1.8.1/torch.nn.quantized.dynamic.html': 'torch.nn.quantized.dynamic', 'https://pytorch.org/docs/1.8.1/torch.nn.quantized.html': 'torch.nn.quantized', "https://pytorch.org/docs/1.8.1/torch.quantization.html#torch-quantization": 'torch.quantization', "https://pytorch.org/docs/1.8.1/torch.nn.intrinsic.html#torch-nn-intrinsic": "torch.nn.intrinsic"}

def solve(save_path):
    for api in apis:
        url = root + api + '.html'
        r = requests.get(url, '''proxies=proxy''')
        links = getRef(r.text)
        for link in links:
            print_hit(link)
            r = requests.get(link, '''proxies=proxy''')
            if link in specialLink.keys():
                getDl(r.text, save_path + specialLink[link] + '/', version='1.8.1')
                continue
            apiName = link.split('#')[1]
            type = isClassOrFunction(r.text)
            print(type)
            params, returnType, desc = getInformation(r.text, type)
            jsonDumps(apiName, params, returnType, desc, path=save_path + api + '/', version='1.8.1')
    for api in directApis:
        url = root + api + '.html'
        print_hit(url)
        r = requests.get(url, '''proxies=proxy''')
        getDl(r.text, save_path + api + '/', version='1.8.1')


if __name__ == "__main__":
    save_path = save_path = "E:/postgraduate/drone/transfer/KGForDLFrame/dao/node/1.8.1_r2.2/pytorch/"
    solve(save_path)

