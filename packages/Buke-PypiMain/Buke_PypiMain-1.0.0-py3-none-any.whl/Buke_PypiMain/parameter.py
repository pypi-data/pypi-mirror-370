from enum import Enum


class Market(Enum):
    kospi = 1
    kosdaq = 2
    etf = 3


class Universe(Enum):
    total = 1
    top350 = 2
    kospi = 3
    kospi200 = 4
    kosdaq = 5
    kosdaq150 = 6


class ExchangeRate(Enum):
    dollar = "USDKRW"
    euro = "EURKRW"
    yen = "JPYKRW"


class MovingAverage(Enum):
    sma = 1
    ema = 2
    ewma = 3
    wma = 4


class KindOfAverage(Enum):
    average = 1
    min = 2
    max = 3
    first = 4
    dense = 5


class UnitPeriod(Enum):
    month = 1
    year = 2
