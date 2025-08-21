from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from .line import Pivot, Line
from .zigzag import Zigzag
from .trendline_patterns import TrendLinePattern, TrendLineProperties, \
    get_pivots_from_zigzag, inspect_pivots

import logging
logger = logging.getLogger(__name__)

@dataclass
class FlagPennantProperties(TrendLineProperties):
    number_of_pivots: int = 4 # minimum number of pivots to form a pattern
    min_periods_lapsed: int = 7 # minimum number of periods to form a pattern
    max_periods_lapsed: int = 21 # maximum periods a flag/pennant can span
    flag_ratio: float = 1.5 # minimum allowed flag/pennant ratio between flag pole and flag width
    flag_pole_span_max: int = 12 # maximum periods a flag/pennant pole can span
    flag_pole_span_min: int = 3 # minimum periods a flag/pennant pole can span
    max_candle_body_crosses: int = 1 # maximum allowed candle body crosses for a valid trend line

class FlagPennantPattern(TrendLinePattern):
    def __init__(self, pivots: List[Pivot],
                 trend_line1: Line, trend_line2: Line,
                 pole_height: Optional[float] = None):
        super().__init__(pivots, trend_line1, trend_line2)
        self.pole_height = pole_height
        self.extra_props = {}

    @classmethod
    def from_dict(cls, dict):
        self = super().from_dict(dict)
        self.pole_height = dict["pole_height"]
        return self

    def dict(self):
        obj = super().dict()
        obj["pole_height"] = self.pole_height
        return obj

    def get_pattern_name_by_id(self, id: int) -> str:
        pattern_names = {
            14: "Bull Pennant",
            15: "Bear Pennant",
            16: "Bull Flag",
            17: "Bear Flag",
        }
        return pattern_names.get(id, "Error")

    def resolve(self, properties: FlagPennantProperties) -> 'FlagPennantPattern':
        """
        Resolve pattern by updating trend lines, pivot points, and ratios

        Args:
            properties: ScanProperties object containing pattern parameters

        Returns:
            self: Returns the pattern object for method chaining
        """
        super().resolve_shape(properties)
        if self.pattern_type == 0:
            return self

        # flag size must be smaller than its pole
        valid, direction = self.check_flag_shape(properties)
        if valid:
            if direction > 0:
                if self.pattern_type == 2:
                    if self.check_profit_flag(True, properties) and self.check_volume(properties) == 1:
                        # descending channel patterns
                        self.pattern_type = 16  # Bull Flag
                    else:
                        logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                                     f"{self.pivots[-1].point.index}, pattern type: {self.pattern_type}, "
                                     f"pole height: {self.pole_height} didn't pass bullish flag profit check")
                        self.pattern_type = 0
                elif self.pattern_type == 11 or self.pattern_type == 10:
                    if self.check_profit_pennant(True, properties) and self.check_volume(properties) == 1:
                        # pennant patterns
                        self.pattern_type = 14  # Bull Pennant
                    else:
                        logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                                     f"{self.pivots[-1].point.index}, pattern type: {self.pattern_type}, "
                                     f"pole height: {self.pole_height} didn't pass bullish pennant profit check")
                        self.pattern_type = 0
                else:
                    logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                                 f"{self.pivots[-1].point.index}, pattern type: {self.pattern_type} wasn't in good shape")
                    self.pattern_type = 0
            elif direction < 0:
                if self.pattern_type == 1:
                    if self.check_profit_flag(False, properties) and self.check_volume(properties) == -1:
                        logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                                     f"{self.pivots[-1].point.index}, pattern type: {self.pattern_type}, "
                                     f"pole height: {self.pole_height} passed bearish flag profit check")
                        self.pattern_type = 17  # Bear Flag
                    else:
                        logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                                     f"{self.pivots[-1].point.index}, pattern type: {self.pattern_type}, "
                                     f"pole height: {self.pole_height} didn't pass bearish flag profit check")
                        self.pattern_type = 0
                elif self.pattern_type == 11 or self.pattern_type == 9:
                    if self.check_profit_pennant(False, properties) and self.check_volume(properties) == -1:
                        self.pattern_type = 15  # Bear Pennant
                    else:
                        logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                                     f"{self.pivots[-1].point.index}, pattern type: {self.pattern_type}, "
                                     f"pole height: {self.pole_height} didn't pass bearish pennant profit check")
                        self.pattern_type = 0
                else:
                    logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                                 f"{self.pivots[-1].point.index}, pattern type: {self.pattern_type} wasn't in good shape")
                    self.pattern_type = 0
            else:
                raise ValueError(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                             f"{self.pivots[-1].point.index} is in invalid direction")
        else:
            # invalidate other pattern types
            logger.debug(f"Pivot start: {self.pivots[0].point.index}, Pivot end: "
                         f"{self.pivots[-1].point.index} didn't pass shape check")
            self.pattern_type = 0

        return self

    def check_profit_pennant(self, is_bullish: bool, properties: TrendLineProperties) -> bool:
        """Check if the profit is greater than the minimum profit"""
        if self.apex is None:
            raise ValueError("Apex point should not be None for triangle pattern!")
        else:
            support_price = self.apex.price
            resistance_price = self.apex.price
        return self.calculate_profit_ratio(support_price, resistance_price,
                                           self.pole_height,
                                           is_bullish, properties)

    def check_profit_flag(self, is_bullish: bool, properties: TrendLineProperties) -> bool:
        if self.pivots[0].direction > 0:
            support_price = self.trend_line1.p2.price
            resistance_price = self.trend_line2.p2.price
        else:
            support_price = self.trend_line2.p2.price
            resistance_price = self.trend_line1.p2.price
        return self.calculate_profit_ratio(support_price, resistance_price,
                                           self.pole_height,
                                           is_bullish, properties)

    def check_flag_shape(self, properties: FlagPennantProperties) -> Tuple[bool, float]:
        """Check if the flag shape is valid"""
        flag_span = self.pivots[-1].point.index - self.pivots[0].point.index + 1
        pivot_0_direction = self.pivots[0].direction
        flag_size = abs(self.trend_line1.p1.price - self.trend_line2.p1.price)
        pivot_0_candle_body_diff = self.pivots[0].candle_body_diff
        pivot_0_cross_candle_body_diff = self.pivots[0].cross_candle_body_diff
        pivot_1_candle_body_diff = self.pivots[1].candle_body_diff
        pivot_0_1_index_diff = self.pivots[1].point.index - self.pivots[0].point.index
        if np.sign(pivot_0_direction) == np.sign(pivot_0_candle_body_diff):
            pole_height = abs(pivot_0_candle_body_diff)
            if pole_height < flag_size * properties.flag_ratio:
                return False, 0
            flag_pole_span = self.pivots[0].index_diff
            flag_span += flag_pole_span
            if flag_pole_span < properties.flag_pole_span_min or \
                flag_pole_span > properties.flag_pole_span_max:
                return False, 0
            elif flag_span < properties.min_periods_lapsed or \
                flag_span > properties.max_periods_lapsed:
                return False, 0
            else:
                self.pole_height = pole_height
                return True, 1 if pivot_0_direction > 0 else -1
        else:
            pole_height = abs(pivot_0_cross_candle_body_diff) + abs(pivot_1_candle_body_diff)
            if pole_height < flag_size * properties.flag_ratio:
                return False, 0
            flag_pole_span = self.pivots[0].cross_index_diff + pivot_0_1_index_diff
            flag_span += flag_pole_span
            if flag_pole_span < properties.flag_pole_span_min or \
                flag_pole_span > properties.flag_pole_span_max:
                return False, 0
            elif flag_span < properties.min_periods_lapsed or \
                flag_span > properties.max_periods_lapsed:
                return False, 0
            else:
                self.pole_height = pole_height
                return True, -1 if pivot_0_direction > 0 else 1

def find_flags_and_pennants(zigzag: Zigzag, offset: int, properties: TrendLineProperties,
                      patterns: List[TrendLinePattern]) -> bool:
    """
    Find flag pennant patterns

    Args:
        zigzag: ZigZag calculator instance
        offset: Offset to start searching for pivots
        properties: Scan properties
        patterns: List to store found patterns

    Returns:
        int: Index of the pivot that was used to find the pattern
    """
    # Get pivots
    if properties.number_of_pivots != 4:
        raise ValueError("Number of pivots must be 4")

    pivots = []
    min_pivots = get_pivots_from_zigzag(zigzag, pivots, offset, properties.number_of_pivots)
    if min_pivots != properties.number_of_pivots:
        return False

    # Validate pattern
    # Create point arrays for trend lines
    trend_pivots1 = ([pivots[0], pivots[2]])
    trend_pivots2 = ([pivots[1], pivots[3]])

    # Validate trend lines using DataFrame
    valid1, trend_line1 = inspect_pivots(trend_pivots1,
                                        np.sign(trend_pivots1[0].direction),
                                        properties, pivots[0], pivots[-1], zigzag)
    valid2, trend_line2 = inspect_pivots(trend_pivots2,
                                        np.sign(trend_pivots2[0].direction),
                                        properties, pivots[0], pivots[-1], zigzag)

    if valid1 and valid2:
        # Create pattern
        pattern = FlagPennantPattern(
            pivots=pivots,
            trend_line1=trend_line1,
            trend_line2=trend_line2,
        ).resolve(properties)

        # Process pattern (resolve type, check if allowed, etc.)
        return pattern.process_pattern(properties, patterns)
    else:
        return False
