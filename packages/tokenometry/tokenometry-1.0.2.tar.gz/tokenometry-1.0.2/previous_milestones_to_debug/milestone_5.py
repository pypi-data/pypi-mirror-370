# milestone_5.py

import time
import pandas as pd
import pandas_ta as ta
from coinbase.rest import RESTClient
import warnings

# Suppress SettingWithCopyWarning, which is common with pandas-ta
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


# --- Configuration ---
# List of assets to monitor
PRODUCT_IDS = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD"] 
GRANULARITY = "ONE_DAY"
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
    """
    Fetches historical candlestick data from Coinbase for a single asset.
    """
    print(f"Fetching data for {product_id}...")
    try:
        client = RESTClient()
        end_time = int(time.time())
        start_time = end_time - (years * 365 * 86400)
        
        print(f"  Time range: {pd.to_datetime(start_time, unit='s').date()} to {pd.to_datetime(end_time, unit='s').date()}")
        print(f"  Estimated total days: {(end_time - start_time) / 86400:.0f}")
        print(f"  Estimated API calls needed: {((end_time - start_time) / 86400 / 300):.1f}")

        all_candles = []
        current_start = start_time
        batch_count = 0
        
        while current_start < end_time:
            batch_count += 1
            current_end = current_start + (300 * 86400)
            if current_end > end_time:
                current_end = end_time

            print(f"  Batch {batch_count}: Fetching from {pd.to_datetime(current_start, unit='s').date()} to {pd.to_datetime(current_end, unit='s').date()}...")

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
            print(f"No data returned from Coinbase for {product_id}.")
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
        
        return df

    except Exception as e:
        print(f"An error occurred while fetching data for {product_id}: {e}")
        return None

def calculate_indicators(df):
    """Calculates all necessary technical indicators for a given DataFrame."""
    if df is None:
        return None
    df.ta.sma(length=SHORT_WINDOW, append=True)
    df.ta.sma(length=LONG_WINDOW, append=True)
    df.ta.rsi(length=RSI_PERIOD, append=True)
    df.ta.macd(fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL, append=True)
    df.ta.atr(length=ATR_PERIOD, append=True)
    return df

def generate_signals(df):
    """Generates buy/sell/hold signals based on the 3-factor confluence strategy."""
    if df is None:
        return None
    short_sma_col = f'SMA_{SHORT_WINDOW}'
    long_sma_col = f'SMA_{LONG_WINDOW}'
    rsi_col = f'RSI_{RSI_PERIOD}'
    macd_line_col = f'MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}'
    macd_signal_col = f'MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}'
    
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

def main():
    """
    Main function to run the multi-asset analysis and print a summary report.
    """
    print("--- Crypto Analysis Bot: Multi-Asset Market Scanner ---")
    
    results = []
    
    for product_id in PRODUCT_IDS:
        data = get_historical_data(product_id, GRANULARITY, years=1)
        
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            data.dropna(inplace=True)
            data = generate_signals(data)
            
            latest_row = data.iloc[-1]
            results.append({'product_id': product_id, 'latest_row': latest_row})
        else:
            print(f"Could not process {product_id}, skipping.")
            
    # --- Print Summary Report ---
    print("\n" + "="*60)
    print(" " * 15 + "MULTI-ASSET SIGNAL SUMMARY")
    print("="*60)
    
    for result in results:
        product_id = result['product_id']
        latest_row = result['latest_row']
        latest_signal = latest_row['Signal']
        latest_close_price = latest_row['Close']
        latest_timestamp = latest_row.name

        signal_text = "HOLD"
        if latest_signal == 1:
            signal_text = "BUY"
        elif latest_signal == -1:
            signal_text = "SELL"
            
        print(f"\n--- {product_id} ---")
        print(f"  Timestamp: {latest_timestamp.strftime('%Y-%m-%d')}")
        print(f"  Last Close: ${latest_close_price:,.2f}")
        print(f"  Signal: {signal_text}")

        if latest_signal == 1:
            atr_col = f'ATRr_{ATR_PERIOD}'
            latest_atr = latest_row[atr_col]
            stop_loss_price = latest_close_price - (latest_atr * ATR_STOP_LOSS_MULTIPLIER)
            
            capital_to_risk = HYPOTHETICAL_PORTFOLIO_SIZE * (RISK_PER_TRADE_PERCENTAGE / 100)
            stop_loss_distance = latest_close_price - stop_loss_price
            
            if stop_loss_distance > 0:
                position_size_crypto = capital_to_risk / stop_loss_distance
                position_size_usd = position_size_crypto * latest_close_price

                print("  --- Suggested Trade Plan ---")
                print(f"    Stop-Loss: ${stop_loss_price:,.2f}")
                print(f"    Position Size: {position_size_crypto:.6f} {product_id.split('-')[0]} (${position_size_usd:,.2f})")

    print("\n" + "="*60)
    print("--- Analysis Complete ---")

if __name__ == "__main__":
    main()
