"""
Data Acquisition Script for Portfolio Risk Analysis
Downloads and stores stock prices and risk-free rate data offline.

Run this script first to download all required data:
    python data_acquisition.py
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime
import os
from config import FRED_API_KEY

# Create data directory
os.makedirs('data', exist_ok=True)

print("="*60)
print("PORTFOLIO RISK ANALYSIS - DATA ACQUISITION")
print("="*60)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# STEP 1: DEFINE STOCK UNIVERSE
# ============================================================================
print("Step 1: Defining stock universe...")

# Top 300 stocks from S&P 500 by market cap (as of Jan 2026)
tier1 = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK.B", "TSLA", "LLY", "V", 
         "UNH", "XOM", "JPM", "MA", "AVGO", "JNJ", "WMT", "PG", "COST", "HD", 
         "ABBV", "CVX", "MRK", "KO", "NFLX", "BAC", "ORCL", "PEP", "AMD", "ADBE", 
         "CRM", "TMO", "CSCO", "MCD", "ABT", "INTC", "ACN", "DHR", "NKE", "TXN", 
         "CMCSA", "WFC", "BMY", "HON", "NEE", "UNP", "VZ", "RTX", "QCOM", "LIN", "T"]

tier2 = ["AMGN", "PM", "LOW", "UPS", "COP", "INTU", "PFE", "SPGI", "MDT", "DE", 
         "C", "IBM", "BLK", "GE", "AMAT", "ADI", "AXP", "SBUX", "PLD", "ISRG", 
         "CAT", "GILD", "MMC", "TJX", "BKNG", "SO", "CB", "CVS", "SYK", "SCHW", 
         "ADP", "AMT", "CI", "ZTS", "MS", "GS", "NOW", "VRTX", "BA", "MO", 
         "REGN", "DUK", "BDX", "CL", "EQIX", "PNC", "ITW", "APD", "ICE", "EOG",
         "USB", "SLB", "HUM", "CME", "MU", "NSC", "AON", "TGT", "LRCX", "ETN", 
         "MCO", "WM", "PSA", "CCI", "MMM", "BSX", "KLAC", "SHW", "FCX", "APH", 
         "ORLY", "D", "ADM", "ROP", "EW", "ECL", "AJG", "MSI", "DG", "MSCI", 
         "PCAR", "F", "TRV", "NXPI", "GM", "KMB", "SRE", "AEP", "EL", "APO", 
         "WELL", "PAYX", "MNST", "FIS", "SPG", "AIG", "AFL", "A", "CDNS", "TEL"]

tier3 = ["KDP", "CTAS", "KMI", "GIS", "CMG", "HLT", "STZ", "NEM", "WMB", "BK", 
         "CARR", "O", "PSX", "YUM", "MCHP", "EXC", "MAR", "CPRT", "ADSK", "AZO", 
         "TDG", "DD", "HSY", "ROST", "ALL", "ODFL", "CTVA", "IDXX", "DVN", "LHX", 
         "PRU", "AMP", "PEG", "AME", "CTSH", "OTIS", "DLR", "IQV", "EA", "RSG", 
         "RMD", "ED", "FAST", "MLM", "HCA", "GWW", "KHC", "BKR", "CNC", "SNPS",
         "KVUE", "BIIB", "DXCM", "FTNT", "JCI", "IR", "IT", "NDAQ", "GLW", "ANSS", 
         "VMC", "DAL", "KEYS", "XYL", "FANG", "FDX", "VRSK", "HES", "ON", "DOW", 
         "EXR", "ROK", "EFX", "MTB", "AVB", "MPWR", "CDW", "TT", "WEC", "CBRE", 
         "HPQ", "RJF", "PPG", "TROW", "CSGP", "STT", "FITB", "TSN", "AWK", "HBAN", 
         "VICI", "WBD", "CHD", "LVS", "NUE", "DFS", "PH", "ZBH", "ES", "URI"]

tier4 = ["ACGL", "MTD", "CPAY", "WY", "PWR", "TYL", "CF", "IFF", "HPE", "CAH", 
         "TTWO", "EQR", "DTE", "AEE", "FTV", "HUBB", "PKG", "IRM", "TSCO", "ETR", 
         "CNP", "GPN", "BAX", "WAB", "VLTO", "BBY", "WTW", "NTRS", "LH", "LYB", 
         "PTC", "STLD", "BR", "HOLX", "STE", "MOH", "SBAC", "TDY", "BALL", "TRGP", 
         "PPL", "INVH", "LDOS", "CLX", "K", "EXPE", "J", "RF", "COF", "EXPD"]

tickers = tier1 + tier2 + tier3 + tier4

print(f"  Total tickers: {len(tickers)}")

# ============================================================================
# STEP 2: DOWNLOAD STOCK PRICES FROM YAHOO FINANCE
# ============================================================================
print("\nStep 2: Downloading stock price data from Yahoo Finance...")
print("  This may take several minutes...\n")

start_date = '2020-01-01'
end_date = '2026-01-19'

try:
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        threads=True,
        progress=True
    )
    
    prices = data['Close'].copy()
    
    print(f"\n✓ Downloaded data for {len(prices.columns)} stocks")
    print(f"  Date range: {prices.index[0].date()} to {prices.index[-1].date()}")
    print(f"  Trading days: {len(prices)}")
    
    # Save raw prices
    prices.to_csv('data/raw_prices.csv')
    print(f"  Saved: data/raw_prices.csv")
    
except Exception as e:
    print(f"✗ Error downloading stock data: {e}")
    exit(1)

# ============================================================================
# STEP 3: DOWNLOAD RISK-FREE RATE FROM FRED
# ============================================================================
print("\nStep 3: Downloading risk-free rate from FRED...")

try:
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': 'DGS3MO',
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start_date,
        'observation_end': '2026-01-18'
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    rf_data = pd.DataFrame(response.json()['observations'])
    rf_data['value'] = pd.to_numeric(rf_data['value'], errors='coerce')
    rf_data['date'] = pd.to_datetime(rf_data['date'])
    rf_data = rf_data[['date', 'value']].set_index('date')
    rf_data.columns = ['rf_rate']
    rf_data['rf_rate_daily'] = rf_data['rf_rate'] / 100 / 252
    
    print(f"✓ Downloaded risk-free rate data")
    print(f"  Date range: {rf_data.index[0].date()} to {rf_data.index[-1].date()}")
    print(f"  Current 3-month Treasury: {rf_data['rf_rate'].iloc[-1]:.2f}%")
    
    # Save risk-free rate
    rf_data.to_csv('data/risk_free_rate.csv')
    print(f"  Saved: data/risk_free_rate.csv")
    
except Exception as e:
    print(f"✗ Error downloading FRED data: {e}")
    print(f"  Check your API key in config.py")
    exit(1)

# ============================================================================
# STEP 4: DATA QUALITY CHECKS AND CLEANING
# ============================================================================
print("\nStep 4: Performing data quality checks...")

# Check for missing data
missing_pct = (prices.isnull().sum() / len(prices)) * 100
print(f"  Missing data analysis:")
print(f"    Stocks with >5% missing: {(missing_pct > 5).sum()}")
print(f"    Stocks with >10% missing: {(missing_pct > 10).sum()}")

# Remove stocks with >5% missing data
valid_stocks = missing_pct[missing_pct <= 5].index.tolist()
prices_clean = prices[valid_stocks].copy()
print(f"    Stocks removed: {len(prices.columns) - len(valid_stocks)}")
print(f"    Stocks retained: {len(valid_stocks)}")

# Check minimum history requirement (1200 days = ~5 years)
min_days_required = 1200
valid_count = prices_clean.notna().sum()
stocks_sufficient_history = valid_count[valid_count >= min_days_required].index.tolist()
prices_clean = prices_clean[stocks_sufficient_history].copy()

print(f"  Minimum history requirement (>={min_days_required} days):")
print(f"    Stocks retained: {len(stocks_sufficient_history)}")

# Forward fill small gaps (≤5 consecutive days)
prices_clean = prices_clean.fillna(method='ffill', limit=5)

# Drop any remaining NaN
prices_clean = prices_clean.dropna(axis=1, how='any')

print(f"  Final stocks after all checks: {len(prices_clean.columns)}")
print(f"  Final trading days: {len(prices_clean)}")

# Calculate log returns
returns = np.log(prices_clean / prices_clean.shift(1)).dropna()

print(f"\n  Returns statistics:")
print(f"    Shape: {returns.shape}")
print(f"    Mean daily return: {returns.mean().mean()*100:.4f}%")
print(f"    Mean daily volatility: {returns.std().mean()*100:.2f}%")
print(f"    Date range: {returns.index[0].date()} to {returns.index[-1].date()}")

# Check for extreme outliers
extreme_returns = (returns.abs() > 0.5).sum().sum()
if extreme_returns > 0:
    print(f"    ⚠ Warning: {extreme_returns} extreme returns detected (>50%)")

# ============================================================================
# STEP 5: SAVE CLEAN DATA
# ============================================================================
print("\nStep 5: Saving clean data...")

# Save clean prices
prices_clean.to_csv('data/clean_prices.csv')
print(f"  ✓ Saved: data/clean_prices.csv ({len(prices_clean.columns)} stocks)")

# Save clean returns
returns.to_csv('data/clean_returns.csv')
print(f"  ✓ Saved: data/clean_returns.csv ({len(returns.columns)} stocks)")

# Save stock list
stock_list = pd.DataFrame({
    'ticker': returns.columns,
    'included': True,
    'missing_pct': missing_pct[returns.columns].values
})
stock_list.to_csv('data/stock_universe.csv', index=False)
print(f"  ✓ Saved: data/stock_universe.csv")

# Create data quality report
report = f"""
DATA QUALITY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{"="*60}

DOWNLOAD PARAMETERS:
  Date range: {start_date} to {end_date}
  Initial tickers: {len(tickers)}

DATA QUALITY SUMMARY:
  Stocks downloaded: {len(prices.columns)}
  Stocks passing quality checks: {len(returns.columns)}
  Stocks removed: {len(prices.columns) - len(returns.columns)}
  Trading days available: {len(returns)}
  Overall missing data: {(prices_clean.isnull().sum().sum() / (len(prices_clean) * len(prices_clean.columns)) * 100):.2f}%

RETURNS STATISTICS:
  Mean daily return: {returns.mean().mean()*100:.4f}%
  Mean daily volatility: {returns.std().mean()*100:.2f}%
  Min daily return: {returns.min().min()*100:.2f}%
  Max daily return: {returns.max().max()*100:.2f}%

REMOVED STOCKS (if any):
"""

removed_stocks = set(tickers) - set(returns.columns)
if removed_stocks:
    for stock in sorted(removed_stocks):
        reason = "Missing data >5%" if stock in missing_pct[missing_pct > 5].index else "Insufficient history"
        report += f"  {stock}: {reason}\n"
else:
    report += "  None\n"

report += f"""
FILES CREATED:
  data/raw_prices.csv       - Raw downloaded prices ({len(prices.columns)} stocks)
  data/clean_prices.csv     - Clean prices after QC ({len(prices_clean.columns)} stocks)
  data/clean_returns.csv    - Log returns ({len(returns.columns)} stocks)
  data/risk_free_rate.csv   - 3-month Treasury rates
  data/stock_universe.csv   - Stock list with metadata
  data/data_quality_report.txt - This report

{"="*60}
DATA ACQUISITION COMPLETE
{"="*60}
"""

with open('data/data_quality_report.txt', 'w') as f:
    f.write(report)

print(f"  ✓ Saved: data/data_quality_report.txt")

print("\n" + "="*60)
print("✓ DATA ACQUISITION COMPLETED SUCCESSFULLY")
print("="*60)
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nFiles saved in 'data/' directory:")
print(f"  • clean_returns.csv ({len(returns.columns)} stocks, {len(returns)} days)")
print(f"  • clean_prices.csv")
print(f"  • risk_free_rate.csv")
print(f"  • stock_universe.csv")
print(f"  • data_quality_report.txt")
print(f"\nYou can now run the main analysis notebook:")
print(f"  portfolio_risk_analysis.ipynb")
print("="*60)
