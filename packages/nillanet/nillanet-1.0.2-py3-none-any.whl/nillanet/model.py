import cupy as cp
import numpy as np
import os
import math
import random
import re
import pickle
import sys

cp.random.seed()
cp.set_printoptions(precision=2,floatmode='fixed',suppress=True)

class NN(object):

  """Minimal feedforward neural network using CuPy.

    This class implements batched SGD with configurable activation,
    classifier, and loss functions. Inputs/targets are kept on device
    to avoid host↔device copies.

    Args:
        features (int): Columnar shape of inputs.
        architecture (list[int]): Units per layer, including output layer.
        activation (Callable[[cupy.ndarray], cupy.ndarray]): Hidden-layer
            activation function.
        derivative1 (Callable[[cupy.ndarray], cupy.ndarray]): Derivative of
            ``activation`` evaluated at pre-activations.
        classifier (Callable[[cupy.ndarray], cupy.ndarray]): Output-layer
            transfer function (e.g., identity, sigmoid, softmax).
        derivative2 (Callable[[cupy.ndarray], cupy.ndarray]): Derivative of
            ``classifier`` evaluated at pre-activations.
        loss (Callable[..., cupy.ndarray]): Loss function that accepts
            named arguments (e.g., ``yhat``, ``y``) and returns per-sample
            losses or their average.
        derivative3 (Callable[..., cupy.ndarray]): Derivative of ``loss``
            with respect to predictions (same signature as ``loss``).
        learning_rate (float): SGD step size.
        dtype (cupy.dtype, optional): Floating point dtype for parameters and data.
            Defaults to ``cupy.float32``.

    Attributes:
        W (list[cupy.ndarray]): Layer weight matrices; ``W[i]`` has shape
            (in_features_i, out_features_i).
  """

  def __init__(self, features, architecture, activation, derivative1,
               classifier, derivative2, loss, derivative3, learning_rate,
               dtype=cp.float32):
    self.architecture = architecture
    self.activation = activation
    self.activation_derivative = derivative1
    self.classifier = classifier
    self.classifier_derivative = derivative2
    self.loss = loss
    self.loss_derivative = derivative3
    self.learning_rate = learning_rate
    self.dtype = dtype

    # weights initialized from [-1, 1]
    self.W = []
    features += 1 # bias
    for i in range(len(self.architecture)):
      nodes = self.architecture[i]
      w = 2 * cp.random.random((features, nodes), dtype=self.dtype) - 1
      self.W.append(w)
      features = nodes

  def train(self, input, output, epochs=1, batch=0):
    """Train the model using simple SGD.

        Args:
            input (cupy.ndarray | numpy.ndarray): Training inputs of shape
              (n_samples, n_features). If NumPy, it will be moved to device.
            output (cupy.ndarray | numpy.ndarray): Training targets of shape
              (n_samples, n_outputs). If NumPy, it will be moved to device.
            epochs: Number of SGD steps to run.
            batch: One of:
                - ``1``: sample a single example per step (pure SGD)
                - ``0``: use all samples per step (full batch)
                - ``>1`` and ``< len(Y)``: use that mini-batch size per step

        Raises:
            SystemExit: If ``batch`` is invalid.
    """
    # keep data on device and in a consistent dtype
    X = cp.asarray(input, dtype=self.dtype)
    Y = cp.asarray(output, dtype=self.dtype)

    # device-side bias column (avoid NumPy)
    bias = cp.ones((X.shape[0], 1), dtype=self.dtype)
    X = cp.concatenate((bias, X), axis=1)

    n = X.shape[0]
    if batch == 1:
      for _ in range(epochs):
        index = random.randint(0, n - 1)
        self.batch(X[index], Y[index])
    elif batch == 0:
      for _ in range(epochs):
        self.batch(X, Y)
    elif 1 < batch < n:
      for _ in range(epochs):
        index = random.randint(0, n - batch)
        x = X[index:index + batch]
        y = Y[index:index + batch]
        self.batch(x, y)
    else:
      sys.exit(f"improper batch size {batch}")

  def batch(self, x, y):
    """Run a single forward/backward/update step.

        Args:
            x (cupy.ndarray | numpy.ndarray): Inputs, shape (B, D) or (D,).
            y (cupy.ndarray | numpy.ndarray): Targets, shape (B, K) or (K,).

        Notes:
            Ensures inputs/targets reside on device and are at least 2D.
    """
    # ensure inputs reside on device & 2D
    x = cp.atleast_2d(cp.asarray(x))
    y = cp.asarray(y)

    inputs = []
    raw_outputs = []

    # forward
    h = x
    for i in range(len(self.architecture)):
      inputs.append(h)
      z = cp.atleast_2d(h @ self.W[i])
      raw_outputs.append(z)
      if i == len(self.architecture) - 1:
        h = self.classifier(z)
      else:
        h = self.activation(z)

    # backward
    prev_grad = None
    for i in range(len(self.architecture) - 1, -1, -1):
      if i == len(self.architecture) - 1:
        loss_grad = self.loss_derivative(yhat=h, y=y)
        grad = cp.atleast_2d(loss_grad * self.classifier_derivative(raw_outputs[i]))
      else:
        grad = (prev_grad @ self.W[i + 1].T) * self.activation_derivative(raw_outputs[i])

      # in-place weight update
      self.W[i] -= self.learning_rate * (inputs[i].T @ grad)
      prev_grad = grad

  def predict(self, input):
    """Run a forward pass to produce predictions.

        Args:
            input (cupy.ndarray | numpy.ndarray): Inputs of shape
                (n_samples, n_features). If NumPy, it will be moved to device.

        Returns:
            cupy.ndarray: Model outputs of shape (n_samples, n_outputs).
    """
    x = cp.asarray(input)
    bias = cp.ones((x.shape[0], 1), dtype=x.dtype)
    x = cp.concatenate((bias, x), axis=1)

    h = x
    for i in range(len(self.architecture)):
      z = cp.atleast_2d(h @ self.W[i])
      if i == len(self.architecture) - 1:
        h = self.classifier(z)
      else:
        h = self.activation(z)
    return h

  def summary(self):
    """Print layer shapes and total parameter count."""
    total = 0
    for idx, w in enumerate(self.W):
      params = w.shape[0] * w.shape[1]
      total += params
      print(f"layer {idx} weights {tuple(w.shape)} parameters {params}")
    print(f"total parameters {total}")

