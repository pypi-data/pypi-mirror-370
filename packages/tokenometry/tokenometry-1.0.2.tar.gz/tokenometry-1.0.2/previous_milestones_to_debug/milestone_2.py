# milestone_2.py - Core Strategy Implementation

import time
import pandas as pd
import pandas_ta as ta
import numpy as np
from coinbase.rest import RESTClient

# --- Configuration ---
PRODUCT_ID = "BTC-USD"
GRANULARITY = "ONE_DAY"
SHORT_WINDOW = 50
LONG_WINDOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

def get_historical_data(product_id, granularity, years=3):
    """
    Fetches historical candlestick data from Coinbase for a specified number of years.
    """
    print(f"Fetching last {years} years of historical data for {product_id}...")
    try:
        client = RESTClient()
        end_time = int(time.time())
        start_time = end_time - (years * 365 * 86400)
        
        print(f"Time range: {pd.to_datetime(start_time, unit='s').date()} to {pd.to_datetime(end_time, unit='s').date()}")
        print(f"Estimated total days: {(end_time - start_time) / 86400:.0f}")
        print(f"Estimated API calls needed: {((end_time - start_time) / 86400 / 300):.1f}")

        all_candles = []
        current_start = start_time
        batch_count = 0
        
        while current_start < end_time:
            batch_count += 1
            current_end = current_start + (300 * 86400)
            if current_end > end_time:
                current_end = end_time

            print(f"Batch {batch_count}: Fetching from {pd.to_datetime(current_start, unit='s').date()} to {pd.to_datetime(current_end, unit='s').date()}...")

            response = client.get_public_candles(
                product_id=product_id,
                start=str(current_start),
                end=str(current_end),
                granularity=granularity
            )
            
            # Convert response to dictionary and extract candles
            response_dict = response.to_dict()
            candles = response_dict.get('candles', [])
            if not candles:
                break
            
            all_candles.extend(candles)
            # Move to the next batch by advancing 300 days (not 1 day)
            current_start = current_end
            time.sleep(0.5)

        if not all_candles:
            print("No data returned from Coinbase.")
            return None

        df = pd.DataFrame(all_candles)
        df.rename(columns={
            'start': 'timestamp', 'low': 'Low', 'high': 'High',
            'open': 'Open', 'close': 'Close', 'volume': 'Volume'
        }, inplace=True)

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        for col in ['Low', 'High', 'Open', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col])
        
        df.drop_duplicates(subset='timestamp', inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)

        print(f"Data fetched successfully. Total candles: {len(df)}")
        return df

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None

def calculate_indicators(df, short_window, long_window, rsi_period):
    """Calculates SMAs and RSI."""
    print("Calculating technical indicators (SMA, RSI)...")
    df.ta.sma(length=short_window, append=True)
    df.ta.sma(length=long_window, append=True)
    df.ta.rsi(length=rsi_period, append=True)
    return df

def generate_signals(df, short_window, long_window, rsi_period):
    """
    Generates buy and sell signals based on a confluence of SMA crossover and RSI conditions.
    """
    print("Generating trading signals with SMA and RSI confluence...")
    short_sma_col = f'SMA_{short_window}'
    long_sma_col = f'SMA_{long_window}'
    rsi_col = f'RSI_{rsi_period}'
    
    df['Signal'] = 0
    
    # --- Buy Signal Conditions ---
    # 1. Golden Cross: Short SMA crosses above Long SMA
    golden_cross = (df[short_sma_col] > df[long_sma_col]) & \
                   (df[short_sma_col].shift(1) <= df[long_sma_col].shift(1))
    # 2. RSI Filter: RSI is not in overbought territory
    rsi_buy_filter = df[rsi_col] < RSI_OVERBOUGHT
    
    df.loc[golden_cross & rsi_buy_filter, 'Signal'] = 1

    # --- Sell Signal Conditions ---
    # 1. Death Cross: Short SMA crosses below Long SMA
    death_cross = (df[short_sma_col] < df[long_sma_col]) & \
                  (df[short_sma_col].shift(1) >= df[long_sma_col].shift(1))
    # 2. RSI Filter: RSI is not in oversold territory
    rsi_sell_filter = df[rsi_col] > RSI_OVERSOLD

    df.loc[death_cross & rsi_sell_filter, 'Signal'] = -1
    
    return df

def analyze_signals(df, short_window, long_window, rsi_period):
    """
    Analyzes and displays the generated trading signals.
    """
    print("\n--- Signal Analysis (SMA + RSI Strategy) ---")
    
    short_sma_col = f'SMA_{short_window}'
    long_sma_col = f'SMA_{long_window}'
    rsi_col = f'RSI_{rsi_period}'
    
    # Count signals
    buy_signals = len(df[df['Signal'] == 1])
    sell_signals = len(df[df['Signal'] == -1])
    total_signals = buy_signals + sell_signals
    
    print(f"Total Buy Signals (Golden Cross + RSI Filter): {buy_signals}")
    print(f"Total Sell Signals (Death Cross + RSI Filter): {sell_signals}")
    print(f"Total Trading Signals: {total_signals}")
    
    # Show signal details
    if buy_signals > 0:
        print(f"\nBuy Signals Found:")
        buy_dates = df[df['Signal'] == 1].index
        for date in buy_dates:
            price = df.loc[date, 'Close']
            rsi_value = df.loc[date, rsi_col]
            print(f"  {date.date()}: Price ${price:.2f}, RSI {rsi_value:.1f}")
    
    if sell_signals > 0:
        print(f"\nSell Signals Found:")
        sell_dates = df[df['Signal'] == -1].index
        for date in sell_dates:
            price = df.loc[date, 'Close']
            rsi_value = df.loc[date, rsi_col]
            print(f"  {date.date()}: Price ${price:.2f}, RSI {rsi_value:.1f}")
    
    if total_signals == 0:
        print("No trading signals generated in the analyzed period.")
    
    # Show current market conditions
    latest_data = df.iloc[-1]
    current_price = latest_data['Close']
    current_rsi = latest_data[rsi_col]
    current_short_sma = latest_data[short_sma_col]
    current_long_sma = latest_data[long_sma_col]
    
    print(f"\n--- Current Market Conditions ---")
    print(f"Latest Date: {df.index[-1].date()}")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Current RSI: {current_rsi:.1f}")
    print(f"50-Day SMA: ${current_short_sma:.2f}")
    print(f"200-Day SMA: ${current_long_sma:.2f}")
    
    # Market trend analysis
    if current_short_sma > current_long_sma:
        trend = "BULLISH"
        if current_rsi < RSI_OVERBOUGHT:
            status = "Trend following with room for growth"
        else:
            status = "Trend following but potentially overbought"
    else:
        trend = "BEARISH"
        if current_rsi > RSI_OVERSOLD:
            status = "Trend following with room for decline"
        else:
            status = "Trend following but potentially oversold"
    
    print(f"Market Trend: {trend}")
    print(f"Status: {status}")

def main():
    """
    Main function to run the core strategy analysis.
    """
    print("--- Crypto Analysis Bot: Milestone 2 - Core Strategy ---")
    
    data = get_historical_data(PRODUCT_ID, GRANULARITY, years=1)
    
    if data is not None and not data.empty:
        data = calculate_indicators(data, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD)
        data.dropna(inplace=True) # Drop NaNs created by indicators
        
        data = generate_signals(data, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD)
        
        analyze_signals(data, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD)
    
    print("\n--- Analysis Complete ---")

if __name__ == "__main__":
    main()
