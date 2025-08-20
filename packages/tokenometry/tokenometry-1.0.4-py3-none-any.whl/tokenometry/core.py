import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from coinbase.rest import RESTClient
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
    
    def _get_historical_data(self, product_id: str, granularity: str) -> Optional[pd.DataFrame]:
        """Fetches a rolling window of historical data."""
        try:
            cfg = self.config
            lookback_days = cfg['LOOKBACK_DAYS']
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=lookback_days)
            
            # Convert granularity to seconds
            granularity_map = {
                '1m': 60, '5m': 300, '15m': 900, '30m': 1800,
                '1h': 3600, '4h': 14400, '1d': 86400, '1w': 604800
            }
            granularity_seconds = granularity_map.get(granularity, 86400)
            
            self.logger.info(f"Fetching {granularity} data for {product_id} from {start_time} to {end_time}")
            
            # Calculate estimated API calls needed
            total_seconds = (end_time - start_time).total_seconds()
            estimated_calls = int(total_seconds / (300 * granularity_seconds)) + 1
            self.logger.info(f"Estimated API calls: {estimated_calls}")
            
            all_candles = []
            current_start = start_time
            batch_count = 0
            
            while current_start < end_time:
                batch_count += 1
                current_end = min(current_start + timedelta(seconds=300 * granularity_seconds), end_time)
                
                self.logger.info(f"Batch {batch_count}: Fetching from {current_start} to {current_end}")
                
                try:
                    response = self.client.get_public_candles(
                        product_id=product_id,
                        start=current_start.isoformat(),
                        end=current_end.isoformat(),
                        granularity=granularity
                    )
                    
                    candles = response.to_dict().get('candles', [])
                    if candles:
                        all_candles.extend(candles)
                        self.logger.info(f"Batch {batch_count}: Retrieved {len(candles)} candles")
                    else:
                        self.logger.warning(f"Batch {batch_count}: No candles returned")
                        
                except Exception as e:
                    self.logger.error(f"Error fetching batch {batch_count}: {e}")
                    break
                
                # Move to next batch
                current_start = current_end
                
                # Rate limiting - be respectful to the API
                time.sleep(0.1)
            
            if not all_candles:
                self.logger.warning(f"No historical data retrieved for {product_id}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(all_candles)
            df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp'], errors='coerce'), unit='s')
            df.set_index('timestamp', inplace=True)
            
            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df.dropna(inplace=True)
            df.sort_index(inplace=True)
            
            self.logger.info(f"Successfully retrieved {len(df)} candles for {product_id}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {product_id}: {e}")
            return None
    
    def _get_trend(self, product_id: str) -> str:
        """Determines the overall trend using the configured trend timeframe and indicator."""
        try:
            cfg = self.config
            trend_granularity = cfg['GRANULARITY_TREND']
            trend_period = cfg['TREND_PERIOD']
            
            df_trend = self._get_historical_data(product_id, trend_granularity)
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
            return "Bullish" if latest_candle['close'] > latest_candle[trend_col] else "Bearish"

        except Exception as e:
            self.logger.error(f"Error determining trend for {product_id}: {e}")
            return "Unknown"

    def _calculate_indicators(self, df):
        """Calculates all necessary technical indicators based on the config."""
        if df is None or df.empty: 
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
        df[column_name] = df['close'].rolling(window=period).mean()
        return df
    
    def _calculate_ema(self, df: pd.DataFrame, period: int, column_name: str) -> pd.DataFrame:
        """Calculate Exponential Moving Average."""
        df[column_name] = df['close'].ewm(span=period, adjust=False).mean()
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Calculate Relative Strength Index."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
        return df
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int, slow: int, signal: int) -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
        
        df[f'MACD_{fast}_{slow}_{signal}'] = macd_line
        df[f'MACDs_{fast}_{slow}_{signal}'] = macd_signal
        return df
    
    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Calculate Average True Range."""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        df[f'ATRr_{period}'] = true_range.rolling(window=period).mean()
        return df

    def _generate_signals(self, df):
        """Generates technical signals based on the configured strategy."""
        if df is None or df.empty: 
            return None
        self.logger.info(f"Generating signals on {self.config['GRANULARITY_SIGNAL']} chart...")
        cfg = self.config
        indicator_type = cfg.get('SIGNAL_INDICATOR_TYPE', 'EMA').upper()
        short_col = f"{indicator_type}_{cfg['SHORT_PERIOD']}"
        long_col = f"{indicator_type}_{cfg['LONG_PERIOD']}"
        rsi_col = f"RSI_{cfg['RSI_PERIOD']}"
        macd_line_col = f"MACD_{cfg['MACD_FAST']}_{cfg['MACD_SLOW']}_{cfg['MACD_SIGNAL']}"
        macd_signal_col = f"MACDs_{cfg['MACD_FAST']}_{cfg['MACD_SLOW']}_{cfg['MACD_SIGNAL']}"
        atr_col = f"ATRr_{cfg['ATR_PERIOD']}"
        
        # Check if required columns exist
        required_cols = [short_col, long_col, rsi_col, macd_line_col, macd_signal_col, atr_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.logger.warning(f"Missing indicator columns: {missing_cols}")
            return None
        
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
                if data is not None:
                    data.dropna(inplace=True)
                    data = self._generate_signals(data)
                    
                    if data is not None and not data.empty:
                        latest_row = data.iloc[-1]
                        tech_signal = latest_row['Signal']
                        
                        final_signal = "HOLD"
                        if tech_signal == 1 and trend == "Bullish":
                            final_signal = "BUY"
                        elif tech_signal == -1 and trend == "Bearish":
                            final_signal = "SELL"
                        
                        # Calculate risk metrics
                        atr_col = f"ATRr_{self.config['ATR_PERIOD']}"
                        if atr_col in latest_row:
                            atr_value = latest_row[atr_col]
                            current_price = latest_row['close']
                            
                            # Risk management calculations
                            risk_per_trade = self.config.get('RISK_PER_TRADE', 0.02)  # 2% default
                            portfolio_value = self.config.get('PORTFOLIO_VALUE', 10000)  # $10k default
                            risk_amount = portfolio_value * risk_per_trade
                            
                            # Position sizing based on ATR
                            stop_loss_pips = self.config.get('STOP_LOSS_ATR_MULTIPLIER', 2) * atr_value
                            position_size = risk_amount / stop_loss_pips if stop_loss_pips > 0 else 0
                            
                            signal_info = {
                                'product_id': product_id,
                                'timestamp': latest_row.name,
                                'price': current_price,
                                'signal': final_signal,
                                'trend': trend,
                                'technical_signal': tech_signal,
                                'rsi': latest_row.get(f"RSI_{self.config['RSI_PERIOD']}", None),
                                'macd': latest_row.get(f"MACD_{self.config['MACD_FAST']}_{self.config['MACD_SLOW']}_{self.config['MACD_SIGNAL']}", None),
                                'atr': atr_value,
                                'stop_loss': current_price - stop_loss_pips,
                                'take_profit': current_price + (stop_loss_pips * self.config.get('RISK_REWARD_RATIO', 2)),
                                'position_size': position_size,
                                'risk_amount': risk_amount
                            }
                        else:
                            signal_info = {
                                'product_id': product_id,
                                'timestamp': latest_row.name,
                                'price': latest_row['close'],
                                'signal': final_signal,
                                'trend': trend,
                                'technical_signal': tech_signal,
                                'rsi': latest_row.get(f"RSI_{self.config['RSI_PERIOD']}", None),
                                'macd': latest_row.get(f"MACD_{self.config['MACD_FAST']}_{self.config['MACD_SLOW']}_{self.config['MACD_SIGNAL']}", None),
                                'atr': None,
                                'stop_loss': None,
                                'take_profit': None,
                                'position_size': None,
                                'risk_amount': None
                            }
                        
                        signals.append(signal_info)
                        self.logger.info(f"Signal for {product_id}: {final_signal} (Trend: {trend}, Technical: {tech_signal})")
                    else:
                        self.logger.warning(f"No signals generated for {product_id}")
                else:
                    self.logger.warning(f"Failed to calculate indicators for {product_id}")
            else:
                self.logger.warning(f"No historical data available for {product_id}")
        
        self.logger.info(f"Scan complete. Found {len(signals)} actionable signals.")
        return signals
