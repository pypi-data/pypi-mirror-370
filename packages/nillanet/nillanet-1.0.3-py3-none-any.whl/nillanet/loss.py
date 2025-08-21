import cupy as cp

class Loss(object):
  """Loss functions for NN class"""

  def __init__(self):
    pass

  def mse(self,yhat,y):
      """
      Mean Squared Error (MSE) between predicted values and actual values.

      Parameters
      -----------
      yhat: tensor
          The predicted values.
      y: tensor
          The actual values.

      Returns
      -------------
      tensor:
          The Mean Squared Error between the predicted and actual values.
      """
      return cp.mean((yhat - y)**2)

  def mse_derivative(self,yhat,y):
    """
    Derivative of the Mean Squared Error (MSE) loss function.

    Parameters
    ----------
    yhat: tensor
        The predicted values.
    y: tensor
        The actual values.

    Returns
    -------
    tensor
        The derivative of the MSE loss function with respect to the inputs.
    """
    if yhat.shape == y.shape:
        return yhat - y
    return yhat - cp.reshape(y,yhat.shape)

  def binary_crossentropy(self,y,yhat):
      """
      Evaluates the distance between the true labels and the predicted probabilities
      by evaluating the logarithmic loss.

      Parameters
      -----------
      y: tensor
          The true labels.
      yhat: tensor
          The predicted probabilities.

      Returns
      --------
      tensor:
          The logarithmic loss between the true labels and the predicted probabilities.
      """
      return -(y * cp.log(yhat) + (1 - y) * cp.log(1 - yhat))

  def binary_crossentropy_derivative(self,y,yhat):
    """
    Derivative of the binary cross-entropy loss function.

    Parameters
    -----------
    y: tensor
        The true labels.
    yhat: tensor
        The predicted probabilities.

    Returns
    --------
    tensor:
        The derivative of the binary cross-entropy loss function with respect to the inputs.
    """
    return -(y / yhat) + (1 - y) / (1 - yhat)
