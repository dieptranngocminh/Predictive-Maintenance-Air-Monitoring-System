import os

from keras.src.callbacks import EarlyStopping

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from keras.models import Model
from keras.layers import Input, Dense
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA

# Get the current directory of the python script
current_directory = os.path.dirname(os.path.abspath(__file__))
# Define the full path to the Excel file
excel_file_path = os.path.join(current_directory, 'SensorData.xlsx')
# Load data from Excel file. Collect all row that contains value
data = pd.read_excel(excel_file_path, nrows=4584)
# data_numeric = data.select_dtypes(include=[np.number])

data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)

sensor_column = 'temp_0001'
data_numeric = data[[sensor_column]]

scaler = StandardScaler()
scaled_data = scaler.fit_transform(data_numeric)

train_data = scaled_data[:int(0.8*len(scaled_data))]
test_data = scaled_data[int(0.8*len(scaled_data)):]

# Define Autoencoder
input_dim = train_data.shape[1]
input_layer = Input(shape=(input_dim,))

# Encoder
encoder = Dense(32, activation="relu")(input_layer)
encoder = Dense(16, activation="tanh")(input_layer)
encoder = Dense(8, activation="relu")(encoder)

# Bottleneck
bottleneck = Dense(4, activation="relu")(encoder)

# Decoder
decoder = Dense(8, activation="relu")(bottleneck)
decoder = Dense(16, activation="tanh")(decoder)
decoder = Dense(32, activation="tanh")(decoder)

output_layer = Dense(input_dim, activation="linear")(decoder)

autoencoder = Model(inputs=input_layer, outputs=output_layer)
autoencoder.compile(optimizer='adam', loss='mean_absolute_error')

# Train model
autoencoder.fit(train_data, train_data, epochs=50, batch_size=32, validation_split=0.2)

# Generate reconstructions for training and test data
train_reconstructions = autoencoder.predict(train_data)
test_reconstructions = autoencoder.predict(test_data)

# Calculate Mean Absolute Error (MAE) loss for training and test data
train_mae_loss = np.mean(np.abs(train_reconstructions - train_data), axis=1)
test_mae_loss = np.mean(np.abs(test_reconstructions - test_data), axis=1)

# Define threshold for HI (Use Gaussian)
threshold = np.mean(train_mae_loss) + 3*np.std(train_mae_loss)

hi_curve = test_mae_loss.copy() + np.linspace(0, threshold, len(test_mae_loss))
hi_curve = np.maximum(hi_curve, 0)

# Plot graph
plt.figure(figsize=(10, 6))
plt.plot(hi_curve, label='Health Index Curve')
plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
plt.legend()
plt.show()

failure_index = np.argmax(hi_curve > threshold)

if failure_index == 0 and np.max(hi_curve) <= threshold:
    print("Health index does not exceed the threshold within the test data.")
    predicted_failure_time = None
else:
    failure_timestamp = data['Date'].iloc[len(train_data) + failure_index]

    # Calculate RUL using linear regression
    time_indices = np.arange(len(test_mae_loss)).reshape(-1, 1)
    hi_values = hi_curve

    reg = LinearRegression().fit(time_indices, hi_values)
    slope = reg.coef_[0]
    intercept = reg.intercept_

    # Ensure the slope is positive
    if slope <= 0:
        print("Health index regression slope is non-positive, indicating no clear degradation trend.")
        predicted_failure_time = None
    else:
        rul_days = (threshold - intercept) / slope
        latest_timestamp = data['Date'].max()
        max_lifespan_days = 365 * 10
        # predicted_failure_time = latest_timestamp + pd.DateOffset(days=min(rul_days, max_lifespan_days))
        predicted_failure_time = latest_timestamp + pd.DateOffset(days=rul_days)

        print(f"Current Time: {latest_timestamp}")
        print(f"Predicted Failure Time: {predicted_failure_time}")
        print(f"Slope: {slope}")

# Plot the linear regression and HI curve for better visualization
plt.figure(figsize=(10, 6))
plt.plot(test_mae_loss, label='Test MAE Loss')
plt.plot(time_indices, reg.predict(time_indices), label='Linear Regression', color='orange')
plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
plt.legend()
plt.show()
