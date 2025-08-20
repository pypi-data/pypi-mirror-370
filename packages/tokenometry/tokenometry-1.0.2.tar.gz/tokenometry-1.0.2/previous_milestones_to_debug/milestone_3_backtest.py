# milestone_3_backtest.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import the core logic functions from the main milestone file
from milestone_3 import get_historical_data, calculate_indicators, generate_signals
from milestone_3 import PRODUCT_ID, GRANULARITY, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL

# --- Configuration for Backtest ---
INITIAL_CAPITAL = 10000.0

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
    print("\n--- Backtest Performance Analysis (SMA + RSI + MACD Strategy) ---")
    
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

def plot_results(df, trades):
    """
    Plots the results of the backtest, including Price, RSI, MACD, and Portfolio Value.
    """
    print("\nGenerating plot...")
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 20), sharex=True, 
                                       gridspec_kw={'height_ratios': [3, 1, 1, 2]})
    
    # --- Plot 1: Price and Signals ---
    ax1.plot(df.index, df['Close'], label='Close Price', color='skyblue', linewidth=1.5)
    ax1.plot(df.index, df[f'SMA_{SHORT_WINDOW}'], label=f'{SHORT_WINDOW}-Day SMA', color='orange', linestyle='--', linewidth=1)
    ax1.plot(df.index, df[f'SMA_{LONG_WINDOW}'], label=f'{LONG_WINDOW}-Day SMA', color='purple', linestyle='--', linewidth=1)
    
    buy_signals = [trade for trade in trades if trade['type'] == 'BUY']
    sell_signals = [trade for trade in trades if trade['type'] == 'SELL']
    
    ax1.plot([s['date'] for s in buy_signals], [s['price'] for s in buy_signals], '^', markersize=10, color='green', label='Buy Signal')
    ax1.plot([s['date'] for s in sell_signals], [s['price'] for s in sell_signals], 'v', markersize=10, color='red', label='Sell Signal')
    
    ax1.set_title(f'{PRODUCT_ID} Price, Moving Averages, and Trade Signals')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # --- Plot 2: RSI ---
    ax2.plot(df.index, df[f'RSI_{RSI_PERIOD}'], label=f'RSI ({RSI_PERIOD})', color='teal', linewidth=1.5)
    ax2.axhline(70, color='red', linestyle='--', linewidth=1, label='Overbought (70)')
    ax2.axhline(30, color='green', linestyle='--', linewidth=1, label='Oversold (30)')
    ax2.fill_between(df.index, 70, 30, color='#e8f5e9', alpha=0.5)
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.set_ylabel('RSI Value')
    ax2.legend(loc='upper left')
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

    # --- Plot 3: MACD ---
    macd_line_col = f'MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}'
    macd_signal_col = f'MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}'
    macd_hist_col = f'MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}'
    ax3.plot(df.index, df[macd_line_col], label='MACD Line', color='blue', linewidth=1.5)
    ax3.plot(df.index, df[macd_signal_col], label='Signal Line', color='red', linestyle='--', linewidth=1.5)
    colors = ['g' if v >= 0 else 'r' for v in df[macd_hist_col]]
    ax3.bar(df.index, df[macd_hist_col], label='Histogram', color=colors, width=0.7, alpha=0.6)
    ax3.set_title('Moving Average Convergence Divergence (MACD)')
    ax3.set_ylabel('MACD Value')
    ax3.legend(loc='upper left')
    ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # --- Plot 4: Portfolio Value ---
    ax4.plot(df.index, df['Portfolio_Value'], label='Strategy Portfolio Value', color='blue', linewidth=2)
    buy_and_hold_value = (df['Close'] / df['Close'].iloc[0]) * INITIAL_CAPITAL
    ax4.plot(df.index, buy_and_hold_value, label='Buy & Hold Portfolio Value', color='grey', linestyle='--', linewidth=1.5)
    
    ax4.set_title('Portfolio Value Over Time')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Portfolio Value (USD)')
    ax4.legend()
    ax4.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to run the backtesting script.
    """
    print("--- Crypto Analysis Bot: Backtesting Milestone 3 ---")
    
    # Fetch 3 years of data for a comprehensive backtest
    data = get_historical_data(PRODUCT_ID, GRANULARITY, years=3)
    
    if data is not None and not data.empty:
        data = calculate_indicators(data)
        data.dropna(inplace=True)
        
        data = generate_signals(data)
        
        data, trades = run_backtest(data.copy(), INITIAL_CAPITAL)
        
        analyze_performance(data, trades, INITIAL_CAPITAL)
        
        plot_results(data, trades)
    
    print("\n--- Backtest Complete ---")

if __name__ == "__main__":
    main()
