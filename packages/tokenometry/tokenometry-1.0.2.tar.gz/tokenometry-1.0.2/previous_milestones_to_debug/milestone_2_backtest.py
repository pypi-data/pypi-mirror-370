# milestone_2_backtest.py

import time
import pandas as pd
import pandas_ta as ta
import numpy as np
from coinbase.rest import RESTClient
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- Configuration ---
PRODUCT_ID = "BTC-USD"
GRANULARITY = "ONE_DAY"
SHORT_WINDOW = 50
LONG_WINDOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
INITIAL_CAPITAL = 10000.0  # Start with $10,000

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

def run_backtest(df, initial_capital):
    """
    Runs a backtest simulation on the generated signals.
    """
    print("Running backtest simulation...")
    cash = initial_capital
    crypto_holdings = 0.0
    portfolio_values = []
    trades = []
    position = 'OUT'
    
    for index, row in df.iterrows():
        close_price = row['Close']
        
        if row['Signal'] == 1 and position == 'OUT':
            crypto_holdings = cash / close_price
            cash = 0.0
            position = 'IN'
            trades.append({'type': 'BUY', 'date': index, 'price': close_price})
        
        elif row['Signal'] == -1 and position == 'IN':
            cash = crypto_holdings * close_price
            crypto_holdings = 0.0
            position = 'OUT'
            trades.append({'type': 'SELL', 'date': index, 'price': close_price})

        portfolio_values.append(cash + (crypto_holdings * close_price))
        
    df['Portfolio_Value'] = portfolio_values
    return df, trades

def analyze_performance(df, trades, initial_capital):
    """
    Analyzes and prints the performance of the backtest.
    """
    print("\n--- Backtest Performance Analysis (SMA + RSI Strategy) ---")
    
    final_portfolio_value = df['Portfolio_Value'].iloc[-1]
    total_return_pct = ((final_portfolio_value - initial_capital) / initial_capital) * 100
    buy_and_hold_return_pct = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Portfolio Value: ${final_portfolio_value:,.2f}")
    print(f"Total Return (Strategy): {total_return_pct:.2f}%")
    print(f"Total Return (Buy & Hold): {buy_and_hold_return_pct:.2f}%")
    
    if len(trades) > 1:
        profitable_trades = 0
        total_trades = 0
        for i in range(len(trades)):
            if trades[i]['type'] == 'SELL':
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

def plot_results(df, trades, short_window, long_window, rsi_period):
    """
    Plots the results of the backtest, including the RSI indicator.
    """
    print("\nGenerating plot...")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 18), sharex=True, 
                                       gridspec_kw={'height_ratios': [3, 1, 2]})
    
    # --- Plot 1: Price and Signals ---
    ax1.plot(df.index, df['Close'], label='Close Price', color='skyblue', linewidth=1.5)
    ax1.plot(df.index, df[f'SMA_{short_window}'], label=f'{short_window}-Day SMA', color='orange', linestyle='--', linewidth=1)
    ax1.plot(df.index, df[f'SMA_{long_window}'], label=f'{long_window}-Day SMA', color='purple', linestyle='--', linewidth=1)
    
    buy_signals = [trade for trade in trades if trade['type'] == 'BUY']
    sell_signals = [trade for trade in trades if trade['type'] == 'SELL']
    
    ax1.plot([s['date'] for s in buy_signals], [s['price'] for s in buy_signals], '^', markersize=10, color='green', label='Buy Signal')
    ax1.plot([s['date'] for s in sell_signals], [s['price'] for s in sell_signals], 'v', markersize=10, color='red', label='Sell Signal')
    
    ax1.set_title(f'{PRODUCT_ID} Price, Moving Averages, and Trade Signals')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # --- Plot 2: RSI ---
    rsi_col = f'RSI_{rsi_period}'
    ax2.plot(df.index, df[rsi_col], label=f'RSI ({rsi_period})', color='teal', linewidth=1.5)
    ax2.axhline(RSI_OVERBOUGHT, color='red', linestyle='--', linewidth=1, label=f'Overbought ({RSI_OVERBOUGHT})')
    ax2.axhline(RSI_OVERSOLD, color='green', linestyle='--', linewidth=1, label=f'Oversold ({RSI_OVERSOLD})')
    ax2.fill_between(df.index, RSI_OVERBOUGHT, RSI_OVERSOLD, color='#e8f5e9', alpha=0.5)
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.set_ylabel('RSI Value')
    ax2.legend(loc='upper left')
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

    # --- Plot 3: Portfolio Value ---
    ax3.plot(df.index, df['Portfolio_Value'], label='Strategy Portfolio Value', color='blue', linewidth=2)
    buy_and_hold_value = (df['Close'] / df['Close'].iloc[0]) * INITIAL_CAPITAL
    ax3.plot(df.index, buy_and_hold_value, label='Buy & Hold Portfolio Value', color='grey', linestyle='--', linewidth=1.5)
    
    ax3.set_title('Portfolio Value Over Time')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Portfolio Value (USD)')
    ax3.legend()
    ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Improve date formatting on x-axis
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to run the backtesting script.
    """
    print("--- Crypto Analysis Bot: Backtesting Milestone 2 ---")
    
    data = get_historical_data(PRODUCT_ID, GRANULARITY, years=3)
    
    if data is not None and not data.empty:
        data = calculate_indicators(data, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD)
        data.dropna(inplace=True) # Drop NaNs created by indicators
        
        data = generate_signals(data, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD)
        
        data, trades = run_backtest(data.copy(), INITIAL_CAPITAL)
        
        analyze_performance(data, trades, INITIAL_CAPITAL)
        
        plot_results(data, trades, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD)
    
    print("\n--- Backtest Complete ---")

if __name__ == "__main__":
    main()
