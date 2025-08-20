# -----------------------------------------------------------------------------
# example_usage.py
# This file shows how to import and use the CryptoScanner library.
# -----------------------------------------------------------------------------

import logging
import sys
import time
from tokenometry import Tokenometry

# --- Strategy Configurations ---

DAY_TRADER_CONFIG = {
    "STRATEGY_NAME": "Day Trader",
    "PRODUCT_IDS": ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD"],
    "GRANULARITY_SIGNAL": "FIVE_MINUTE",
    "GRANULARITY_TREND": "ONE_HOUR",
    "GRANULARITY_SECONDS": {"ONE_HOUR": 3600, "FIVE_MINUTE": 300, "ONE_DAY": 86400, "ONE_WEEK": 604800},
    "TREND_INDICATOR_TYPE": "EMA",
    "TREND_PERIOD": 50,
    "SIGNAL_INDICATOR_TYPE": "EMA",
    "SHORT_PERIOD": 9,
    "LONG_PERIOD": 21,
    "RSI_PERIOD": 14, "RSI_OVERBOUGHT": 70, "RSI_OVERSOLD": 30,
    "MACD_FAST": 12, "MACD_SLOW": 26, "MACD_SIGNAL": 9,
    "ATR_PERIOD": 14,
    "HYPOTHETICAL_PORTFOLIO_SIZE": 100000.0,
    "RISK_PER_TRADE_PERCENTAGE": 0.5,
    "ATR_STOP_LOSS_MULTIPLIER": 2.0,
}

SWING_TRADER_CONFIG = {
    "STRATEGY_NAME": "Aggressive Swing Trader",
    "PRODUCT_IDS": ["BTC-USD", "ETH-USD", "LINK-USD"],
    "GRANULARITY_SIGNAL": "FOUR_HOUR",
    "GRANULARITY_TREND": "ONE_DAY",
    "GRANULARITY_SECONDS": {"ONE_HOUR": 3600, "FIVE_MINUTE": 300, "ONE_DAY": 86400, "FOUR_HOUR": 14400, "ONE_WEEK": 604800},
    "TREND_INDICATOR_TYPE": "EMA",
    "TREND_PERIOD": 50,
    "SIGNAL_INDICATOR_TYPE": "EMA",
    "SHORT_PERIOD": 20,
    "LONG_PERIOD": 50,
    "RSI_PERIOD": 14, "RSI_OVERBOUGHT": 70, "RSI_OVERSOLD": 30,
    "MACD_FAST": 12, "MACD_SLOW": 26, "MACD_SIGNAL": 9,
    "ATR_PERIOD": 14,
    "HYPOTHETICAL_PORTFOLIO_SIZE": 100000.0,
    "RISK_PER_TRADE_PERCENTAGE": 1.0,
    "ATR_STOP_LOSS_MULTIPLIER": 2.5,
}

LONG_TERM_CONFIG = {
    "STRATEGY_NAME": "Long-Term Investor",
    "PRODUCT_IDS": ["BTC-USD", "ETH-USD"],
    "GRANULARITY_SIGNAL": "ONE_DAY",
    "GRANULARITY_TREND": "ONE_WEEK",
    "GRANULARITY_SECONDS": {"ONE_HOUR": 3600, "FIVE_MINUTE": 300, "ONE_DAY": 86400, "ONE_WEEK": 604800},
    "TREND_INDICATOR_TYPE": "SMA",
    "TREND_PERIOD": 30,
    "SIGNAL_INDICATOR_TYPE": "SMA",
    "SHORT_PERIOD": 50,
    "LONG_PERIOD": 200,
    "RSI_PERIOD": 14, "RSI_OVERBOUGHT": 70, "RSI_OVERSOLD": 30,
    "MACD_FAST": 12, "MACD_SLOW": 26, "MACD_SIGNAL": 9,
    "ATR_PERIOD": 14,
    "HYPOTHETICAL_PORTFOLIO_SIZE": 100000.0,
    "RISK_PER_TRADE_PERCENTAGE": 1.0,
    "ATR_STOP_LOSS_MULTIPLIER": 2.5,
}


if __name__ == "__main__":
    # --- Logger Setup for the runner script ---
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("CryptoTraderApp")
    logger.setLevel(logging.INFO)
    
    # Prevents duplicate handlers if you re-run this in an interactive session
    if not logger.handlers:
        file_handler = logging.FileHandler("trading_app.log")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    # --- Initialize and run the scanner ---
    
    # CHOOSE YOUR STRATEGY HERE
    chosen_config = DAY_TRADER_CONFIG
    # chosen_config = SWING_TRADER_CONFIG
    # chosen_config = LONG_TERM_CONFIG
    
    # The user of the library now controls the execution loop
    scanner = Tokenometry(config=chosen_config, logger=logger)
    
    while True:
        signals = scanner.scan()
        
        if signals:
            logger.info("--- ACTIONABLE SIGNALS FOUND ---")
            for signal in signals:
                logger.info(f"  Signal: {signal}")
                # Here, you could add code to send an email, a Discord alert,
                # or even place a trade via the API.
        
        sleep_duration = chosen_config['GRANULARITY_SECONDS'][chosen_config['GRANULARITY_SIGNAL']]
        logger.info(f"Sleeping for {sleep_duration / 60} minutes until the next scan.")
        time.sleep(sleep_duration)
