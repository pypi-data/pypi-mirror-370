from nillanet.model import NN
from nillanet.activations import Activations
from nillanet.loss import Loss
from nillanet.distributions import Distributions

d = Distributions()
x,y = d.linear_distribution(10)
print(x.shape)
print(y.shape)

a = Activations()
activation = a.sigmoid
derivative1 = a.sigmoid_derivative
classifier = a.linear
derivative2 = a.linear_derivative

l = Loss()
loss = l.mse
derivative3 = l.mse_derivative

input = x
output = y
features = x.shape[1]
architecture = [2,4,1]
learning_rate = 0.1
epochs = 1000

model = NN(features,architecture,activation,derivative1,classifier,derivative2,loss,derivative3,learning_rate)
model.train(input,output,epochs)
prediction = model.predict(x)

print("prediction")
print(prediction)
print("expected")
print(y)
