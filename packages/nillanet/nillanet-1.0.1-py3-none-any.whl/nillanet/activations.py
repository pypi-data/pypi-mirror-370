import cupy as cp
import math

class Activations(object):
  """Activation functions for NN class.
  """

  def __init__(self):
    pass

  def sigmoid(self,x):
    return 1 / (1 + cp.exp(-x))

  def sigmoid_derivative(self,x):
    return self.sigmoid(x) * (1 - self.sigmoid(x))

  def tanh(self,x):
    return cp.tanh(x) # return (1 - cp.exp(-2 * x)) / (1 + cp.exp(-2 * x))

  def tanh_derivative(self,x):
    return 1 - (x ** 2)

  def linear(self,x):
    return x

  def linear_derivative(self,x):
    if isinstance(x,cp.ndarray) or isinstance(x,list):
      return cp.atleast_2d(cp.ones(x.shape)).astype(cp.float64)
    return 1

  def relu(self,x):
    return cp.maximum(0,x)

  def relu_derivative(self,x):
    if isinstance(x,list) or isinstance(x,cp.ndarray):
      x[x > 0] = 1
      return x
    else:
      return 1 if x > 0 else 0

  def softmax(self,x):
    x = cp.exp(x)
    sums = cp.sum(x, axis=1)
    sums = sums.reshape(sums.shape[0],1)
    x /= sums
    return x