import time
import pandas as pd
import pandas_ta as ta
from coinbase.rest import RESTClient
import warnings
import logging
import sys


# --- Library Class ---

class Tokenometry:
    """
    A sophisticated crypto analysis bot that can be configured with different
    timeframes and indicator strategies to generate trading signals.
    """
    def __init__(self, config, logger):
        """
        Initializes the Tokenometry bot with a specific strategy configuration.

        Args:
            config (dict): A dictionary containing all strategy parameters.
            logger: An external logging object.
        """
        self.config = config
        self.logger = logger
        self.client = RESTClient()
        # Suppress pandas warnings for cleaner output
        warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
        warnings.simplefilter(action='ignore', category=FutureWarning)

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
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=['Low', 'High', 'Open', 'Close'], inplace=True)
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
            df_trend.ta.sma(length=trend_period, append=True)
        else: # Default to EMA
            df_trend.ta.ema(length=trend_period, append=True)
            
        df_trend.dropna(inplace=True)
        
        if df_trend.empty:
            return "Unknown"
            
        latest_candle = df_trend.iloc[-1]
        return "Bullish" if latest_candle['Close'] > latest_candle[trend_col] else "Bearish"

    def _calculate_indicators(self, df):
        """Calculates all necessary technical indicators based on the config."""
        if df is None or df.empty: 
            return None
        self.logger.info("Calculating technical indicators...")
        cfg = self.config
        signal_indicator_type = cfg.get('SIGNAL_INDICATOR_TYPE', 'EMA').upper()

        if signal_indicator_type == 'SMA':
            df.ta.sma(length=cfg['SHORT_PERIOD'], append=True)
            df.ta.sma(length=cfg['LONG_PERIOD'], append=True)
        else: # Default to EMA
            df.ta.ema(length=cfg['SHORT_PERIOD'], append=True)
            df.ta.ema(length=cfg['LONG_PERIOD'], append=True)

        df.ta.rsi(length=cfg['RSI_PERIOD'], append=True)
        df.ta.macd(fast=cfg['MACD_FAST'], slow=cfg['MACD_SLOW'], signal=cfg['MACD_SIGNAL'], append=True)
        df.ta.atr(length=cfg['ATR_PERIOD'], append=True)
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
