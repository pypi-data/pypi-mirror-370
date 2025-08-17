import logging
import datetime
import pandas as pd
from auto_chart_patterns.rsi_div_patterns import find_rsi_divergences
from .helpers import calculate_patterns, load_expected_patterns, START_DATE, END_DATE

def test_static_rsi_divergences(tickers, zigzag_rsi_divergences,
                                default_properties_rsi_divergences):
    for ticker in tickers:
        success, patterns = calculate_patterns(ticker, zigzag_rsi_divergences,
                                              default_properties_rsi_divergences,
                                              find_rsi_divergences,
                                              start_date=START_DATE, end_date=END_DATE,
                                              category=4)
        assert success
        expected_patterns = load_expected_patterns(ticker, category=4)
        for expected_pattern in expected_patterns:
            assert expected_pattern in patterns, f"ticker: {ticker}"

def test_dynamic_rsi_divergences(tickers, zigzag_rsi_divergences,
                                 default_properties_rsi_divergences):
    for ticker in tickers:
        logging.debug(f"ticker: {ticker}")
        for expected_pattern in load_expected_patterns(ticker, category=4):
            pattern_end_date = pd.to_datetime(expected_pattern.pivots[-1].point.time)
            # add 3 days to the pattern end date to account for the fact that the pattern may not be complete
            pattern_end_date += datetime.timedelta(days=3)
            success, patterns = calculate_patterns(ticker, zigzag_rsi_divergences,
                                          default_properties_rsi_divergences,
                                          find_rsi_divergences,
                                          start_date=START_DATE, end_date=pattern_end_date,
                                          category=4,
                                          min_index=expected_pattern.pivots[0].point.index)
            if success:
                assert expected_pattern in patterns, f"ticker: {ticker}"