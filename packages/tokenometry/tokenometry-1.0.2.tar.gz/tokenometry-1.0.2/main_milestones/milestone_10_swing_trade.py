# milestone_10_aggressive.py

import time
import pandas as pd
import pandas_ta as ta
from coinbase.rest import RESTClient
import warnings
import logging
import sys
import requests
from textblob import TextBlob
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Logger Setup ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("crypto_scanner.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

# --- Configuration ---
# API keys are now loaded securely from the .env file
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GLASSNODE_API_KEY = os.getenv("GLASSNODE_API_KEY")

PRODUCT_IDS = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD"] 

# --- STRATEGY TIMEFRAME & INDICATOR SETTINGS (AGGRESSIVE) ---
GRANULARITY_SIGNAL = "FOUR_HOUR" # Signal Timeframe: 4-Hour Chart
GRANULARITY_TREND = "ONE_DAY"      # Trend Timeframe: Daily Chart

TREND_EMA_PERIOD = 50   # Use a 50-day EMA to determine the main trend
SHORT_EMA = 20          # Short-term EMA for signal generation
LONG_EMA = 50           # Long-term EMA for signal generation

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ATR_PERIOD = 14

# --- Risk & Filter Configuration ---
HYPOTHETICAL_PORTFOLIO_SIZE = 100000.0
RISK_PER_TRADE_PERCENTAGE = 1.0
ATR_STOP_LOSS_MULTIPLIER = 2.5
SENTIMENT_THRESHOLD_BULLISH = 0.05
SENTIMENT_THRESHOLD_BEARISH = -0.05

def get_historical_data(product_id, granularity, years=1):
    """Fetches historical candlestick data from Coinbase."""
    logger.info(f"Fetching {granularity} data for {product_id}...")
    try:
        client = RESTClient()
        end_time = int(time.time())
        start_time = end_time - (years * 365 * 86400)
        
        # Determine seconds per candle for pagination
        granularity_seconds = {"ONE_DAY": 86400, "FOUR_HOUR": 14400}.get(granularity, 86400)
        
        logger.info(f"  Time range: {pd.to_datetime(start_time, unit='s').date()} to {pd.to_datetime(end_time, unit='s').date()}")
        logger.info(f"  Estimated total periods: {(end_time - start_time) / granularity_seconds:.0f}")
        logger.info(f"  Estimated API calls needed: {((end_time - start_time) / granularity_seconds / 300):.1f}")
        
        all_candles = []
        current_start = start_time
        batch_count = 0
        while current_start < end_time:
            batch_count += 1
            current_end = current_start + (300 * granularity_seconds)
            if current_end > end_time: current_end = end_time

            logger.info(f"  Batch {batch_count}: Fetching from {pd.to_datetime(current_start, unit='s').date()} to {pd.to_datetime(current_end, unit='s').date()}...")
            response = client.get_public_candles(product_id=product_id, start=str(current_start), end=str(current_end), granularity=granularity)
            
            # Convert response to dictionary and extract candles
            response_dict = response.to_dict()
            candles = response_dict.get('candles', [])
            if not candles: break
            all_candles.extend(candles)
            # Move to the next batch by advancing 300 periods (not 1 period)
            current_start = current_end
            time.sleep(0.5)
        if not all_candles: 
            logger.warning(f"No price data from Coinbase for {product_id}.")
            return None
        df = pd.DataFrame(all_candles)
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

def get_news_sentiment(product_id):
    """Fetches news and calculates an aggregate sentiment score."""
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not found. Skipping sentiment analysis.")
        return "Neutral"
    search_term = product_id.split('-')[0]
    logger.info(f"Fetching news sentiment for {search_term}...")
    try:
        url = f"https://newsapi.org/v2/everything?q={search_term}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        if not articles: return "Neutral"
        total_polarity = sum(TextBlob(article['title']).sentiment.polarity for article in articles[:20] if article['title'])
        avg_polarity = total_polarity / len(articles[:20])
        logger.info(f"Average sentiment polarity for {search_term}: {avg_polarity:.4f}")
        if avg_polarity > SENTIMENT_THRESHOLD_BULLISH: return "Positive"
        elif avg_polarity < SENTIMENT_THRESHOLD_BEARISH: return "Negative"
        else: return "Neutral"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news for {search_term}: {e}")
        return "Neutral"

def get_onchain_status(product_id):
    """Fetches on-chain data to gauge accumulation/distribution."""
    if not GLASSNODE_API_KEY:
        logger.warning("GLASSNODE_API_KEY not found. Skipping on-chain analysis.")
        return "Neutral"
    asset = product_id.split('-')[0]
    logger.info(f"Fetching on-chain exchange flow for {asset}...")
    since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    try:
        url = f"https://api.glassnode.com/v1/metrics/distribution/exchange_net_position_change?a={asset}&s={since_date}&i=24h"
        params = {'api_key': GLASSNODE_API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data: return "Neutral"
        net_flow_sum = sum(item['v'] for item in data)
        logger.info(f"7-day cumulative exchange netflow for {asset}: {net_flow_sum:,.2f} {asset}")
        return "Accumulation" if net_flow_sum < 0 else "Distribution"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching on-chain data for {asset}: {e}")
        return "Neutral"

def get_daily_trend(product_id):
    """Determines the main market trend using a daily EMA."""
    df_daily = get_historical_data(product_id, GRANULARITY_TREND, years=1)
    if df_daily is None or df_daily.empty: return "Unknown"
    df_daily.ta.ema(length=TREND_EMA_PERIOD, append=True)
    df_daily.dropna(inplace=True)
    latest_day = df_daily.iloc[-1]
    trend_ema_col = f'EMA_{TREND_EMA_PERIOD}'
    return "Bullish" if latest_day['Close'] > latest_day[trend_ema_col] else "Bearish"

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
    """Generates technical buy/sell/hold signals based on the EMA Crossover."""
    if df is None: return None
    logger.info("Generating technical signals...")
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
        daily_trend = get_daily_trend(product_id)
        sentiment = get_news_sentiment(product_id)
        # On-chain is kept for context but not used in the final aggressive signal
        onchain = get_onchain_status(product_id) 
        logger.info(f"Analysis for {product_id} -> Trend: {daily_trend}, Sentiment: {sentiment}, On-Chain: {onchain}")

        data = get_historical_data(product_id, GRANULARITY_SIGNAL, years=1)
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            data.dropna(inplace=True)
            data = generate_signals(data)
            latest_row = data.iloc[-1]
            results.append({'product_id': product_id, 'latest_row': latest_row, 'trend': daily_trend, 'sentiment': sentiment})
        else:
            logger.warning(f"Could not process 4-Hour data for {product_id}, skipping.")
            
    logger.info("="*80 + "\n" + " " * 25 + "AGGRESSIVE SWING SIGNAL SUMMARY" + "\n" + "="*80)
    
    for result in results:
        product_id, latest_row, trend, sentiment = result['product_id'], result['latest_row'], result['trend'], result['sentiment']
        tech_signal, latest_close_price = latest_row['Signal'], latest_row['Close']
        latest_timestamp = latest_row.name

        # --- RELAXED FINAL SIGNAL LOGIC ---
        final_signal = "HOLD"
        if tech_signal == 1 and trend == "Bullish" and sentiment != "Negative":
            final_signal = "BUY"
        elif tech_signal == -1 and trend == "Bearish" and sentiment != "Positive":
            final_signal = "SELL"
            
        logger.info(f"--- {product_id} (Trend: {trend}, Sentiment: {sentiment}) ---")
        logger.info(f"  Timestamp: {latest_timestamp.strftime('%Y-%m-%d %H:%M')}, Last Close: ${latest_close_price:,.2f}")
        logger.info(f"  Final Signal: {final_signal}")

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
    logger.info("Crypto Analysis Bot (Aggressive Swing Strategy) started.")
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY is not set. Sentiment analysis will be skipped.")
    if not GLASSNODE_API_KEY:
        logger.warning("GLASSNODE_API_KEY is not set. On-chain analysis will be skipped (context only).")

    while True:
        run_analysis_cycle()
        sleep_duration = 4 * 60 * 60 # Run every 4 hours
        logger.info(f"Sleeping for 4 hours until the next analysis cycle.")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
