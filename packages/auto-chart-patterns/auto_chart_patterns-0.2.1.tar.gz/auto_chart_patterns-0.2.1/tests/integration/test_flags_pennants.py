import datetime
import pandas as pd
import logging
from auto_chart_patterns.flag_pennant_patterns import find_flags_and_pennants
from .helpers import load_expected_patterns, START_DATE, END_DATE, calculate_patterns

def test_static_flags_pennants(tickers, zigzag_flags_pennants, default_properties_flags_pennants):
    for ticker in tickers:
        success, patterns = calculate_patterns(ticker, zigzag_flags_pennants,
                                     default_properties_flags_pennants,
                                     find_flags_and_pennants,
                                     start_date=START_DATE, end_date=END_DATE, category=1)
        assert success
        expected_patterns = load_expected_patterns(ticker, category=1)
        for expected_pattern in expected_patterns:
            assert expected_pattern in patterns, f"ticker: {ticker}"

def test_dynamic_flags_pennants(tickers, zigzag_flags_pennants, default_properties_flags_pennants):
    for ticker in tickers:
        logging.debug(f"ticker: {ticker}")
        for expected_pattern in load_expected_patterns(ticker, 1):
            pattern_end_date = pd.to_datetime(expected_pattern.pivots[-1].point.time)
            # add 3 days to the pattern end date to account for the fact that the pattern may not be complete
            pattern_end_date += datetime.timedelta(days=zigzag_flags_pennants.forwardcandles + 1)
            success, patterns = calculate_patterns(ticker, zigzag_flags_pennants,
                                          default_properties_flags_pennants,
                                          find_flags_and_pennants,
                                          start_date=START_DATE, end_date=pattern_end_date,
                                          category=1,
                                          min_index=expected_pattern.pivots[0].point.index)
            if success:
                assert expected_pattern in patterns, f"ticker: {ticker}"

def test_incremental_flags_pennants(tickers, zigzag_flags_pennants, default_properties_flags_pennants):
    time_delta_before = default_properties_flags_pennants.flag_pole_span_max
    time_delta_after = zigzag_flags_pennants.forwardcandles + 1
    for ticker in tickers:
        logging.debug(f"ticker: {ticker}")
        if ticker == "SHIBUSDT":
            # skip SHIBUSDT because it has incomplete data in July 2024
            continue
        for expected_pattern in load_expected_patterns(ticker, 1):
            pattern_start_date = pd.to_datetime(expected_pattern.pivots[0].point.time)
            pattern_end_date = pd.to_datetime(expected_pattern.pivots[-1].point.time)
            # add days to the pattern start and end dates to account for the fact that the pattern may not be complete
            pattern_start_date -= datetime.timedelta(days=time_delta_before)
            pattern_end_date += datetime.timedelta(days=time_delta_after)
            success, patterns = calculate_patterns(ticker, zigzag_flags_pennants,
                                          default_properties_flags_pennants,
                                          find_flags_and_pennants,
                                          start_date=pattern_start_date,
                                          end_date=pattern_end_date,
                                          category=1,
                                          start_index=expected_pattern.pivots[0].point.index-time_delta_before,
                                          min_index=expected_pattern.pivots[0].point.index)
            if success:
                assert expected_pattern in patterns, f"ticker: {ticker}"
