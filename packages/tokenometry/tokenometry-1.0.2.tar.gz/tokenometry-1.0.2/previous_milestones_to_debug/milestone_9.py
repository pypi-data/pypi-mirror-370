# milestone_9.py

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

warnings.simplefilter(action='ignore', category=pd.core.common.SettingWithCopyWarning)

# --- Configuration ---
# API keys are now loaded securely from the .env file
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GLASSNODE_API_KEY = os.getenv("GLASSNODE_API_KEY")

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
        all_candles = []
        current_start = start_time
        granularity_seconds = {"ONE_DAY": 86400, "ONE_WEEK": 604800}.get(granularity, 86400)
        while current_start < end_time:
            current_end = current_start + (300 * granularity_seconds)
            if current_end > end_time: current_end = end_time
            response = client.get_market_candles(product_id=product_id, start=str(current_start), end=str(current_end), granularity=granularity)
            candles = response.get('candles')
            if not candles: break
            all_candles.extend(candles)
            last_candle_start = int(candles[-1]['start'])
            current_start = last_candle_start + granularity_seconds
            time.sleep(0.5)
        if not all_candles: 
            logger.warning(f"No price data from Coinbase for {product_id}.")
            return None
        df = pd.DataFrame(all_candles)
        df.rename(columns={'start': 'timestamp', 'low': 'Low', 'high': 'High', 'open': 'Open', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
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
        logger.warning("NEWS_API_KEY not found in .env file. Skipping sentiment analysis.")
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
    """Fetches on-chain data (exchange netflow) to gauge accumulation/distribution."""
    if not GLASSNODE_API_KEY:
        logger.warning("GLASSNODE_API_KEY not found in .env file. Skipping on-chain analysis.")
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
        
        if not data:
            logger.warning(f"No on-chain data returned for {asset}.")
            return "Neutral"

        net_flow_sum = sum(item['v'] for item in data)
        logger.info(f"7-day cumulative exchange netflow for {asset}: {net_flow_sum:,.2f} {asset}")

        if net_flow_sum < 0:
            return "Accumulation"
        else:
            return "Distribution"

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching on-chain data for {asset}: {e}")
        return "Neutral"

def get_long_term_trend(product_id):
    """Determines the long-term market trend using a weekly SMA."""
    df_weekly = get_historical_data(product_id, GRANULARITY_TREND, years=3)
    if df_weekly is None or df_weekly.empty: return "Unknown"
    df_weekly.ta.sma(length=TREND_SMA_PERIOD, append=True)
    df_weekly.dropna(inplace=True)
    latest_week = df_weekly.iloc[-1]
    trend_sma_col = f'SMA_{TREND_SMA_PERIOD}'
    return "Bullish" if latest_week['Close'] > latest_week[trend_sma_col] else "Bearish"

def calculate_indicators(df):
    """Calculates all necessary technical indicators."""
    if df is None: return None
    logger.info("Calculating technical indicators...")
    df.ta.sma(length=SHORT_WINDOW, append=True); df.ta.sma(length=LONG_WINDOW, append=True)
    df.ta.rsi(length=RSI_PERIOD, append=True)
    df.ta.macd(fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL, append=True)
    df.ta.atr(length=ATR_PERIOD, append=True)
    return df

def generate_signals(df):
    """Generates technical buy/sell/hold signals."""
    if df is None: return None
    logger.info("Generating technical signals...")
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
        sentiment = get_news_sentiment(product_id)
        onchain = get_onchain_status(product_id)
        logger.info(f"Analysis for {product_id} -> Trend: {long_term_trend}, Sentiment: {sentiment}, On-Chain: {onchain}")

        data = get_historical_data(product_id, GRANULARITY_SIGNAL, years=1)
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            data.dropna(inplace=True)
            data = generate_signals(data)
            latest_row = data.iloc[-1]
            results.append({'product_id': product_id, 'latest_row': latest_row, 'trend': long_term_trend, 'sentiment': sentiment, 'onchain': onchain})
        else:
            logger.warning(f"Could not process daily data for {product_id}, skipping.")
            
    logger.info("="*80 + "\n" + " " * 25 + "MULTI-FACTOR SIGNAL SUMMARY" + "\n" + "="*80)
    
    for result in results:
        product_id, latest_row, trend, sentiment, onchain = result['product_id'], result['latest_row'], result['trend'], result['sentiment'], result['onchain']
        tech_signal, latest_close_price = latest_row['Signal'], latest_row['Close']
        latest_timestamp = latest_row.name

        final_signal = "HOLD"
        if tech_signal == 1 and trend == "Bullish" and sentiment != "Negative" and onchain == "Accumulation":
            final_signal = "STRONG BUY"
        elif tech_signal == -1 and trend == "Bearish" and sentiment != "Positive" and onchain == "Distribution":
            final_signal = "STRONG SELL"
            
        logger.info(f"--- {product_id} (Trend: {trend}, Sentiment: {sentiment}, On-Chain: {onchain}) ---")
        logger.info(f"  Timestamp: {latest_timestamp.strftime('%Y-%m-%d')}, Last Close: ${latest_close_price:,.2f}")
        logger.info(f"  Final Signal: {final_signal}")

        if final_signal == "STRONG BUY":
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
    logger.info("Crypto Analysis Bot started.")
    # Check for API keys at startup
    if not NEWS_API_KEY or not GLASSNODE_API_KEY:
        logger.error("CRITICAL: NEWS_API_KEY or GLASSNODE_API_KEY is not set in the .env file. Exiting.")
        return # Exit if keys are missing

    while True:
        run_analysis_cycle()
        sleep_duration = 24 * 60 * 60
        logger.info(f"Sleeping for 24 hours until the next analysis cycle.")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()
