from dataclasses import dataclass
from auto_chart_patterns.chart_pattern import ChartPattern, ChartPatternProperties
from auto_chart_patterns.line import Line, Pivot, Point
from auto_chart_patterns.zigzag import window_peaks
from typing import List
import pandas as pd
import logging

log = logging.getLogger(__name__)

@dataclass
class RsiDivergenceProperties(ChartPatternProperties):
    rsi_period: int = 14 # RSI period
    rsi_overbought: int = 70 # RSI overbought level
    rsi_oversold: int = 30 # RSI oversold level
    min_periods_lapsed: int = 5 # minimum number of days to form a pattern
    max_periods_lapsed: int = 30 # maximum number of days to form a pattern
    min_price_change_pct: float = 0.03 # minimum change percentage
    min_rsi_change_points: float = 5 # minimum change points

class RsiDivergencePattern(ChartPattern):
    def __init__(self, pivots: List[Pivot], divergence_line: Line):
        self.pivots = pivots
        self.divergence_line = divergence_line
        self.extra_props = {}

    @classmethod
    def from_dict(cls, dict):
        self = cls(pivots=[Pivot.from_dict(p) for p in dict["pivots"]],
                   divergence_line=Line.from_dict(dict["divergence_line"]))
        self.pattern_type = dict["pattern_type"]
        self.pattern_name = dict["pattern_name"]
        return self

    def dict(self):
        obj = super().dict()
        obj["divergence_line"] = self.divergence_line.dict()
        return obj

    def get_pattern_name_by_id(self, id: int) -> str:
        pattern_names = {
            1: "Bullish",
            2: "Bearish",
            3: "Hidden Bullish",
            4: "Hidden Bearish",
        }
        return pattern_names[id]

    def get_change_direction(self, value1: float, value2: float,
                             min_change_threshold: float, is_pct: bool = True) -> int:
        if is_pct:
            diff = (value2 - value1) / value1
        else:
            diff = value2 - value1
        if diff > min_change_threshold:
            return 1
        elif diff < -min_change_threshold:
            return -1
        return 0

    def check_profit(self, prices: pd.DataFrame, properties: RsiDivergenceProperties) -> bool:
        """Check if the pattern is profitable"""
        start_price = self.pivots[0].point.price
        end_price = self.pivots[-1].point.price
        end_time = self.pivots[-1].point.time
        reference_price = prices.loc[end_time]['close']
        target_delta = abs(end_price - start_price)
        log.debug(f"start_price: {start_price}, end_price: {end_price}, reference_price: {reference_price}, "
                  f"target_delta: {target_delta}, min_profit_pct: {properties.min_profit_pct}")
        return target_delta > reference_price * properties.min_profit_pct

    def resolve(self, properties: RsiDivergenceProperties,
                prices: pd.DataFrame) -> 'RsiDivergencePattern':
        if len(self.pivots) != 2:
            raise ValueError("Rsi Divergence must have 2 pivots")
        self.pattern_type = 0

        rsi = self.divergence_line.p2.price
        # makes prices always greater than the rsi values
        price_change_dir = self.get_change_direction(self.pivots[0].point.price,
            self.pivots[1].point.price, properties.min_price_change_pct)
        rsi_change_dir = self.get_change_direction(self.divergence_line.p1.price,
            self.divergence_line.p2.price, properties.min_rsi_change_points, False)

        log.debug(f"points: {self.pivots[0].point.time}, {self.pivots[1].point.time}, "
                  f"rsi: {self.divergence_line.p1.price}, {self.divergence_line.p2.price}, "
                  f"price_change_dir: {price_change_dir}, rsi_change_dir: {rsi_change_dir}")

        if price_change_dir == 1 and rsi_change_dir == -1:
            if self.pivots[0].direction > 0 and rsi > properties.rsi_overbought:
                # higher high but lower RSI
                self.pattern_type = 2 # bearish
            elif self.pivots[0].direction < 0 and rsi < properties.rsi_oversold:
                # higher low but lower RSI
                self.pattern_type = 3 # hidden bullish
        elif price_change_dir == -1 and rsi_change_dir == 1:
            if self.pivots[0].direction > 0 and rsi > properties.rsi_overbought:
                # lower high but higher RSI
                self.pattern_type = 4 # hidden bearish
            elif self.pivots[0].direction < 0 and rsi < properties.rsi_oversold:
                # lower low but higher RSI
                self.pattern_type = 1 # bullish

        if self.pattern_type != 0:
            if self.check_profit(prices, properties):
                self.pattern_name = self.get_pattern_name_by_id(self.pattern_type)
            else:
                self.pattern_type = 0
        return self

def calc_rsi(prices: pd.DataFrame, period: int) -> pd.Series:
    """Calculate RSI"""
    series = prices["close"]
    ewm = dict(alpha=1.0 / period, min_periods=period, adjust=True, ignore_na=True)
    diff = series.diff()
    ups = diff.clip(lower=0).ewm(**ewm).mean()
    downs = diff.clip(upper=0).abs().ewm(**ewm).mean()

    return 100.0 - (100.0 / (1.0 + ups / downs))

def handle_rsi_pivots(rsi_pivots: pd.DataFrame, is_high_pivots: bool,
                      prices: pd.DataFrame,
                      properties: RsiDivergenceProperties,
                      patterns: List[RsiDivergencePattern]):
    if is_high_pivots:
        rsi_col = 'rsi_high'
        price_col = 'close'
    else:
        rsi_col = 'rsi_low'
        price_col = 'close'

    for i in range(len(rsi_pivots)-1):
        current_row = rsi_pivots.iloc[i]
        next_row = rsi_pivots.iloc[i+1]
        current_index = current_row['row_number'].astype(int)
        next_index = next_row['row_number'].astype(int)
        lapse = next_index - current_index + 1
        if lapse < properties.min_periods_lapsed or lapse > properties.max_periods_lapsed:
            continue

        point1 = Point(current_row.name, current_index,
                       current_row[rsi_col])
        point2 = Point(next_row.name, next_index,
                       next_row[rsi_col])
        divergence_line = Line(point1, point2)
        direction = 1 if is_high_pivots else -1
        price_pivots = [
            Pivot(
                Point(current_row.name, current_index,
                       current_row[price_col], current_row['volume']),
                direction),
            Pivot(
                Point(next_row.name, next_index,
                       next_row[price_col], next_row['volume']),
                direction)]
        pattern = RsiDivergencePattern(price_pivots, divergence_line).resolve(properties, prices)
        if pattern.pattern_type != 0:
            patterns.append(pattern)

def find_rsi_divergences(backcandles: int, forwardcandles: int,
                         properties: RsiDivergenceProperties,
                         patterns: List[RsiDivergencePattern],
                         prices: pd.DataFrame):
    """dfpricesdfprices
    Find RSI divergences using zigzag pivots

    Args:
        backcandles: Number of backcandles
        forwardcandles: Number of forwardcandles
        properties: RSI divergence properties
        patterns: List to store found patterns
        df: DataFrame with prices
    """
    # calculate rsi
    rsi = calc_rsi(prices, properties.rsi_period)
    # get rsi peaksprices
    rsi_highs, rsi_lows = window_peaks(rsi, backcandles, forwardcandles)

    # Merge for highs - including RSI values
    rsi_pivots= pd.DataFrame({
        'rsi_high': rsi.where(rsi == rsi_highs),
        'rsi_low': rsi.where(rsi == rsi_lows),
        'close': prices['close'],
        'volume': prices['volume'],
        'row_number': pd.RangeIndex(len(prices))
    })

    handle_rsi_pivots(
        rsi_pivots[['rsi_high', 'close', 'volume', 'row_number']].dropna(),
        True, prices, properties, patterns)
    handle_rsi_pivots(
        rsi_pivots[['rsi_low', 'close', 'volume', 'row_number']].dropna(),
        False, prices, properties, patterns)
