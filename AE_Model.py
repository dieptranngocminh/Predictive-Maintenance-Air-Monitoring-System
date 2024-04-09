import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from keras.models import Model
from keras.layers import Input, Dense
from keras.optimizers import RMSprop
from sklearn.linear_model import LinearRegression
from keras.callbacks import EarlyStopping

# Get the current directory of the python script
current_directory = os.path.dirname(os.path.abspath(__file__))
# Define the full path to the Excel file
excel_file_path = os.path.join(current_directory, 'SensorData.xlsx')
# Load data from Excel file
data = pd.read_excel(excel_file_path)
print("adgafdad")
print("excel file: ", excel_file_path)
# Select only temperature sensor data - column temp_0001
temp_data = data['temp_0001'].values.reshape(-1, 1) # About 4500 values

# Normalize data - Calculate z-normalization data using Scaler
scaler = StandardScaler()
temp_data_scaled = scaler.fit_transform(temp_data)

# Split data into train and test sets
X_train, X_test = train_test_split(temp_data_scaled, test_size=0.2, random_state=42)

# Define autoencoder architecture. Autoencoder = Encoder + Decoder
input_dim = X_train.shape[1]
encoding_dim = 4  # Number of nodes in hidden layer
input_layer = Input(shape=(input_dim,))
encoded = Dense(encoding_dim, activation='tanh')(input_layer) # Encoder use tanh - f activation function
decoded = Dense(input_dim, activation='linear')(encoded) # Decoder use g - linear function

# Define autoencoder - AE model
autoencoder = Model(input_layer, decoded)

# Compile autoencoder. Use RMS & MSE
autoencoder.compile(optimizer=RMSprop(), loss='mean_squared_error')

# Define early stopping criteria to avoid overfitting & find epochs
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train autoencoder
autoencoder.fit(X_train, X_train,
                epochs=100,
                batch_size=32, # Number of samples in each iteration, can be 2^n
                shuffle=True,
                validation_data=(X_test, X_test),
                callbacks=[early_stopping])

# Obtain reconstructed data
reconstructed_data = autoencoder.predict(temp_data_scaled)

# Calculate MAE for Health Index (HI)
mae = np.mean(np.abs(temp_data_scaled - reconstructed_data), axis=0)

# Calculate threshold based on 3-sigma rule
hi_mean = np.mean(mae)  # HI mean
hi_std_dev = np.std(mae)  # HI Standard Deviation
threshold = 3 * hi_std_dev + hi_mean
# Predict RUL using Linear regression
# RUL prediction based on trend of HI
# Additional code needed for regression model fitting and prediction

# Display results
print("MAE for Health Index (HI):", mae)
print("Threshold (3-sigma rule):", threshold)
