# 🇱🇰 Sri Lanka National Tourism Intelligence & Forecasting Platform

An end-to-end data-driven tourism analytics and forecasting platform designed for policymakers, researchers, and tourism stakeholders in Sri Lanka.

## 📋 Overview

This platform combines real-time data integration, advanced machine learning, and interactive visualizations to provide comprehensive insights into Sri Lanka's tourism industry.

### Key Features

- 📊 **Interactive Dashboards** - Streamlit-based dashboards with KPIs, year-over-year comparisons, regional insights, and seasonal trend analysis
- 🤖 **AI-Based Forecasting** - XGBoost and LSTM models for predicting tourist arrivals
- 🗂️ **Automated Data Processing** - Pipeline with cleaning, feature engineering, and outlier handling
- 📈 **Advanced Visualizations** - Plotly interactive charts for data exploration
- 🌐 **Real-Time Integration** - Weather, hotels, flights, and travel advisory data

## 👨‍💻 Author

**Rusiru Fernando**  
3rd Year Undergraduate – Data Science Specialization  
Sri Lanka Institute of Information Technology (SLIIT)

## 📄 License

MIT License

## 🏗️ Project Structure

```
SRI-LANKA-NATIONAL-TOURISM-INTELLIGENCE-FORECASTING-PLATFORM/
├── backend/                          # Backend API & ML Models
│   ├── app.py                       # Flask API Server
│   ├── config.py                    # Configuration Management
│   ├── api_config.py                # External API Integration
│   ├── api_services.py              # Service Layer
│   ├── data_collection.py           # Data Generation & Collection
│   ├── preprocessing.py             # Data Preprocessing Pipeline
│   ├── modeling.py                  # Machine Learning Models
│   └── requirements.txt             # Backend dependencies
├── pages/                           # Streamlit page modules
│   ├── overview_page.py            # Dashboard Overview
│   ├── trends_page.py              # Trend Analysis
│   ├── ai_forecast.py              # AI Forecasting
│   ├── country_insight.py          # Country Analysis
│   └── weather_tourism.py          # Real-Time Information
├── utils/                           # Utility functions
│   ├── data_loader.py              # Data loading and API calls
│   └── styles.py                   # Custom CSS styling
├── scripts/                         # Setup & execution scripts
│   ├── setup.sh                    # Initial setup script
│   └── run.sh                      # Runtime execution script
├── streamlit_app.py                # Main Streamlit application
├── requirements.txt                # Frontend/Main dependencies
└── sri-lanka-tourism-dashboard.css # Custom styling
```

## 🔧 Backend Components

### Flask API Server (`app.py`)
RESTful API backend serving the Streamlit frontend with CORS support.

**Key Endpoints:**
- `GET /api/health` - Health check endpoint returning model status
- `GET /api/overview` - Overall statistics (total arrivals, top countries, date ranges)
- `GET /api/monthly-trends` - Monthly arrival trends

**Models Loaded:**
- XGBoost model for time series forecasting
- LSTM neural network model
- MinMaxScaler for data normalization

### Configuration Management (`config.py`)
- **Base Paths**: Data directories (raw, processed, models)
- **API Configuration**: SLTDA base URL, weather API endpoints
- **Sri Lankan Holidays**: Hard-coded holiday mapping (2020-2024)
- **Seasons Definition**: Southwest/Northeast Monsoon periods

### External API Integration (`api_config.py`)
Manages multiple external tourism data sources:
- **OpenWeatherMap API** - Weather data for Sri Lankan cities
- **Booking.com API** (via RapidAPI) - Hotel information
- **AviationStack API** - Flight data
- **Amadeus API** - Travel insights
- **Exchange Rate API** - Currency conversions
- **Travel Advisory API** - Safety information

**Supported Cities**: Colombo, Kandy, Galle, Jaffna, Nuwara Eliya, Anuradhapura, Trincomalee

### Service Layer (`api_services.py`)
Implements service classes with API key management:
- `WeatherService` - Current weather & 5-day forecasts
- `HotelService` - Hotel search integration
- `FlightService` - Flight data aggregation
- `ExchangeRateService` - Real-time currency data
- `TravelAdvisoryService` - Travel safety alerts

All services use `@st.cache_data` decorator for performance optimization.

### Data Generation & Collection (`data_collection.py`)
- **Sample Data Generation**: Creates realistic tourism data (2018-2025)
- **Seasonality Modeling**:
  - High season (Dec-Mar): 1.8x multiplier
  - Low season (May-Sep): 0.6x multiplier
- **Historical Events Modeling**:
  - COVID-19 impact (2020-2021)
  - Economic crisis (2022)
  - Recovery phase (2023-2024)
- **15 Top Source Countries**: Simulated arrivals with country-specific variations

### Data Preprocessing Pipeline (`preprocessing.py`)
Transforms raw data through multiple stages:

**Feature Engineering:**
- Seasonal features (Southwest/Northeast Monsoon classification)
- Holiday indicators & proximity features
- Country region grouping with one-hot encoding
- Temporal features: quarter, day of year, week of year
- Cyclical encoding (month sine/cosine transformations)

**Data Handling:**
- Forward fill + backward fill for missing values
- Outlier management
- Regional grouping (Asia, Europe, Americas, Middle East, Oceania)

### Machine Learning Models (`modeling.py`)
Implements two forecasting approaches:

**Time Features:**
- Year, month, quarter, year-month composite
- Cyclical sine/cosine encoding for seasonality

**Lag Features:**
- Autoregressive lags: [1, 2, 3, 6, 12 months]
- Rolling statistics: mean & std dev (3, 6, 12-month windows)

**XGBoost Model:**
- Gradient boosting for time series
- Hyperparameter tuning for optimal performance
- Feature importance analysis

**LSTM Model:**
- Sequence-to-sequence neural network
- Handles temporal dependencies
- Trained with MinMaxScaler normalization

## 🖥️ Frontend Components (Streamlit)

### Main Application (`streamlit_app.py`)
- **Page Config**: Wide layout with expanded sidebar
- **Custom Styling**: CSS-based glass-morphism design with gradient backgrounds
- **Dynamic Navigation**: Custom tab-based navigation system
- **API Status Checking**: Displays which external APIs are configured and active

### Dashboard Pages

#### Overview Page (`overview_page.py`)
- KPI Metrics Display (total arrivals, country breakdown, monthly averages)
- Time Series Analysis with interactive Plotly charts
- Regional Distribution (bar/pie charts)
- Yearly Comparison metrics

#### Trend Analysis (`trends_page.py`)
- Monthly arrivals trend with fill area
- Seasonality patterns (average by month)
- Year-over-year comparison tables
- Cyclical patterns visualization

#### AI Forecasting (`ai_forecast.py`)
- Ensemble model explanation (XGBoost + LSTM)
- 12-month projection metrics
- Peak/low forecast indicators
- Historical vs. forecast comparison chart
- Model confidence intervals

#### Country Insights (`country_insight.py`)
- Top 15 source countries bar chart
- Country data table (top 20)
- Regional breakdown pie chart
- Regional performance metrics
- Color-coded by arrival volume

#### Real-Time Information (`weather_tourism.py`)
Five integrated tabs:
- 🌡️ **Weather** - Current conditions + 5-day forecast
- 🏨 **Hotels** - Hotel search with date/guest filters
- ✈️ **Flights** - Flight information & schedules
- 💱 **Exchange Rates** - Currency conversions
- ⚠️ **Travel Advisory** - Safety alerts by country

### Utility Modules

**Data Loader (`utils/data_loader.py`)**
- `fetch_data(endpoint)` - API calls with caching (5 min TTL)
- `load_local_data()` - Direct CSV loading
- `format_number()` - Thousands separator formatting

**Styles (`utils/styles.py`)**
- Glass-card effect with blur backdrop
- Animated gradient backgrounds
- Enhanced metrics with hover effects
- Dark theme optimized colors

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+

### Automated Setup

```bash
# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This script will:
1. Verify Python and Node.js installations
2. Create Python virtual environment
3. Install backend dependencies
4. Run data collection script
5. Execute preprocessing pipeline
6. Train ML models (XGBoost + LSTM)

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Application

### Automated Execution
```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

### Manual Execution

**Start Backend:**
```bash
cd backend
python app.py
```
Backend runs on `http://localhost:5000`

**Start Frontend:**
```bash
streamlit run streamlit_app.py
```
Frontend runs on `http://localhost:8501`

## 📦 Dependencies

### Backend Requirements
```
Flask==3.0.3
Flask-CORS==4.0.1
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.5.1
prophet==1.1.5
tensorflow==2.16.2
xgboost
plotly==5.22.0
requests==2.32.3
joblib==1.4.2
```

### Frontend Requirements
```
streamlit==1.35.0
plotly==5.22.0
pandas==2.2.2
numpy==1.26.4
requests==2.32.3
```

## 🔌 Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit 1.35.0 |
| Backend API | Flask 3.0.3 |
| Data Processing | Pandas 2.2.2, NumPy 1.26.4 |
| Machine Learning | XGBoost, TensorFlow 2.16.2 (LSTM) |
| Time Series | Prophet 1.1.5 |
| Visualizations | Plotly 5.22.0 |
| Data Science | Scikit-learn 1.5.1 |
| API Integration | Requests 2.32.3 |
| Model Persistence | Joblib 1.4.2 |

## 📊 Data Pipeline

```
Raw Data → Collection → Preprocessing → Feature Engineering → Model Training → API Serving → Dashboard Visualization
   ↓            ↓              ↓               ↓                   ↓             ↓              ↓
CSV/APIs   Sample Gen    Clean/Normalize  Temporal/Seasonal  XGBoost+LSTM  Flask REST  Streamlit UI
```

## 🎯 Use Cases & Applications

- **Tourism Demand Forecasting** - Predict future visitor arrivals
- **Policy Planning** - Evidence-based decision making for tourism authorities
- **Seasonal Analysis** - Understand monsoon and holiday impacts on tourism
- **Country Insights** - Source market analysis for targeted marketing
- **Real-time Conditions** - Weather, flights, and hotel availability integration
- **Academic Research** - Data science portfolio and research project

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please contact:
- **Rusiru Fernando**
- **Institution**: SLIIT, Sri Lanka
- **Program**: Data Science Specialization (3rd Year)

## 📝 Citation

If you use this project in your research or work, please cite:

```
Fernando, R. (2025). Sri Lanka National Tourism Intelligence & Forecasting Platform.
Sri Lanka Institute of Information Technology.
```

---

**Made with ❤️ for Sri Lanka's Tourism Industry**
