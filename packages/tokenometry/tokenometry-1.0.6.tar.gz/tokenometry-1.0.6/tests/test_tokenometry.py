"""
Tests for the Tokenometry package.
"""

import pytest
import logging
from unittest.mock import Mock, patch
from tokenometry import Tokenometry


class TestTokenometry:
    """Test cases for the Tokenometry class."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return Mock(spec=logging.Logger)
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        return {
            "STRATEGY_NAME": "Test Strategy",
            "PRODUCT_IDS": ["BTC-USD"],
            "GRANULARITY_SIGNAL": "ONE_HOUR",
            "GRANULARITY_TREND": "ONE_DAY",
            "GRANULARITY_SECONDS": {"ONE_HOUR": 3600, "ONE_DAY": 86400},
            "TREND_INDICATOR_TYPE": "EMA",
            "TREND_PERIOD": 50,
            "SIGNAL_INDICATOR_TYPE": "EMA",
            "SHORT_PERIOD": 20,
            "LONG_PERIOD": 50,
            "RSI_PERIOD": 14,
            "RSI_OVERBOUGHT": 70,
            "RSI_OVERSOLD": 30,
            "MACD_FAST": 12,
            "MACD_SLOW": 26,
            "MACD_SIGNAL": 9,
            "ATR_PERIOD": 14,
            "HYPOTHETICAL_PORTFOLIO_SIZE": 100000.0,
            "RISK_PER_TRADE_PERCENTAGE": 1.0,
            "ATR_STOP_LOSS_MULTIPLIER": 2.5,
        }
    
    def test_tokenometry_initialization(self, mock_logger, sample_config):
        """Test that Tokenometry initializes correctly."""
        with patch('tokenometry.core.RESTClient'):
            bot = Tokenometry(config=sample_config, logger=mock_logger)
            assert bot.config == sample_config
            assert bot.logger == mock_logger
            assert bot.config["STRATEGY_NAME"] == "Test Strategy"
    
    def test_config_validation(self, mock_logger):
        """Test that Tokenometry validates configuration properly."""
        invalid_config = {"STRATEGY_NAME": "Invalid"}
        
        with pytest.raises(KeyError):
            with patch('tokenometry.core.RESTClient'):
                Tokenometry(config=invalid_config, logger=mock_logger)
    
    def test_strategy_name_access(self, mock_logger, sample_config):
        """Test accessing strategy name from configuration."""
        with patch('tokenometry.core.RESTClient'):
            bot = Tokenometry(config=sample_config, logger=mock_logger)
            assert bot.config["STRATEGY_NAME"] == "Test Strategy"
    
    def test_product_ids_configuration(self, mock_logger, sample_config):
        """Test that product IDs are configured correctly."""
        with patch('tokenometry.core.RESTClient'):
            bot = Tokenometry(config=sample_config, logger=mock_logger)
            assert "BTC-USD" in bot.config["PRODUCT_IDS"]
            assert len(bot.config["PRODUCT_IDS"]) == 1


if __name__ == "__main__":
    pytest.main([__file__])
