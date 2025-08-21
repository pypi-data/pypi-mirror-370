import glob
import os
import pandas as pd
import datetime
import json
import logging
from typing import List, Tuple
from pathlib import Path
from auto_chart_patterns.zigzag import Zigzag
from auto_chart_patterns.chart_pattern import ChartPattern
from auto_chart_patterns.trendline_patterns import TrendLineProperties
from auto_chart_patterns.reversal_patterns import ReversalPatternProperties
from auto_chart_patterns.rsi_div_patterns import RsiDivergenceProperties
from auto_chart_patterns.flag_pennant_patterns import FlagPennantProperties

columns = [
    'open time',
    'open',
    'high',
    'low',
    'close',
    'volume',
    'close time',
    'quote volume',
    'number of trades',
    'taker buy volume',
    'taker buy quote volume',
    'ignore'
]

PATTERN_CATEGORIES = {1:"flags_pennants",
                      2:"trend_lines",
                      3:"reversals",
                      4:"rsi_divergences"}
START_DATE = datetime.datetime(2024, 1, 1)
END_DATE = datetime.datetime(2024, 10, 30)

zigzag_fp = Zigzag(backcandles=1, forwardcandles=1, pivot_limit=200, offset=0, strong_trend_threshold=0.1)
scan_properties_fp = FlagPennantProperties(
    number_of_pivots=4,
    min_periods_lapsed=7,
    max_periods_lapsed=21,
    flat_ratio=0.05,
    align_ratio=0.4,
    flag_ratio=1.6,
    flag_pole_span_min=3,
    flag_pole_span_max=12,
    max_candle_body_crosses=2,
    major_volume_diff_pct=0.05,
    minor_volume_diff_pct=0.01,
    min_profit_pct=0.1,
)

zigzag_tl = Zigzag(backcandles=3, forwardcandles=3, pivot_limit=100, offset=0, strong_trend_threshold=0.1)
scan_properties_tl = TrendLineProperties(
    min_periods_lapsed=21,
    number_of_pivots=4,
    flat_ratio=0.05,
    align_ratio=0.4,
    max_candle_body_crosses=1,
    major_volume_diff_pct=0.1,
    minor_volume_diff_pct=0.01,
    min_profit_pct=0.1,
)

zigzag_rp = Zigzag(backcandles=2, forwardcandles=2, pivot_limit=100, offset=0)
scan_properties_rp = ReversalPatternProperties(
    min_periods_lapsed=14, # minimum number of days to form a pattern
    flat_ratio=0.15, # maximum allowed ratio between aligned horizontal pivots
    allowed_patterns=[
        True, # double top
        True, # double bottom
        True, # triple top
        True, # triple bottom
        True, # head and shoulders
        True, # inverted head and shoulders
    ],
    avoid_overlap=False,
    peak_symmetry_ratio=0.5,
    min_peak_distance=7,
    major_volume_diff_pct=0.1,
    minor_volume_diff_pct=0.01,
    min_profit_pct=0.1,
)

zigzag_rsi = Zigzag(backcandles=2, forwardcandles=3, pivot_limit=100, offset=0)
scan_properties_rsi = RsiDivergenceProperties(
    rsi_period=14,
    rsi_overbought=60,
    rsi_oversold=40,
    min_periods_lapsed=4,
    max_periods_lapsed=30,
    min_price_change_pct=0.02,
    min_rsi_change_points=1.5,
    min_profit_pct=0.02,
)

def get_data_for_ticker(ticker: str, start_date: datetime.datetime = None,
                        end_date: datetime.datetime = None, frequency: str = "daily"):
    # Get the directory where helpers.py is located
    current_file_dir = Path(__file__).parent
    # Go up to project root and then to data directory
    data_dir = current_file_dir / "data"

    # Read all CSV files in the directory
    all_files = glob.glob(os.path.join(data_dir, ticker, "*.csv"))
    df_list = []

    for file in all_files:
        df = pd.read_csv(file, names=columns)
        df_list.append(df)

    # Combine all dataframes
    combined_df = pd.concat(df_list, ignore_index=True)

    # Convert timestamp to datetime and sort
    combined_df['date'] = pd.to_datetime(combined_df['close time'], unit='ms')
    combined_df = combined_df.set_index('date')
    combined_df = combined_df.sort_values('date')

    # Convert string dates to datetime if provided
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)

    # Filter the dataframe by date range
    if start_date:
        combined_df = combined_df[combined_df.index >= start_date]
    if end_date:
        combined_df = combined_df[combined_df.index <= end_date]

    if frequency == "daily":
        combined_df = combined_df.resample('D')
    elif frequency == "hourly":
        combined_df = combined_df.resample('h')
    elif frequency == "weekly":
        combined_df = combined_df.resample('W')
    else:
        raise ValueError(f"Invalid frequency: {frequency}")

    combined_df = combined_df.agg({
            'open time': 'first',
            'close time': 'last',
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            "quote volume": 'sum',
            "number of trades": 'sum',
            "taker buy volume": 'sum',
            "taker buy quote volume": 'sum'
        }).dropna()

    return combined_df

def load_expected_patterns(ticker: str, category: int) -> List[ChartPattern]:
    # Get the directory where helpers.py is located
    current_file_dir = Path(__file__).parent
    # Go up to project root and then to data directory
    fixtures_dir = current_file_dir / "fixtures" / PATTERN_CATEGORIES[category]
    # Load expected patterns from JSON file
    with open(f'{fixtures_dir}/{ticker}_{PATTERN_CATEGORIES[category]}_patterns.json', 'r') as f:
        raw_patterns = json.load(f)
        # Convert to list of ChartPattern objects
        patterns = [ChartPattern.from_dict(pattern) for pattern in raw_patterns]
    return patterns

def calculate_patterns(ticker, zigzag, default_properties, find_pattern_func,
                       start_date, end_date, category,
                       start_index: int = 0,
                       min_index: int = None) -> Tuple[bool, List[ChartPattern]]:
    patterns: List[ChartPattern] = []
    prices = get_data_for_ticker(ticker, start_date=start_date, end_date=end_date)
    # check if the last date in prices is the same as the end date
    if prices[prices.index == end_date-datetime.timedelta(days=1)].empty:
        logging.warning(f"{ticker}: {PATTERN_CATEGORIES[category]}: Not enough data "
                        f"for pattern end date {end_date}, "
                        f"last date in prices: {prices.iloc[-1].name}")
        return False, patterns

    logging.debug(f"ticker: {ticker}, start_index: {start_index}, "
                  f"prices start date: {prices.iloc[0].name}, "
                  f"prices end date: {prices.iloc[-1].name}")
    if category == 4:
        find_pattern_func(zigzag.backcandles, zigzag.forwardcandles,
                          default_properties, patterns, prices)
    else:
        zigzag.calculate(prices, start_index)
        for i in range(0, len(zigzag.zigzag_pivots)):
            found = find_pattern_func(zigzag, i, default_properties, patterns)
            if min_index is not None and found and \
                    patterns[-1].pivots[0].point.index < min_index:
                break
    return True, patterns
