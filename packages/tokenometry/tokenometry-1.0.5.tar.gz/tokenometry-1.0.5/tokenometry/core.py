import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from coinbase.rest import RESTClient
import warnings
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Tokenometry:
    """
    A sophisticated multi-strategy crypto analysis bot for trading signals.
    
    This class provides a flexible framework for cryptocurrency market analysis,
    supporting multiple trading strategies including day trading, swing trading,
    and long-term investment approaches.
    """
    
    def __init__(self, config: Dict, logger: Optional[logging.Logger] = None):
        """
        Initialize the Tokenometry scanner.
        
        Args:
            config: Configuration dictionary containing strategy parameters
            logger: Optional logger instance
        """
        self.config = config
        self.client = RESTClient()
        
        # Set up logging
        if logger:
            self.logger = logger
        else:
            self.logger = self._setup_logging()
            
        # Suppress pandas warnings for cleaner output
        warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
        warnings.simplefilter(action='ignore', category=FutureWarning)
            
        self.logger.info(f"Initialized Tokenometry with '{config['STRATEGY_NAME']}' strategy")
    
    def _setup_logging(self) -> logging.Logger:
        """Sets up logging configuration."""
        logger = logging.getLogger('Tokenometry')
        logger.setLevel(logging.INFO)
        
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('tokenometry.log')
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(log_format)
        f_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
        return logger
    
    def _get_historical_data(self, product_id, granularity):
        """Fetches a rolling window of historical data."""
        self.logger.info(f"Fetching {granularity} data for {product_id}...")
        try:
            # Fetch the max 300 candles per request
            granularity_seconds = self.config['GRANULARITY_SECONDS'][granularity]
            duration_seconds = 300 * granularity_seconds
            start_time = int(time.time() - duration_seconds)
            end_time = int(time.time())

            response = self.client.get_public_candles(
                product_id=product_id, 
                start=str(start_time), 
                end=str(end_time), 
                granularity=granularity
            )
            
            # Convert response to dictionary and extract candles
            response_dict = response.to_dict()
            candles = response_dict.get('candles', [])
            if not candles: 
                self.logger.warning(f"No price data from Coinbase for {product_id}.")
                return None
                
            df = pd.DataFrame(candles)
            df.rename(columns={'start': 'timestamp', 'low': 'Low', 'high': 'High', 'open': 'Open', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
            df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='s')
            for col in ['Low', 'High', 'Open', 'Close', 'Volume']: 
                df[col] = pd.to_numeric(df[col])
            df.drop_duplicates(subset='timestamp', inplace=True)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error fetching price data for {product_id}: {e}")
            return None
    
    def _get_trend(self, product_id):
        """Determines the main trend using the configured trend timeframe and indicator."""
        df_trend = self._get_historical_data(product_id, self.config['GRANULARITY_TREND'])
        if df_trend is None or df_trend.empty: 
            return "Unknown"
        
        cfg = self.config
        trend_indicator_type = cfg.get('TREND_INDICATOR_TYPE', 'EMA').upper()
        trend_period = cfg['TREND_PERIOD']
        trend_col = f"{trend_indicator_type}_{trend_period}"

        if trend_indicator_type == 'SMA':
            df_trend = self._calculate_sma(df_trend, trend_period, trend_col)
        else: # Default to EMA
            df_trend = self._calculate_ema(df_trend, trend_period, trend_col)
            
        df_trend.dropna(inplace=True)
        
        if df_trend.empty:
            return "Unknown"
            
        latest_candle = df_trend.iloc[-1]
        return "Bullish" if latest_candle['Close'] > latest_candle[trend_col] else "Bearish"

    def _calculate_indicators(self, df):
        """Calculates all necessary technical indicators based on the config."""
        if df is None: 
            return None
        self.logger.info("Calculating technical indicators...")
        cfg = self.config
        signal_indicator_type = cfg.get('SIGNAL_INDICATOR_TYPE', 'EMA').upper()

        if signal_indicator_type == 'SMA':
            df = self._calculate_sma(df, cfg['SHORT_PERIOD'], f"SMA_{cfg['SHORT_PERIOD']}")
            df = self._calculate_sma(df, cfg['LONG_PERIOD'], f"SMA_{cfg['LONG_PERIOD']}")
        else: # Default to EMA
            df = self._calculate_ema(df, cfg['SHORT_PERIOD'], f"EMA_{cfg['SHORT_PERIOD']}")
            df = self._calculate_ema(df, cfg['LONG_PERIOD'], f"EMA_{cfg['LONG_PERIOD']}")

        df = self._calculate_rsi(df, cfg['RSI_PERIOD'])
        df = self._calculate_macd(df, cfg['MACD_FAST'], cfg['MACD_SLOW'], cfg['MACD_SIGNAL'])
        df = self._calculate_atr(df, cfg['ATR_PERIOD'])
        return df

    def _calculate_sma(self, df: pd.DataFrame, period: int, column_name: str) -> pd.DataFrame:
        """Calculate Simple Moving Average."""
        df[column_name] = df['Close'].rolling(window=period).mean()
        return df
    
    def _calculate_ema(self, df: pd.DataFrame, period: int, column_name: str) -> pd.DataFrame:
        """Calculate Exponential Moving Average."""
        df[column_name] = df['Close'].ewm(span=period, adjust=False).mean()
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Calculate Relative Strength Index."""
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
        return df
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int, slow: int, signal: int) -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
        
        df[f'MACD_{fast}_{slow}_{signal}'] = macd_line
        df[f'MACDs_{fast}_{slow}_{signal}'] = macd_signal
        return df
    
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Calculate Average True Range."""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        df[f'ATRr_{period}'] = true_range.rolling(window=period).mean()
        return df

    def _generate_signals(self, df):
        """Generates technical signals based on the configured strategy."""
        if df is None: 
            return None
        self.logger.info(f"Generating signals on {self.config['GRANULARITY_SIGNAL']} chart...")
        cfg = self.config
        indicator_type = cfg.get('SIGNAL_INDICATOR_TYPE', 'EMA').upper()
        short_col = f"{indicator_type}_{cfg['SHORT_PERIOD']}"
        long_col = f"{indicator_type}_{cfg['LONG_PERIOD']}"
        rsi_col = f"RSI_{cfg['RSI_PERIOD']}"
        macd_line_col = f"MACD_{cfg['MACD_FAST']}_{cfg['MACD_SLOW']}_{cfg['MACD_SIGNAL']}"
        macd_signal_col = f"MACDs_{cfg['MACD_FAST']}_{cfg['MACD_SLOW']}_{cfg['MACD_SIGNAL']}"
        
        df['Signal'] = 0
        
        golden_cross = (df[short_col] > df[long_col]) & (df[short_col].shift(1) <= df[long_col].shift(1))
        rsi_buy_filter = df[rsi_col] < cfg['RSI_OVERBOUGHT']
        macd_buy_filter = df[macd_line_col] > df[macd_signal_col]
        df.loc[golden_cross & rsi_buy_filter & macd_buy_filter, 'Signal'] = 1
        
        death_cross = (df[short_col] < df[long_col]) & (df[short_col].shift(1) >= df[long_col].shift(1))
        rsi_sell_filter = df[rsi_col] > cfg['RSI_OVERSOLD']
        macd_sell_filter = df[macd_line_col] < df[macd_signal_col]
        df.loc[death_cross & rsi_sell_filter & macd_sell_filter, 'Signal'] = -1
        return df

    def scan(self):
        """
        Runs one full analysis cycle for all configured assets and returns the results.
        
        Returns:
            list: A list of dictionaries, where each dictionary represents a signal.
        """
        self.logger.info(f"Starting new scan with '{self.config['STRATEGY_NAME']}' strategy.")
        signals = []
        
        for product_id in self.config['PRODUCT_IDS']:
            trend = self._get_trend(product_id)
            self.logger.info(f"Trend for {product_id} on {self.config['GRANULARITY_TREND']} chart: {trend}")

            data = self._get_historical_data(product_id, self.config['GRANULARITY_SIGNAL'])
            if data is not None and not data.empty:
                data = self._calculate_indicators(data)
                data.dropna(inplace=True)
                data = self._generate_signals(data)
                
                latest_row = data.iloc[-1]
                tech_signal = latest_row['Signal']
                
                final_signal = "HOLD"
                if tech_signal == 1 and trend == "Bullish":
                    final_signal = "BUY"
                elif tech_signal == -1 and trend == "Bearish":
                    final_signal = "SELL"
                
                if final_signal != "HOLD":
                    trade_plan = {}
                    if final_signal == "BUY":
                        cfg = self.config
                        atr_col = f"ATRr_{cfg['ATR_PERIOD']}"
                        if atr_col in latest_row.index:
                            latest_atr = latest_row[atr_col]
                            stop_loss = latest_row['Close'] - (latest_atr * cfg['ATR_STOP_LOSS_MULTIPLIER'])
                            capital_to_risk = cfg['HYPOTHETICAL_PORTFOLIO_SIZE'] * (cfg['RISK_PER_TRADE_PERCENTAGE'] / 100)
                            stop_loss_dist = latest_row['Close'] - stop_loss
                            if stop_loss_dist > 0:
                                position_size = capital_to_risk / stop_loss_dist
                                trade_plan = {
                                    'stop_loss': round(stop_loss, 4),
                                    'position_size_crypto': round(position_size, 6),
                                    'position_size_usd': round(position_size * latest_row['Close'], 2)
                                }

                    signal_data = {
                        'timestamp': latest_row.name.strftime('%Y-%m-%d %H:%M:%S'),
                        'asset': product_id,
                        'signal': final_signal,
                        'trend': trend,
                        'close_price': latest_row['Close'],
                        'trade_plan': trade_plan
                    }
                    signals.append(signal_data)
        
        self.logger.info(f"Scan complete. Found {len(signals)} actionable signals.")
        return signals
