# Stock Historical Data Viewer

An interactive web application to view and analyze historical stock pricing data using real-time data from Yahoo Finance.

## Features

### 📊 Multiple Chart Types
- **Line Chart**: Closing price with filled area
- **Candlestick Chart**: OHLC (Open, High, Low, Close) visualization
- **Volume Chart**: Trading volume with color-coded bars
- **Combined Chart**: Price and volume in synchronized subplots

### 🎯 Interactive Capabilities
- **Pan**: Click and drag to move around the chart
- **Zoom**: Scroll wheel or box select (click-drag)
- **Hover**: Automatic tooltips showing exact values
- **Reset**: Double-click to return to original view
- **Export**: Download charts as PNG images
- **Toggle**: Click legend items to show/hide data series

### 🔧 User Interface
- **Web-based**: Everything runs in your browser
- **Sidebar Controls**: Stock symbol, date ranges, candle intervals, chart types, display options
- **Candle/Bar Intervals**: Choose from 1 Hour, 4 Hours, 1 Day (default), or 1 Week
- **Moving Average Overlay**: Toggle on/off with customizable period (2-200)
- **Summary Statistics**: Key metrics and performance indicators
- **Data Download**: Export raw data to CSV
- **Auto-updates**: Charts refresh when you change settings

## Requirements

- Python 3.8+
- Internet connection (for fetching stock data)
- Modern web browser

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 🌐 Web App (Recommended)

Run the Streamlit web application:

```bash
streamlit run app.py
```

This will:
1. Start a local web server
2. Automatically open your browser to http://localhost:8501
3. Display the interactive web interface

**Using the app:**
1. Enter a stock symbol in the sidebar (e.g., AAPL, MSFT, TSLA)
2. Select a date range using presets or custom dates
3. Choose a chart type
4. Click "Fetch Data" or just change settings (auto-updates)
5. Interact with the chart: pan, zoom, hover for details

### 📟 Terminal Version (Legacy)

Run the command-line version:

```bash
python3 stock_viewer.py
```

This provides a hybrid terminal/browser experience where you enter inputs in the terminal and charts open in your browser.

## Examples

**Popular Stock Symbols:**
- **US Stocks**: AAPL (Apple), MSFT (Microsoft), GOOGL (Alphabet), TSLA (Tesla), AMZN (Amazon), NVDA (NVIDIA), META (Meta)
- **International**: VOD.L (London), 0700.HK (Hong Kong)
- **ETFs**: SPY, QQQ, VTI
- **Crypto**: BTC-USD, ETH-USD

## Technologies

- **Streamlit**: Web application framework
- **Plotly**: Interactive charting library
- **yfinance**: Yahoo Finance data API
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing

## Tips

- Try different chart types to visualize different aspects of the data
- Enable Moving Average to overlay trend lines - popular periods: 20 (short-term), 50 (medium-term), 200 (long-term)
- Combine different intervals with moving averages for multi-timeframe analysis
- Download data as CSV for further analysis in Excel or other tools
- Charts are cached for 5 minutes to improve performance
- The web app auto-updates when you change settings

## Data Source

Stock data is fetched in real-time from Yahoo Finance using the `yfinance` library.

## License

MIT License