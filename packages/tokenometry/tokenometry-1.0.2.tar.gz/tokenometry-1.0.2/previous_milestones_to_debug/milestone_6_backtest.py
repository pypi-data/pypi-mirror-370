# milestone_6_backtest.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from milestone_6 import (get_historical_data, calculate_indicators, 
                         generate_signals, PRODUCT_IDS, GRANULARITY_SIGNAL, 
                         GRANULARITY_TREND, TREND_SMA_PERIOD, ATR_PERIOD, 
                         ATR_STOP_LOSS_MULTIPLIER, RISK_PER_TRADE_PERCENTAGE)

INITIAL_CAPITAL = 100000.0

def prepare_mta_data(product_id, years=3):
    """Fetches and merges daily and weekly data for MTA backtesting."""
    print(f"Preparing MTA data for {product_id}...")
    df_daily = get_historical_data(product_id, GRANULARITY_SIGNAL, years=years)
    df_weekly = get_historical_data(product_id, GRANULARITY_TREND, years=years+1) # Fetch extra year for SMA
    
    if df_daily is None or df_weekly is None:
        return None
        
    # Calculate weekly trend
    trend_sma_col = f'SMA_{TREND_SMA_PERIOD}'
    df_weekly.ta.sma(length=TREND_SMA_PERIOD, append=True)
    df_weekly['Trend'] = 'Bearish'
    df_weekly.loc[df_weekly['Close'] > df_weekly[trend_sma_col], 'Trend'] = 'Bullish'
    
    # Merge trend data into daily data
    # Forward-fill the weekly trend so each day knows the trend of its week
    df_merged = pd.merge_asof(df_daily.sort_index(), df_weekly[['Trend']].sort_index(), 
                              left_index=True, right_index=True, direction='backward')
    return df_merged

def run_mta_backtest(df, initial_capital):
    """Runs a backtest simulation using the MTA filter."""
    print("Running MTA backtest simulation...")
    portfolio_value = initial_capital
    cash, crypto_holdings = initial_capital, 0.0
    active_trade, stop_loss_price = False, 0.0
    portfolio_history, trades = [], []
    atr_col = f'ATRr_{ATR_PERIOD}'

    for index, row in df.iterrows():
        # --- Active Trade Management ---
        if active_trade:
            if row['Low'] <= stop_loss_price:
                exit_price = stop_loss_price
                cash += crypto_holdings * exit_price
                trades.append({'type': 'STOP-LOSS', 'date': index, 'price': exit_price})
                crypto_holdings, active_trade = 0.0, False
                portfolio_value = cash
            # Exit on sell signal ONLY if trend is bearish
            elif row['Signal'] == -1 and row['Trend'] == 'Bearish':
                exit_price = row['Close']
                cash += crypto_holdings * exit_price
                trades.append({'type': 'SELL', 'date': index, 'price': exit_price})
                crypto_holdings, active_trade = 0.0, False
                portfolio_value = cash

        # --- New Trade Entry ---
        # Enter on buy signal ONLY if trend is bullish
        elif not active_trade and row['Signal'] == 1 and row['Trend'] == 'Bullish':
            entry_price = row['Close']
            stop_loss_price = entry_price - (row[atr_col] * ATR_STOP_LOSS_MULTIPLIER)
            capital_to_risk = portfolio_value * (RISK_PER_TRADE_PERCENTAGE / 100)
            stop_loss_distance = entry_price - stop_loss_price
            if stop_loss_distance > 0:
                position_size = capital_to_risk / stop_loss_distance
                if cash >= position_size * entry_price:
                    crypto_holdings = position_size
                    cash -= crypto_holdings * entry_price
                    active_trade = True
                    trades.append({'type': 'BUY', 'date': index, 'price': entry_price})
        
        current_portfolio_value = cash + (crypto_holdings * row['Close'])
        portfolio_history.append(current_portfolio_value)
        if not active_trade:
            portfolio_value = current_portfolio_value

    df['Portfolio_Value'] = portfolio_history
    return df, trades

def analyze_performance(df, trades, initial_capital, product_id):
    """Analyzes and prints the performance of the MTA backtest."""
    print(f"\n--- MTA Backtest Performance: {product_id} ---")
    final_value = df['Portfolio_Value'].iloc[-1]
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    bh_return = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
    
    print(f"  Return (Strategy): {total_return:.2f}% | Return (Buy & Hold): {bh_return:.2f}%")
    
    buy_trades = [t for t in trades if t['type'] == 'BUY']
    sell_trades = [t for t in trades if t['type'] in ['SELL', 'STOP-LOSS']]
    
    if len(buy_trades) > 0 and len(sell_trades) > 0:
        wins, losses = 0, 0
        num_cycles = min(len(buy_trades), len(sell_trades))
        for i in range(num_cycles):
            if sell_trades[i]['price'] > buy_trades[i]['price']: wins += 1
            else: losses += 1
        total_trades = wins + losses
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        print(f"  Total Trades: {total_trades}, Wins: {wins}, Losses: {losses}, Win Rate: {win_rate:.2f}%")

def plot_results(df, trades, product_id):
    """Plots the results of the MTA backtest."""
    print(f"  Generating plot for {product_id}...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    
    ax1.plot(df.index, df['Close'], label='Close Price', color='skyblue', lw=1.5, zorder=1)
    # Shade background based on long-term trend
    ax1.fill_between(df.index, 0, df['Close'].max()*1.2, where=df['Trend']=='Bullish', color='green', alpha=0.1, label='Bullish Trend')
    ax1.fill_between(df.index, 0, df['Close'].max()*1.2, where=df['Trend']=='Bearish', color='red', alpha=0.1, label='Bearish Trend')

    buy_signals = [t for t in trades if t['type'] == 'BUY']
    sell_signals = [t for t in trades if t['type'] == 'SELL']
    stop_signals = [t for t in trades if t['type'] == 'STOP-LOSS']
    
    ax1.plot([s['date'] for s in buy_signals], [s['price'] for s in buy_signals], '^', ms=10, color='lime', label='Buy', zorder=2)
    ax1.plot([s['date'] for s in sell_signals], [s['price'] for s in sell_signals], 'v', ms=10, color='blue', label='Sell (Signal)', zorder=2)
    ax1.plot([s['date'] for s in stop_signals], [s['price'] for s in stop_signals], 'x', ms=10, color='maroon', label='Sell (Stop-Loss)', zorder=2)
    
    ax1.set_title(f'{product_id} MTA Backtest')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True, which='both', ls='--', lw=0.5)

    ax2.plot(df.index, df['Portfolio_Value'], label='Strategy Portfolio Value', color='blue', lw=2)
    ax2.plot(df.index, (df['Close'] / df['Close'].iloc[0]) * INITIAL_CAPITAL, label='Buy & Hold', color='grey', ls='--', lw=1.5)
    ax2.set_title('Portfolio Value Over Time')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Portfolio Value (USD)')
    ax2.legend()
    ax2.grid(True, which='both', ls='--', lw=0.5)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()

def main():
    """Main function to run the MTA backtesting script for each asset."""
    print("--- Crypto Analysis Bot: Multi-Asset MTA Backtesting ---")
    for product_id in PRODUCT_IDS:
        print("\n" + "="*60 + f"\nSTARTING BACKTEST FOR: {product_id}\n" + "="*60)
        data = prepare_mta_data(product_id, years=3)
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            data.dropna(inplace=True)
            data = generate_signals(data)
            data, trades = run_mta_backtest(data.copy(), INITIAL_CAPITAL)
            analyze_performance(data, trades, INITIAL_CAPITAL, product_id)
            plot_results(data, trades, product_id)
        else:
            print(f"Could not backtest {product_id}, skipping.")
    print("\n--- All Backtests Complete ---")

if __name__ == "__main__":
    main()
