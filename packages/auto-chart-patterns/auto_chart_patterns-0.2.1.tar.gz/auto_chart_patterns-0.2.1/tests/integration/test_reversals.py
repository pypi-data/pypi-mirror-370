import datetime
import pandas as pd
import logging
from auto_chart_patterns.reversal_patterns import find_reversal_patterns
from .helpers import load_expected_patterns, START_DATE, END_DATE, calculate_patterns

def test_static_reversals(tickers, zigzag_reversals, default_properties_reversals):
    for ticker in tickers:
        success, patterns = calculate_patterns(ticker, zigzag_reversals,
                                     default_properties_reversals,
                                     find_reversal_patterns,
                                     start_date=START_DATE, end_date=END_DATE, category=3)
        assert success
        expected_patterns = load_expected_patterns(ticker, category=3)
        for expected_pattern in expected_patterns:
            assert expected_pattern in patterns, f"ticker: {ticker}"

def test_dynamic_reversals(tickers, zigzag_reversals, default_properties_reversals):
    for ticker in tickers:
        logging.debug(f"ticker: {ticker}")
        for expected_pattern in load_expected_patterns(ticker, category=3):
            pattern_end_date = pd.to_datetime(expected_pattern.pivots[-1].point.time)
            # add 3 days to the pattern end date to account for the fact that the pattern may not be complete
            pattern_end_date += datetime.timedelta(days=3)
            success, patterns = calculate_patterns(ticker, zigzag_reversals,
                                          default_properties_reversals,
                                          find_reversal_patterns,
                                          start_date=START_DATE, end_date=pattern_end_date,
                                          category=3,
                                          min_index=expected_pattern.pivots[0].point.index)
            if success:
                assert expected_pattern in patterns, f"ticker: {ticker}"

def test_incremental_reversals(tickers, zigzag_reversals, default_properties_reversals):
    time_delta_before = zigzag_reversals.backcandles + 1
    time_delta_after = zigzag_reversals.forwardcandles + 1
    for ticker in tickers:
        logging.debug(f"ticker: {ticker}")
        for expected_pattern in load_expected_patterns(ticker, category=3):
            pattern_start_date = pd.to_datetime(expected_pattern.pivots[0].point.time)
            pattern_end_date = pd.to_datetime(expected_pattern.pivots[-1].point.time)
            # add days to the pattern start and end dates to account for the fact that the pattern may not be complete
            pattern_start_date -= datetime.timedelta(days=time_delta_before)
            pattern_end_date += datetime.timedelta(days=time_delta_after)
            success, patterns = calculate_patterns(ticker, zigzag_reversals,
                                          default_properties_reversals,
                                          find_reversal_patterns,
                                          start_date=pattern_start_date,
                                          end_date=pattern_end_date,
                                          category=3,
                                          start_index=expected_pattern.pivots[0].point.index-time_delta_before,
                                          min_index=expected_pattern.pivots[0].point.index)
            if success:
                assert expected_pattern in patterns, f"ticker: {ticker}"
