from dataclasses import dataclass
from typing import List, Optional
from .chart_pattern import ChartPattern, ChartPatternProperties, get_pivots_from_zigzag, \
    is_same_height, volume_exceeds
from .line import Pivot, Line, Point
from .zigzag import Zigzag
import logging

logger = logging.getLogger(__name__)

@dataclass
class ReversalPatternProperties(ChartPatternProperties):
    # minimum number of days to form a pattern
    min_periods_lapsed: int = 14
    # maximum allowed ratio between aligned horizontal pivots
    flat_ratio: float = 0.15
    # maximum allowed ratio between the two side peaks and the middle peak
    peak_symmetry_ratio: float = 0.5
    # minimum distance between peaks
    min_peak_distance: int = 7
    # major volume difference percentage between peaks or troughs
    major_volume_diff_pct: float = 0.1
    # minor volume difference percentage between peaks or troughs
    minor_volume_diff_pct: float = 0.01

class ReversalPattern(ChartPattern):
    def __init__(self, pivots: List[Pivot], support_line: Line):
        self.pivots = pivots
        self.pivots_count = len(pivots)
        self.support_line = support_line
        self.extra_props = {}

    @classmethod
    def from_dict(cls, dict):
        self = cls(pivots=[Pivot.from_dict(p) for p in dict["pivots"]],
                   support_line=Line.from_dict(dict["support_line"]))
        self.pattern_type = dict["pattern_type"]
        self.pattern_name = dict["pattern_name"]
        return self

    def dict(self):
        obj = super().dict()
        obj["support_line"] = self.support_line.dict()
        return obj

    def get_pattern_name_by_id(self, id: int) -> str:
        pattern_names = {
            1: "Double Tops",
            2: "Double Bottoms",
            3: "Triple Tops",
            4: "Triple Bottoms",
            5: "Head and Shoulders",
            6: "Inverted Head and Shoulders",
        }
        return pattern_names[id]

    def check_volumes_head_n_shoulders(self, properties: ReversalPatternProperties) -> bool:
        # left shoulder and head should have larger volumes than right shoulder
        return volume_exceeds(self.pivots[1].point.volume, self.pivots[5].point.volume, properties.major_volume_diff_pct) and \
            volume_exceeds(self.pivots[3].point.volume, self.pivots[5].point.volume, properties.major_volume_diff_pct)

    def check_volumes_inverse_head_n_shoulders(self, properties: ReversalPatternProperties) -> bool:
        # The right shoulder should show the level of volume often exceeds that on the left shoulder.
        # The dip to the right shoulder should be on very light volume
        return volume_exceeds(self.pivots[4].point.volume, self.pivots[2].point.volume, properties.minor_volume_diff_pct) and \
            volume_exceeds(self.pivots[4].point.volume, self.pivots[5].point.volume, properties.major_volume_diff_pct)

    def check_volumes_3_tops(self, properties: ReversalPatternProperties) -> bool:
        # each rally peak should be on lighter volume
        return volume_exceeds(self.pivots[1].point.volume, self.pivots[3].point.volume, properties.minor_volume_diff_pct) and \
            volume_exceeds(self.pivots[3].point.volume, self.pivots[5].point.volume, properties.minor_volume_diff_pct)

    def check_volumes_3_bottoms(self, properties: ReversalPatternProperties) -> bool:
        # The volume of the middle trough should be lighter than the left trough
        # The volume of right peak should exceed the one on the left
        # The volume of the right trough should be very light
        return volume_exceeds(self.pivots[1].point.volume, self.pivots[3].point.volume, properties.minor_volume_diff_pct) and \
            volume_exceeds(self.pivots[4].point.volume, self.pivots[2].point.volume, properties.minor_volume_diff_pct) and \
            volume_exceeds(self.pivots[4].point.volume, self.pivots[5].point.volume, properties.major_volume_diff_pct)

    def check_volumes_2_tops(self, properties: ReversalPatternProperties) -> bool:
        # left peak should have larger volumes than right peak
        return volume_exceeds(self.pivots[1].point.volume, self.pivots[3].point.volume, properties.minor_volume_diff_pct)

    def check_volumes_2_bottoms(self, properties: ReversalPatternProperties) -> bool:
        # center peak should have larger volumes than the right trough
        # left trough should have larger volume than the right trough
        return volume_exceeds(self.pivots[2].point.volume, self.pivots[3].point.volume, properties.major_volume_diff_pct) and \
            volume_exceeds(self.pivots[1].point.volume, self.pivots[3].point.volume, properties.minor_volume_diff_pct)

    def check_profit(self, properties: ReversalPatternProperties) -> bool:
        max_price = max([p.point.price for p in self.pivots])
        min_price = min([p.point.price for p in self.pivots])
        reference_price = self.pivots[-3].point.price
        if self.pivots[0].direction < 0:
            profit = (max_price - reference_price) / reference_price
        else:
            profit = (reference_price - min_price) / reference_price
        logger.debug(f"Reversal pattern {self.pattern_type} profit: {profit}")
        return profit >= properties.min_profit_pct

    def resolve(self, properties: ReversalPatternProperties) -> 'ReversalPattern':
        self.pattern_type = 0
        if not self.check_profit(properties):
            return self
        if self.pivots_count == 5:
            if self.pivots[0].direction < 0:
                if self.check_volumes_2_tops(properties):
                    self.pattern_type = 1 # Double Tops
            else:
                if self.check_volumes_2_bottoms(properties):
                    self.pattern_type = 2 # Double Bottoms
        elif self.pivots_count == 7:
            if is_same_height(self.pivots[1], self.pivots[5], self.pivots, properties.flat_ratio):
                # check if three pivots are approximately flat
                if is_same_height(self.pivots[1], self.pivots[3], self.pivots, properties.flat_ratio) and \
                    is_same_height(self.pivots[3], self.pivots[5], self.pivots, properties.flat_ratio):
                    # 3 pivots are approximately flat, we have a triple top or bottom
                    logger.debug(f"Pivots: {self.pivots[1].point.index}, {self.pivots[3].point.index}, "
                                 f"{self.pivots[5].point.index} are flat")
                    if self.pivots[0].direction < 0:
                        if self.check_volumes_3_tops(properties):
                            self.pattern_type = 3 # Triple Tops
                    else:
                        if self.check_volumes_3_bottoms(properties):
                            self.pattern_type = 4 # Triple Bottoms
                # check if the side peaks are lower than the middle peak
                elif self.pivots[0].direction < 0 and self.pivots[3].cross_candle_body_diff > 0 and \
                    self.pivots[5].cross_candle_body_diff < 0:
                    if self.check_volumes_head_n_shoulders(properties):
                        self.pattern_type = 5 # Head and Shoulders
                elif self.pivots[0].direction > 0 and self.pivots[3].cross_candle_body_diff < 0 and \
                    self.pivots[5].cross_candle_body_diff > 0:
                    if self.check_volumes_inverse_head_n_shoulders(properties):
                        self.pattern_type = 6 # Inverted Head and Shoulders
        else:
            raise ValueError("Invalid number of pivots")
        return self

def check_peak_symmetry(diff1: int, diff2: int, threshold: float) -> bool:
    # check the symmetry of the side peaks and the middle peak
    ratio = float(diff1) / float(diff2)
    fit_pct = 1 - threshold
    if ratio < 1:
        valid = ratio >= fit_pct
    else:
        valid = ratio <= 1 / fit_pct
    return valid

def inspect_five_pivot_pattern(pivots: List[Pivot], properties: ReversalPatternProperties) -> bool:
    # check tops or bottoms are approximately flat
    if is_same_height(pivots[1], pivots[3], pivots, properties.flat_ratio):
        valid = check_peak_symmetry(pivots[2].point.index - pivots[1].point.index,
                                   pivots[3].point.index - pivots[2].point.index,
                                   properties.peak_symmetry_ratio)
        logger.debug(f"Pivot {pivots[1].point.index} "
                     f"and {pivots[3].point.index} "
                     f"failed peak symmetry check")
        return valid
    return False

def inspect_seven_pivot_pattern(pivots: List[Pivot], properties: ReversalPatternProperties) -> bool:
    # check the double sandle points price range and flat ratio
    if pivots[0].direction > 0:
        if pivots[2].point.price >= pivots[0].point.price or \
            pivots[4].point.price >= pivots[0].point.price:
            return False
    else:
        if pivots[2].point.price <= pivots[0].point.price or \
            pivots[4].point.price <= pivots[0].point.price:
            return False
    # check the symmetry of the side peaks and the middle peak
    return check_peak_symmetry(pivots[3].point.index - pivots[1].point.index,
                              pivots[5].point.index - pivots[3].point.index,
                              properties.peak_symmetry_ratio)

def find_cross_point(line: Line, start_index: int, end_index: int, zigzag: Zigzag) -> Optional[Point]:
    if start_index > end_index:
        return None
    for i in range(start_index, end_index):
        current = zigzag.get_df_data_by_index(i)
        high = current['high']
        low = current['low']
        volume = current['volume']
        price = line.get_price(i)
        if high >= price and low <= price:
            return Point(zigzag.get_df_data_by_index(i).name, i, price, volume)
    return None

def get_support_line(pivots: List[Pivot], start_index: int, end_index: int, zigzag: Zigzag) -> Optional[Line]:
    if len(pivots) > 2:
        raise ValueError("At most two points are required to form a line")
    if len(pivots) == 1:
        line = Line(pivots[0].point, pivots[0].point)
        cross_point2 = find_cross_point(line, pivots[0].point.index+1, end_index, zigzag)
    else:
        line = Line(pivots[0].point, pivots[1].point)
        cross_point2 = find_cross_point(line, pivots[1].point.index+1, end_index, zigzag)

    cross_point1 = find_cross_point(line, start_index, pivots[0].point.index, zigzag)
    if cross_point1 is None:
        # the line is not crossing the chart on the left side
        return None
    # the cross point on the right side can be none as the chart is still trending
    if cross_point2 is None:
        cross_point2 = Point(zigzag.get_df_data_by_index(end_index).name,
                             end_index, line.get_price(end_index))
    return Line(cross_point1, cross_point2)

def find_reversal_patterns(zigzag: Zigzag, offset: int, properties: ReversalPatternProperties,
                  patterns: List[ReversalPattern]) -> bool:
    """
    Find reversal patterns using zigzag pivots

    Args:
        zigzag: Zigzag instance
        offset: Offset to start searching for pivots
        properties: Reversal pattern properties
        patterns: List to store found patterns

    Returns:
        List[ReversalPattern]: Found patterns
    """
    found_7_pattern = False
    found_5_pattern = False
    pivots = []
    pivots_count = get_pivots_from_zigzag(zigzag, pivots, offset, 7)
    if pivots_count == 7:
        if inspect_seven_pivot_pattern(pivots, properties):
            # we may have a triple top or bottom or head and shoulders
            support_line = get_support_line(
                [pivots[2], pivots[4]], pivots[0].point.index, pivots[6].point.index, zigzag)

            index_delta = pivots[-1].point.index - pivots[0].point.index + 1
            peak_distance = pivots[-3].point.index - pivots[2].point.index + 1
            if support_line is not None and index_delta >= properties.min_periods_lapsed and \
                peak_distance >= properties.min_peak_distance:
                pattern = ReversalPattern(pivots, support_line).resolve(properties)
                found_7_pattern = pattern.process_pattern(properties, patterns)

    # continue to inspect 5 point pattern
    if pivots_count >= 5:
        for i in range(0, pivots_count - 5 + 1):
            pivots = []
            get_pivots_from_zigzag(zigzag, pivots, offset + i, 5) # check the last 5 pivots as the pivots are in reverse order
            if inspect_five_pivot_pattern(pivots, properties):
                # use the sandle point to form a support line
                support_line = get_support_line(
                    [pivots[2]], pivots[0].point.index, pivots[4].point.index, zigzag)

                index_delta = pivots[-1].point.index - pivots[0].point.index + 1
                peak_distance = pivots[-2].point.index - pivots[1].point.index + 1
                if support_line is not None and index_delta >= properties.min_periods_lapsed and \
                    peak_distance >= properties.min_peak_distance:
                    pattern = ReversalPattern(pivots, support_line).resolve(properties)
                    found = pattern.process_pattern(properties, patterns)

                    if found:
                        found_5_pattern = True

    return found_7_pattern or found_5_pattern


