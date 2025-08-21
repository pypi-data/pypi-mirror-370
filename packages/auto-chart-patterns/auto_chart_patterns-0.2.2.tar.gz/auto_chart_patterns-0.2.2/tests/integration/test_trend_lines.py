import datetime
import pandas as pd
import logging
from auto_chart_patterns.trendline_patterns import find_trend_lines
from .helpers import load_expected_patterns, START_DATE, END_DATE, calculate_patterns

def test_static_trend_lines(tickers, zigzag_trend_lines, default_properties_trend_lines):
    for ticker in tickers:
        success, patterns = calculate_patterns(ticker, zigzag_trend_lines,
                                     default_properties_trend_lines,
                                     find_trend_lines,
                                     start_date=START_DATE, end_date=END_DATE, category=2)
        assert success
        expected_patterns = load_expected_patterns(ticker, category=2)
        for expected_pattern in expected_patterns:
            assert expected_pattern in patterns, f"ticker: {ticker}"

def test_dynamic_trend_lines(tickers, zigzag_trend_lines, default_properties_trend_lines):
    for ticker in tickers:
        logging.debug(f"ticker: {ticker}")
        for expected_pattern in load_expected_patterns(ticker, category=2):
            pattern_end_date = pd.to_datetime(expected_pattern.pivots[-1].point.time)
            # add 3 days to the pattern end date to account for the fact that the pattern may not be complete
            pattern_end_date += datetime.timedelta(days=3)
            success, patterns = calculate_patterns(ticker, zigzag_trend_lines,
                                          default_properties_trend_lines,
                                          find_trend_lines,
                                          start_date=START_DATE, end_date=pattern_end_date,
                                          category=2,
                                          min_index=expected_pattern.pivots[0].point.index)
            if success:
                assert expected_pattern in patterns, f"ticker: {ticker}"

def test_incremental_trend_lines(tickers, zigzag_trend_lines, default_properties_trend_lines):
    time_delta_before = zigzag_trend_lines.backcandles + 3
    time_delta_after = zigzag_trend_lines.forwardcandles + 1
    for ticker in tickers:
        logging.debug(f"ticker: {ticker}")
        for expected_pattern in load_expected_patterns(ticker, category=2):
            pattern_start_date = pd.to_datetime(expected_pattern.pivots[0].point.time)
            pattern_end_date = pd.to_datetime(expected_pattern.pivots[-1].point.time)
            # add days to the pattern start and end dates to account for the fact that the pattern may not be complete
            pattern_start_date -= datetime.timedelta(days=time_delta_before)
            pattern_end_date += datetime.timedelta(days=time_delta_after)
            success, patterns = calculate_patterns(
                ticker, zigzag_trend_lines,
                default_properties_trend_lines,
                find_trend_lines,
                start_date=pattern_start_date,
                end_date=pattern_end_date,
                category=2,
                start_index=expected_pattern.pivots[0].point.index-time_delta_before,
                min_index=expected_pattern.pivots[0].point.index)

            if success:
                assert expected_pattern in patterns, f"ticker: {ticker}"
