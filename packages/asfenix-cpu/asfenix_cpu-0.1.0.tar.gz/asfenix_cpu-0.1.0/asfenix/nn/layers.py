import numpy as np
from asfenix.core.tensor import Tensor
from asfenix.core.ops import matmul, relu

class Linear:
    def __init__(self, in_features, out_features):
        self.W = Tensor(np.random.randn(in_features, out_features) * 0.01, requires_grad=True)
        self.b = Tensor(np.zeros(out_features), requires_grad=True)

    def __call__(self, x):
        return Tensor(matmul(x.data, self.W.data) + self.b.data, requires_grad=True)

class ReLU:
    def __call__(self, x):
        return Tensor(relu(x.data), requires_grad=True)
