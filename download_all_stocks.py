#!/usr/bin/env python3
"""
Download Historical Data for All NASDAQ and NYSE Tickers

This script downloads historical stock data for all publicly traded companies
on the NASDAQ and NYSE exchanges and saves them as CSV files.

Features:
- Downloads ticker lists from NASDAQ FTP
- Fetches historical data using yfinance
- Saves data to organized directory structure
- Handles errors and retries
- Progress tracking and resumable downloads
- Configurable date ranges and intervals
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time
import logging
from pathlib import Path
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_stocks.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_nasdaq_tickers():
    """
    Fetch list of NASDAQ tickers from NASDAQ FTP.

    Returns:
        list: List of ticker symbols
    """
    try:
        logger.info("Fetching NASDAQ ticker list...")
        url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
        df = pd.read_csv(url, sep='|')
        # Remove last row (file creation timestamp) and filter test symbols
        df = df[df['Symbol'].notna()]
        df = df[df['Test Issue'] == 'N']
        df = df[df['Financial Status'].notna()]
        tickers = df['Symbol'].str.strip().tolist()
        # Remove the last entry if it's the file creation info
        if tickers and 'File Creation Time' in str(tickers[-1]):
            tickers = tickers[:-1]
        logger.info(f"Found {len(tickers)} NASDAQ tickers")
        return tickers
    except Exception as e:
        logger.error(f"Error fetching NASDAQ tickers: {e}")
        return []


def get_nyse_tickers():
    """
    Fetch list of NYSE tickers from NASDAQ FTP (includes other exchanges).

    Returns:
        list: List of ticker symbols
    """
    try:
        logger.info("Fetching NYSE ticker list...")
        url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
        df = pd.read_csv(url, sep='|')
        # Filter for NYSE only
        df = df[df['Exchange'] == 'N']  # N = NYSE
        df = df[df['ACT Symbol'].notna()]
        df = df[df['Test Issue'] == 'N']
        tickers = df['ACT Symbol'].str.strip().tolist()
        # Remove the last entry if it's the file creation info
        if tickers and 'File Creation Time' in str(tickers[-1]):
            tickers = tickers[:-1]
        logger.info(f"Found {len(tickers)} NYSE tickers")
        return tickers
    except Exception as e:
        logger.error(f"Error fetching NYSE tickers: {e}")
        return []


def download_stock_data(ticker, start_date, end_date, interval='1d', max_retries=3):
    """
    Download historical data for a single ticker.

    Args:
        ticker (str): Stock ticker symbol
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        interval (str): Data interval (1d, 1wk, 1mo)
        max_retries (int): Maximum number of retry attempts

    Returns:
        pandas.DataFrame or None: Historical data or None if failed
    """
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date, interval=interval)

            if data.empty:
                logger.warning(f"{ticker}: No data available")
                return None

            return data

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"{ticker}: Attempt {attempt + 1} failed, retrying in {wait_time}s... ({e})")
                time.sleep(wait_time)
            else:
                logger.error(f"{ticker}: Failed after {max_retries} attempts - {e}")
                return None

    return None


def save_to_csv(ticker, data, output_dir):
    """
    Save stock data to CSV file.

    Args:
        ticker (str): Stock ticker symbol
        data (pandas.DataFrame): Historical data
        output_dir (str): Output directory path
    """
    try:
        filepath = os.path.join(output_dir, f"{ticker}.csv")
        data.to_csv(filepath)
        logger.debug(f"{ticker}: Saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"{ticker}: Error saving to CSV - {e}")
        return False


def load_progress(progress_file):
    """
    Load download progress from file.

    Args:
        progress_file (str): Path to progress file

    Returns:
        set: Set of already downloaded tickers
    """
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return set(line.strip() for line in f)
    return set()


def save_progress(ticker, progress_file):
    """
    Save download progress to file.

    Args:
        ticker (str): Ticker that was successfully downloaded
        progress_file (str): Path to progress file
    """
    with open(progress_file, 'a') as f:
        f.write(f"{ticker}\n")


def download_all_stocks(exchanges=['NASDAQ', 'NYSE'],
                        output_dir='stock_data',
                        start_date=None,
                        end_date=None,
                        interval='1d',
                        delay=0.5,
                        resume=True):
    """
    Download historical data for all stocks in specified exchanges.

    Args:
        exchanges (list): List of exchanges ('NASDAQ', 'NYSE')
        output_dir (str): Directory to save CSV files
        start_date (str): Start date in YYYY-MM-DD format (default: 5 years ago)
        end_date (str): End date in YYYY-MM-DD format (default: today)
        interval (str): Data interval (1d, 1wk, 1mo)
        delay (float): Delay between requests in seconds
        resume (bool): Resume from previous download
    """
    # Set default dates
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')

    logger.info(f"Download Configuration:")
    logger.info(f"  Exchanges: {', '.join(exchanges)}")
    logger.info(f"  Date Range: {start_date} to {end_date}")
    logger.info(f"  Interval: {interval}")
    logger.info(f"  Output Directory: {output_dir}")
    logger.info(f"  Resume: {resume}")

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get tickers for each exchange
    all_tickers = []
    if 'NASDAQ' in exchanges:
        nasdaq_tickers = get_nasdaq_tickers()
        all_tickers.extend(nasdaq_tickers)

    if 'NYSE' in exchanges:
        nyse_tickers = get_nyse_tickers()
        all_tickers.extend(nyse_tickers)

    # Remove duplicates while preserving order
    all_tickers = list(dict.fromkeys(all_tickers))

    logger.info(f"Total tickers to download: {len(all_tickers)}")

    if not all_tickers:
        logger.error("No tickers found. Exiting.")
        return

    # Load progress
    progress_file = os.path.join(output_dir, '.download_progress.txt')
    completed_tickers = load_progress(progress_file) if resume else set()

    if completed_tickers:
        logger.info(f"Resuming download: {len(completed_tickers)} already completed")

    # Statistics
    stats = {
        'total': len(all_tickers),
        'completed': len(completed_tickers),
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    # Download data
    start_time = time.time()

    for idx, ticker in enumerate(all_tickers, 1):
        # Skip if already completed
        if ticker in completed_tickers:
            stats['skipped'] += 1
            continue

        # Progress update
        progress_pct = (idx / stats['total']) * 100
        elapsed = time.time() - start_time
        rate = idx / elapsed if elapsed > 0 else 0
        eta = (stats['total'] - idx) / rate if rate > 0 else 0

        logger.info(f"[{idx}/{stats['total']} - {progress_pct:.1f}%] Downloading {ticker}... "
                   f"(ETA: {eta/60:.1f}m, Rate: {rate:.1f} tickers/s)")

        # Download data
        data = download_stock_data(ticker, start_date, end_date, interval)

        if data is not None and not data.empty:
            # Save to CSV
            if save_to_csv(ticker, data, output_dir):
                stats['success'] += 1
                save_progress(ticker, progress_file)
            else:
                stats['failed'] += 1
        else:
            stats['failed'] += 1

        # Rate limiting
        time.sleep(delay)

    # Final statistics
    total_time = time.time() - start_time
    logger.info("=" * 80)
    logger.info("Download Complete!")
    logger.info(f"Total Time: {total_time/60:.1f} minutes")
    logger.info(f"Total Tickers: {stats['total']}")
    logger.info(f"Successful: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Skipped: {stats['skipped']}")
    logger.info(f"Success Rate: {(stats['success']/(stats['total']-stats['skipped'])*100):.1f}%")
    logger.info(f"Output Directory: {os.path.abspath(output_dir)}")
    logger.info("=" * 80)


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Download historical stock data for all NASDAQ and NYSE tickers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all NASDAQ and NYSE stocks (last 5 years, daily data)
  python download_all_stocks.py

  # Download only NASDAQ stocks
  python download_all_stocks.py --exchanges NASDAQ

  # Download with custom date range
  python download_all_stocks.py --start 2020-01-01 --end 2023-12-31

  # Download weekly data with custom output directory
  python download_all_stocks.py --interval 1wk --output data/weekly

  # Start fresh (don't resume from previous download)
  python download_all_stocks.py --no-resume
        """
    )

    parser.add_argument(
        '--exchanges',
        nargs='+',
        choices=['NASDAQ', 'NYSE'],
        default=['NASDAQ', 'NYSE'],
        help='Exchanges to download (default: NASDAQ NYSE)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='stock_data',
        help='Output directory for CSV files (default: stock_data)'
    )

    parser.add_argument(
        '--start',
        type=str,
        help='Start date in YYYY-MM-DD format (default: 5 years ago)'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='End date in YYYY-MM-DD format (default: today)'
    )

    parser.add_argument(
        '--interval',
        type=str,
        choices=['1d', '1wk', '1mo'],
        default='1d',
        help='Data interval (default: 1d)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )

    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Start fresh instead of resuming from previous download'
    )

    args = parser.parse_args()

    # Download stocks
    download_all_stocks(
        exchanges=args.exchanges,
        output_dir=args.output,
        start_date=args.start,
        end_date=args.end,
        interval=args.interval,
        delay=args.delay,
        resume=not args.no_resume
    )


if __name__ == '__main__':
    main()
