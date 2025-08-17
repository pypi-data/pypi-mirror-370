from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from .line import Point, Pivot, Line
from .zigzag import Zigzag
from .chart_pattern import ChartPattern, ChartPatternProperties, get_pivots_from_zigzag, \
    is_same_height, volume_exceeds

import logging
logger = logging.getLogger(__name__)

@dataclass
class TrendLineProperties(ChartPatternProperties):
    # minimum number of pivots to form a pattern
    number_of_pivots: int = 5
    # minimum number of periods lapsed between pivots
    min_periods_lapsed: int = 21
    # maximum allowed flat ratio between flat trend lines
    flat_ratio: float = 0.1
    # maximum allowed ratio between aligned diagonal pivots
    align_ratio: float = 0.4
    # maximum allowed candle body crosses for a valid trend line
    max_candle_body_crosses: int = 1
    # major volume percentage difference percentage
    major_volume_diff_pct: float = 0.1
    # minor volume percentage difference percentage
    minor_volume_diff_pct: float = 0.02

class TrendLinePattern(ChartPattern):
    apex: Point = None

    def __init__(self, pivots: List[Pivot], trend_line1: Line, trend_line2: Line):
        self.pivots = pivots
        self.trend_line1 = trend_line1
        self.trend_line2 = trend_line2
        self.extra_props = {}

    @classmethod
    def from_dict(cls, dict):
        self = cls(pivots=[Pivot.from_dict(p) for p in dict["pivots"]],
                   trend_line1=Line.from_dict(dict["trend_line1"]),
                   trend_line2=Line.from_dict(dict["trend_line2"]))
        if 'apex' in dict:
            self.apex = Point.from_dict(dict["apex"])
        self.pattern_type = dict["pattern_type"]
        self.pattern_name = dict["pattern_name"]
        return self

    def dict(self):
        obj = super().dict()
        obj["trend_line1"] = self.trend_line1.dict()
        obj["trend_line2"] = self.trend_line2.dict()
        if self.apex is not None:
            obj["apex"] = self.apex.dict()
        return obj

    def get_pattern_name_by_id(self, id: int) -> str:
        pattern_names = {
            1: "Ascending Channel",
            2: "Descending Channel",
            3: "Ranging Channel",
            4: "Ranging Channel (Bullish)",
            5: "Ranging Channel (Bearish)",
            6: "Diverging Triangle",
            7: "Converging Triangle (Bullish)",
            8: "Converging Triangle (Bearish)",
            9: "Rising Wedge (Contracting)",
            10: "Falling Wedge (Contracting)",
            11: "Converging Triangle",
            12: "Descending Triangle (Contracting)",
            13: "Ascending Triangle (Contracting)",
        }
        return pattern_names.get(id, "Error")

    def get_apex(self, start_index: int, start_time: datetime, interval: timedelta) -> Optional[Point]:
        """Get the apex point of the pattern if two trend lines converge"""
        max_iterations = 100
        if self.pivots[0].direction > 0:
            upper_line = self.trend_line1
            lower_line = self.trend_line2
        else:
            upper_line = self.trend_line2
            lower_line = self.trend_line1
        for i in range(1, max_iterations):
            index = start_index + i
            p1 = upper_line.get_price(index)
            p2 = lower_line.get_price(index)
            if p1 <= p2:
                return Point(index=index, time=start_time + i * interval, price=p1)
        return None

    def check_volume(self, properties: TrendLineProperties) -> int:
        up_pivots = [p for p in self.pivots[-2:] if p.point.candle_direction > 0]
        down_pivots = [p for p in self.pivots[-2:] if p.point.candle_direction < 0]
        if len(up_pivots) > len(down_pivots):
            return 1
        elif len(down_pivots) > len(up_pivots):
            return -1
        elif len(up_pivots) == 0:
            return 0
        else:
            up_pivot = up_pivots[-1]
            down_pivot = down_pivots[-1]
            logger.debug(f"Up pivot {up_pivot.point.index}: "
                         f"candle direction {up_pivot.point.candle_direction}, "
                         f"volume {up_pivot.point.volume}, "
                         f"Down pivot {down_pivot.point.index}: "
                         f"candle direction {down_pivot.point.candle_direction}, "
                         f"volume {down_pivot.point.volume}")
            if volume_exceeds(up_pivot.point.volume, down_pivot.point.volume,
                                        properties.major_volume_diff_pct):
                return 1
            elif volume_exceeds(down_pivot.point.volume, up_pivot.point.volume,
                                        properties.minor_volume_diff_pct):
                return -1
            else:
                return 0

    def check_profit_triangle(self, is_bullish: bool, properties: TrendLineProperties) -> bool:
        """Check if the profit is greater than the minimum profit"""
        if self.apex is None:
            raise ValueError("Apex point should not be None for triangle pattern!")
        else:
            support_price = self.apex.price
            resistance_price = self.apex.price
            target_price_delta = abs(self.trend_line1.p1.price - self.trend_line2.p1.price)
        return self.calculate_profit_ratio(support_price, resistance_price,
                                           target_price_delta, is_bullish, properties)

    def check_profit_channel(self, is_bullish: bool, properties: TrendLineProperties) -> bool:
        """Check if the profit is greater than the minimum profit"""
        if self.pivots[0].direction > 0:
            support_price = self.trend_line1.p2.price
            resistance_price = self.trend_line2.p2.price
        else:
            support_price = self.trend_line2.p2.price
            resistance_price = self.trend_line1.p2.price
        target_price_delta = abs(self.trend_line1.p1.price - self.trend_line2.p1.price)
        return self.calculate_profit_ratio(support_price, resistance_price,
                                           target_price_delta, is_bullish, properties)

    def calculate_profit_ratio(self, support_price: float, resistance_price: float,
                                target_price_delta: float, is_bullish: bool,
                                properties: TrendLineProperties) -> float:
        if is_bullish:
            return target_price_delta >= support_price * properties.min_profit_pct
        else:
            return target_price_delta >= resistance_price * properties.min_profit_pct

    def resolve(self, properties: TrendLineProperties) -> 'TrendLinePattern':
        self.resolve_shape(properties)
        if self.pattern_type == 1:
            # Ascending channel patterns
            if not self.check_profit_channel(False, properties):
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Ascending channel pattern bearish profit check failed")
                self.pattern_type = 0
            elif self.check_volume(properties) != -1:
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Ascending channel pattern bearish volume check failed")
                self.pattern_type = 0
        elif self.pattern_type == 2:
            # Descending channel patterns
            if not self.check_profit_channel(True, properties):
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Descending channel pattern bullish profit check failed")
                self.pattern_type = 0
            elif self.check_volume(properties) != 1:
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Descending channel pattern bullish volume check failed")
                self.pattern_type = 0
        elif self.pattern_type == 3:
            # Ranging channel patterns
            if self.pivots[0].direction > 0:
                if not self.check_profit_channel(True, properties):
                    logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                                f"Ranging channel pattern bullish profit check failed")
                    self.pattern_type = 0
                elif self.check_volume(properties) != 1:
                    logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                                f"Ranging channel pattern bullish volume check failed")
                    self.pattern_type = 0
                else:
                    self.pattern_type = 4 # Ranging Channel (Bullish)
            elif self.pivots[0].direction < 0:
                if not self.check_profit_channel(False, properties):
                    logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                                f"Ranging channel pattern bearish profit check failed")
                    self.pattern_type = 0
                elif self.check_volume(properties) != -1:
                    logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                                f"Ranging channel pattern bearish volume check failed")
                    self.pattern_type = 0
                else:
                    self.pattern_type = 5 # Ranging Channel (Bearish)
        elif self.pattern_type == 9:
            # Rising wedge patterns
            if not self.check_profit_triangle(False, properties):
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Rising wedge pattern bearish profit check failed")
                self.pattern_type = 0
            elif self.check_volume(properties) != -1:
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Rising wedge pattern bearish volume check failed")
                self.pattern_type = 0
        elif self.pattern_type == 10:
            # Falling wedge patterns
            if not self.check_profit_triangle(True, properties):
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Falling wedge pattern bullish profit check failed")
                self.pattern_type = 0
            elif self.check_volume(properties) != 1:
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Falling wedge pattern bullish volume check failed")
                self.pattern_type = 0
        elif self.pattern_type == 11:
            # Converging triangle patterns
            if self.check_profit_triangle(True, properties) and self.check_volume(properties) == 1:
                self.pattern_type = 7 # Converging Triangle (Bullish)
            elif self.check_profit_triangle(False, properties) and self.check_volume(properties) == -1:
                self.pattern_type = 8 # Converging Triangle (Bearish)
            else:
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Converging triangle pattern profit/volume check failed")
                self.pattern_type = 0
        elif self.pattern_type == 12:
            # Descending triangle patterns
            if not self.check_profit_triangle(False, properties):
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Descending triangle pattern bearish profit check failed")
                self.pattern_type = 0
            elif self.check_volume(properties) != -1:
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Descending triangle pattern bearish volume check failed")
                self.pattern_type = 0
        elif self.pattern_type == 13:
            # Ascending triangle patterns
            if not self.check_profit_triangle(True, properties):
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Ascending triangle pattern bullish profit check failed")
            elif self.check_volume(properties) != 1:
                logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                            f"Ascending triangle pattern bullish volume check failed")
                self.pattern_type = 0
        else:
            # invalidate other patterns
            self.pattern_type = 0
        return self

    def resolve_shape(self, properties: TrendLineProperties) -> 'TrendLinePattern':
        """
        Resolve pattern by updating trend lines, pivot points, and ratios

        Args:
            properties: ScanProperties object containing pattern parameters

        Returns:
            self: Returns the pattern object for method chaining
        """
        # Get first and last indices/times from pivots
        first_index = self.pivots[0].point.index
        last_index = self.pivots[-1].point.index
        first_time = self.pivots[0].point.time
        last_time = self.pivots[-1].point.time

        # Update trend line 1 endpoints
        self.trend_line1.p1 = Point(
            time=first_time,
            index=first_index,
            price=self.trend_line1.get_price(first_index)
        )
        self.trend_line1.p2 = Point(
            time=last_time,
            index=last_index,
            price=self.trend_line1.get_price(last_index)
        )

        # Update trend line 2 endpoints
        self.trend_line2.p1 = Point(
            time=first_time,
            index=first_index,
            price=self.trend_line2.get_price(first_index)
        )
        self.trend_line2.p2 = Point(
            time=last_time,
            index=last_index,
            price=self.trend_line2.get_price(last_index)
        )

        # Update pivot points to match trend lines
        for i, pivot in enumerate(self.pivots):
            current_trend_line = self.trend_line2 if i % 2 == 1 else self.trend_line1

            # Update pivot price to match trend line
            pivot.point.price = current_trend_line.get_price(pivot.point.index)

        # Resolve pattern name
        self.resolve_pattern_name(properties)
        if self.pattern_type == 9 or self.pattern_type == 10 or self.pattern_type == 11 or \
           self.pattern_type == 12 or self.pattern_type == 13:
            interval = (pd.to_datetime(last_time) - pd.to_datetime(first_time)) / (last_index - first_index)
            self.apex = self.get_apex(first_index, first_time, interval)
        return self

    def resolve_pattern_name(self, properties: TrendLineProperties) -> 'TrendLinePattern':
        """Determine the pattern type based on trend lines and angles"""
        t1p1 = self.trend_line1.p1.price
        t1p2 = self.trend_line1.p2.price
        t2p1 = self.trend_line2.p1.price
        t2p2 = self.trend_line2.p2.price

        # Calculate differences and ratios
        start_diff = abs(t1p1 - t2p1)
        end_diff = abs(t1p2 - t2p2)
        min_diff = min(start_diff, end_diff)
        is_expanding = end_diff > start_diff
        is_contracting = start_diff > end_diff

        if min_diff == 0:
            if start_diff == end_diff:
                # two trend lines are the same
                self.pattern_type = 0
                return self
            elif start_diff == 0:
                # expanding
                upper_diff = max(t1p2, t2p2) - t1p1
                lower_diff = min(t1p2, t2p2) - t1p1
            else:
                # contracting
                upper_diff = max(t1p1, t2p1) - t1p2
                lower_diff = min(t1p1, t2p1) - t1p2

            upper_line_dir = 1 if is_expanding else -1
            lower_line_dir = -1 if is_expanding else 1
            if upper_diff == 0:
                upper_line_dir = 0
            elif lower_diff == 0:
                lower_line_dir = 0
            else:
                ratio = abs(upper_diff / lower_diff)
                if ratio <= properties.flat_ratio:
                    upper_line_dir = 0
                elif ratio >= 1 / properties.flat_ratio:
                    lower_line_dir = 0
                else:
                    if upper_diff < 0:
                        upper_line_dir = -1 if is_expanding else 1
                    elif lower_diff > 0:
                        lower_line_dir = 1 if is_expanding else -1
        else:
            # Calculate angles between trend lines
            upper_angle = ((t1p2 - min(t2p1, t2p2)) / (t1p1 - min(t2p1, t2p2))
                          if t1p1 > t2p1 else
                          (t2p2 - min(t1p1, t1p2)) / (t2p1 - min(t1p1, t1p2)))

            lower_angle = ((t2p2 - max(t1p1, t1p2)) / (t2p1 - max(t1p1, t1p2))
                          if t1p1 > t2p1 else
                          (t1p2 - max(t2p1, t2p2)) / (t1p1 - max(t2p1, t2p2)))

            # Determine line directions
            upper_line_dir = (1 if upper_angle > 1 + properties.flat_ratio else
                             -1 if upper_angle < 1 - properties.flat_ratio else 0)

            lower_line_dir = (-1 if lower_angle > 1 + properties.flat_ratio else
                             1 if lower_angle < 1 - properties.flat_ratio else 0)

        # Calculate differences and ratios
        bar_diff = self.trend_line1.p2.index - self.trend_line2.p1.index
        price_diff = abs(start_diff - end_diff) / bar_diff if bar_diff != 0 else 0

        probable_converging_bars = min_diff / price_diff if price_diff != 0 else float('inf')

        is_channel = (probable_converging_bars > 2 * bar_diff or
                     (not is_expanding and not is_contracting) or
                     (upper_line_dir == 0 and lower_line_dir == 0))

        invalid = np.sign(t1p1 - t2p1) != np.sign(t1p2 - t2p2)

        # Determine pattern type
        if invalid:
            self.pattern_type = 0
        elif is_channel:
            if upper_line_dir > 0 and lower_line_dir > 0 :
                if self.pivots[0].direction == -2:
                    self.pattern_type = 1  # Ascending Channel
                else:
                    logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                                f"Invalid ascending channel pattern")
                    self.pattern_type = 0
            elif upper_line_dir < 0 and lower_line_dir < 0 :
                if self.pivots[0].direction == 2:
                    self.pattern_type = 2  # Descending Channel
                else:
                    logger.debug(f"Pivot start {self.pivots[0].point.index}, end {self.pivots[-1].point.index} "
                                f"Invalid descending channel pattern")
                    self.pattern_type = 0
            else:
                self.pattern_type = 3  # Ranging Channel
        elif is_expanding:
            self.pattern_type = 6  # Diverging Triangle
        elif is_contracting:
            if upper_line_dir > 0 and lower_line_dir > 0 and self.pivots[0].direction < 0:
                self.pattern_type = 9  # Rising Wedge (Contracting)
            elif upper_line_dir < 0 and lower_line_dir < 0 and self.pivots[0].direction > 0:
                self.pattern_type = 10  # Falling Wedge (Contracting)
            elif upper_line_dir < 0 and lower_line_dir > 0:
                self.pattern_type = 11  # Converging Triangle
            elif lower_line_dir == 0 and upper_line_dir < 0 and self.pivots[0].direction == -2:
                self.pattern_type = 12  # Descending Triangle (Contracting)
            elif upper_line_dir == 0 and lower_line_dir > 0 and self.pivots[0].direction == 2:
                self.pattern_type = 13 # Ascending Triangle (Contracting)
            else:
                self.pattern_type = 0
        else:
            self.pattern_type = 0

        return self

def is_aligned(pivots: List[Pivot], ref_pivots: List[Pivot], align_ratio: float,
               flat_ratio: float) -> bool:
    if len(pivots) > 3:
        raise ValueError("Pivots can't be more than 3")
    if len(pivots) < 3:
        return True

    first = pivots[0]
    second = pivots[1]
    third = pivots[2]
    if is_same_height(first, second, ref_pivots, flat_ratio) and \
        is_same_height(second, third, ref_pivots, flat_ratio):
        logger.debug(f"Pivots: {first.point.index}, {second.point.index}, {third.point.index} "
                     f"are aligned as a horizontal line")
        return True

    # check the ratio of the price differences to the bar differences
    if third.cross_diff == 0:
        # the first and third pivots are the same height, but they are not aligned
        # with the second pivot
        return False
    price_ratio = second.cross_diff / third.cross_diff
    bar_ratio = float(second.point.index - first.point.index) / \
        float(third.point.index - second.point.index)
    ratio = price_ratio / bar_ratio
    fit_pct = 1 - align_ratio
    if ratio < 1:
        aligned = ratio >= fit_pct
    else:
        aligned = ratio <= 1 / fit_pct
    logger.debug(f"Pivots: {first.point.index}, {second.point.index}, {third.point.index} "
                 f"price ratio: {price_ratio:.4f}, bar ratio: {bar_ratio:.4f}, ratio: {ratio:.4f}")
    return aligned

def check_if_line_cross_candle_body(line: Line, direction: float, zigzag: Zigzag,
                                    line_start_index: Optional[int] = None,
                                    line_end_index: Optional[int] = None) -> int:
    """
    Check if a line crosses the candle body
    """
    if line_start_index is not None and line_start_index < line.p1.index:
        start_index = line_start_index
    else:
        start_index = line.p1.index

    if line_end_index is not None and line_end_index > line.p2.index:
        end_index = line_end_index
    else:
        end_index = line.p2.index

    crosses = 0
    for i in range(start_index + 1, end_index):
        bar_data = zigzag.get_df_data_by_index(i)
        if direction > 0 and line.get_price(i) < max(bar_data['open'], bar_data['close']):
            crosses += 1
        elif direction < 0 and line.get_price(i) > min(bar_data['open'], bar_data['close']):
            crosses += 1
    return crosses

def inspect_line_by_point(line: Line, point_bar: int, direction: float,
                          zigzag: Zigzag) -> Tuple[bool, float]:
    """
    Inspect a single line against price data from a pandas DataFrame

    Args:
        line: Line object to inspect
        point_bar: Index of the point to inspect
        direction: Direction of the trend (1 for up, -1 for down)
        zigzag: Zigzag calculator instance

    Returns:
        Tuple of (valid: bool, diff: float)
    """
    # Get price data from DataFrame
    bar_data = zigzag.get_df_data_by_index(point_bar)

    # Determine prices based on direction
    line_price = line.get_price(point_bar)
    line_price_diff = abs(line.p1.price - line.p2.price)
    if direction > 0:
        # upper line
        body_high_price = max(bar_data['open'], bar_data['close'])
        if line_price < body_high_price:
            # invalid if line is crossing the candle body
            return False, float('inf') # make the difference as large as possible
        elif line_price > bar_data['high']:
            # line is above the candle wick
            diff = line_price - bar_data['high']
            return diff < line_price_diff, diff
        else:
            # line is crossing the candle wick
            return True, 0
    else:
        # lower line
        body_low_price = min(bar_data['open'], bar_data['close'])
        if line_price > body_low_price:
            # invalid if line is crossing the candle body
            return False, float('inf') # make the difference as large as possible
        elif line_price < bar_data['low']:
            # line is below the candle wick
            diff = bar_data['low'] - line_price
            return diff < line_price_diff, diff
        else:
            # line is crossing the candle wick
            return True, 0

def inspect_pivots(pivots: List[Pivot], direction: float, properties: TrendLineProperties,
                   first_pivot: Pivot, last_pivot: Pivot, zigzag: Zigzag) -> Tuple[bool, Line]:
    """
    Inspect multiple pivots to find the best trend line using DataFrame price data

    Args:
        pivots: List of pivots to create trend lines
        direction: Direction of the trend
        properties: TrendLineProperties object containing pattern parameters
        first_pivot: The first pivot to inspect
        last_pivot: The last pivot to inspect
        zigzag: Zigzag calculator instance

    Returns:
        Tuple of (valid: bool, best_trend_line: Line)
    """
    if len(pivots) == 3:
        # Create three possible trend lines
        trend_line1 = Line(pivots[0].point, pivots[2].point)  # First to last
        # check if the line consisting of the first and last points crosses the candle body
        if check_if_line_cross_candle_body(trend_line1, direction, zigzag) > \
            properties.max_candle_body_crosses:
            return False, None
        # inspect line by middle point
        valid1, diff1 = inspect_line_by_point(trend_line1, pivots[1].point.index,
                                              direction, zigzag)
        if valid1 and diff1 == 0:
            # prefer the line connecting the first and last points
            return True, trend_line1

        trend_line2 = Line(pivots[0].point, pivots[1].point)  # First to middle
        valid2, diff2 = inspect_line_by_point(trend_line2, pivots[2].point.index,
                                              direction, zigzag)

        trend_line3 = Line(pivots[1].point, pivots[2].point)  # Middle to last
        valid3, diff3 = inspect_line_by_point(trend_line3, pivots[0].point.index,
                                              direction, zigzag)

        if not valid1 and not valid2 and not valid3:
            return False, None

        # Find the best line
        if valid1:
            trendline = trend_line1
        elif valid2 and diff2 < diff1:
            trendline = trend_line2
        elif valid3 and diff3 < min(diff1, diff2):
            trendline = trend_line3
        else:
            return False, None

        return True, trendline
    else:
        # For 2 points, simply create one trend line
        trend_line = Line(pivots[0].point, pivots[1].point)
        valid = check_if_line_cross_candle_body(
            trend_line, direction, zigzag,
            first_pivot.point.index, last_pivot.point.index) <= \
            properties.max_candle_body_crosses
        return valid, trend_line

def find_trend_lines(zigzag: Zigzag, offset: int, properties: TrendLineProperties,
                patterns: List[TrendLinePattern]) -> bool:
    """
    Find patterns using DataFrame price data

    Args:
        zigzag: ZigZag calculator instance
        offset: Offset to start searching for pivots
        properties: Scan properties
        patterns: List to store found patterns

    Returns:
        int: Index of the pivot that was used to find the pattern
    """
    # Get pivots
    if properties.number_of_pivots < 4 or properties.number_of_pivots > 6:
        raise ValueError("Number of pivots must be between 4 and 6")

    pivots = []
    min_pivots = get_pivots_from_zigzag(zigzag, pivots, offset, properties.number_of_pivots)
    if min_pivots != properties.number_of_pivots:
        return False

    # Validate pattern
    # Create point arrays for trend lines
    trend_pivots1 = ([pivots[0], pivots[2], pivots[4]]
                      if properties.number_of_pivots == 5
                      else [pivots[0], pivots[2]])
    trend_pivots2 = ([pivots[1], pivots[3], pivots[5]]
                      if properties.number_of_pivots == 6
                      else [pivots[1], pivots[3]])

    if not is_aligned(trend_pivots1, pivots, properties.align_ratio,
                      properties.flat_ratio) or \
        not is_aligned(trend_pivots2, pivots, properties.align_ratio,
                       properties.flat_ratio):
        return False

    # Validate trend lines using DataFrame
    valid1, trend_line1 = inspect_pivots(trend_pivots1,
                                        np.sign(trend_pivots1[0].direction),
                                        properties, pivots[0], pivots[-1], zigzag)
    valid2, trend_line2 = inspect_pivots(trend_pivots2,
                                        np.sign(trend_pivots2[0].direction),
                                        properties, pivots[0], pivots[-1], zigzag)

    if valid1 and valid2:
        index_delta = pivots[-1].point.index - pivots[0].point.index + 1
        if index_delta < properties.min_periods_lapsed:
            # only consider patterns with enough time lapsed
            return False

        # Create pattern
        pattern = TrendLinePattern(
            pivots=pivots,
            trend_line1=trend_line1,
            trend_line2=trend_line2,
        ).resolve(properties)

        # Process pattern (resolve type, check if allowed, etc.)
        return pattern.process_pattern(properties, patterns)
    else:
        return False
