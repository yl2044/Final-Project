# Import the NumPy library for efficient numerical computations and array handling
# Import the pandas library for data manipulation and analysis, especially for structured data operations using DataFrames
# Import the pyplot module from matplotlib for data visualization and plotting
# Import the seaborn library, built on top of matplotlib, for making statistical graphics in Python more attractive and informative
# Import the sys library to access some variables used or maintained by the Python interpreter and to interact with the environment, used here to read command-line arguments
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Read the first command-line argument (excluding the script name itself, which is sys.argv[0]) as an integer and store it in variable 'a'
# This could be used, for example, to specify a number of hours for prediction in a forecasting script
a = int(sys.argv[1])
# Read the second command-line argument as a file path and store it in the variable 'filepath'
# This is likely used to specify the path to a data file that the script will process
filepath = sys.argv[2]


data = pd.read_csv(filepath)
data = data.sort_values('date')
# print(data.head())
# print(data.shape)

# 1. Characteristic engineering
# Selecting Close as a feature
price = data[['SystemProduction']]
# print(price.info())

from sklearn.preprocessing import MinMaxScaler
# Performs different data scaling, scaling data to between -1 and 1
scaler = MinMaxScaler(feature_range=(-1, 1))
price['SystemProduction'] = scaler.fit_transform(price['SystemProduction'].values.reshape(-1, 1))
# print(price['SystemProduction'].shape)

# 2. Data set production
# lookback indicates the span of the observation
def split_data(stock, lookback):
    data_raw = stock.to_numpy()
    data = []
    # print(data)

    # Freely play（seq_length）
    for index in range(len(data_raw) - lookback):
        data.append(data_raw[index: index + lookback])

    data = np.array(data);
    test_set_size = int(np.round(0.2 * data.shape[0]))
    train_set_size = data.shape[0] - (test_set_size)

    x_train = data[:train_set_size, :-1, :]
    y_train = data[:train_set_size, -1, :]

    x_test = data[train_set_size:, :-1]
    y_test = data[train_set_size:, -1, :]

    return [x_train, y_train, x_test, y_test]

lookback = 20
x_train, y_train, x_test, y_test = split_data(price, lookback)

# Note：pytorch nn.LSTM input shape=(seq_length, batch_size, input_size)

# 3. Model construction -- LSTM

import torch
import torch.nn as nn

x_train = torch.from_numpy(x_train).type(torch.Tensor)
x_test = torch.from_numpy(x_test).type(torch.Tensor)
y_train_lstm = torch.from_numpy(y_train).type(torch.Tensor)
y_test_lstm = torch.from_numpy(y_test).type(torch.Tensor)
y_train_gru = torch.from_numpy(y_train).type(torch.Tensor)
y_test_gru = torch.from_numpy(y_test).type(torch.Tensor)
# The input dimension is 1
input_dim = 1
# Dimension of hidden layer features
hidden_dim = 32
# Loop of layers
num_layers = 2
# Predicting the day after
output_dim = 1
num_epochs = 100


class LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim):
        super(LSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        out = self.fc(out[:, -1, :])
        return out



model = LSTM(input_dim=input_dim, hidden_dim=hidden_dim, output_dim=output_dim, num_layers=num_layers)
criterion = torch.nn.MSELoss()
optimiser = torch.optim.Adam(model.parameters(), lr=0.01)

# 4. Model training
import time

hist = np.zeros(num_epochs)
start_time = time.time()
lstm = []

for t in range(num_epochs):
    y_train_pred = model(x_train)

    loss = criterion(y_train_pred, y_train_lstm)
    # print("Epoch ", t, "MSE: ", loss.item())
    hist[t] = loss.item()

    optimiser.zero_grad()
    loss.backward()
    optimiser.step()

training_time = time.time() - start_time
# print("Training time: {}".format(training_time))

# 5. Visualisation of model results

predict = pd.DataFrame(scaler.inverse_transform(y_train_pred.detach().numpy()))
original = pd.DataFrame(scaler.inverse_transform(y_train_lstm.detach().numpy()))

import seaborn as sns
sns.set_style("darkgrid")

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))
fig.subplots_adjust(hspace=0.2, wspace=0.2)

# Plotting the last 50 hours of actual and predicted data
axes[0].plot(original.index[:a], original[0].head(a), label="Actual Data", color='royalblue')
axes[0].plot(predict.index[:a], predict[0].head(a), label="Predicted Data (LSTM)", color='tomato')

axes[0].set_title('Comparison of predicted and actual values', size=14, fontweight='bold')
axes[0].set_xlabel("Hours", size=14)
axes[0].set_ylabel("SystemProduction", size=14)
axes[0].legend()

# Plotting the training loss for the last 50 epochs
axes[1].plot(range(0, num_epochs), hist[:], color='royalblue')
axes[1].set_xlabel("Epoch", size=14)
axes[1].set_ylabel("Loss", size=14)
axes[1].set_title("Training Loss for the Epochs", size=14, fontweight='bold')
path = "./images"
plt.savefig(path)
print(path)
print(11)

# 6. Model validation
# print(x_test[-1])
import math, time
from sklearn.metrics import mean_squared_error

# make predictions
y_test_pred = model(x_test)

# invert predictions
y_train_pred = scaler.inverse_transform(y_train_pred.detach().numpy())
y_train = scaler.inverse_transform(y_train_lstm.detach().numpy())
y_test_pred = scaler.inverse_transform(y_test_pred.detach().numpy())
y_test = scaler.inverse_transform(y_test_lstm.detach().numpy())

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(y_train[:,0], y_train_pred[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(y_test[:,0], y_test_pred[:,0]))
print('Test Score: %.2f RMSE' % (testScore))
lstm.append(trainScore)
lstm.append(testScore)
lstm.append(training_time)


# In[40]:


# shift train predictions for plotting
trainPredictPlot = np.empty_like(price)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[lookback:len(y_train_pred)+lookback, :] = y_train_pred

# shift test predictions for plotting
testPredictPlot = np.empty_like(price)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(y_train_pred)+lookback-1:len(price)-1, :] = y_test_pred

original = scaler.inverse_transform(price['SystemProduction'].values.reshape(-1,1))

predictions = np.append(trainPredictPlot, testPredictPlot, axis=1)
predictions = np.append(predictions, original, axis=1)
result = pd.DataFrame(predictions)
