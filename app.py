#!/usr/bin/env python3
"""
Stock Historical Data Viewer - Streamlit Web App
An interactive web application to view historical stock pricing data using yfinance and Plotly.
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Stock Historical Data Viewer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📈 Stock Historical Data Viewer")
st.markdown("Interactive stock price visualization with pan, zoom, and hover features")

# Sidebar for inputs
st.sidebar.header("Settings")

# Stock symbol input
symbol = st.sidebar.text_input(
    "Stock Symbol",
    value="AAPL",
    help="Enter a stock ticker symbol (e.g., AAPL, MSFT, TSLA)"
).upper()

# Date range selection
st.sidebar.subheader("Date Range")

# Preset date ranges
preset_options = {
    "Last Week": 7,
    "Last Month": 30,
    "Last 3 Months": 90,
    "Last 6 Months": 180,
    "Last Year": 365,
    "Year to Date": None,
    "Custom": 0
}

preset_choice = st.sidebar.selectbox(
    "Select Preset",
    options=list(preset_options.keys()),
    index=1  # Default to "Last Month"
)

end_date = datetime.now()
start_date = end_date - timedelta(days=30)  # Default

# Calculate dates based on preset
if preset_choice == "Year to Date":
    start_date = datetime(end_date.year, 1, 1)
elif preset_choice == "Custom":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=end_date - timedelta(days=30),
            max_value=end_date
        )
        start_date = datetime.combine(start_date, datetime.min.time())
    with col2:
        end_date_input = st.date_input(
            "End Date",
            value=end_date,
            max_value=datetime.now()
        )
        end_date = datetime.combine(end_date_input, datetime.min.time())
else:
    days = preset_options[preset_choice]
    if days:
        start_date = end_date - timedelta(days=days)

# Interval selection
st.sidebar.subheader("Candle/Bar Interval")
interval_options = {
    "1 Hour": "1h",
    "4 Hours": "4h",
    "1 Day": "1d",
    "1 Week": "1wk"
}

interval_choice = st.sidebar.selectbox(
    "Time Interval",
    options=list(interval_options.keys()),
    index=2,  # Default to "1 Day"
    help="Select the timeframe for each candle/bar"
)

interval = interval_options[interval_choice]

# Interval validation warning
days_diff = (end_date - start_date).days
if interval in ["1h", "2h", "4h"]:
    if days_diff > 730:  # 2 years
        st.sidebar.warning(f"⚠️ {interval_choice} data is limited to last 730 days")
    elif days_diff > 60:
        st.sidebar.info(f"ℹ️ Using {interval_choice} over {days_diff} days may result in many data points")

# Chart type selection
st.sidebar.subheader("Chart Type")
chart_type = st.sidebar.radio(
    "Select Visualization",
    options=["Line Chart", "Candlestick Chart", "Volume Chart", "Combined Chart"],
    index=0
)

# Additional options
st.sidebar.subheader("Display Options")
show_summary = st.sidebar.checkbox("Show Summary Statistics", value=True)

# Features section
st.sidebar.subheader("Features")

# Initialize features in session state
if 'features' not in st.session_state:
    st.session_state['features'] = []

# Display current features
if len(st.session_state['features']) == 0:
    st.sidebar.info("No features added yet")
else:
    for idx, feature in enumerate(st.session_state['features']):
        with st.sidebar.expander(f"📊 {feature['name']}", expanded=True):
            if feature['type'] == 'moving_average':
                # Period input
                period = st.number_input(
                    "Period",
                    min_value=2,
                    max_value=200,
                    value=feature.get('period', 20),
                    step=1,
                    key=f"ma_period_{idx}",
                    help="Number of periods for calculation"
                )

                # Smoothness (MA type) selector
                ma_type = st.selectbox(
                    "Smoothness",
                    options=["SMA (Simple)", "EMA (Exponential)", "WMA (Weighted)"],
                    index=["SMA", "EMA", "WMA"].index(feature.get('ma_type', 'SMA')),
                    key=f"ma_type_{idx}",
                    help="Type of moving average - affects smoothness"
                )

                # Update feature
                st.session_state['features'][idx]['period'] = period
                st.session_state['features'][idx]['ma_type'] = ma_type.split()[0]  # Extract SMA, EMA, or WMA

                # Remove button
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state['features'].pop(idx)
                    st.rerun()

            elif feature['type'] == 'rsi':
                # Period input for RSI
                rsi_period = st.number_input(
                    "Period",
                    min_value=2,
                    max_value=50,
                    value=feature.get('period', 14),
                    step=1,
                    key=f"rsi_period_{idx}",
                    help="Number of periods for RSI calculation (typical: 14)"
                )

                # Update feature
                st.session_state['features'][idx]['period'] = rsi_period

                # Remove button
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state['features'].pop(idx)
                    st.rerun()

# Add new feature button
st.sidebar.markdown("---")
feature_to_add = st.sidebar.selectbox(
    "Add New Feature",
    options=["None", "Moving Average", "RSI"],
    key="feature_selector"
)

if st.sidebar.button("➕ Add Feature"):
    if feature_to_add == "Moving Average":
        new_feature = {
            'type': 'moving_average',
            'name': 'Moving Average',
            'period': 20,
            'ma_type': 'SMA'
        }
        st.session_state['features'].append(new_feature)
        st.rerun()
    elif feature_to_add == "RSI":
        new_feature = {
            'type': 'rsi',
            'name': 'RSI',
            'period': 14
        }
        st.session_state['features'].append(new_feature)
        st.rerun()
    elif feature_to_add == "None":
        st.sidebar.warning("Please select a feature type")


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(symbol, start_date, end_date, interval="1d"):
    """Fetch historical stock data using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval=interval
        )

        if data.empty:
            return None

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


def calculate_moving_average(data, period, ma_type='SMA'):
    """
    Calculate moving average.

    Args:
        data: DataFrame with price data
        period: Number of periods for MA calculation
        ma_type: Type of MA - 'SMA' (Simple), 'EMA' (Exponential), or 'WMA' (Weighted)

    Returns:
        Pandas Series with MA values
    """
    if ma_type == 'SMA':
        # Simple Moving Average
        return data['Close'].rolling(window=period).mean()
    elif ma_type == 'EMA':
        # Exponential Moving Average (more weight to recent prices)
        return data['Close'].ewm(span=period, adjust=False).mean()
    elif ma_type == 'WMA':
        # Weighted Moving Average (linear weights)
        weights = np.arange(1, period + 1)
        return data['Close'].rolling(window=period).apply(
            lambda prices: np.dot(prices, weights) / weights.sum(), raw=True
        )
    else:
        # Default to SMA
        return data['Close'].rolling(window=period).mean()


def calculate_rsi(data, period=14):
    """
    Calculate Relative Strength Index (RSI).

    Args:
        data: DataFrame with price data
        period: Number of periods for RSI calculation (default: 14)

    Returns:
        Pandas Series with RSI values (0-100)
    """
    # Calculate price changes
    delta = data['Close'].diff()

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    # Calculate average gain and loss using EMA (Wilder's smoothing)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def display_summary_stats(symbol, data):
    """Display summary statistics."""
    st.subheader(f"📊 Summary for {symbol}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Current Price",
            f"${data['Close'].iloc[-1]:.2f}",
            f"{((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100):+.2f}%"
        )

    with col2:
        st.metric(
            "High",
            f"${data['High'].max():.2f}"
        )

    with col3:
        st.metric(
            "Low",
            f"${data['Low'].min():.2f}"
        )

    with col4:
        st.metric(
            "Avg Volume",
            f"{data['Volume'].mean():,.0f}"
        )

    # Additional details in expandable section
    with st.expander("📈 Detailed Statistics"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Price Statistics:**")
            st.write(f"Period: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
            st.write(f"Trading Days: {len(data)}")
            st.write(f"Opening Price: ${data['Open'].iloc[0]:.2f}")
            st.write(f"Closing Price: ${data['Close'].iloc[-1]:.2f}")
            st.write(f"Average Close: ${data['Close'].mean():.2f}")

        with col2:
            price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
            percent_change = (price_change / data['Close'].iloc[0]) * 100

            st.write("**Performance:**")
            st.write(f"Price Change: ${price_change:+.2f}")
            st.write(f"Percent Change: {percent_change:+.2f}%")
            st.write(f"Volatility (Std): ${data['Close'].std():.2f}")
            st.write(f"Total Volume: {data['Volume'].sum():,.0f}")


def create_line_chart(symbol, data, interval_label="1 Day", features=None):
    """Create line chart with Plotly."""
    # Check if RSI features exist
    has_rsi = any(f['type'] == 'rsi' for f in features) if features else False

    if has_rsi:
        # Create subplots for price + RSI
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'{symbol} - Closing Price ({interval_label})', 'RSI')
        )
        price_row = 1
    else:
        # Single plot for price only
        fig = go.Figure()
        price_row = None

    # Add price trace
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#2E86AB', width=2),
        fill='tozeroy',
        fillcolor='rgba(162, 59, 114, 0.3)',
        hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br><b>Price</b>: $%{y:.2f}<extra></extra>'
    ), row=price_row, col=1 if has_rsi else None)

    # Add features
    if features:
        colors = ['#FF6B35', '#4ECDC4', '#FFE66D', '#FF6B9D']
        ma_idx = 0
        for feature in features:
            if feature['type'] == 'moving_average':
                ma = calculate_moving_average(data, feature['period'], feature['ma_type'])
                color = colors[ma_idx % len(colors)]
                ma_idx += 1
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=ma,
                    mode='lines',
                    name=f"{feature['ma_type']}-{feature['period']}",
                    line=dict(color=color, width=2),
                    hovertemplate=f"<b>{feature['ma_type']}-{feature['period']}</b>: $%{{y:.2f}}<extra></extra>"
                ), row=price_row, col=1 if has_rsi else None)
            elif feature['type'] == 'rsi':
                rsi = calculate_rsi(data, feature['period'])
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=rsi,
                    mode='lines',
                    name=f"RSI-{feature['period']}",
                    line=dict(color='#9B59B6', width=2),
                    hovertemplate=f"<b>RSI-{feature['period']}</b>: %{{y:.2f}}<extra></extra>"
                ), row=2, col=1)

                # Add reference lines at 30 and 70
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)

    # Update layout
    if has_rsi:
        fig.update_xaxes(title_text='Date', row=2, col=1)
        fig.update_yaxes(title_text='Price ($)', row=1, col=1)
        fig.update_yaxes(title_text='RSI', range=[0, 100], row=2, col=1)
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=700,
            showlegend=True
        )
    else:
        fig.update_layout(
            title=f'{symbol} - Closing Price History ({interval_label} Intervals)',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            hovermode='x unified',
            template='plotly_white',
            height=600
        )

    return fig


def create_candlestick_chart(symbol, data, interval_label="1 Day", features=None):
    """Create candlestick chart with Plotly."""
    # Check if RSI features exist
    has_rsi = any(f['type'] == 'rsi' for f in features) if features else False

    if has_rsi:
        # Create subplots for price + RSI
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'{symbol} - Candlestick ({interval_label})', 'RSI')
        )
        price_row = 1
    else:
        # Single plot for price only
        fig = go.Figure()
        price_row = None

    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='OHLC',
        increasing_line_color='#06A77D',
        decreasing_line_color='#D62828'
    ), row=price_row, col=1 if has_rsi else None)

    # Add features
    if features:
        colors = ['#FF6B35', '#4ECDC4', '#FFE66D', '#FF6B9D']
        ma_idx = 0
        for feature in features:
            if feature['type'] == 'moving_average':
                ma = calculate_moving_average(data, feature['period'], feature['ma_type'])
                color = colors[ma_idx % len(colors)]
                ma_idx += 1
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=ma,
                    mode='lines',
                    name=f"{feature['ma_type']}-{feature['period']}",
                    line=dict(color=color, width=2),
                    hovertemplate=f"<b>{feature['ma_type']}-{feature['period']}</b>: $%{{y:.2f}}<extra></extra>"
                ), row=price_row, col=1 if has_rsi else None)
            elif feature['type'] == 'rsi':
                rsi = calculate_rsi(data, feature['period'])
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=rsi,
                    mode='lines',
                    name=f"RSI-{feature['period']}",
                    line=dict(color='#9B59B6', width=2),
                    hovertemplate=f"<b>RSI-{feature['period']}</b>: %{{y:.2f}}<extra></extra>"
                ), row=2, col=1)

                # Add reference lines at 30 and 70
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)

    # Update layout
    if has_rsi:
        fig.update_xaxes(title_text='Date', row=2, col=1)
        fig.update_yaxes(title_text='Price ($)', row=1, col=1)
        fig.update_yaxes(title_text='RSI', range=[0, 100], row=2, col=1)
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=700,
            showlegend=True
        )
    else:
        fig.update_layout(
            title=f'{symbol} - Candlestick Chart ({interval_label} Candles)',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=600
        )

    return fig


def create_volume_chart(symbol, data, interval_label="1 Day"):
    """Create volume chart with Plotly."""
    fig = go.Figure()

    colors = ['#06A77D' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#D62828'
              for i in range(len(data))]

    fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        marker_color=colors,
        opacity=0.7,
        name='Volume',
        hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br><b>Volume</b>: %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title=f'{symbol} - Trading Volume ({interval_label} Bars)',
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_white',
        height=600
    )

    return fig


def create_combined_chart(symbol, data, interval_label="1 Day", features=None):
    """Create combined price and volume chart with Plotly."""
    # Check if RSI features exist
    has_rsi = any(f['type'] == 'rsi' for f in features) if features else False

    if has_rsi:
        # 3 subplots: price, volume, RSI
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=(
                f'{symbol} - Price History ({interval_label} Intervals)',
                f'Trading Volume ({interval_label} Bars)',
                'RSI'
            )
        )
        volume_row = 2
        rsi_row = 3
    else:
        # 2 subplots: price, volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(
                f'{symbol} - Price History ({interval_label} Intervals)',
                f'Trading Volume ({interval_label} Bars)'
            )
        )
        volume_row = 2
        rsi_row = None

    # Price chart with high/low range
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['High'],
        fill=None,
        mode='lines',
        line_color='rgba(162, 59, 114, 0)',
        showlegend=False,
        hoverinfo='skip'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Low'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(162, 59, 114, 0)',
        fillcolor='rgba(162, 59, 114, 0.2)',
        name='High/Low Range',
        hoverinfo='skip'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name='Close',
        line=dict(color='#2E86AB', width=2),
        hovertemplate='<b>Close</b>: $%{y:.2f}<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Open'],
        mode='lines',
        name='Open',
        line=dict(color='#F77F00', width=1),
        opacity=0.7,
        hovertemplate='<b>Open</b>: $%{y:.2f}<extra></extra>'
    ), row=1, col=1)

    # Add features
    if features:
        colors = ['#FF6B35', '#4ECDC4', '#FFE66D', '#FF6B9D']
        ma_idx = 0
        for feature in features:
            if feature['type'] == 'moving_average':
                ma = calculate_moving_average(data, feature['period'], feature['ma_type'])
                color = colors[ma_idx % len(colors)]
                ma_idx += 1
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=ma,
                    mode='lines',
                    name=f"{feature['ma_type']}-{feature['period']}",
                    line=dict(color=color, width=2),
                    hovertemplate=f"<b>{feature['ma_type']}-{feature['period']}</b>: $%{{y:.2f}}<extra></extra>"
                ), row=1, col=1)
            elif feature['type'] == 'rsi':
                rsi = calculate_rsi(data, feature['period'])
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=rsi,
                    mode='lines',
                    name=f"RSI-{feature['period']}",
                    line=dict(color='#9B59B6', width=2),
                    hovertemplate=f"<b>RSI-{feature['period']}</b>: %{{y:.2f}}<extra></extra>"
                ), row=rsi_row, col=1)

                # Add reference lines at 30 and 70
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=rsi_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=rsi_row, col=1)

    # Volume chart
    vol_colors = ['#06A77D' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#D62828'
                  for i in range(len(data))]

    fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        marker_color=vol_colors,
        opacity=0.7,
        name='Volume',
        hovertemplate='<b>Volume</b>: %{y:,.0f}<extra></extra>'
    ), row=volume_row, col=1)

    # Update axes
    fig.update_xaxes(title_text='Date', row=rsi_row if has_rsi else volume_row, col=1)
    fig.update_yaxes(title_text='Price ($)', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=volume_row, col=1)
    if has_rsi:
        fig.update_yaxes(title_text='RSI', range=[0, 100], row=rsi_row, col=1)

    fig.update_layout(
        height=800 if has_rsi else 700,
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )

    return fig


# Main content area
if st.sidebar.button("🔄 Fetch Data", type="primary"):
    st.session_state['fetch_data'] = True

# Auto-fetch on first load or when button clicked
if 'fetch_data' not in st.session_state:
    st.session_state['fetch_data'] = True

if st.session_state.get('fetch_data', False):
    with st.spinner(f'Fetching data for {symbol}...'):
        data = fetch_stock_data(symbol, start_date, end_date, interval)

    if data is not None and not data.empty:
        # Display summary statistics
        if show_summary:
            display_summary_stats(symbol, data)
            st.divider()

        # Create and display the selected chart
        st.subheader("📊 Interactive Chart")

        if chart_type == "Line Chart":
            fig = create_line_chart(symbol, data, interval_choice, st.session_state['features'])
        elif chart_type == "Candlestick Chart":
            fig = create_candlestick_chart(symbol, data, interval_choice, st.session_state['features'])
        elif chart_type == "Volume Chart":
            fig = create_volume_chart(symbol, data, interval_choice)
        else:  # Combined Chart
            fig = create_combined_chart(symbol, data, interval_choice, st.session_state['features'])

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

        # Instructions
        st.info(
            "**💡 Interactive Features:** "
            "Drag to pan | Scroll to zoom | Box select to zoom area | "
            "Double-click to reset | Hover for details | Click legend to toggle traces"
        )

        # Download data option
        with st.expander("📥 Download Data"):
            csv = data.to_csv()
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.error(f"❌ No data found for symbol '{symbol}'. Please check the symbol and try again.")
        st.info("💡 Try popular symbols like: AAPL, MSFT, GOOGL, TSLA, AMZN")

# Sidebar footer
st.sidebar.divider()
st.sidebar.markdown("**About**")
st.sidebar.info(
    "This app provides interactive stock price visualizations using real-time data from Yahoo Finance. "
    "Powered by yfinance, Plotly, and Streamlit."
)
