import cupy as cp

class Loss(object):
  """Loss functions for NN class"""

  def __init__(self):
    pass

  def mse(self,yhat,y):
    return cp.mean((yhat - y)**2)

  def mse_derivative(self,yhat,y):
    if yhat.shape == y.shape:
      return yhat - y
    return yhat - cp.reshape(y,yhat.shape)

  def mse_alt(y,yhat):
    return cp.mean((y - yhat)**2)

  def mse_alt_derivative(y,yhat):
    if y.shape == yhat.shape:
      return y - yhat
    return cp.reshape(y,yhat.shape) - yhat

  def binary_crossentropy(self,y,yhat,epsilon=1e-7):
    yhat = cp.clip(yhat, epsilon, 1 - epsilon)
    return -(y * cp.log(yhat) + (1 - y) * cp.log(1 - yhat))

  def binary_crossentropy_derivative(self,y,yhat,epsilon=1e-7):
    yhat = cp.clip(yhat, epsilon, 1 - epsilon)
    return -(y / yhat) + (1 - y) / (1 - yhat)