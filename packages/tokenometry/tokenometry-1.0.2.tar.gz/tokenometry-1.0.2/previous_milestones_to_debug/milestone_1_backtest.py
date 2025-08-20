# backtest_milestone_1.py

import time
import pandas as pd
import pandas_ta as ta
import numpy as np
from coinbase.rest import RESTClient
import matplotlib.pyplot as plt

# --- Configuration ---
PRODUCT_ID = "BTC-USD"
GRANULARITY = "ONE_DAY"
SHORT_WINDOW = 50
LONG_WINDOW = 200
INITIAL_CAPITAL = 10000.0  # Start with $10,000

def get_historical_data(product_id, granularity, years=3):
    """
    Fetches historical candlestick data from Coinbase for a specified number of years.

    Args:
        product_id (str): The trading pair (e.g., 'BTC-USD').
        granularity (str): The candle timeframe (e.g., 'ONE_DAY').
        years (int): The number of years of historical data to fetch.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the historical data,
                      or None if the request fails.
        """
    print(f"Fetching last {years} years of historical data for {product_id}...")
    try:
        client = RESTClient()
        
        # Calculate start and end times
        end_time = int(time.time())
        # Seconds in a day: 86400
        start_time = end_time - (years * 365 * 86400)
        
        print(f"Time range: {pd.to_datetime(start_time, unit='s').date()} to {pd.to_datetime(end_time, unit='s').date()}")
        print(f"Estimated total days: {(end_time - start_time) / 86400:.0f}")
        print(f"Estimated API calls needed: {((end_time - start_time) / 86400 / 300):.1f}")

        # The API returns a max of 300 candles per request. We'll need to paginate.
        all_candles = []
        current_start = start_time
        batch_count = 0
        
        while current_start < end_time:
            batch_count += 1
            # Calculate the end for this specific request (300 candles worth of time)
            # For daily granularity, 300 days = 300 * 86400 seconds
            current_end = current_start + (300 * 86400)  # 300 days for daily granularity
            if current_end > end_time:
                current_end = end_time

            print(f"Batch {batch_count}: Fetching from {pd.to_datetime(current_start, unit='s').date()} to {pd.to_datetime(current_end, unit='s').date()}...")

            # Use get_public_candles for public data access
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
                print("No more data in this batch or an error occurred.")
                break # No more data to fetch
            
            all_candles.extend(candles)
            
            # Move to the next batch by advancing 300 days (not 1 day)
            # This ensures we fetch the next 300 candles without overlap
            current_start = current_end
            time.sleep(0.5) # Add a small delay to avoid hitting rate limits

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
        
        # Remove duplicate timestamps and sort
        df.drop_duplicates(subset='timestamp', inplace=True)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)

        print(f"Data fetched successfully. Total candles: {len(df)}")
        return df

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None

def calculate_moving_averages(df, short_window, long_window):
    """Calculates short-term and long-term Simple Moving Averages (SMAs)."""
    print("Calculating moving averages...")
    df.ta.sma(length=short_window, append=True)
    df.ta.sma(length=long_window, append=True)
    return df

def generate_signals(df, short_window, long_window):
    """Generates buy and sell signals based on SMA crossovers."""
    print("Generating trading signals...")
    short_sma_col = f'SMA_{short_window}'
    long_sma_col = f'SMA_{long_window}'
    
    df['Signal'] = 0
    
    # Generate the buy signal (Golden Cross)
    buy_condition = (df[short_sma_col] > df[long_sma_col]) & \
                    (df[short_sma_col].shift(1) <= df[long_sma_col].shift(1))
    df.loc[buy_condition, 'Signal'] = 1

    # Generate the sell signal (Death Cross)
    sell_condition = (df[short_sma_col] < df[long_sma_col]) & \
                     (df[short_sma_col].shift(1) >= df[long_sma_col].shift(1))
    df.loc[sell_condition, 'Signal'] = -1
    
    return df

def run_backtest(df, initial_capital):
    """
    Runs a backtest simulation on the generated signals.
    """
    print("Running backtest simulation...")
    cash = initial_capital
    crypto_holdings = 0.0
    portfolio_values = []
    trades = []
    position = 'OUT' # Can be 'IN' or 'OUT'
    
    for index, row in df.iterrows():
        close_price = row['Close']
        
        # Buy Signal
        if row['Signal'] == 1 and position == 'OUT':
            crypto_holdings = cash / close_price
            cash = 0.0
            position = 'IN'
            trades.append({'type': 'BUY', 'date': index, 'price': close_price})
        
        # Sell Signal
        elif row['Signal'] == -1 and position == 'IN':
            cash = crypto_holdings * close_price
            crypto_holdings = 0.0
            position = 'OUT'
            trades.append({'type': 'SELL', 'date': index, 'price': close_price})

        # Calculate portfolio value for this day
        portfolio_values.append(cash + (crypto_holdings * close_price))
        
    df['Portfolio_Value'] = portfolio_values
    return df, trades

def analyze_performance(df, trades, initial_capital):
    """
    Analyzes and prints the performance of the backtest.
    """
    print("\n--- Backtest Performance Analysis ---")
    
    final_portfolio_value = df['Portfolio_Value'].iloc[-1]
    total_return_pct = ((final_portfolio_value - initial_capital) / initial_capital) * 100
    
    # Buy and Hold strategy for comparison
    buy_and_hold_return_pct = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Portfolio Value: ${final_portfolio_value:,.2f}")
    print(f"Total Return (Strategy): {total_return_pct:.2f}%")
    print(f"Total Return (Buy & Hold): {buy_and_hold_return_pct:.2f}%")
    
    # Calculate Win Rate
    if len(trades) > 1:
        profitable_trades = 0
        total_trades = 0
        for i in range(len(trades)):
            if trades[i]['type'] == 'SELL':
                # The corresponding buy trade is the one before it
                buy_price = trades[i-1]['price']
                sell_price = trades[i]['price']
                if sell_price > buy_price:
                    profitable_trades += 1
                total_trades += 1
        
        win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
        print(f"\nTotal Trades (Buy/Sell cycles): {total_trades}")
        print(f"Profitable Trades: {profitable_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
    else:
        print("\nNot enough trades to calculate win rate.")

def plot_results(df, trades, short_window, long_window):
    """
    Plots the results of the backtest.
    """
    print("\nGenerating plot...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True)
    
    # --- Plot 1: Price and Signals ---
    ax1.plot(df.index, df['Close'], label='Close Price', color='skyblue', linewidth=1.5)
    ax1.plot(df.index, df[f'SMA_{short_window}'], label=f'{short_window}-Day SMA', color='orange', linestyle='--', linewidth=1)
    ax1.plot(df.index, df[f'SMA_{long_window}'], label=f'{long_window}-Day SMA', color='purple', linestyle='--', linewidth=1)
    
    buy_signals = [trade for trade in trades if trade['type'] == 'BUY']
    sell_signals = [trade for trade in trades if trade['type'] == 'SELL']
    
    ax1.plot([s['date'] for s in buy_signals], [s['price'] for s in buy_signals], '^', markersize=10, color='green', label='Buy Signal (Golden Cross)')
    ax1.plot([s['date'] for s in sell_signals], [s['price'] for s in sell_signals], 'v', markersize=10, color='red', label='Sell Signal (Death Cross)')
    
    ax1.set_title(f'{PRODUCT_ID} Price, Moving Averages, and Trade Signals')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # --- Plot 2: Portfolio Value ---
    ax2.plot(df.index, df['Portfolio_Value'], label='Strategy Portfolio Value', color='blue', linewidth=2)
    
    # Calculate Buy & Hold portfolio value
    buy_and_hold_value = (df['Close'] / df['Close'].iloc[0]) * INITIAL_CAPITAL
    ax2.plot(df.index, buy_and_hold_value, label='Buy & Hold Portfolio Value', color='grey', linestyle='--', linewidth=1.5)
    
    ax2.set_title('Portfolio Value Over Time')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Portfolio Value (USD)')
    ax2.legend()
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to run the backtesting script.
    """
    print("--- Crypto Analysis Bot: Backtesting ---")
    
    data = get_historical_data(PRODUCT_ID, GRANULARITY, years=3)
    
    if data is not None and not data.empty:
        data.dropna(inplace=True)
        data = calculate_moving_averages(data, SHORT_WINDOW, LONG_WINDOW)
        data = generate_signals(data, SHORT_WINDOW, LONG_WINDOW)
        
        # Drop rows with NaN values created by the long SMA
        data.dropna(inplace=True)
        
        data, trades = run_backtest(data.copy(), INITIAL_CAPITAL)
        
        analyze_performance(data, trades, INITIAL_CAPITAL)
        
        plot_results(data, trades, SHORT_WINDOW, LONG_WINDOW)
    
    print("\n--- Backtest Complete ---")

if __name__ == "__main__":
    main()
