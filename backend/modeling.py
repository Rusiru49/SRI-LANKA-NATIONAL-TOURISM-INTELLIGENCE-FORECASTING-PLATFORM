import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import joblib
import warnings
import config

warnings.filterwarnings('ignore')

def load_processed_data():
    """Load preprocessed data"""
    file_path = config.PROCESSED_DATA_FILE.replace('.csv', '_engineered.csv')
    try:
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        # Fallback to original file
        df = pd.read_csv(config.PROCESSED_DATA_FILE)
        df['date'] = pd.to_datetime(df['date'])
        return df

def prepare_prophet_data(df):
    """Prepare data for Prophet model"""
    # Aggregate by date
    prophet_df = df.groupby('date')['arrivals'].sum().reset_index()
    prophet_df.columns = ['ds', 'y']
    return prophet_df

def train_prophet_model(df):
    """Train Prophet model for time series forecasting"""
    print("\n" + "=" * 60)
    print("TRAINING PROPHET MODEL")
    print("=" * 60)
    
    # Prepare data
    prophet_df = prepare_prophet_data(df)
    
    # Split data
    train_size = int(len(prophet_df) * 0.8)
    train_df = prophet_df[:train_size]
    test_df = prophet_df[train_size:]
    
    print(f"\nTraining set: {len(train_df)} months")
    print(f"Test set: {len(test_df)} months")
    
    # Train model
    print("\nTraining Prophet...")
    model = Prophet(**config.PROPHET_PARAMS)
    model.fit(train_df)
    
    # Make predictions
    future = model.make_future_dataframe(periods=len(test_df), freq='MS')
    forecast = model.predict(future)
    
    # Evaluate
    train_pred = forecast.iloc[:train_size]['yhat'].values
    test_pred = forecast.iloc[train_size:]['yhat'].values
    
    train_mae = mean_absolute_error(train_df['y'], train_pred)
    test_mae = mean_absolute_error(test_df['y'], test_pred)
    train_rmse = np.sqrt(mean_squared_error(train_df['y'], train_pred))
    test_rmse = np.sqrt(mean_squared_error(test_df['y'], test_pred))
    
    print(f"\nTrain MAE: {train_mae:.2f}")
    print(f"Train RMSE: {train_rmse:.2f}")
    print(f"Test MAE: {test_mae:.2f}")
    print(f"Test RMSE: {test_rmse:.2f}")
    
    # Save model
    joblib.dump(model, config.PROPHET_MODEL_FILE)
    print(f"\nModel saved to: {config.PROPHET_MODEL_FILE}")
    
    return model, forecast

def prepare_lstm_data(df, lookback=12):
    """Prepare data for LSTM model"""
    # Aggregate by date
    ts_df = df.groupby('date')['arrivals'].sum().reset_index()
    ts_df = ts_df.sort_values('date')
    
    # Scale data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(ts_df[['arrivals']])
    
    # Create sequences
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    
    return X, y, scaler, ts_df

def build_lstm_model(lookback):
    """Build LSTM model"""
    model = Sequential([
        LSTM(config.LSTM_PARAMS['units'], activation='relu', 
             return_sequences=True, input_shape=(lookback, 1)),
        Dropout(0.2),
        LSTM(50, activation='relu'),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1)
    ])
    
    optimizer = Adam(learning_rate=config.LSTM_PARAMS['learning_rate'])
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
    
    return model

def train_lstm_model(df):
    """Train LSTM model for time series forecasting"""
    print("\n" + "=" * 60)
    print("TRAINING LSTM MODEL")
    print("=" * 60)
    
    lookback = config.LSTM_PARAMS['lookback']
    
    # Prepare data
    X, y, scaler, ts_df = prepare_lstm_data(df, lookback)
    
    # Split data
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Lookback window: {lookback} months")
    
    # Build and train model
    print("\nBuilding LSTM model...")
    model = build_lstm_model(lookback)
    
    print("\nModel architecture:")
    model.summary()
    
    print("\nTraining LSTM...")
    history = model.fit(
        X_train, y_train,
        epochs=config.LSTM_PARAMS['epochs'],
        batch_size=config.LSTM_PARAMS['batch_size'],
        validation_data=(X_test, y_test),
        verbose=0
    )
    
    # Evaluate
    train_pred = model.predict(X_train, verbose=0)
    test_pred = model.predict(X_test, verbose=0)
    
    # Inverse transform
    train_pred = scaler.inverse_transform(train_pred)
    test_pred = scaler.inverse_transform(test_pred)
    y_train_inv = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    train_mae = mean_absolute_error(y_train_inv, train_pred)
    test_mae = mean_absolute_error(y_test_inv, test_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train_inv, train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test_inv, test_pred))
    
    print(f"\nTrain MAE: {train_mae:.2f}")
    print(f"Train RMSE: {train_rmse:.2f}")
    print(f"Test MAE: {test_mae:.2f}")
    print(f"Test RMSE: {test_rmse:.2f}")
    
    # Save model and scaler
    model.save(config.LSTM_MODEL_FILE)
    joblib.dump(scaler, config.SCALER_FILE)
    
    print(f"\nModel saved to: {config.LSTM_MODEL_FILE}")
    print(f"Scaler saved to: {config.SCALER_FILE}")
    
    return model, scaler, history

def forecast_future(prophet_model, lstm_model, scaler, df, months_ahead=12):
    """Generate future forecasts"""
    print("\n" + "=" * 60)
    print(f"GENERATING {months_ahead}-MONTH FORECAST")
    print("=" * 60)
    
    # Prophet forecast
    future = prophet_model.make_future_dataframe(periods=months_ahead, freq='MS')
    prophet_forecast = prophet_model.predict(future)
    
    # LSTM forecast
    ts_df = df.groupby('date')['arrivals'].sum().reset_index().sort_values('date')
    scaled_data = scaler.transform(ts_df[['arrivals']])
    
    lookback = config.LSTM_PARAMS['lookback']
    last_sequence = scaled_data[-lookback:]
    
    lstm_predictions = []
    current_sequence = last_sequence.copy()
    
    for _ in range(months_ahead):
        pred = lstm_model.predict(current_sequence.reshape(1, lookback, 1), verbose=0)
        lstm_predictions.append(pred[0, 0])
        current_sequence = np.append(current_sequence[1:], pred)
    
    lstm_predictions = scaler.inverse_transform(np.array(lstm_predictions).reshape(-1, 1))
    
    # Combine forecasts (ensemble)
    last_date = ts_df['date'].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                  periods=months_ahead, freq='MS')
    
    prophet_future = prophet_forecast[prophet_forecast['ds'] > last_date].head(months_ahead)
    
    ensemble_forecast = pd.DataFrame({
        'date': future_dates,
        'prophet_forecast': prophet_future['yhat'].values,
        'lstm_forecast': lstm_predictions.flatten(),
        'ensemble_forecast': (prophet_future['yhat'].values + lstm_predictions.flatten()) / 2
    })
    
    print("\nForecast generated:")
    print(ensemble_forecast)
    
    # Save forecast
    forecast_file = config.PROCESSED_DATA_DIR + '/forecast.csv'
    ensemble_forecast.to_csv(forecast_file, index=False)
    print(f"\nForecast saved to: {forecast_file}")
    
    return ensemble_forecast

if __name__ == '__main__':
    print("=" * 60)
    print("TOURISM FORECASTING MODEL TRAINING")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    df = load_processed_data()
    print(f"Loaded {len(df)} records")
    
    # Train Prophet
    prophet_model, prophet_forecast = train_prophet_model(df)
    
    # Train LSTM
    lstm_model, scaler, history = train_lstm_model(df)
    
    # Generate forecast
    forecast = forecast_future(prophet_model, lstm_model, scaler, df, months_ahead=12)
    
    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nModels saved:")
    print(f"  - Prophet: {config.PROPHET_MODEL_FILE}")
    print(f"  - LSTM: {config.LSTM_MODEL_FILE}")
    print(f"  - Scaler: {config.SCALER_FILE}")