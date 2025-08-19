from datetime import date
from math import floor

from Buke_PypiMain.parameter import Market


def year_to_date(year: int):
    return date(year=year, month=1, day=1)


def get_hoga(price: int or float, market: Market, day: date) -> int:
    """
    주가에 따른 1호가 가격을 구하는 함수
    :param price: 주가
    :param market: kospi / kosdaq
    :return: 1호가 가격
    """
    if day < date(2023,1,25):

        if market == Market.kospi:
            if price >= 500000:
                hoga = 1000
            elif price >= 100000:
                hoga = 500
            elif price >= 50000:
                hoga = 100
            elif price >= 10000:
                hoga = 50
            elif price >= 5000:
                hoga = 10
            elif price >= 1000:
                hoga = 5
            else:
                hoga = 1

        elif market == Market.kosdaq:
            if price >= 50000:
                hoga = 100
            elif price >= 10000:
                hoga = 50
            elif price >= 5000:
                hoga = 10
            elif price >= 1000:
                hoga = 5
            else:
                hoga = 1

        elif market == Market.etf:
            hoga = 5
        else:
            raise ValueError("market should be kospi or kosdaq")

    else :

        if market == Market.kospi or market == Market.kosdaq:
            if price >= 500000:
                hoga = 1000
            elif price >= 200000:
                hoga = 500
            elif price >= 50000:
                hoga = 100
            elif price >= 20000:
                hoga = 50
            elif price >= 5000:
                hoga = 10
            elif price >= 2000:
                hoga = 5
            else:
                hoga = 1

        elif market == Market.etf:
            hoga = 5

        else:
            raise ValueError("market should be kospi or kosdaq")

    return hoga


def get_bid_price(price: int or float, market: Market, day: date) -> int:
    """
    살 가격을 구하는 함수
    :param price: 현재가
    :param market: 시장
    :return: 매수 가격
    """
    hoga = get_hoga(floor(price), market, day)
    return int(price // hoga) * hoga + hoga


def get_ask_price(price: int or float, market: Market, day: date) -> int:
    """
    팔 가격을 구하는 함수
    :param price: 현재가
    :param market: 시장
    :return: 매도 가격
    """
    hoga = get_hoga(floor(price), market, day)
    if price % hoga == 0:
        return int(price // hoga) * hoga - hoga
    else:
        return int(price // hoga) * hoga


def get_limit_percent(today: date) -> float:
    if today < date(2015, 6, 15):
        return 0.15
    else:
        return 0.3


def get_upper_limit_price(yesterday_close: int, today: date, market: Market) -> int:
    """
    당일 상한가를 반환하는 함수
    :param yesterday_close: 전일 종가
    :param today: 당일 날짜
    :param market: kospi 또는 kosdaq
    :return: 당일 상한가
    """
    limit_percent = get_limit_percent(today)
    predict_upper_limit_price = yesterday_close * (1 + limit_percent)
    hoga = get_hoga(floor(predict_upper_limit_price), market, today)
    real_upper_limit_price = int(predict_upper_limit_price // hoga) * hoga

    return real_upper_limit_price


def get_lower_limit_price(yesterday_close: int, today: date, market: Market) -> int:
    """
    당일 하한가를 반환하는 함수
    :param yesterday_close: 전일 종가
    :param today: 당일 날짜
    :param market: kospi 또는 kosdaq
    :return: 당일 하한가
    """
    limit_percent = get_limit_percent(today)
    predict_lower_limit_price = yesterday_close * (1 - limit_percent)
    hoga = get_hoga(floor(predict_lower_limit_price), market, today)
    real_lower_limit_price = int(predict_lower_limit_price // hoga) * hoga + hoga

    return real_lower_limit_price


def get_stock_exchange_tax(day: date):
    """
    당일의 증권거래세를 반환하는 함수
    :param day: 당일 날짜
    :return: 당일의 증권거래세
    """
    if day < date(2019, 6, 3):
        stock_exchange_tax = 0.003
    elif day < date(2021, 1, 1):
        stock_exchange_tax = 0.0025
    elif day < date(2023, 1, 1):
        stock_exchange_tax = 0.0023
    elif day < date(2024, 1, 1):
        stock_exchange_tax = 0.002
    elif day < date(2025, 1, 1):
        stock_exchange_tax = 0.0018
    else:
        stock_exchange_tax = 0.0015
    return stock_exchange_tax
