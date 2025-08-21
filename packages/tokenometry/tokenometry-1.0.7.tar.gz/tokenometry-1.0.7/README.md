# Tokenometry

A tool that measures and analyzes all the critical data points of a crypto token—such as its price, volume, volatility, and market sentiment—to help users make informed decisions.

NOTE: in the 1.0.7 I removed the external API to fectch the data for Sentiment. It slows down the process, the code is still in `main_milesstone` in case you want to take a look.

## Crypto Analysis Bot

This repository contains a sophisticated, multi-strategy crypto analysis bot written in Python. The bot is designed to scan the cryptocurrency market, apply a range of analytical models, and generate trading signals based on a confluence of technical, sentiment, and on-chain data. It is architected to be flexible, allowing the user to switch between long-term investment, swing trading, and high-frequency day trading strategies.

## Features

* **Multi-Asset Scanning**: Monitors a configurable list of cryptocurrencies from Coinbase.
* **Multi-Timeframe Analysis (MTA)**: Establishes a long-term trend on a higher timeframe to filter and confirm signals on a lower timeframe.
* **Multi-Factor Signal Confirmation**:
    * **Technical Analysis**: Utilizes a robust combination of indicators, including Exponential Moving Averages (EMAs), the Relative Strength Index (RSI), and the Moving Average Convergence Divergence (MACD).
    * **Volume Filter**: Optional volume spike confirmation to improve signal quality and reduce false signals.
    * **Signal Strength Analysis**: Advanced scoring system that rates signal quality as "Low", "Medium", or "Strong" based on RSI extremity, MACD momentum, and volume conviction.
    * **News Sentiment Analysis**: Integrates with NewsAPI to gauge the prevailing market narrative and filter signals that run contrary to strong market sentiment.
    * **On-Chain Analysis**: Connects to the Glassnode API to analyze fundamental investor behavior, such as accumulation or distribution patterns based on exchange net flows.
* **Automated & Continuous Operation**: Designed to run 24/7 on a server, with a configurable analysis frequency and comprehensive logging for performance tracking and debugging.
* **Dynamic Risk Management**: Automatically calculates a suggested stop-loss and position size for every BUY signal based on market volatility (using the Average True Range - ATR) and a predefined risk percentage.
* **Secure Configuration**: All API keys and sensitive information are managed securely using an `.env` file.

## Signal Strength Analysis

When a valid BUY or SELL signal is found, the bot now performs a secondary analysis to score its strength based on three key factors:

### RSI Extremity
How deep into "oversold" or "overbought" territory is the RSI? A signal that occurs when the RSI is below 30 (for a buy) is stronger than one that occurs when it's at 50.

### MACD Momentum
What is the momentum behind the crossover? This is measured by the MACD Histogram (the distance between the MACD line and its signal line). A large, expanding histogram indicates powerful momentum and a stronger signal.

### Volume Conviction
How significant was the volume spike? A crossover that occurs on a volume spike 3x the recent average is a much stronger signal than one that occurs on a 1.5x spike.

These factors are combined into a "strength score," which is then translated into a simple "Low," "Medium," or "Strong" rating that is included with the signal notification. This allows you to prioritize and have more confidence in the high-strength signals.

## Strategies

The bot can be run in one of three distinct modes, each designed for a different trading style.

| Feature | Milestone 7 (Long-Term) | Milestone 10 (Aggressive Swing) | Milestone 11 (Day Trader) |
| :--- | :--- | :--- | :--- |
| **Primary Goal** | Identify major, multi-month market trends | Capture multi-day or multi-week market swings | Capture intraday momentum shifts |
| **Trader Profile** | Position Trader / Long-Term Investor | Swing Trader | Day Trader |
| **Analysis Frequency** | Every 24 hours | Every 4 hours | Every 5 minutes |
| **Trend Timeframe** | Weekly (W1) | Daily (D1) | 1-Hour (H1) |
| **Signal Timeframe** | Daily (D1) | 4-Hour (H4) | 5-Minute (M5) |
| **Core Indicators** | 50/200 SMA Crossover | 20/50 EMA Crossover | 9/21 EMA Crossover |
| **Data Filters** | Technicals + Sentiment + On-Chain | Technicals + Sentiment | Technicals Only |
| **Risk Per Trade** | 1.0% | 1.0% | 0.5% (Tighter) |

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install tokenometry
```

### Option 2: Install from Source

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nguyenph88/Tokenometry.git](https://github.com/nguyenph88/Tokenometry.git)
    cd Tokenometry
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the package in development mode:**
    ```bash
    pip install -e .
    ```

4.  **Set up your API keys (optional):**
    * Copy `env.example` to `.env`
    * Add your API keys to the `.env` file. The bot will gracefully handle missing keys by skipping the corresponding analysis.
    ```bash
    cp env.example .env
    # Edit .env with your actual API keys
    ```

## Usage

The bot can be configured to run in three different trading modes, each optimized for different trading styles and timeframes. The configuration is handled through the `example_usage.py` script, which demonstrates how to use the `Tokenometry` library.

### Quick Start

1. **Run the example script:**
   ```bash
   python example_usage.py
   ```

2. **Choose your strategy** by uncommenting one of the three configurations in the script:
   ```python
   # CHOOSE YOUR STRATEGY HERE
   chosen_config = DAY_TRADER_CONFIG      # For day trading
   # chosen_config = SWING_TRADER_CONFIG  # For swing trading
   # chosen_config = LONG_TERM_CONFIG     # For long-term investing
   ```

### Strategy Configurations

#### 1. Day Trader Strategy (High-Frequency)
**Best for:** Active day traders who want to capture intraday momentum shifts
**Analysis Frequency:** Every 5 minutes
**Timeframes:** 5-minute signals, 1-hour trend confirmation

```python
DAY_TRADER_CONFIG = {
    "STRATEGY_NAME": "Day Trader",
    "PRODUCT_IDS": ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD"],
    "GRANULARITY_SIGNAL": "FIVE_MINUTE",    # 5-minute chart for signals
    "GRANULARITY_TREND": "ONE_HOUR",        # 1-hour chart for trend
    "SHORT_PERIOD": 9,                      # Fast EMA
    "LONG_PERIOD": 21,                      # Slow EMA
    "VOLUME_FILTER_ENABLED": True,          # Enable volume filter
    "VOLUME_MA_PERIOD": 20,                 # Volume moving average period
    "VOLUME_SPIKE_MULTIPLIER": 2.0,         # Volume spike multiplier
    "RISK_PER_TRADE_PERCENTAGE": 0.5,      # Conservative 0.5% risk
    "ATR_STOP_LOSS_MULTIPLIER": 2.0,       # Tight stop-loss
}
```

**When to use:** During active trading hours when you want to catch quick momentum shifts and scalp small profits.

#### 2. Aggressive Swing Trader Strategy
**Best for:** Swing traders who hold positions for days to weeks
**Analysis Frequency:** Every 4 hours
**Timeframes:** 4-hour signals, daily trend confirmation

```python
SWING_TRADER_CONFIG = {
    "STRATEGY_NAME": "Aggressive Swing Trader",
    "PRODUCT_IDS": ["BTC-USD", "ETH-USD", "LINK-USD"],
    "GRANULARITY_SIGNAL": "FOUR_HOUR",     # 4-hour chart for signals
    "GRANULARITY_TREND": "ONE_DAY",        # Daily chart for trend
    "SHORT_PERIOD": 20,                    # Medium-term EMA
    "LONG_PERIOD": 50,                     # Long-term EMA
    "VOLUME_FILTER_ENABLED": True,         # Enable volume filter
    "VOLUME_MA_PERIOD": 20,                # Volume moving average period
    "VOLUME_SPIKE_MULTIPLIER": 1.5,        # Volume spike multiplier
    "RISK_PER_TRADE_PERCENTAGE": 1.0,     # Standard 1% risk
    "ATR_STOP_LOSS_MULTIPLIER": 2.5,      # Moderate stop-loss
}
```

**When to use:** For capturing multi-day market swings and trend reversals, ideal for part-time traders.

#### 3. Long-Term Investor Strategy
**Best for:** Position traders and long-term investors
**Analysis Frequency:** Every 24 hours
**Timeframes:** Daily signals, weekly trend confirmation

```python
LONG_TERM_CONFIG = {
    "STRATEGY_NAME": "Long-Term Investor",
    "PRODUCT_IDS": ["BTC-USD", "ETH-USD"],
    "GRANULARITY_SIGNAL": "ONE_DAY",       # Daily chart for signals
    "GRANULARITY_TREND": "ONE_WEEK",       # Weekly chart for trend
    "TREND_INDICATOR_TYPE": "SMA",         # Simple Moving Average
    "SHORT_PERIOD": 50,                    # 50-day SMA
    "LONG_PERIOD": 200,                    # 200-day SMA
    "VOLUME_FILTER_ENABLED": True,         # Enable volume filter
    "VOLUME_MA_PERIOD": 20,                # Volume moving average period
    "VOLUME_SPIKE_MULTIPLIER": 1.5,        # Volume spike multiplier
    "RISK_PER_TRADE_PERCENTAGE": 1.0,     # Standard 1% risk
    "ATR_STOP_LOSS_MULTIPLIER": 2.5,      # Moderate stop-loss
}
```

**When to use:** For identifying major market trends and making long-term investment decisions.

### Customizing Your Strategy

You can modify any configuration by editing the parameters:

```python
# Example: Custom day trading configuration
CUSTOM_DAY_TRADE = {
    "STRATEGY_NAME": "Custom Day Trader",
    "PRODUCT_IDS": ["BTC-USD", "ETH-USD"],  # Monitor fewer assets
    "GRANULARITY_SIGNAL": "FIVE_MINUTE",
    "GRANULARITY_TREND": "ONE_HOUR",
    "SHORT_PERIOD": 5,                      # Faster signals
    "LONG_PERIOD": 13,                      # Shorter trend
    "RSI_PERIOD": 10,                       # More sensitive RSI
    "RISK_PER_TRADE_PERCENTAGE": 0.25,     # Very conservative
    "ATR_STOP_LOSS_MULTIPLIER": 1.5,       # Tighter stops
}
```

### Understanding the Signals

The bot generates three types of signals:

- **BUY**: Golden cross (fast EMA > slow EMA) + bullish trend + RSI not overbought + MACD bullish + volume spike (if enabled)
- **SELL**: Death cross (fast EMA < slow EMA) + bearish trend + RSI not oversold + MACD bearish + volume spike (if enabled)
- **HOLD**: No crossover or trend misalignment

### Volume Filter

The volume filter improves signal quality by requiring significant volume spikes to confirm technical crossovers:

```python
# Enable volume filter (recommended)
config["VOLUME_FILTER_ENABLED"] = True
config["VOLUME_MA_PERIOD"] = 20          # Volume moving average period
config["VOLUME_SPIKE_MULTIPLIER"] = 2.0  # Current volume must be 2x the average

# Disable volume filter (more signals, potentially lower quality)
config["VOLUME_FILTER_ENABLED"] = False
```

**Benefits:**
- Reduces false signals by requiring volume confirmation
- Only trades with significant volume spikes
- Configurable sensitivity via multiplier
- Optional feature - can be disabled for more signals

### Risk Management Features

- **Automatic Stop-Loss**: Calculated using ATR (Average True Range) for volatility-adjusted stops
- **Position Sizing**: Automatically calculates position size based on your risk percentage
- **Portfolio Protection**: Each trade risks only the specified percentage of your portfolio

### Logging and Monitoring

The bot provides comprehensive logging:
- **Console Output**: Real-time signal information
- **File Logging**: Complete audit trail in `trading_app.log`
- **Signal Details**: Timestamp, asset, signal type, trend, price, and trade plan

### Running in Production

For 24/7 operation on a server:

1. **Use a process manager** like `systemd`, `supervisord`, or `PM2`
2. **Set up monitoring** to restart the bot if it crashes
3. **Configure log rotation** to manage log file sizes
4. **Set up alerts** for critical errors or signal generation

### Example Output

```
2025-08-19 21:20:12,698 - CryptoTraderApp - INFO - Starting new scan with 'Day Trader' strategy.
2025-08-19 21:20:12,699 - CryptoTraderApp - INFO - Fetching ONE_HOUR data for BTC-USD...
2025-08-19 21:20:12,886 - CryptoTraderApp - INFO - Trend for BTC-USD on ONE_HOUR chart: Bearish
2025-08-19 21:20:12,886 - CryptoTraderApp - INFO - Fetching FIVE_MINUTE data for BTC-USD...
2025-08-19 21:20:13,108 - CryptoTraderApp - INFO - Calculating technical indicators...
2025-08-19 21:20:13,114 - CryptoTraderApp - INFO - Generating signals on FIVE_MINUTE chart...
2025-08-19 21:20:14,249 - CryptoTraderApp - INFO - Scan complete. Found 0 actionable signals.
2025-08-19 21:20:14,249 - CryptoTraderApp - INFO - Sleeping for 5.0 minutes until the next scan.
```



## Disclaimer

This tool is for analytical and educational purposes only. It is **not financial advice**. The signals generated by this bot are based on algorithmic analysis and do not guarantee any specific outcome. Always conduct your own research and consult with a qualified financial advisor before making any investment decisions.

Disclaimer
This tool is for analytical and educational purposes only. It is not financial advice. The signals generated by this bot are based on algorithmic analysis and do not guarantee any specific outcome. Always conduct your own research and consult with a qualified financial advisor before making any investment decisions.
