# milestone_7.py

import time
import pandas as pd
import pandas_ta as ta
from coinbase.rest import RESTClient
import warnings
import logging
import sys

# --- Logger Setup ---
# Configure logger to output to both a file and the console
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("crypto_scanner.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)


# Suppress SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# --- Configuration ---
PRODUCT_IDS = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD"] 
GRANULARITY_SIGNAL = "ONE_DAY"
GRANULARITY_TREND = "ONE_WEEK"
TREND_SMA_PERIOD = 30 
SHORT_WINDOW = 50
LONG_WINDOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ATR_PERIOD = 14

# --- Risk Management Configuration ---
HYPOTHETICAL_PORTFOLIO_SIZE = 100000.0
RISK_PER_TRADE_PERCENTAGE = 1.0
ATR_STOP_LOSS_MULTIPLIER = 2.5

def get_historical_data(product_id, granularity, years=1):
    """Fetches historical candlestick data from Coinbase for a single asset."""
    logger.info(f"Fetching {granularity} data for {product_id}...")
    try:
        client = RESTClient()
        end_time = int(time.time())
        start_time = end_time - (years * 365 * 86400)
        
        # Determine seconds per candle for pagination
        granularity_seconds = {"ONE_DAY": 86400, "ONE_WEEK": 604800}.get(granularity, 86400)
        
        logger.info(f"  Time range: {pd.to_datetime(start_time, unit='s').date()} to {pd.to_datetime(end_time, unit='s').date()}")
        logger.info(f"  Estimated total periods: {(end_time - start_time) / granularity_seconds:.0f}")
        logger.info(f"  Estimated API calls needed: {((end_time - start_time) / granularity_seconds / 300):.1f}")
        
        all_candles = []
        current_start = start_time
        batch_count = 0

        while current_start < end_time:
            batch_count += 1
            current_end = current_start + (300 * granularity_seconds)
            if current_end > end_time:
                current_end = end_time

            logger.info(f"  Batch {batch_count}: Fetching from {pd.to_datetime(current_start, unit='s').date()} to {pd.to_datetime(current_end, unit='s').date()}...")

            response = client.get_public_candles(
                product_id=product_id,
                start=str(current_start),
                end=str(current_end),
                granularity=granularity
            )
            
            # Convert response to dictionary and extract candles
            response_dict = response.to_dict()
            candles = response_dict.get('candles', [])
            if not candles: break
            
            all_candles.extend(candles)
            # Move to the next batch by advancing 300 periods (not 1 period)
            current_start = current_end
            time.sleep(0.5)

        if not all_candles: 
            logger.warning(f"No data returned from Coinbase for {product_id}.")
            return None

        df = pd.DataFrame(all_candles)
        df.rename(columns={'start': 'timestamp', 'low': 'Low', 'high': 'High', 'open': 'Open', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        for col in ['Low', 'High', 'Open', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col])
        df.drop_duplicates(subset='timestamp', inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        logger.error(f"An error occurred fetching data for {product_id}: {e}")
        return None

def get_long_term_trend(product_id):
    """Determines the long-term market trend using a weekly SMA."""
    df_weekly = get_historical_data(product_id, GRANULARITY_TREND, years=3)
    if df_weekly is None or df_weekly.empty:
        return "Unknown"
    
    df_weekly.ta.sma(length=TREND_SMA_PERIOD, append=True)
    df_weekly.dropna(inplace=True)
    
    latest_week = df_weekly.iloc[-1]
    trend_sma_col = f'SMA_{TREND_SMA_PERIOD}'
    
    if latest_week['Close'] > latest_week[trend_sma_col]:
        return "Bullish"
    else:
        return "Bearish"

def calculate_indicators(df):
    """Calculates all necessary technical indicators for a given DataFrame."""
    if df is None: return None
    logger.info("Calculating indicators: SMA, RSI, MACD, ATR...")
    df.ta.sma(length=SHORT_WINDOW, append=True)
    df.ta.sma(length=LONG_WINDOW, append=True)
    df.ta.rsi(length=RSI_PERIOD, append=True)
    df.ta.macd(fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL, append=True)
    df.ta.atr(length=ATR_PERIOD, append=True)
    return df

def generate_signals(df):
    """Generates buy/sell/hold signals based on the 3-factor confluence strategy."""
    if df is None: return None
    logger.info("Generating signals based on strategy...")
    short_sma_col, long_sma_col = f'SMA_{SHORT_WINDOW}', f'SMA_{LONG_WINDOW}'
    rsi_col = f'RSI_{RSI_PERIOD}'
    macd_line_col, macd_signal_col = f'MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}', f'MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}'
    
    df['Signal'] = 0
    golden_cross = (df[short_sma_col] > df[long_sma_col]) & (df[short_sma_col].shift(1) <= df[long_sma_col].shift(1))
    rsi_buy_filter = df[rsi_col] < RSI_OVERBOUGHT
    macd_buy_filter = df[macd_line_col] > df[macd_signal_col]
    df.loc[golden_cross & rsi_buy_filter & macd_buy_filter, 'Signal'] = 1

    death_cross = (df[short_sma_col] < df[long_sma_col]) & (df[short_sma_col].shift(1) >= df[long_sma_col].shift(1))
    rsi_sell_filter = df[rsi_col] > RSI_OVERSOLD
    macd_sell_filter = df[macd_line_col] < df[macd_signal_col]
    df.loc[death_cross & rsi_sell_filter & macd_sell_filter, 'Signal'] = -1
    return df

def run_analysis_cycle():
    """Runs one full analysis cycle for all configured assets."""
    logger.info("Starting new analysis cycle.")
    results = []
    
    for product_id in PRODUCT_IDS:
        long_term_trend = get_long_term_trend(product_id)
        logger.info(f"Long-term trend for {product_id}: {long_term_trend}")

        data = get_historical_data(product_id, GRANULARITY_SIGNAL, years=1)
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            data.dropna(inplace=True)
            data = generate_signals(data)
            
            latest_row = data.iloc[-1]
            results.append({'product_id': product_id, 'latest_row': latest_row, 'trend': long_term_trend})
        else:
            logger.warning(f"Could not process daily data for {product_id}, skipping.")
            
    # --- Log Summary Report ---
    logger.info("="*60)
    logger.info(" " * 15 + "MULTI-ASSET SIGNAL SUMMARY (MTA FILTERED)")
    logger.info("="*60)
    
    for result in results:
        product_id, latest_row, trend = result['product_id'], result['latest_row'], result['trend']
        latest_signal, latest_close_price = latest_row['Signal'], latest_row['Close']
        latest_timestamp = latest_row.name

        final_signal = "HOLD"
        if latest_signal == 1 and trend == "Bullish":
            final_signal = "BUY"
        elif latest_signal == -1 and trend == "Bearish":
            final_signal = "SELL"
            
        logger.info(f"--- {product_id} (Trend: {trend}) ---")
        logger.info(f"  Timestamp: {latest_timestamp.strftime('%Y-%m-%d')}")
        logger.info(f"  Last Close: ${latest_close_price:,.2f}")
        logger.info(f"  Signal: {final_signal}")

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

    logger.info("="*60)
    logger.info("Analysis cycle complete.")

def main():
    """Main loop to run the analysis periodically."""
    logger.info("Crypto Analysis Bot started.")
    while True:
        run_analysis_cycle()
        sleep_duration = 24 * 60 * 60 # 24 hours in seconds
        logger.info(f"Sleeping for 24 hours until the next analysis cycle.")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
