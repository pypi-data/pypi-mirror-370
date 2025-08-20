# milestone_11_daytrader.py

import time
import pandas as pd
import pandas_ta as ta
from coinbase.rest import RESTClient
import warnings
import logging
import sys
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Logger Setup ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("crypto_daytrader.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# --- Configuration ---
PRODUCT_IDS = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD"] 

# --- STRATEGY TIMEFRAME & INDICATOR SETTINGS (DAY TRADER) ---
GRANULARITY_SIGNAL = "FIVE_MINUTE" # Signal Timeframe: 5-Minute Chart
GRANULARITY_TREND = "ONE_HOUR"     # Trend Timeframe: 1-Hour Chart

TREND_EMA_PERIOD = 50   # Use a 50-period EMA on the 1-hour chart for the trend
SHORT_EMA = 9           # Short-term EMA for 5-minute chart signals
LONG_EMA = 21           # Long-term EMA for 5-minute chart signals

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ATR_PERIOD = 14

# --- Risk & Filter Configuration ---
HYPOTHETICAL_PORTFOLIO_SIZE = 100000.0
RISK_PER_TRADE_PERCENTAGE = 0.5 # Tighter risk for day trading
ATR_STOP_LOSS_MULTIPLIER = 2.0  # Tighter stop-loss for day trading

def get_historical_data(product_id, granularity):
    """
    Fetches the last 300 candles of historical data from Coinbase.
    This is the maximum per request and sufficient for these indicator settings.
    """
    logger.info(f"Fetching {granularity} data for {product_id}...")
    try:
        client = RESTClient()
        
        # Calculate a start time to ensure we get enough data for indicators to mature
        # 300 candles is the max per request.
        granularity_seconds = {"ONE_HOUR": 3600, "FIVE_MINUTE": 300}.get(granularity, 3600)
        duration_seconds = 300 * granularity_seconds
        start_time = int(time.time() - duration_seconds)
        end_time = int(time.time())

        response = client.get_public_candles(
            product_id=product_id, 
            start=str(start_time), 
            end=str(end_time), 
            granularity=granularity
        )
        
        # Convert response to dictionary and extract candles
        response_dict = response.to_dict()
        candles = response_dict.get('candles', [])
        if not candles: 
            logger.warning(f"No price data from Coinbase for {product_id}.")
            return None
            
        df = pd.DataFrame(candles)
        df.rename(columns={'start': 'timestamp', 'low': 'Low', 'high': 'High', 'open': 'Open', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='s')
        for col in ['Low', 'High', 'Open', 'Close', 'Volume']: df[col] = pd.to_numeric(df[col])
        df.drop_duplicates(subset='timestamp', inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        logger.error(f"Error fetching price data for {product_id}: {e}")
        return None

def get_intraday_trend(product_id):
    """Determines the main intraday trend using the 1-Hour EMA."""
    df_hourly = get_historical_data(product_id, GRANULARITY_TREND)
    if df_hourly is None or df_hourly.empty: return "Unknown"
    
    df_hourly.ta.ema(length=TREND_EMA_PERIOD, append=True)
    df_hourly.dropna(inplace=True)
    
    latest_hour = df_hourly.iloc[-1]
    trend_ema_col = f'EMA_{TREND_EMA_PERIOD}'
    
    return "Bullish" if latest_hour['Close'] > latest_hour[trend_ema_col] else "Bearish"

def calculate_indicators(df):
    """Calculates all necessary technical indicators."""
    if df is None: return None
    logger.info("Calculating technical indicators...")
    df.ta.ema(length=SHORT_EMA, append=True)
    df.ta.ema(length=LONG_EMA, append=True)
    df.ta.rsi(length=RSI_PERIOD, append=True)
    df.ta.macd(fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL, append=True)
    df.ta.atr(length=ATR_PERIOD, append=True)
    return df

def generate_signals(df):
    """Generates technical buy/sell/hold signals based on the 5-minute EMA Crossover."""
    if df is None: return None
    logger.info("Generating technical signals on 5-minute chart...")
    short_ema_col = f'EMA_{SHORT_EMA}'
    long_ema_col = f'EMA_{LONG_EMA}'
    rsi_col = f'RSI_{RSI_PERIOD}'
    macd_line_col, macd_signal_col = f'MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}', f'MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}'
    df['Signal'] = 0
    
    # Bullish EMA Crossover
    golden_cross = (df[short_ema_col] > df[long_ema_col]) & (df[short_ema_col].shift(1) <= df[long_ema_col].shift(1))
    rsi_buy_filter = df[rsi_col] < RSI_OVERBOUGHT
    macd_buy_filter = df[macd_line_col] > df[macd_signal_col]
    df.loc[golden_cross & rsi_buy_filter & macd_buy_filter, 'Signal'] = 1
    
    # Bearish EMA Crossover
    death_cross = (df[short_ema_col] < df[long_ema_col]) & (df[short_ema_col].shift(1) >= df[long_ema_col].shift(1))
    rsi_sell_filter = df[rsi_col] > RSI_OVERSOLD
    macd_sell_filter = df[macd_line_col] < df[macd_signal_col]
    df.loc[death_cross & rsi_sell_filter & macd_sell_filter, 'Signal'] = -1
    return df

def run_analysis_cycle():
    """Runs one full analysis cycle for all configured assets."""
    logger.info("Starting new analysis cycle.")
    results = []
    
    for product_id in PRODUCT_IDS:
        intraday_trend = get_intraday_trend(product_id)
        logger.info(f"Intraday (H1) Trend for {product_id}: {intraday_trend}")

        data = get_historical_data(product_id, GRANULARITY_SIGNAL)
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            data.dropna(inplace=True)
            data = generate_signals(data)
            latest_row = data.iloc[-1]
            results.append({'product_id': product_id, 'latest_row': latest_row, 'trend': intraday_trend})
        else:
            logger.warning(f"Could not process 5-Minute data for {product_id}, skipping.")
            
    logger.info("="*80 + "\n" + " " * 25 + "INTRADAY TRADING SIGNAL SUMMARY" + "\n" + "="*80)
    
    for result in results:
        product_id, latest_row, trend = result['product_id'], result['latest_row'], result['trend']
        tech_signal, latest_close_price = latest_row['Signal'], latest_row['Close']
        latest_timestamp = latest_row.name

        # --- FINAL SIGNAL LOGIC (H1 Trend + M5 Signal) ---
        final_signal = "HOLD"
        if tech_signal == 1 and trend == "Bullish":
            final_signal = "BUY"
        elif tech_signal == -1 and trend == "Bearish":
            final_signal = "SELL"
            
        # Log all assets with their current status
        logger.info(f"--- {product_id} (H1 Trend: {trend}) ---")
        logger.info(f"  Timestamp: {latest_timestamp.strftime('%Y-%m-%d %H:%M')}, Last Close: ${latest_close_price:,.2f}")
        logger.info(f"  Signal: {final_signal}")

        # Only show trade plan for active BUY signals
        if final_signal == "BUY":
            atr_col = f'ATRr_{ATR_PERIOD}'
            latest_atr = latest_row[atr_col]
            stop_loss_price = latest_close_price - (latest_atr * ATR_STOP_LOSS_MULTIPLIER)
            capital_to_risk = HYPOTHETICAL_PORTFOLIO_SIZE * (RISK_PER_TRADE_PERCENTAGE / 100)
            stop_loss_distance = latest_close_price - stop_loss_price
            if stop_loss_distance > 0:
                position_size_crypto = capital_to_risk / stop_loss_distance
                position_size_usd = position_size_crypto * latest_close_price
                logger.info("  --- Suggested Trade Plan ---")
                logger.info(f"    Stop-Loss: ${stop_loss_price:,.2f}")
                logger.info(f"    Position Size: {position_size_crypto:.6f} {product_id.split('-')[0]} (${position_size_usd:,.2f})")

    logger.info("="*80 + "\nAnalysis cycle complete.")

def main():
    """Main loop to run the analysis periodically."""
    logger.info("Crypto Day Trading Bot started.")
    
    while True:
        run_analysis_cycle()
        sleep_duration = 5 * 60 # Run every 5 minutes
        logger.info(f"Sleeping for 5 minutes until the next analysis cycle.")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
