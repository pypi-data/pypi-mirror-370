# milestone_5_backtest.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import the core logic functions and asset list from the main milestone file
from milestone_5 import get_historical_data, calculate_indicators, generate_signals
from milestone_5 import PRODUCT_IDS, GRANULARITY, SHORT_WINDOW, LONG_WINDOW, RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL, ATR_PERIOD, ATR_STOP_LOSS_MULTIPLIER, RISK_PER_TRADE_PERCENTAGE

# --- Configuration for Backtest ---
INITIAL_CAPITAL = 100000.0

def run_backtest(df, initial_capital):
    """
    Runs a single-asset backtest simulation with ATR-based stop-loss and position sizing.
    """
    portfolio_value = initial_capital
    cash = initial_capital
    crypto_holdings = 0.0
    active_trade = False
    stop_loss_price = 0.0
    portfolio_history = []
    trades = []
    atr_col = f'ATRr_{ATR_PERIOD}'

    for index, row in df.iterrows():
        if active_trade:
            if row['Low'] <= stop_loss_price:
                exit_price = stop_loss_price
                cash += crypto_holdings * exit_price
                trades.append({'type': 'STOP-LOSS', 'date': index, 'price': exit_price, 'size': crypto_holdings})
                crypto_holdings = 0.0
                active_trade = False
                portfolio_value = cash
            elif row['Signal'] == -1:
                exit_price = row['Close']
                cash += crypto_holdings * exit_price
                trades.append({'type': 'SELL', 'date': index, 'price': exit_price, 'size': crypto_holdings})
                crypto_holdings = 0.0
                active_trade = False
                portfolio_value = cash
        elif not active_trade and row['Signal'] == 1:
            entry_price = row['Close']
            current_atr = row[atr_col]
            stop_loss_price = entry_price - (current_atr * ATR_STOP_LOSS_MULTIPLIER)
            capital_to_risk = portfolio_value * (RISK_PER_TRADE_PERCENTAGE / 100)
            stop_loss_distance = entry_price - stop_loss_price
            if stop_loss_distance > 0:
                position_size = capital_to_risk / stop_loss_distance
                if cash >= position_size * entry_price:
                    crypto_holdings = position_size
                    cash -= crypto_holdings * entry_price
                    active_trade = True
                    trades.append({'type': 'BUY', 'date': index, 'price': entry_price, 'size': crypto_holdings})
        
        current_portfolio_value = cash + (crypto_holdings * row['Close'])
        portfolio_history.append(current_portfolio_value)
        if not active_trade:
            portfolio_value = current_portfolio_value

    df['Portfolio_Value'] = portfolio_history
    return df, trades

def analyze_performance(df, trades, initial_capital, product_id):
    """
    Analyzes and prints the performance of the backtest for a single asset.
    """
    print(f"\n--- Backtest Performance Analysis: {product_id} ---")
    
    final_portfolio_value = df['Portfolio_Value'].iloc[-1]
    total_return_pct = ((final_portfolio_value - initial_capital) / initial_capital) * 100
    buy_and_hold_return_pct = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    
    print(f"  Initial Capital: ${initial_capital:,.2f}")
    print(f"  Final Portfolio Value: ${final_portfolio_value:,.2f}")
    print(f"  Total Return (Strategy): {total_return_pct:.2f}%")
    print(f"  Total Return (Buy & Hold): {buy_and_hold_return_pct:.2f}%")
    
    buy_trades = [t for t in trades if t['type'] == 'BUY']
    sell_trades = [t for t in trades if t['type'] in ['SELL', 'STOP-LOSS']]
    
    if len(buy_trades) > 0 and len(sell_trades) > 0:
        wins, losses, total_profit, total_loss = 0, 0, 0, 0
        num_cycles = min(len(buy_trades), len(sell_trades))
        
        for i in range(num_cycles):
            buy_price = buy_trades[i]['price']
            sell_price = sell_trades[i]['price']
            if sell_price > buy_price:
                wins += 1
                total_profit += (sell_price - buy_price) * buy_trades[i]['size']
            else:
                losses += 1
                total_loss += (buy_price - sell_price) * buy_trades[i]['size']

        total_trades = wins + losses
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        avg_win = total_profit / wins if wins > 0 else 0
        avg_loss = total_loss / losses if losses > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        print(f"  Total Trades: {total_trades}, Wins: {wins}, Losses: {losses}")
        print(f"  Win Rate: {win_rate:.2f}% | Profit Factor: {profit_factor:.2f}")

def plot_results(df, trades, product_id):
    """
    Plots the results of the backtest for a single asset.
    """
    print(f"  Generating plot for {product_id}...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True, 
                                   gridspec_kw={'height_ratios': [2, 1]})
    
    ax1.plot(df.index, df['Close'], label='Close Price', color='skyblue', linewidth=1.5, zorder=1)
    
    buy_signals = [t for t in trades if t['type'] == 'BUY']
    sell_signals = [t for t in trades if t['type'] == 'SELL']
    stop_signals = [t for t in trades if t['type'] == 'STOP-LOSS']
    
    ax1.plot([s['date'] for s in buy_signals], [s['price'] for s in buy_signals], '^', markersize=10, color='green', label='Buy', zorder=2)
    ax1.plot([s['date'] for s in sell_signals], [s['price'] for s in sell_signals], 'v', markersize=10, color='blue', label='Sell (Signal)', zorder=2)
    ax1.plot([s['date'] for s in stop_signals], [s['price'] for s in stop_signals], 'x', markersize=10, color='red', label='Sell (Stop-Loss)', zorder=2)
    
    ax1.set_title(f'{product_id} Backtest with Risk Management')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    ax2.plot(df.index, df['Portfolio_Value'], label='Strategy Portfolio Value', color='blue', linewidth=2)
    buy_and_hold_value = (df['Close'] / df['Close'].iloc[0]) * INITIAL_CAPITAL
    ax2.plot(df.index, buy_and_hold_value, label='Buy & Hold Portfolio Value', color='grey', linestyle='--', linewidth=1.5)
    
    ax2.set_title('Portfolio Value Over Time')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Portfolio Value (USD)')
    ax2.legend()
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to run the backtesting script for each asset in the list.
    """
    print("--- Crypto Analysis Bot: Multi-Asset Backtesting ---")
    
    for product_id in PRODUCT_IDS:
        print("\n" + "="*60)
        print(f" " * 15 + f"STARTING BACKTEST FOR: {product_id}")
        print("="*60)
        
        data = get_historical_data(product_id, GRANULARITY, years=3)
        
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            data.dropna(inplace=True)
            data = generate_signals(data)
            
            data, trades = run_backtest(data.copy(), INITIAL_CAPITAL)
            
            analyze_performance(data, trades, INITIAL_CAPITAL, product_id)
            plot_results(data, trades, product_id)
        else:
            print(f"Could not backtest {product_id}, skipping.")
    
    print("\n--- All Backtests Complete ---")

if __name__ == "__main__":
    main()
