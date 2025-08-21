import torch
from ts.torch_handler.base_handler import BaseHandler


class Handler(BaseHandler):
    def preprocess(self, data):
        print("pre: ", data)
        return torch.FloatTensor(data[0])

    def postprocess(self, data):
        print("post: ", data)
        return [torch.argmax(data, dim=0).tolist()]
