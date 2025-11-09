# Stock Historical Data Viewer

An interactive Python program that uses yfinance to view and visualize historical stock pricing data.

## Features

- Interactive command-line interface
- Multiple predefined date range options (week, month, 3 months, 6 months, year, YTD)
- Custom date range selection
- Multiple visualization types:
  - Line chart (closing prices)
  - Candlestick chart
  - Volume chart
  - Combined chart (price + volume)
- Comprehensive stock statistics and summaries
- Color-coded charts for better readability

## Requirements

- Python 3.7 or higher
- WSL Ubuntu Linux (tested on version 5.15)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd phinneas
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the program:
```bash
python3 stock_viewer.py
```

Or make it executable and run directly:
```bash
chmod +x stock_viewer.py
./stock_viewer.py
```

### Interactive Steps

1. **Enter Stock Symbol**: Type any valid stock ticker (e.g., AAPL, MSFT, TSLA, GOOGL)
2. **Select Date Range**: Choose from preset options or enter a custom date range
3. **View Summary**: Review key statistics about the stock's performance
4. **Choose Chart Type**: Select how you want to visualize the data
5. **Repeat or Exit**: View another stock or quit the program

## Examples

### Quick Start Example
```bash
$ python3 stock_viewer.py

Enter stock symbol: AAPL
Select date range: 2 (Last month)
Select chart type: 4 (All charts)
```

### Supported Stock Symbols

Any stock symbol available on Yahoo Finance, including:
- US Stocks: AAPL, MSFT, GOOGL, AMZN, TSLA, etc.
- International: VOD.L (London), 0700.HK (Hong Kong), etc.
- ETFs: SPY, QQQ, VTI, etc.
- Crypto: BTC-USD, ETH-USD, etc.

## Dependencies

- **yfinance**: Fetches stock data from Yahoo Finance
- **matplotlib**: Creates visualizations and charts
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical operations

## Troubleshooting

### Display Issues on WSL

If you encounter issues displaying charts on WSL, ensure you have X server configured:

1. Install VcXsrv or X410 on Windows
2. Set the DISPLAY variable:
```bash
export DISPLAY=:0
```

Alternatively, use WSLg (built-in GUI support in WSL2 on Windows 11).

### Network Issues

If data fetching fails, check your internet connection and ensure you can access Yahoo Finance.

## License

MIT License