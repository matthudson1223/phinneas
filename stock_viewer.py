#!/usr/bin/env python3
"""
Stock Historical Data Viewer
An interactive tool to view historical stock pricing data using yfinance.
"""

import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import sys


def get_stock_symbol():
    """Prompt user for a valid stock symbol."""
    while True:
        symbol = input("\nEnter stock symbol (e.g., AAPL, MSFT, TSLA) or 'q' to quit: ").strip().upper()
        if symbol.lower() == 'q':
            return None
        if symbol:
            return symbol
        print("Error: Stock symbol cannot be empty. Please try again.")


def get_date_range():
    """Prompt user for date range with validation."""
    print("\nDate Range Options:")
    print("1. Last week")
    print("2. Last month")
    print("3. Last 3 months")
    print("4. Last 6 months")
    print("5. Last year")
    print("6. Year to date")
    print("7. Custom date range")

    while True:
        choice = input("\nSelect option (1-7): ").strip()

        end_date = datetime.now()

        if choice == '1':
            start_date = end_date - timedelta(days=7)
            return start_date, end_date
        elif choice == '2':
            start_date = end_date - timedelta(days=30)
            return start_date, end_date
        elif choice == '3':
            start_date = end_date - timedelta(days=90)
            return start_date, end_date
        elif choice == '4':
            start_date = end_date - timedelta(days=180)
            return start_date, end_date
        elif choice == '5':
            start_date = end_date - timedelta(days=365)
            return start_date, end_date
        elif choice == '6':
            start_date = datetime(end_date.year, 1, 1)
            return start_date, end_date
        elif choice == '7':
            return get_custom_date_range()
        else:
            print("Error: Invalid option. Please select 1-7.")


def get_custom_date_range():
    """Get custom date range from user."""
    print("\nEnter dates in YYYY-MM-DD format")

    while True:
        try:
            start_input = input("Start date: ").strip()
            start_date = datetime.strptime(start_input, "%Y-%m-%d")
            break
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2023-01-01)")

    while True:
        try:
            end_input = input("End date: ").strip()
            end_date = datetime.strptime(end_input, "%Y-%m-%d")

            if end_date < start_date:
                print("Error: End date must be after start date.")
                continue

            if end_date > datetime.now():
                print("Warning: End date is in the future. Using today's date.")
                end_date = datetime.now()

            break
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2023-12-31)")

    return start_date, end_date


def fetch_stock_data(symbol, start_date, end_date):
    """Fetch historical stock data using yfinance."""
    try:
        print(f"\nFetching data for {symbol}...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date.strftime("%Y-%m-%d"),
                            end=end_date.strftime("%Y-%m-%d"))

        if data.empty:
            print(f"Error: No data found for symbol '{symbol}'. Please check the symbol and try again.")
            return None

        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def display_summary(symbol, data):
    """Display summary statistics of the stock data."""
    print(f"\n{'='*60}")
    print(f"Summary for {symbol}")
    print(f"{'='*60}")
    print(f"Period: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"Trading days: {len(data)}")
    print(f"\nPrice Statistics:")
    print(f"  Opening Price:  ${data['Open'].iloc[0]:.2f} (first day)")
    print(f"  Closing Price:  ${data['Close'].iloc[-1]:.2f} (last day)")
    print(f"  Highest Price:  ${data['High'].max():.2f}")
    print(f"  Lowest Price:   ${data['Low'].min():.2f}")
    print(f"  Average Close:  ${data['Close'].mean():.2f}")

    price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
    percent_change = (price_change / data['Close'].iloc[0]) * 100
    print(f"\nPrice Change: ${price_change:.2f} ({percent_change:+.2f}%)")

    print(f"\nVolume Statistics:")
    print(f"  Average Volume: {data['Volume'].mean():,.0f}")
    print(f"  Total Volume:   {data['Volume'].sum():,.0f}")
    print(f"{'='*60}\n")


def choose_chart_type():
    """Let user choose the type of chart to display."""
    print("\nChart Type Options:")
    print("1. Line chart (Close price)")
    print("2. Candlestick chart")
    print("3. Volume chart")
    print("4. All charts (combined view)")

    while True:
        choice = input("\nSelect chart type (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("Error: Invalid option. Please select 1-4.")


def plot_line_chart(symbol, data):
    """Plot a simple line chart of closing prices."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data.index, data['Close'], linewidth=2, color='#2E86AB')
    ax.fill_between(data.index, data['Close'], alpha=0.3, color='#A23B72')

    ax.set_title(f'{symbol} - Closing Price History', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_candlestick_chart(symbol, data):
    """Plot a candlestick chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Calculate width for candlesticks
    width = 0.6
    width2 = 0.1

    # Colors for up and down days
    up = data[data['Close'] >= data['Open']]
    down = data[data['Close'] < data['Open']]

    # Plot up prices
    ax.bar(up.index, up['Close'] - up['Open'], width, bottom=up['Open'], color='#06A77D', label='Up')
    ax.bar(up.index, up['High'] - up['Close'], width2, bottom=up['Close'], color='#06A77D')
    ax.bar(up.index, up['Low'] - up['Open'], width2, bottom=up['Open'], color='#06A77D')

    # Plot down prices
    ax.bar(down.index, down['Close'] - down['Open'], width, bottom=down['Open'], color='#D62828', label='Down')
    ax.bar(down.index, down['High'] - down['Open'], width2, bottom=down['Open'], color='#D62828')
    ax.bar(down.index, down['Low'] - down['Close'], width2, bottom=down['Close'], color='#D62828')

    ax.set_title(f'{symbol} - Candlestick Chart', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_volume_chart(symbol, data):
    """Plot volume chart."""
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#06A77D' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#D62828'
              for i in range(len(data))]

    ax.bar(data.index, data['Volume'], color=colors, alpha=0.7)
    ax.set_title(f'{symbol} - Trading Volume', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Volume', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_combined_chart(symbol, data):
    """Plot combined chart with price and volume."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10),
                                    gridspec_kw={'height_ratios': [3, 1]})

    # Price chart
    ax1.plot(data.index, data['Close'], linewidth=2, color='#2E86AB', label='Close')
    ax1.plot(data.index, data['Open'], linewidth=1, color='#F77F00', alpha=0.7, label='Open')
    ax1.fill_between(data.index, data['Low'], data['High'], alpha=0.2, color='#A23B72', label='High/Low Range')

    ax1.set_title(f'{symbol} - Price and Volume History', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Volume chart
    colors = ['#06A77D' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#D62828'
              for i in range(len(data))]
    ax2.bar(data.index, data['Volume'], color=colors, alpha=0.7)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')

    # Format x-axis
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_data(symbol, data):
    """Visualize the stock data based on user choice."""
    chart_type = choose_chart_type()

    if chart_type == '1':
        plot_line_chart(symbol, data)
    elif chart_type == '2':
        plot_candlestick_chart(symbol, data)
    elif chart_type == '3':
        plot_volume_chart(symbol, data)
    elif chart_type == '4':
        plot_combined_chart(symbol, data)


def main():
    """Main program loop."""
    print("="*60)
    print("Stock Historical Data Viewer".center(60))
    print("="*60)
    print("\nView historical pricing data for any stock using yfinance")

    while True:
        # Get stock symbol
        symbol = get_stock_symbol()
        if symbol is None:
            print("\nThank you for using Stock Historical Data Viewer!")
            sys.exit(0)

        # Get date range
        start_date, end_date = get_date_range()

        # Fetch data
        data = fetch_stock_data(symbol, start_date, end_date)

        if data is not None:
            # Display summary
            display_summary(symbol, data)

            # Visualize data
            visualize_data(symbol, data)

            # Ask if user wants to continue
            while True:
                continue_choice = input("\nWould you like to view another stock? (y/n): ").strip().lower()
                if continue_choice in ['y', 'yes']:
                    break
                elif continue_choice in ['n', 'no']:
                    print("\nThank you for using Stock Historical Data Viewer!")
                    sys.exit(0)
                else:
                    print("Please enter 'y' or 'n'.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
