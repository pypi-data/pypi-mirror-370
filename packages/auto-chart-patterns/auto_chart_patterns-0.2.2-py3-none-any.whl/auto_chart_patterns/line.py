from dataclasses import dataclass
import pandas as pd
@dataclass
class Point:
    time: str
    index: int
    price: float
    volume: float = 0.0
    candle_body_price: float = 0.0
    candle_direction: int = 0

    def dict(self):
        return {
            "time": str(self.time),
            "price": float(self.price)
        }

    @classmethod
    def from_dict(cls, dict: dict):
        self = cls(time=pd.to_datetime(dict["time"]),
                   index=0,
                   price=dict["price"])
        return self

    def copy(self):
        return Point(self.time, self.index, self.price, self.volume,
                    self.candle_body_price, self.candle_direction)

@dataclass
class Pivot:
    point: Point
    direction: int # 1 for high, -1 for low
    index_diff: int = 0 # index difference between the pivot and the previous pivot
    cross_index_diff: int = 0 # index difference between the pivot and the previous pivot of the same direction
    cross_diff: float = 0.0 # price difference between the pivot and the previous pivot of the same direction
    candle_body_diff: float = 0.0 # price difference between the pivot and the previous pivot of the same direction
    cross_candle_body_diff: float = 0.0 # price difference between the pivot and the previous pivot of the same direction

    def dict(self):
        return {
            "point": self.point.dict(),
            "direction": self.direction
        }

    @classmethod
    def from_dict(cls, dict: dict):
        self = cls(point=Point.from_dict(dict["point"]),
                   direction=dict["direction"])
        return self

    def deep_copy(self):
        return Pivot(
            point=self.point.copy(),
            direction=self.direction,
            cross_diff=self.cross_diff,
            candle_body_diff=self.candle_body_diff,
            cross_candle_body_diff=self.cross_candle_body_diff,
            index_diff=self.index_diff,
            cross_index_diff=self.cross_index_diff
        )

@dataclass
class Line:
    def dict(self):
        return {
            "p1": self.p1.dict(),
            "p2": self.p2.dict()
        }

    @classmethod
    def from_dict(cls, dict):
        return cls(p1=Point.from_dict(dict["p1"]), p2=Point.from_dict(dict["p2"]))

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def get_price(self, index: int) -> float:
        """Calculate price at given index using linear interpolation"""
        if self.p2.index == self.p1.index:
            return self.p1.price

        slope = (self.p2.price - self.p1.price) / (self.p2.index - self.p1.index)
        return self.p1.price + slope * (index - self.p1.index)

    def get_slope(self) -> float:
        if self.p2.index == self.p1.index:
            return 0.0
        return (self.p2.price - self.p1.price) / (self.p2.index - self.p1.index)

    def copy(self):
        return Line(self.p1.copy(), self.p2.copy())
