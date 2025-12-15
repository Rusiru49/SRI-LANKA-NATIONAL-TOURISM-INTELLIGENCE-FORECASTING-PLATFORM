import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb
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

def create_time_features(df):
    """Create time-based features for XGBoost"""
    df = df.copy()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['year_month'] = df['year'] * 12 + df['month']
    
    # Cyclical encoding for seasonality
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['quarter_sin'] = np.sin(2 * np.pi * df['quarter'] / 4)
    df['quarter_cos'] = np.cos(2 * np.pi * df['quarter'] / 4)
    
    return df

def create_lag_features(df, target_col='arrivals', lags=[1, 2, 3, 6, 12]):
    """Create lag features"""
    df = df.copy()
    for lag in lags:
        df[f'lag_{lag}'] = df[target_col].shift(lag)
    
    # Rolling statistics
    df['rolling_mean_3'] = df[target_col].shift(1).rolling(window=3).mean()
    df['rolling_mean_6'] = df[target_col].shift(1).rolling(window=6).mean()
    df['rolling_mean_12'] = df[target_col].shift(1).rolling(window=12).mean()
    df['rolling_std_3'] = df[target_col].shift(1).rolling(window=3).std()
    df['rolling_std_6'] = df[target_col].shift(1).rolling(window=6).std()
    
    return df

def prepare_xgboost_data(df):
    """Prepare data for XGBoost model"""
    # Aggregate by date
    ts_df = df.groupby('date')['arrivals'].sum().reset_index()
    ts_df = ts_df.sort_values('date').reset_index(drop=True)
    
    # Create features
    ts_df = create_time_features(ts_df)
    ts_df = create_lag_features(ts_df, target_col='arrivals')
    
    # Drop rows with NaN (from lag features)
    ts_df = ts_df.dropna().reset_index(drop=True)
    
    return ts_df

def train_xgboost_model(df):
    """Train XGBoost model for time series forecasting"""
    print("\n" + "=" * 60)
    print("TRAINING XGBOOST MODEL")
    print("=" * 60)
    
    # Prepare data
    ts_df = prepare_xgboost_data(df)
    
    # Define features and target
    feature_cols = [col for col in ts_df.columns if col not in ['date', 'arrivals']]
    X = ts_df[feature_cols]
    y = ts_df['arrivals']
    
    # Split data (80/20)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Number of features: {len(feature_cols)}")
    
    # Define XGBoost parameters
    xgb_params = {
        'objective': 'reg:squarederror',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'early_stopping_rounds': 20
    }
    
    # Train model
    print("\nTraining XGBoost...")
    model = xgb.XGBRegressor(**xgb_params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=False
    )
    
    # Make predictions
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    # Evaluate
    train_mae = mean_absolute_error(y_train, train_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    
    print(f"\nTrain MAE: {train_mae:.2f}")
    print(f"Train RMSE: {train_rmse:.2f}")
    print(f"Test MAE: {test_mae:.2f}")
    print(f"Test RMSE: {test_rmse:.2f}")
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(feature_importance.head(10).to_string(index=False))
    
    # Save model
    xgb_model_file = config.PROPHET_MODEL_FILE.replace('prophet', 'xgboost')
    joblib.dump(model, xgb_model_file)
    
    # Save feature columns for future use
    feature_cols_file = config.PROCESSED_DATA_DIR + '/xgb_feature_cols.pkl'
    joblib.dump(feature_cols, feature_cols_file)
    
    print(f"\nModel saved to: {xgb_model_file}")
    print(f"Feature columns saved to: {feature_cols_file}")
    
    return model, feature_cols, ts_df

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

def forecast_future(xgb_model, feature_cols, lstm_model, scaler, df, months_ahead=12):
    """Generate future forecasts"""
    print("\n" + "=" * 60)
    print(f"GENERATING {months_ahead}-MONTH FORECAST")
    print("=" * 60)
    
    # Prepare historical data
    ts_df = df.groupby('date')['arrivals'].sum().reset_index().sort_values('date')
    last_date = ts_df['date'].max()
    
    # Generate future dates
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                  periods=months_ahead, freq='MS')
    
    # XGBoost forecast (recursive)
    xgb_predictions = []
    forecast_df = ts_df.copy()
    
    for future_date in future_dates:
        # Create features for the next month
        next_row = pd.DataFrame({'date': [future_date], 'arrivals': [np.nan]})
        forecast_df = pd.concat([forecast_df, next_row], ignore_index=True)
        forecast_df = create_time_features(forecast_df)
        forecast_df = create_lag_features(forecast_df, target_col='arrivals')
        
        # Get the last row features
        last_row = forecast_df.iloc[-1:][feature_cols]
        
        # Predict
        pred = xgb_model.predict(last_row)[0]
        xgb_predictions.append(pred)
        
        # Update the forecast_df with prediction for next iteration
        forecast_df.loc[forecast_df.index[-1], 'arrivals'] = pred
    
    # LSTM forecast
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
    
    # Create ensemble forecast
    ensemble_forecast = pd.DataFrame({
        'date': future_dates,
        'xgboost_forecast': xgb_predictions,
        'lstm_forecast': lstm_predictions.flatten(),
        'ensemble_forecast': np.mean([xgb_predictions, lstm_predictions.flatten()], axis=0)
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
    
    # Train XGBoost
    xgb_model, feature_cols, ts_df = train_xgboost_model(df)
    
    # Train LSTM
    lstm_model, scaler, history = train_lstm_model(df)
    
    # Generate forecast
    forecast = forecast_future(xgb_model, feature_cols, lstm_model, scaler, df, months_ahead=12)
    
    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nModels saved:")
    print(f"  - XGBoost: {config.PROPHET_MODEL_FILE.replace('prophet', 'xgboost')}")
    print(f"  - LSTM: {config.LSTM_MODEL_FILE}")
    print(f"  - Scaler: {config.SCALER_FILE}")