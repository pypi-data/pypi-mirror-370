# milestone_1.py

import time
import pandas as pd
import pandas_ta as ta
import numpy as np
from coinbase.rest import RESTClient

# --- Configuration ---
# Define the cryptocurrency pair and the timeframe for analysis.
# Product ID follows the format 'BASE-QUOTE', e.g., 'BTC-USD'.
PRODUCT_ID = "BTC-USD"
# Granularity for the candlestick data. Options include:
# ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, THIRTY_MINUTE, ONE_HOUR,
# TWO_HOUR, FOUR_HOUR, SIX_HOUR, ONE_DAY.
GRANULARITY = "ONE_DAY"

# Define the periods for the short and long Simple Moving Averages (SMA).
SHORT_WINDOW = 50
LONG_WINDOW = 200

def get_historical_data(product_id, granularity):
    """
    Fetches historical candlestick data from Coinbase.

    This function connects to the public Coinbase Advanced Trade API endpoint
    to retrieve OHLCV (Open, High, Low, Close, Volume) data.
    It fetches the maximum number of candles (300) per request.

    Args:
        product_id (str): The trading pair (e.g., 'BTC-USD').
        granularity (str): The candle timeframe (e.g., 'ONE_DAY').

    Returns:
        pd.DataFrame: A pandas DataFrame containing the historical data,
                      or None if the request fails.
    """
    print(f"Fetching historical data for {product_id}...")
    try:
        # We use the public client here, no API keys needed for this endpoint.
        client = RESTClient()
        
        # The API returns a maximum of 300 candles per request.
        # We calculate a start and end time to fetch roughly 300 of the latest candles.
        # Note: For more extensive historical data, a loop with pagination would be needed.
        end_time = int(time.time())
        
        # Calculate start_time based on granularity for ~300 candles
        if granularity == "ONE_DAY":
            start_time = end_time - (300 * 24 * 60 * 60)
        elif granularity == "ONE_HOUR":
            start_time = end_time - (300 * 60 * 60)
        # Add other granularities as needed
        else:
            # Default to fetching last 300 minutes for smaller timeframes
            start_time = end_time - (300 * 60)

        # Fetch the candle data
        response = client.get_public_candles(
            product_id=product_id,
            start=str(start_time),
            end=str(end_time),
            granularity=granularity
        )

        # Convert response to dictionary and extract candles
        response_dict = response.to_dict()
        candles = response_dict.get('candles', [])
        if not candles:
            print("No data returned from Coinbase.")
            return None

        # Convert the list of candle dictionaries to a pandas DataFrame
        df = pd.DataFrame(candles)
        
        # Rename columns for clarity
        df.rename(columns={
            'start': 'timestamp',
            'low': 'Low',
            'high': 'High',
            'open': 'Open',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)

        # Convert columns to appropriate data types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        for col in ['Low', 'High', 'Open', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col])
        
        # Set the timestamp as the index and sort it
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)

        print("Data fetched and processed successfully.")
        return df

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None

def calculate_moving_averages(df, short_window, long_window):
    """
    Calculates short-term and long-term Simple Moving Averages (SMAs).

    Args:
        df (pd.DataFrame): DataFrame with historical price data.
        short_window (int): The lookback period for the short-term SMA.
        long_window (int): The lookback period for the long-term SMA.

    Returns:
        pd.DataFrame: The original DataFrame with added SMA columns.
    """
    print("Calculating moving averages...")
    # Use pandas_ta to calculate the SMAs and append them to the DataFrame
    df.ta.sma(length=short_window, append=True)
    df.ta.sma(length=long_window, append=True)
    return df

def generate_signals(df, short_window, long_window):
    """
    Generates buy and sell signals based on SMA crossovers.

    Args:
        df (pd.DataFrame): DataFrame with price data and SMAs.
        short_window (int): The period of the short-term SMA.
        long_window (int): The period of the long-term SMA.

    Returns:
        pd.DataFrame: The DataFrame with an added 'Signal' column.
                       1 indicates a Buy signal (Golden Cross).
                      -1 indicates a Sell signal (Death Cross).
                       0 indicates no signal.
    """
    print("Generating trading signals...")
    short_sma_col = f'SMA_{short_window}'
    long_sma_col = f'SMA_{long_window}'
    
    # Create a 'Signal' column initialized to 0
    df['Signal'] = 0

    # Generate the buy signal (Golden Cross)
    # This occurs when the short SMA crosses ABOVE the long SMA.
    # We check the condition for the current candle and the opposite for the previous one.
    buy_condition = (df[short_sma_col] > df[long_sma_col]) & \
                    (df[short_sma_col].shift(1) <= df[long_sma_col].shift(1))
    df.loc[buy_condition, 'Signal'] = 1

    # Generate the sell signal (Death Cross)
    # This occurs when the short SMA crosses BELOW the long SMA.
    sell_condition = (df[short_sma_col] < df[long_sma_col]) & \
                     (df[short_sma_col].shift(1) >= df[long_sma_col].shift(1))
    df.loc[sell_condition, 'Signal'] = -1
    
    return df

def main():
    """
    Main function to run the analysis bot for Milestone 1.
    """
    print("--- Crypto Analysis Bot: Milestone 1 ---")
    
    # 1. Fetch historical data from Coinbase
    data = get_historical_data(PRODUCT_ID, GRANULARITY)
    
    if data is not None and not data.empty:
        # 2. Calculate technical indicators (SMAs)
        data = calculate_moving_averages(data, SHORT_WINDOW, LONG_WINDOW)
        
        # 3. Generate trading signals based on the strategy
        data = generate_signals(data, SHORT_WINDOW, LONG_WINDOW)
        
        # 4. Display the signals
        signals = data[data['Signal'] != 0]
        
        print("\n--- Trading Signals Found ---")
        if signals.empty:
            print("No trading signals generated in the fetched historical data.")
        else:
            for index, row in signals.iterrows():
                signal_type = "BUY (Golden Cross)" if row['Signal'] == 1 else "SELL (Death Cross)"
                print(f"Date: {index.date()} | Signal: {signal_type} | Close Price: ${row['Close']:.2f}")
    
    print("\n--- Analysis Complete ---")

if __name__ == "__main__":
    main()
