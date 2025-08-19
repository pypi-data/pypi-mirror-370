# -*- coding:utf-8 -*-
from typing import Tuple
from pandas import DataFrame, Series
import numpy as np

from Buke_PypiMain.parameter import MovingAverage


def sma(price: Series, period: int) -> Series:
    """
    단순이동평균

    <설명>
    단순 이동평균을 구하는 함수입니다.
    단순 이동평균은 특정 기간(period) 동안의 가격(price)의 산술평균을 구합니다.

    <사용 방법>
    첫 번째 인자에는 단순 이동평균을 구하는데 사용하는 가격을,
    두 번째 인자에는 단순 이동평균을 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 5일간 종가의 단순 이동평균을 구하고자 하는 경우
    'sma(close, 5)' 또는 '단순이동평균(종가, 5)'와 같이 작성하면 됩니다.

    <계산 방법>
    5일간 종가의 단순 이동평균은 다음과 같이 구합니다.
    (당일 종가 + 1일 전 종가 + 2일 전 종가 + 3일 전 종가 + 4일 전 종가) / 5

    :param price: (가격데이터) 단순 이동평균을 구하는데 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 단순 이동평균을 구하는데 사용하는 기간
    :return:
    """
    return price.rolling(window=period).mean()


def ema(price: Series, period: int) -> Series:
    """
    지수이동평균

    <설명>
    지수 이동평균을 구하는 함수입니다.
    지수 이동평균은 가격(price)의 최근 데이터에 가중치를 두어 평균을 구합니다.

    <사용 법>
    첫 번째 인자에는 지수 이동평균을 구하는데 사용하는 가격을,
    두 번째 인자에는 지수 이동평균을 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 5일간 종가의 지수 이동평균을 구하고자 하는 경우
    'ema(close, 5)' 또는 '지수이동평균(종가, 5)'와 같이 작성하면 됩니다.

    <계산 방법>
    5일간 종가의 지수 이동평균은 다음과 같이 구합니다.
    당일 지수 이동평균 = 당일 종가 * 평활 계수 + 전일 지수 이동평균 * (1 - 평활 계수)
    평활 계수 = 2 / (5 + 1)

    :param price: (가격데이터) 지수 이동평균을 구하는데 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 지수 이동평균을 구하는데 사용하는 기간
    :return:
    """
    return price.ewm(span=period, min_periods=period, adjust=False).mean()


def ewma(price: Series, period: int) -> Series:
    return price.ewm(span=period, min_periods=period, adjust=True).mean()


def wma(price: Series, period: int) -> Series:
    """
    가중이동평균

    <설명>
    가중 이동평균을 구하는 함수입니다.
    가중 이동평균은 평균을 구하는 데 있어서 주어지는 가중값을 반영시킵니다.

    <사용 방법>
    첫 번째 인자에는 가중 이동평균을 구하는데 사용하는 가격을,
    두 번째 인자에는 가중 이동평균을 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 5일간 종가의 가중 이동평균을 구하고자 하는 경우
    'wma(close, 5)' 또는 '가중이동평균(종가, 5)'와 같이 작성하면 됩니다.

    <계산 방법>
    5일간 종가의 가중 이동평균은 다음과 같이 구합니다.
    (당일 종가 * 5 + 1일 전 종가 * 4 + 2일 전 종가 * 3 + 3일 전 종가 * 2 + 4일 전 종가 * 1) / (5 + 4 + 3 + 2 + 1)

    :param price: (가격데이터) 가중 이동평균을 구하는데 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 가중 이동평균을 구하는데 사용하는 기간
    :return:
    """
    weight = np.arange(1, period + 1)
    return price.rolling(window=period).apply(lambda prices: np.dot(prices, weight) / weight.sum(), raw=True)


def _bollinger_band(
        price: Series, period: int, moving_average: MovingAverage, multiplier: int
) -> Tuple[Series, Series]:
    if moving_average == MovingAverage.sma:
        line_mid = sma(price, period)
    elif moving_average == MovingAverage.ema:
        line_mid = ema(price, period)
    elif moving_average == MovingAverage.ewma:
        line_mid = ewma(price, period)
    elif moving_average == MovingAverage.wma:
        line_mid = wma(price, period)
    line_std = price.rolling(window=period).std(ddof=0)
    bollinger_range = line_std.multiply(multiplier)

    return line_mid, bollinger_range


def bollinger_upper(price: Series, period: int, moving_average: MovingAverage, multiplier: int) -> Series:
    """
    볼린저밴드상한선

    <설명>
    볼린저 밴드 상한선(상향 밴드)을 구하는 함수입니다.
    볼린저 밴드의 상한선은 표준 편차에 의해 산출된 이동평균 값이며,
    주가나 지수의 움직임이 큰 시기에는 밴드의 폭이 넓어지고 움직임이 작은 시기에는 밴드의 폭이 좁아지는 특성을 가지고 있습니다.
    즉, 가격 움직임의 크기에 따라 밴드의 넓이가 결정되는 것입니다.

    <사용 방법>
    첫 번째 인자에는 상향 밴드를 구하는데 사용하는 가격을,
    두 번째 인자에는 상향 밴드를 구하는데 사용하는 기간을,
    세 번째 인자에는 중간 밴드를 구하는데 사용하는 이동평균 종류를,
    네 번째 인자에는 상향 밴드를 구할 때 사용하는 표준편차 승수를 적으면 됩니다.
    예를 들어, 20일간 종가의 단순 이동평균으로 중간 밴드를 구하고 상향 밴드는 중간 밴드에 20일간 종가의 표준편차에 2배를 더한 값을 사용하고자 할 경우
    'bollinger_upper(close, 20, sma, 2)' 또는 '볼린저밴드상한선(종가, 20, 단순이동평균, 2)'와 같이 작성하면 됩니다.

    :param price: (가격데이터) 상향 밴드를 구하는데 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 상향 밴드를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 중간 밴드를 구할 때 사용하는 이동평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :param multiplier: (승수값) 상향 밴드를 구할 때 사용하는 표준편차 승수
    :return:
    """
    line_mid, bollinger_range = _bollinger_band(price, period, moving_average, multiplier)
    return line_mid + bollinger_range


def bollinger_lower(price: Series, period: int, moving_average: MovingAverage, multiplier: int) -> Series:
    """
    볼린저밴드하한선

    <설명>
    볼린저 밴드 하한선(하향 밴드)을 구하는 함수입니다.
    볼린저 밴드의 하한선은 표준 편차에 의해 산출된 이동평균 값이며,
    주가나 지수의 움직임이 큰 시기에는 밴드의 폭이 넓어지고 움직임이 작은 시기에는 밴드의 폭이 좁아지는 특성을 가지고 있습니다.
    즉, 가격 움직임의 크기에 따라 밴드의 넓이가 결정되는 것입니다.

    <사용 방법>
    첫 번째 인자에는 하향 밴드를 구하는데 사용하는 가격을,
    두 번째 인자에는 하향 밴드를 구하는데 사용하는 기간을,
    세 번째 인자에는 중간 밴드를 구하는데 사용하는 이동평균 종류를,
    네 번째 인자에는 하향 밴드를 구할 때 사용하는 표준편차 승수를 적으면 됩니다.
    예를 들어, 20일간 종가의 단순 이동평균으로 중간 밴드를 구하고 하향 밴드는 중간 밴드에 20일간 종가의 표준편차에 2배를 뺀 값을 사용하고자 할 경우
    'bollinger_lower(close, 20, sma, 2)' 또는 '볼린저밴드하한선(종가, 20, 단순이동평균, 2)'와 같이 작성하면 됩니다.

    :param price: (가격데이터) 하향 밴드를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 하향 밴드를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 중간 밴드를 구할 때 사용하는 이동평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :param multiplier: (승수값) 하향 밴드를 구할 때 사용하는 표준편차 승수
    :return:
    """
    line_mid, bollinger_range = _bollinger_band(price, period, moving_average, multiplier)
    return line_mid - bollinger_range


def _envelope(price: Series, period: int, moving_average: MovingAverage, ratio: float) -> Tuple[Series, Series]:
    if moving_average == MovingAverage.sma:
        line_mid = sma(price, period)
    elif moving_average == MovingAverage.ema:
        line_mid = ema(price, period)
    elif moving_average == MovingAverage.ewma:
        line_mid = ewma(price, period)
    elif moving_average == MovingAverage.wma:
        line_mid = wma(price, period)

    envelope_range = line_mid.multiply(ratio)
    return line_mid, envelope_range


def envelope_upper(price: Series, period: int, moving_average: MovingAverage, ratio: float) -> Series:
    """
    엔벨로프상한선

    <설명>
    엔벨로프 상한선을 구하는 함수입니다.
    엔벨로프 상한선은 주가의 이동평균 선에서 일정 비율 만큼 더한 선입니다.

    <사용 방법>
    첫 번째 인자에는 엔벨로프 상한선을 구하는데 사용하는 가격을,
    두 번째 인자에는 엔벨로프 상한선을 구하는데 사용하는 기간을,
    세 번째 인자에는 엔벨로프 상한선을 구하는데 사용하는 이동평균 종류를,
    네 번째 인자에는 엔벨로프 상한선을 구할 때 사용하는 비율을 적으면 됩니다.
    예를 들어, 20일간 종가의 단순 이동평균으로 기준선을 구하고 엔벨로프 상한선은 기준선에서 8% 위의 선으로 하고자 하는 경우
    'envelope_upper(close, 20, sma, 0.08)' 또는 엔벨로프상한선(종가, 20, 단순이동평균, 0.08)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 엔벨로프 상한선을 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 엔벨로프 상한선을 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 엔벨로프 상한선을 구하는데 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :param ratio: (비율) 엔벨로프 상한선을 구하는데 사용하는 비율
    :return:
    """
    line_mid, envelope_range = _envelope(price, period, moving_average, ratio)
    return line_mid + envelope_range


def envelope_lower(price: Series, period: int, moving_average: MovingAverage, ratio: float) -> Series:
    """
    엔벨로프하한선

    <설명>
    엔벨로프 하한선을 구하는 함수입니다.
    엔벨로프 하한선은 주가의 이동평균 선에서 일정 비율 만큼 뺀 선입니다.

    <사용 방법>
    첫 번째 인자에는 엔벨로프 하한선을 구하는데 사용하는 가격을,
    두 번째 인자에는 엔벨로프 하한선을 구하는데 사용하는 기간을,
    세 번째 인자에는 엔벨로프 하한선을 구하는데 사용하는 이동평균 종류를,
    네 번째 인자에는 엔벨로프 하한선을 구할 때 사용하는 비율을 적으면 됩니다.
    예를 들어, 20일간 종가의 단순 이동평균으로 기준선을 구하고 엔벨로프 하한선은 기준선에서 8% 아래의 선으로 하고자 하는 경우
    'envelope_lower(close, 20, sma, 0.08)' 또는 '엔벨로프하한선(종가, 20, 단순이동평균, 0.08)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 엔벨로프 하한선을 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 엔벨로프 하한선을 구하는 기간
    :param moving_average: (이동평균종류) 엔벨로프 하한선을 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :param ratio: (비율) 엔벨로프 상한선을 구하는데 사용하는 비율
    :return:
    """
    line_mid, envelope_range = _envelope(price, period, moving_average, ratio)
    return line_mid - envelope_range


def pivot_standard(price_high: Series, price_low: Series, price_close: Series) -> Series:
    """
    피봇기준선

    <설명>
    피봇기준선을 구하는 함수입니다.
    피봇기준선은 전일 고가, 저가, 종가의 평균입니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    피봇기준선을 구하고자 하는 경우
    'pivot_standard(high, low, close)' 또는 '피봇기준선(고가, 저가, 종가)'와 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    return (price_high + price_low + price_close).shift(1) / 3


def pivot_standard_for_sellprice(price_high: Series, price_low: Series, price_close: Series) -> Series:
    """
    피봇기준선

    <설명>
    피봇기준선을 구하는 함수입니다.
    피봇기준선은 전일 고가, 저가, 종가의 평균입니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    피봇기준선을 구하고자 하는 경우
    'pivot_standard(high, low, close)' 또는 '피봇기준선(고가, 저가, 종가)'와 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    return (price_high + price_low + price_close) / 3


def pivot_second_upper(price_high: Series, price_low: Series, price_close: Series) -> Series:
    """
    피봇2차저항선

    <설명>
    피봇2차저항선을 구하는 함수입니다.
    피봇2차저항선은 피봇 기준선에 전일 변동폭을 더한 값입니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    피봇2차저항선을 구하고자 하는 경우
    'pivot_second_upper(high, low, close)' 또는 '피봇2차저항선(고가, 저가, 종가)'와 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    pivot = pivot_standard(price_high, price_low, price_close)
    return pivot + price_high.shift(1).sub(price_low.shift(1))


def pivot_first_upper(price_high: Series, price_low: Series, price_close: Series) -> Series:
    """
    피봇1차저항선

    <설명>
    피봇1차저항선을 구하는 함수입니다.
    피봇1차저항선은 피봇 기준선에 두배를 곱한 후 전일 저가를 뺀 값입니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    피봇1차저항선을 구하고자 하는 경우
    'pivot_first_upper(high, low, close)' 또는 '피봇1차저항선(고가, 저가, 종가)'와 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    pivot = pivot_standard(price_high, price_low, price_close)
    return (pivot * 2).sub(price_low.shift(1))


def pivot_first_lower(price_high: Series, price_low: Series, price_close: Series) -> Series:
    """
    피봇1차지지선

    <설명>
    피봇1차지지선을 구하는 함수입니다.
    피봇1차지지선은 피봇 기준선에 두배를 곱한 후 전일 고가를 뺀 값입니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    피봇1차지지선을 구하고자 하는 경우
    'pivot_first_lower(high, low, close)' 또는 '피봇1차지지선(고가, 저가, 종가)'와 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    pivot = pivot_standard(price_high, price_low, price_close)
    return (pivot * 2).sub(price_high.shift(1))


def pivot_second_lower(price_high: Series, price_low: Series, price_close: Series) -> Series:
    """
    피봇2차지지선

    <설명>
    피봇2차지지선을 구하는 함수입니다.
    피봇2차지지선은 피봇 기준선에 전일 변동폭을 뺀 값입니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    피봇2차지지선 구하고자 하는 경우
    'pivot_second_lower(high, low, close)' 또는 '피봇2차지지선(고가, 저가, 종가)'와 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    pivot = pivot_standard(price_high, price_low, price_close)
    return pivot.sub(price_high.shift(1)) + price_low.shift(1)


def price_channel_upper(price_high: Series, period: int) -> Series:
    """
    가격채널상한선

    <설명>
    가격 채널 상한선을 구하는 함수입니다.
    가격 채널 상한선은 일정 기간 내의 최고가를 이은 선입니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 가격 채널 상한선을 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 20일간 채널 지표 상한선을 구하고자 하는 경우
    'price_channel_upper(high, 20)' 또는 '가격채널상한선(고가, 20)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param period: (기간) 가격 채널 상한선을 구할 때 사용하는 기간
    :return:
    """
    return price_high.shift(1).rolling(window=period).max()


def price_channel_lower(price_low: Series, period: int) -> Series:
    """
    가격채널하한선

    <설명>
    가격 채널 하한선을 구하는 함수입니다.
    가격 채널 하한선은 일정 기간 내의 최저가를 이은 선입니다.

    <사용 방법>
    첫 번째 인자에는 저가를,
    두 번째 인자에는 가격 채널 하한선을 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 20일간 채널 지표 하한선을 구하고자 하는 경우
    'price_channel_lower(low, 20)' 또는 '가격채널하한선(저가, 20)'과 같이 작성하면 됩니다.

    :param price_low: (저가) 저가
    :param period: (기간) 가격 채널 상한선을 구하는 기간
    :return:
    """
    return price_low.shift(1).rolling(window=period).min()


def _tr(price_high: Series, price_low: Series, price_close: Series) -> Series:
    data = {
        "range": price_high - price_low,
        "up": abs(price_high - price_close.shift(1)),
        "down": abs(price_close.shift(1) - price_low),
    }
    data = DataFrame(data, columns=["range", "up", "down"])

    return data.max(axis=1)


def pdi(
        price_high: Series, price_low: Series, price_close: Series, period: int, moving_average: MovingAverage
) -> Series:
    """
    매수방향지표

    <설명>
    매수방향지표(PDI)를 구하는 함수입니다.
    매수방향지표(PDI)는 실질적으로 상승하는 폭의 비율을 나타냅니다.
    매수방향지표(PDI)는 0에서 1사이의 값으로 표현됩니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 매수방향지표(PDI)를 구하는데 사용하는 기간을,
    다섯 번째 인자에는 매수방향지표(PDI)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 지수 이동 평균을 이용한 14일간 매수방향지표(PDI)를 구하고자 하는 경우
    'pdi(high, low, close, 14, ema)' 또는 '매수방향지표(고가, 저가, 종가, 14, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param period: (기간) 매수방향지표(PDI)를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 매수방향지표(PDI)를 구하는데 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    pdm = np.where(
        ((price_high.diff(1) > 0) & (price_high.diff(1) > price_low.shift(1) - price_low)), price_high.diff(1), 0
    )

    if moving_average == MovingAverage.sma:
        pdmn = sma(Series(pdm), period)
    elif moving_average == MovingAverage.ema:
        pdmn = ema(Series(pdm), period)
    elif moving_average == MovingAverage.ewma:
        pdmn = ewma(Series(pdm), period)
    elif moving_average == MovingAverage.wma:
        pdmn = wma(Series(pdm), period)

    tr = _tr(price_high, price_low, price_close)

    if moving_average == MovingAverage.sma:
        trn = sma(tr, period)
    elif moving_average == MovingAverage.ema:
        trn = ema(tr, period)
    elif moving_average == MovingAverage.ewma:
        trn = ewma(tr, period)
    elif moving_average == MovingAverage.wma:
        trn = wma(tr, period)

    return pdmn.divide(trn)


def mdi(
        price_high: Series, price_low: Series, price_close: Series, period: int, moving_average: MovingAverage
) -> Series:
    """
    매도방향지표

    <설명>
    매도방향지표(MDI)를 구하는 함수입니다.
    매도방향지표(MDI)는 실질적으로 하락하는 폭의 비율을 나타냅니다.
    매도방향지표(MDI)는 0에서 1사이의 값으로 표현됩니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 매도방향지표(MDI)를 구하는데 사용하는 기간을,
    다섯 번째 인자에는 매도방향지표(MDI)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 지수 이동 평균을 이용한 14일간 매도방향지표(MDI)를 구하고자 하는 경우
    'mdi(high, low, close, 14, ema)' 또는 '매도방향지표(고가, 저가, 종가, 14, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param period: (기간) 매도방향지표(MDI)를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 매도방향지표(MDI)를 구하는데 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    mdm = np.where(
        (((price_low.shift(1) - price_low) > 0) & (price_high.diff(1) < (price_low.shift(1) - price_low))),
        price_low.shift(1) - price_low,
        0,
    )

    if moving_average == MovingAverage.sma:
        mdmn = sma(Series(mdm), period)
    elif moving_average == MovingAverage.ema:
        mdmn = ema(Series(mdm), period)
    elif moving_average == MovingAverage.ewma:
        mdmn = ewma(Series(mdm), period)
    elif moving_average == MovingAverage.wma:
        mdmn = wma(Series(mdm), period)

    tr = _tr(price_high, price_low, price_close)

    if moving_average == MovingAverage.sma:
        trn = sma(tr, period)
    elif moving_average == MovingAverage.ema:
        trn = ema(tr, period)
    elif moving_average == MovingAverage.ewma:
        trn = ewma(tr, period)
    elif moving_average == MovingAverage.wma:
        trn = wma(tr, period)

    return mdmn.divide(trn)


def adx(
        price_high: Series, price_low: Series, price_close: Series, period: int, moving_average: MovingAverage
) -> Series:
    """
    평균방향이동지표

    <설명>
    평균방향이동지표(ADX)를 구하는 함수입니다.
    평균방향이동지표(ADX)는 추세의 강도를 의미합니다.
    평균방향이동지표(ADX)는 0에서 1사이의 값으로 표현됩니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 ADX를 구하는데 사용하는 기간을,
    다섯 번째 인자에는 ADX를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 지수 이동 평균을 이용한 14일간 ADX를 구하고자 하는 경우
    'adx(high, low, close, 14, ema)' 또는 '평균방향이동지표(고가, 저가, 종가, 14, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param period: (기간) ADX를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) ADX를 구하는데 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """

    pdi_val = pdi(price_high, price_low, price_close, period, moving_average)
    mdi_val = mdi(price_high, price_low, price_close, period, moving_average)
    dx = abs(pdi_val - mdi_val).divide(pdi_val + mdi_val)

    if moving_average == MovingAverage.sma:
        return sma(dx, period)
    elif moving_average == MovingAverage.ema:
        return ema(dx, period)
    elif moving_average == MovingAverage.ewma:
        return ewma(dx, period)
    elif moving_average == MovingAverage.wma:
        return wma(dx, period)


def macd(price: Series, short_period: int, long_period: int, moving_average: MovingAverage) -> Series:
    """
    이동평균수렴확산지수

    <설명>
    이동평균수렴확산지수(MACD)를 구하는 함수입니다.
    이동평균수렴확산지수(MACD)는 단기 이동평균 값과 장기 이동평균 값의 차이를 이용한 지표입니다.

    <사용 방법>
    첫 번째 인자에는 이동평균수렴확산지수(MACD)를 구하는데 사용하는 가격을,
    두 번째 인자에는 단기 이동 평균을 구하는데 사용하는 기간을,
    세 번째 인자에는 장기 이동 평균을 구하는데 사용하는 기간을,
    네 번째 인자에는 이동평균수렴확산지수(MACD)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 12일간 종가의 단순 이동 평균과 26일간 종가의 단순 이동 평균을 이용하여 이동평균수렴확산지수(MACD)를 구하고자 하는 경우에는
    'macd(close, 12, 26, sma)' 또는 '이동평균수렴확산지수(종가, 12, 26, 단순이동평균)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 이동평균수렴확산지수(MACD)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param short_period: (단기이동평균기간) 단기 이동 평균을 구하는데 사용하는 기간
    :param long_period: (장기이동평균기간) 장기 이동 평균을 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 이동평균수렴확산지수(MACD)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    if moving_average == MovingAverage.sma:
        short_term = sma(price, short_period)
        long_term = sma(price, long_period)
    elif moving_average == MovingAverage.ema:
        short_term = ema(price, short_period)
        long_term = ema(price, long_period)
    elif moving_average == MovingAverage.ewma:
        short_term = ewma(price, short_period)
        long_term = ewma(price, long_period)
    elif moving_average == MovingAverage.wma:
        short_term = wma(price, short_period)
        long_term = wma(price, long_period)

    return short_term - long_term


def macd_signal(
        price: Series, short_period: int, long_period: int, signal_period: int, moving_average: MovingAverage
) -> Series:
    """
    이동평균수렴확산시그널

    <설명>
    이동평균수렴확산시그널(MACD_signal)을 구하는 함수입니다.
    이동평균수렴확산시그널(MACD_signal)은 이동평균수렴확산지수(MACD)의 일정 기간 동안의 평균입니다.

    <사용 방법>
    첫 번째 인자에는 이동평균수렴확산시그널(MACD_signal)을 구하는데 사용하는 가격을,
    두 번째 인자에는 단기 이동 평균을 구하는데 사용하는 기간을,
    세 번째 인자에는 장기 이동 평균을 구하는데 사용하는 기간을,
    네 번째 인자에는 시그널 기간을,
    다섯 번째 인자에는 이동평균수렴확산시그널(MACD_signal)을 구하는데 이용할 이동 평균 종류를 적으면 됩니다.
    예를 들어, 12일간 종가의 단순 이동 평균, 26일간 종가의 단순 이동 평균, 9일의 signal 기간을 이용하여
    이동평균수렴확산시그널(MACD_signal)을 구하고자 하는 경우에는
    'macd_signal(close, 12, 26, 9, sma)' 또는 '이동평균수렴확산시그널(종가, 12, 26, 9, 단순이동평균)'과 같이 작성하면 됩니다.

    :param price: (기간) 이동평균수렴확산시그널(MACD_signal)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param short_period: (단기이동평균기간) 단기 이동 평균을 구하는데 사용하는 기간
    :param long_period: (장기이동평균기간) 장기 이동 평균을 구하는데 사용하는 기간
    :param signal_period: (시그널기간) 이동평균수렴확산시그널(MACD_signal)를 구할 때 사용하는 시그널 기간
    :param moving_average: (이동평균종류) 이동평균수렴확산시그널(MACD_signal)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    macd_val = macd(price, short_period, long_period, moving_average)
    if moving_average == MovingAverage.sma:
        signal = sma(macd_val, signal_period)
    elif moving_average == MovingAverage.ema:
        signal = ema(macd_val, signal_period)
    elif moving_average == MovingAverage.ewma:
        signal = ewma(macd_val, signal_period)
    elif moving_average == MovingAverage.wma:
        signal = wma(macd_val, signal_period)

    return signal


def macd_oscillator(
        price: Series, short_period: int, long_period: int, signal_period: int, moving_average: MovingAverage
) -> Series:
    """
    이동평균수렴확산오실레이터

    <설명>
    이동평균수렴확산오실레이터(MACD_oscillator)를 구하는 함수입니다.
    이동평균수렴확산오실레이터(MACD_oscillator)는 MACD와 Signal의 차를 통해 계산됩니다.

    <사용 방법>
    첫 번째 인자에는 이동평균수렴확산오실레이터(MACD_oscillator)를 구하는데 사용하는 가격을,
    두 번째 인자에는 단기 이동 평균을 구하는데 사용하는 기간을,
    세 번째 인자에는 장기 이동 평균을 구하는데 사용하는 기간을,
    네 번째 인자에는 시그널 기간을,
    다섯 번째 인자에는 이동평균수렴확산오실레이터(MACD_oscillator)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 12일간 종가의 단순 이동 평균, 26일간 종가의 단순 이동 평균, 9일의 signal 기간을 이용하여
    이동평균수렴확산오실레이터(MACD_oscillator)를 구하고자 하는 경우에는
    'macd_oscillator(close, 12, 26, 9, sma)' 또는 '이동평균수렴확산오실레이터(종가, 12, 26, 9, 단순이동평균)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 이동평균수렴확산오실레이터(MACD_oscillator)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param short_period: (단기이동평균기간) 단기 이동 평균을 구하는데 사용하는 기간
    :param long_period: (장기이동평균기간) 장기 이동 평균을 구하는데 사용하는 기간
    :param signal_period: (시그널기간) 이동평균수렴확산오실레이터(MACD_oscillator)를 구할 때 사용하는 시그널 기간
    :param moving_average: (이동평균종류) 이동평균수렴확산오실레이터(MACD_oscillator)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    macd_val = macd(price, short_period, long_period, moving_average)
    if moving_average == MovingAverage.sma:
        signal = sma(macd_val, signal_period)
    elif moving_average == MovingAverage.ema:
        signal = ema(macd_val, signal_period)
    elif moving_average == MovingAverage.ewma:
        signal = ewma(macd_val, signal_period)
    elif moving_average == MovingAverage.wma:
        signal = wma(macd_val, signal_period)

    return macd_val - signal


def stochastic_fast_k(price_high: Series, price_low: Series, price_close: Series, k_period: int) -> Series:
    """
    스토캐스틱

    <설명>
    스토캐스틱(stochastic_fast_k)을 구하는 함수입니다.
    정해진 기간동안(k_period)의 가격 범위에서 오늘의 시장가격이 상대적으로 어디에 위치하고 있는지를 알려주는 지표로써,
    시장가격이 상승추세에 있다면 현재가격은 최고가 부근에 위치할 가능성이 높고,
    하락추세에 있다면 현재가는 최저가 부근에서 형성될 가능성이 높다는 것에 착안하여 만들어진 지표입니다.

    <사용방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 스토캐스틱(stochastic_fast_k)을 구하는데 사용할 기간을 적으면 됩니다.
    예를 들어, 20일간의 스토캐스틱(stochastic_fast_k)을 구하고자 하는 경우에는
    'stochastic_fast_k(high, low, close, 20)' 또는 '스토캐스틱(고가, 저가, 종가, 20)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param k_period: (스토캐스틱기간) 스토캐스틱(stochastic_fast_k)을 구하는데 사용할 기간
    :return:
    """
    return (price_close - price_low.rolling(window=k_period).min()) / (
            price_high.rolling(window=k_period).max() - price_low.rolling(window=k_period).min()
    )


def stochastic_fast_d(
        price_high: Series,
        price_low: Series,
        price_close: Series,
        k_period: int,
        d_period: int,
        moving_average: MovingAverage,
) -> Series:
    """
    스토캐스틱이동평균

    <설명>
    스토캐스틱이동평균(stochastic_fast_d)을 구하는 함수입니다.
    스토캐스틱이동평균은 스토캐스틱을 정해진 기간(d_period)동안 평균을 낸 값입니다.

    <사용방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 스토캐스틱(stochastic_fast_k)을 구하는데 사용할 기간을,
    다섯 번째 인자에는 스토캐스틱이동평균(stochastic_fast_d)을 구하는데 사용한 기간을,
    여섯 번째 인자에는 스토캐스틱이동평균(stochastic_fast_d)을 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 20일간의 스토캐스틱(stochastic_fast_k)을 구하고 이를 5일간 단순 이동평균을 낸 값을 사용하고자 하는 경우에는
    'stochastic_fast_d(high, low, close, 20, 5, sma)' 또는 '스토캐스틱이동평균(고가, 저가, 종가, 20, 5, 단순이동평균)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param k_period: (스토캐스틱기간) 스토캐스틱(stochastic_fast_k)을 구하는데 사용할 기간
    :param d_period: (이동평균기간) 스토캐스틱이동평균(stochastic_fast_d)을 구하는데 사용할 기간
    :param moving_average (이동평균종류) 스토캐스틱이동평균(stochastic_fast_d)을 구하는데 사용할 이동평균 종류
    :return:
    """
    stochastic_fast_k_val = stochastic_fast_k(price_high, price_low, price_close, k_period)

    if moving_average == MovingAverage.sma:
        return sma(stochastic_fast_k_val, d_period)
    elif moving_average == MovingAverage.ema:
        return ema(stochastic_fast_k_val, d_period)
    elif moving_average == MovingAverage.ewma:
        return ewma(stochastic_fast_k_val, d_period)
    elif moving_average == MovingAverage.wma:
        return wma(stochastic_fast_k_val, d_period)


def volume_ratio(price: Series, volume: Series, period: int) -> Series:
    """
    거래량비율

    <설명>
    거래량비율(Volume Ratio)을 구하는 함수입니다.
    거래량비율(Volume Ratio)은 일정 기간 동안의 상승일의 거래량과 하락일의 거래량을 비교합니다.
    거래량비율(Volume Ratio)은 0에서 1사이의 값으로 표현됩니다.

    <사용 방법>
    첫 번째 인자에는 거래량비율(Volume Ratio)을 구하는데 사용하는 가격을,
    두 번째 인자에는 거래량을,
    세 번째 인자에는 거래량비율(Volume Ratio)을 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 20일간의 종가를 이용한 거래량비율(Volume Ratio)을 구하고자 하는 경우에는
    'volume_ratio(close, volume, 20)' 또는 '거래량비율(종가, 거래량, 20)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 거래량비율(Volume Ratio)을 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param volume: (거래량) 거래량
    :param period: (기간) 거래량비율(Volume Ratio)을 구하는데 사용하는 기간
    :return:
    """
    up = np.where(price.diff(1).gt(0), volume, 0)
    down = np.where(price.diff(1).lt(0), volume, 0)
    maintain = np.where(price.diff(1).equals(0), volume.mul(0.5), 0)

    up = up + maintain
    down = down + maintain
    sum_up = Series(up).rolling(window=period, min_periods=period).sum()
    sum_down = Series(down).rolling(window=period, min_periods=period).sum()
    return sum_up.div(sum_down)


def 순거래대금(price: Series, volume: Series, period: int) -> Series:

    up = np.where(price.diff(1).gt(0), price * volume, 0)
    down = np.where(price.diff(1).lt(0), -1 * price * volume, 0)
    sum = up + down

    rolling_sum = Series(sum).rolling(window=period, min_periods=period).sum()
    return rolling_sum


def psychological_line(price: Series, period: int) -> Series:
    """
    투자심리도

    <설명>
    투자심리도(Psychological Line)를 구하는 함수입니다.
    투자심리도(Psychological Line)를 이용하면 과열 및 침체도를 파악할 수 있습니다.
    투자심리도(Psychological Line)는 0에서 1사이의 값으로 표현됩니다.

    <사용 방법>
    첫 번째 인자에는 투자심리도(Psychological Line)를 구하는데 사용하는 가격을,
    두 번째 인자에는 투자심리도(Psychological Line)를 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 10일간의 종가를 이용한 투자심리도(Psychological Line)를 구하고자 하는 경우에는
    'psychological_line(close, 10)' 또는 '투자심리도(종가, 10)'과 같이 작성하면 됩니다.

    <계산 방법>
    10일간의 종가를 이용한 투자심리도(Psychological Line)는 다음과 같이 구합니다.
    (10일간 전일 종가 대비 상승 일수) / 10

    :param price: (가격데이터) 투자심리도(Psychological Line)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 투자심리도(Psychological Line)를 구하는데 사용하는 기간
    :return:
    """
    up = np.where(price.diff(1).gt(0), 1, 0)
    sum_up = Series(up).rolling(window=period, min_periods=period).sum()

    return sum_up.divide(period)


def new_psychological_line(price: Series, period: int) -> Series:
    """
    신심리도

    <설명>
    신심리도(Psychological Line)를 구하는 함수입니다.
    신심리도(New Psychological Line)는 주가 등락 폭을 반영하지 못하는 투자심리도(Psychological Line)의 단점을 개선하였습니다.

    <사용 방법>
    첫 번째 인자에는 신심리도(New Psychological Line)를 구하는데 사용하는 가격을,
    두 번째 인자에는 신심리도(New Psychological Line)를 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 10일간의 종가를 이용한 신심리도(New Psychological Line)를 구하고자 하는 경우에는
    'new_psychological_line(close, 10)' 또는 '신심리도(종가, 10)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 신심리도(New Psychological Line)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 신심리도(New Psychological Line)를 구하는데 사용하는 기간
    :return:
    """
    up_cnt = np.where(price.diff(1).gt(0), 1, 0)
    up_cnt_cum = Series(up_cnt).rolling(window=period, min_periods=period).sum()
    up_width = np.where(price.diff(1).gt(0), price.diff(1), 0)
    up_width_cum = Series(up_width).rolling(window=period, min_periods=period).sum()

    down_cnt = np.where(price.diff(1).lt(0), 1, 0)
    down_cnt_cum = Series(down_cnt).rolling(window=period, min_periods=period).sum()
    down_width = np.where(price.diff(1).lt(1), abs(price.diff(1)), 0)
    down_width_cum = Series(down_width).rolling(window=period, min_periods=period).sum()

    up = up_cnt_cum.multiply(up_width_cum)
    down = down_cnt_cum.multiply(down_width_cum)

    quo = up.subtract(down)
    deno = (up_width_cum + down_width_cum).multiply(period)

    return quo.divide(deno)


def disparity(price: Series, period: int, moving_average: MovingAverage) -> Series:
    """
    이격도

    <설명>
    이격도(Disparity)를 구하는 함수입니다.
    이격도(Disparity)는 주가가 이동 평균과 어느 정도 떨어져 있는가 나타냅니다.

    <사용 방법>
    첫 번째 인자에는 이격도(Disparity)를 구하는데 사용하는 가격을,
    두 번째 인자에는 이격도(Disparity)를 구하는데 사용하는 기간을,
    세 번째 인자에는 이격도(Disparity)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 종가와 5일간의 단순 이동평균을 이용한 이격도(Disparity)를 구하고자 하는 경우에는
    'disparity(close, 5, sma)' 또는 '이격도(종가, 5, 단순이동평균)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 이격도(Disparity)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 이격도(Disparity)를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 이격도(Disparity)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    if moving_average == MovingAverage.sma:
        ma = sma(price, period)
    elif moving_average == MovingAverage.ema:
        ma = ema(price, period)
    elif moving_average == MovingAverage.wma:
        ma = wma(price, period)
    return price.divide(ma)


def ibs(price_high: Series, price_low: Series, price_close: Series) -> Series:
    """
    종가위치비율

    <설명>
    종가위치비율(IBS)을 구하는 함수입니다.
    종가위치비율(IBS)은 종가가 당일 변동폭에서 어떠한 지점에 위치해있는지를 나타냅니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가,
    세 번째 인자에는 종가를 적으면 됩니다.
    종가위치비율(IBS)을 구하고자 하는 경우에는
    'ibs(high, low, close)' 또는 '종가위치비율(고가, 저가, 종가)'와 같이 작성하면 됩니다.

    <계산 방법>
    (종가 - 저가) / (고가 - 저가)

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    return (price_close - price_low) / (price_high - price_low)


def upper_tail_ratio(price_open: Series, price_high: Series, price_close: Series) -> Series:
    """
    윗꼬리비율

    <설명>
    윗꼬리비율(Upper Tail Ratio)을 구하는 함수입니다.

    <사용 방법>
    첫 번째 인자에는 시가를,
    두 번째 인자에는 고가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    윗꼬리비율은 'upper_tail_ratio(open, high, close)' 또는 '윗꼬리비율(시가, 고가, 종가)'과 같이 작성하면 됩니다.

    :param price_open: (시가) 시가
    :param price_high: (고가) 고가
    :param price_close: (종가) 종가
    :return:
    """
    price_upper = np.where(price_open >= price_open, price_open, price_close)
    price_upper = Series(price_upper)

    return (price_high - price_upper) / (price_close - price_open).abs()


def lower_tail_ratio(price_open: Series, price_low: Series, price_close: Series) -> Series:
    """
    아랫꼬리비율

    <설명>
    아랫꼬리비율(Lower Tail Ratio)을 구하는 함수입니다.

    <사용 방법>
    첫 번째 인자에는 시가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를 적으면 됩니다.
    아랫꼬리비율을 구하고자 하는 경우에는
    'lower_tail_ratio(open, low, close)' 또는 '아랫꼬리비율(시가, 저가, 종가)'과 같이 작성하면 됩니다.

    :param price_open: (시가) 시가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :return:
    """
    price_under = np.where(price_open >= price_open, price_close, price_open)
    price_under = Series(price_under)

    return (price_under - price_low) / (price_close - price_open).abs()


def a_ratio(price_open: Series, price_high: Series, price_low: Series, period: int) -> Series:
    """
    에이비율

    <설명>
    A Ratio를 구하는 함수입니다.
    A Ratio는 주가 변동을 이용하여 강, 약 에너지를 파악합니다.

    <사용 방법>
    첫 번째 인자에는 시가를,
    두 번째 인자에는 고가를,
    세 번째 인자에는 저가를,
    네 번째 인자에는 A Ratio를 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 26일간의 A Ratio를 구하고자 하는 경우에는
    'a_ratio(open, high, low, 26)' 또는 '에이비율(시가, 고자, 저가, 26)'과 같이 작성하면 됩니다.

    :param price_open: (시가) 시가
    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param period: (기간) A Ratio를 구하는데 사용하는 기간
    :return:
    """
    strength = price_high - price_open
    weakness = price_open - price_low
    return strength.rolling(window=period).sum() / weakness.rolling(window=period).sum()


def b_ratio(price_high: Series, price_low: Series, price_close: Series, period: int) -> Series:
    """
    비비율

    <설명>
    B Ratio를 구하는 함수입니다.
    B Ratio는 주가 변동을 이용하여 강, 약 에너지를 파악합니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 B Ratio를 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 26일간의 B Ratio를 구하고자 하는 경우에는
    'b_ratio(high, low, close, 26)' 또는 '비비율(고가, 저가, 종가, 26)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param period: (기간) B Ratio를 구하는데 사용하는 기간
    :return:
    """
    strength = price_high - price_close.shift(1)
    weakness = price_close.shift(1) - price_low
    return strength.rolling(window=period).sum() / weakness.rolling(window=period).sum()


def mass_index(
        price_high: Series, price_low: Series, period: int, moving_average: MovingAverage = MovingAverage.ewma
) -> Series:
    """
    질량지수

    <설명>
    질량지수(Mass Index)를 구하는 함수입니다.
    질량지수(Mass Index)는 고가와 저가 사이의 변동폭을 측정하여 단기적인 추세의 전환점을 찾아냅니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 질량지수(Mass Index)를 구하는데 사용하는 기간을,
    네 번째 인자에는 질량지수(Mass Index)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 단순 이동평균을 이용한 25일간 질량지수(Mass Index)를 구하고자 하는 경우에는
    'mass_index(high, low, 25, sma)' 또는 '질량지수(고가, 저가, 25, 단순이동평균)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param period: (기간) 질량지수(Mass Index)를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 질량지수(Mass Index)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    day_range = price_high - price_low

    if moving_average == MovingAverage.sma:
        single = sma(day_range, 9)
        double = sma(single, 9)
    elif moving_average == MovingAverage.ema:
        single = ema(day_range, 9)
        double = ema(single, 9)
    elif moving_average == MovingAverage.ewma:
        single = ewma(day_range, 9)
        double = ewma(single, 9)
    elif moving_average == MovingAverage.wma:
        single = wma(day_range, 9)
        double = wma(single, 9)
    ratio = single / double

    return ratio.rolling(window=period).sum()


def mao(price: Series, short_period: int, long_period: int, moving_average: MovingAverage) -> Series:
    """
    이동평균오실레이터

    <설명>
    이동평균오실레이터(MAO)를 구하는 함수입니다.
    이동평균오실레이터(MAO)는 단기 이동 평균 값과 장기 이동 평균 값의 차를 통해 계산되며 주가의 추세를 판단할 수 있습니다.

    <사용 방법>
    첫 번째 인자에는 이동평균오실레이터(MAO)를 구하는데 사용하는 가격을,
    두 번째 인자에는 단기 이동 평균을 구하는데 사용하는 기간을,
    세 번째 인자에는 장기 이동 평균을 구하는데 사용하는 기간을,
    네 번째 인자에는 이동평균오실레이터(MAO)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 5일간 종가의 단순 이동 평균과 10일간 종가의 단순 이동 평균을 사용하여 이동평균오실레이터(MAO)를 구하고자 하는 경우에는
    'mao(close, 5, 10, sma)' 또는 '이동평균오실레이터(종가, 5, 10, 단순이동평균)'과 같이 작성하면 됩니다.

    :param price: (기간) 이동평균오실레이터(MAO)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param short_period: (단기이동평균기간) 단기 이동 평균을 구하는데 사용하는 기간
    :param long_period: (장기이동평균기간) 장기 이동 평균을 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 이동평균오실레이터(MAO)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """

    if moving_average == MovingAverage.sma:
        return sma(price, short_period) - sma(price, long_period)
    elif moving_average == MovingAverage.ema:
        return ema(price, short_period) - ema(price, long_period)
    elif moving_average == MovingAverage.ewma:
        return ewma(price, short_period) - ewma(price, long_period)
    elif moving_average == MovingAverage.wma:
        return wma(price, short_period) - wma(price, long_period)


def sonar(price: Series, period: int, sonar_period: int, moving_average: MovingAverage) -> Series:
    """
    소나

    <설명>
    소나(Sonar)를 구하는 함수입니다.
    소나(Sonar)는 주가의 추세 전환 시점을 파악하기 위한 지표입니다.

    <사용 방법>
    첫 번째 인자에는 소나(Sonar)를 구하는데 사용하는 가격을,
    두 번째 인자에는 이동 평균을 구하는데 사용하는 기간을,
    세 번째 인자에는 소나(Sonar)를 구하는데 사용하는 과거 이동 평균 값의 기간을,
    네 번째 인자에는 소나(Sonar)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 20일간 종가의 지수 이동 평균과 9일전 지수 이동 평균을 이용하여 소나(Sonar)를 구하고자 하는 경우에는
    'sonar(close, 20, 9, ema)' 또는 '소나(종가, 20, 9, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 소나(Sonar)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 이동 평균을 구하는데 사용하는 기간
    :param sonar_period: (소나기간) 사용하고자 하는 과거 이동 평균 값의 기간
    :param moving_average: (이동평균종류) 소나(Sonar)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    if moving_average == MovingAverage.sma:
        ma = sma(price, period)
    elif moving_average == MovingAverage.ema:
        ma = ema(price, period)
    elif moving_average == MovingAverage.ewma:
        ma = ewma(price, period)
    elif moving_average == MovingAverage.wma:
        ma = wma(price, period)

    return ma - ma.shift(sonar_period)


def sonar_signal(
        price: Series, period: int, sonar_period: int, signal_period: int, moving_average: MovingAverage
) -> Series:
    """
    소나시그널

    <설명>
    소나시그널(Sonar Signal)을 구하는 함수입니다.
    소나시그널(Sonar Signal)은 주가의 추세 전환 시점을 파악하기 위한 지표입니다.

    <사용 방법>
    첫 번째 인자에는 소나(Sonar)를 구하는데 사용하는 가격을,
    두 번째 인자에는 이동 평균을 구하는데 사용하는 기간을,
    세 번째 인자에는 소나(Sonar)를 구하는데 사용하는 과거 이동 평균 값의 기간을,
    네 번째 인자에는 소나시그널(Sonar Signal)을 구하는데 사용하는 소나(Sonar)의 이동 평균 기간을,
    네 번째 인자에는 소나(Sonar)를 구하는데 이용할 이동 평균 종류를 적으면 됩니다.
    예를 들어, 20일간 종가의 지수 이동 평균과 9일전 지수 이동 평균을 이용하여 시그널 기간이 9인 소나시그널(Sonar Signal)를 구하고자 하는 경우에는
    'sonar_signal(close, 20, 9, 9, ema)' 또는 '소나시그널(종가, 20, 9, 9, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 소나(Sonar)를 구할 때 사용하는 가격 ex) 시가, 고가, 저가, 종가
    :param period: (기간) 이동 평균을 구하는데 사용하는 기간
    :param sonar_period: (소나기간) 사용하고자 하는 과거 이동 평균 값의 기간
    :param signal_period: (시그널기간) 소나시그널(Sonar Signal)을 구하는데 사용하는 소나(Sonar)의 이동 평균 기간
    :param moving_average: (이동평균종류) 소나(Sonar)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    sonar_val = sonar(price, period, sonar_period, moving_average)

    if moving_average == MovingAverage.sma:
        return sma(sonar_val, signal_period)
    elif moving_average == MovingAverage.ema:
        return ema(sonar_val, signal_period)
    elif moving_average == MovingAverage.ewma:
        return ewma(sonar_val, signal_period)
    elif moving_average == MovingAverage.wma:
        return wma(sonar_val, signal_period)


def mfi(price_high: Series, price_low: Series, price_close: Series, vol: Series, period: int) -> Series:
    """
    자금흐름지수

    <설명>
    자금흐름지수(MFI)를 구하는 함수입니다.
    자금흐름지수(MFI)는 주식시장으로 자금이 유입되거나 유출되는 양을 측정합니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 거래량을,
    네 번째 인자에는 자금흐름지수(MFI)를 구하는데 사용하는 기간을 적으면 됩니다.
    예를 들어, 14일간 자금흐름지수(MFI)를 구하고자 하는 경우에는
    'mfi(high, low, close, volume, 14)' 또는 '자금흐름지수(고가, 저가, 종가, 거래량, 14)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param vol: (거래량) 거래량
    :param period: (기간) 자금흐름지수(MFI)를 구하는데 사용하는 기간
    :return:
    """
    typical_price = (price_high + price_low + price_close) / 3
    money_flow = vol * typical_price

    positive_money_flow = np.where(typical_price.diff(1) > 0, money_flow, 0)
    positive_money_flow = Series(positive_money_flow).rolling(window=period, min_periods=period).sum()
    negative_money_flow = np.where(typical_price.diff(1) < 0, money_flow, 0)
    negative_money_flow = Series(negative_money_flow).rolling(window=period, min_periods=period).sum()

    money_flow_ratio = positive_money_flow / negative_money_flow
    return money_flow_ratio / (1 + money_flow_ratio)


def trix(price: Series, period: int, moving_average: MovingAverage) -> Series:
    """
    트라이엄프엑스

    <설명>
    트라이엄프엑스(TRIX)를 구하는 함수입니다.
    트라이엄프엑스(TRIX)는 이동 평균을 세 번 구한 후 이 값의 전일 대비 상승비율을 계산합니다.

    <사용 방법>
    첫 번째 인자에는 트라이엄프엑스(TRIX)를 구하는데 사용하는 가격을,
    두 번째 인자에는 트라이엄프엑스(TRIX)를 구하는데 사용하는 기간을,
    세 번째 인자에는 트라이엄프엑스(TRIX)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 10일간 종가의 지수 이동 평균으로 트라이엄프엑스(TRIX)를 구하고자 하는 경우에는
    'trix(close, 10, ema)' 또는 '소나시그널(종가, 10, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 트라이엄프엑스(TRIX)를 구하는데 사용하는 가격
    :param period: (기간) 트라이엄프엑스(TRIX)를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 트라이엄프엑스(TRIX)를 구할 때 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    if moving_average == MovingAverage.sma:
        ma3 = sma(sma(sma(price, period), period), period)
    elif moving_average == MovingAverage.ema:
        ma3 = ema(ema(ema(price, period), period), period)
    elif moving_average == MovingAverage.ewma:
        ma3 = ewma(ewma(ewma(price, period), period), period)
    elif moving_average == MovingAverage.wma:
        ma3 = wma(wma(wma(price, period), period), period)

    return ma3.diff(1) / ma3.shift(1)


def trix_signal(price: Series, period: int, signal_period: int, moving_average: MovingAverage) -> Series:
    """
    트라이엄프엑스시그널

    <설명>
    트라이엄프엑스시그널(TRIX Signal)을 구하는 함수입니다.
    트라이엄프엑스시그널(TRIX Signal)은 트라이엄프엑스(TRIX)의 이동 평균 값입니다.

    <사용 방법>
    첫 번째 인자에는 트라이엄프엑스(TRIX)를 구하는데 사용하는 가격을,
    두 번째 인자에는 트라이엄프엑스(TRIX)를 구하는데 사용하는 기간을,
    세 번째 인자에는 트라이엄프엑스시그널(TRIX Signal)을 구하는데 사용하는 시그널 기간을,
    네 번째 인자에는 트라이엄프엑스(TRIX)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 10일간 종가의 지수 이동 평균으로 트라이엄프엑스(TRIX)를 구하고 9일간 트라이엄프엑스(TRIX)의 지수 이동 평균을 구하고자 하는 경우에는
    'trix_signal(close, 10, 9, ema)' 또는 '소나시그널(종가, 10, 9, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price: (가격데이터) 트라이엄프엑스(TRIX)를 구하는데 사용하는 가격
    :param period: (기간) 트라이엄프엑스(TRIX)를 구하는데 사용하는 기간
    :param signal_period: (시그널기간) 트라이엄프엑스시그널(TRIX Signal)을 구하는데 사용하는 시그널 기간
    :param moving_average: (이동평균종류) 트라이엄프엑스(TRIX)를 구하는데 사용하는 이동 평균 종류
    :return:
    """
    trix_val = trix(price, period, moving_average)
    if moving_average == MovingAverage.sma:
        return sma(trix_val, signal_period)
    elif moving_average == MovingAverage.ema:
        return ema(trix_val, signal_period)
    elif moving_average == MovingAverage.ewma:
        return ewma(trix_val, signal_period)
    elif moving_average == MovingAverage.wma:
        return wma(trix_val, signal_period)

def pdi(
        price_high: Series, price_low: Series, price_close: Series, period: int, moving_average: MovingAverage
) -> Series:
    """
    매수방향지표

    <설명>
    매수방향지표(PDI)를 구하는 함수입니다.
    매수방향지표(PDI)는 실질적으로 상승하는 폭의 비율을 나타냅니다.
    매수방향지표(PDI)는 0에서 1사이의 값으로 표현됩니다.

    <사용 방법>
    첫 번째 인자에는 고가를,
    두 번째 인자에는 저가를,
    세 번째 인자에는 종가를,
    네 번째 인자에는 매수방향지표(PDI)를 구하는데 사용하는 기간을,
    다섯 번째 인자에는 매수방향지표(PDI)를 구하는데 사용하는 이동 평균 종류를 적으면 됩니다.
    예를 들어, 지수 이동 평균을 이용한 14일간 매수방향지표(PDI)를 구하고자 하는 경우
    'pdi(high, low, close, 14, ema)' 또는 '매수방향지표(고가, 저가, 종가, 14, 지수이동평균)'과 같이 작성하면 됩니다.

    :param price_high: (고가) 고가
    :param price_low: (저가) 저가
    :param price_close: (종가) 종가
    :param period: (기간) 매수방향지표(PDI)를 구하는데 사용하는 기간
    :param moving_average: (이동평균종류) 매수방향지표(PDI)를 구하는데 사용하는 이동 평균 종류 ex) 단순 이동평균, 지수 이동평균, 가중 이동평균
    :return:
    """
    pdm = np.where(
        ((price_high.diff(1) > 0) & (price_high.diff(1) > price_low.shift(1) - price_low)), price_high.diff(1), 0
    )

    if moving_average == MovingAverage.sma:
        pdmn = sma(Series(pdm), period)
    elif moving_average == MovingAverage.ema:
        pdmn = ema(Series(pdm), period)
    elif moving_average == MovingAverage.ewma:
        pdmn = ewma(Series(pdm), period)
    elif moving_average == MovingAverage.wma:
        pdmn = wma(Series(pdm), period)

    tr = _tr(price_high, price_low, price_close)

    if moving_average == MovingAverage.sma:
        trn = sma(tr, period)
    elif moving_average == MovingAverage.ema:
        trn = ema(tr, period)
    elif moving_average == MovingAverage.ewma:
        trn = ewma(tr, period)
    elif moving_average == MovingAverage.wma:
        trn = wma(tr, period)

    return pdmn.divide(trn)


def RSI(price: Series, period: int):

    U = np.where(price.diff(1) > 0, price.diff(1), 0)
    D = np.where(price.diff(1) < 0, price.diff(1) * (-1), 0)

    AU = DataFrame(U).rolling(window=period, min_periods=period).mean()
    AD = DataFrame(D).rolling(window=period, min_periods=period).mean()
    RSI = AU.div(AD + AU)
    return RSI