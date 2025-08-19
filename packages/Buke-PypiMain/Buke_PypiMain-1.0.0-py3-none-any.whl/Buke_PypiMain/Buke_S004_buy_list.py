from datetime import date
import pandas as pd
from pandas import DataFrame

from Buke_PypiMain.indicator import sma, ibs, pivot_standard, stochastic_fast_d, stochastic_fast_k, 순거래대금
from Buke_PypiMain.function import rank, ts_min
from Buke_PypiMain.parameter import Market, MovingAverage
from Buke_PypiMain.tools import get_ask_price


def str_to_date(trading_day: str) -> date:
    return date(int(trading_day[:4]), int(trading_day[5:7]), int(trading_day[8:]))


def int_to_str(x: int) -> str:
    return "%06d" % x


def read_trading_days(dir, end_date: date):

    df = pd.read_csv(f"{dir}/data_file/korea_trading_days.csv", index_col=0)
    df['날짜'] = df['날짜'].apply(lambda day: str_to_date(day))
    trading_days = df['날짜'].to_list()
    trading_days = [day for day in trading_days if day <= end_date]

    return trading_days


def read_day_price(dir, end_date: date):

    df = pd.read_csv(f"{dir}/data_file/수급데이터_2022_to_{end_date.year}.csv", index_col=0)
    df['날짜'] = df['날짜'].apply(lambda day: str_to_date(day))
    # df['종목코드'] = df['종목코드'].apply(lambda x: int_to_str(x))
    return df


def read_index_day_price(dir):

    df = pd.read_csv(f"{dir}/data_file/MSCI_한국_ETF.csv", index_col=0)
    df['날짜'] = df['날짜'].apply(lambda day: str_to_date(day))
    return df


def read_index_history(dir, end_date: date):

    ks_history = pd.read_csv(f"{dir}/data_file/코스피_종목리스트_2022_to_{end_date.year}.csv", index_col=0)
    ks_history['날짜'] = ks_history['날짜'].apply(lambda day: str_to_date(day))
    ks_history = ks_history.set_index('날짜')

    kq_history = pd.read_csv(f"{dir}/data_file/코스닥_종목리스트_2022_to_{end_date.year}.csv")
    kq_history['날짜'] = kq_history['날짜'].apply(lambda day: str_to_date(day))
    kq_history = kq_history.set_index('날짜')
    return ks_history, kq_history


def add_indicator(day_price: DataFrame, index_day_price: DataFrame) -> DataFrame:

    group_list = []
    grouped = day_price.groupby('종목코드')
    for key, group in grouped:
        group = group.reset_index(drop=True)
        group['거래대금_이평선_5'] = sma(group['거래대금'], 5)
        group['pivot_기준선'] = pivot_standard(group['고가'], group['저가'], group['종가'])

        group['ibs'] = ibs(group['고가'], group['저가'], group['종가'])

        group['기관순거래대금_이평선_5'] = sma(group['기관순거래대금'], 5)
        group['기관순거래대금_이평선_10'] = sma(group['기관순거래대금'], 10)

        group['종가_최솟값_10'] = ts_min(group['종가'], 10)

        group['순거래대금'] = 순거래대금(group['종가'], group['거래량'], 1)
        group['순거래대금_이평선_5'] = sma(group['순거래대금'], 5)

        group['종가_이평선_20'] = sma(group['종가'], 20)

        group['스토캐스틱_fast'] = stochastic_fast_k(group['고가'], group['저가'], group['종가'], 20)
        group['스토캐스틱_slow'] = stochastic_fast_d(group['고가'], group['저가'], group['종가'], 20, 5, MovingAverage.sma)

        group_list.append(group)

    day_price = pd.concat(group_list, axis=0)
    day_price = day_price.reset_index(drop=True)

    group_list = []
    grouped = day_price.groupby('날짜')
    for key, group in grouped:
        group = group.reset_index(drop=True)
        group['거래대금_이평선_5_순위'] = rank(group['거래대금_이평선_5'])
        group['순거래대금_이평선_5_순위'] = rank(group['순거래대금_이평선_5'])
        group['시가총액_순위'] = rank(group['시가총액'])

        group_list.append(group)
    day_price = pd.concat(group_list, axis=0)
    day_price = day_price.reset_index(drop=True)

    day_price_dict = {}
    grouped = day_price.groupby('종목코드')
    for key, group in grouped:

        increase_condition1 = group['ibs'] < 0.7
        increase_condition2 = group['거래대금_이평선_5'] > group['거래대금']
        increase_condition3 = group['종가'] / group['종가_최솟값_10'] > 1.1
        increase_condition4 = group['종가'] / group['종가_이평선_20'] > 1.05
        increase_condition5 = group['기관순거래대금_이평선_5'] > 0
        increase_condition6 = group['기관순거래대금_이평선_10'] > 0

        increase_condition = increase_condition1 & increase_condition2 & increase_condition3 & increase_condition4 & \
                             increase_condition5 & increase_condition6

        liquidity_condition1 = group['순거래대금_이평선_5_순위'] > 0.3
        liquidity_condition2 = group['시가총액_순위'] > 0.3

        liquidity_condition = liquidity_condition1 & liquidity_condition2

        # Result
        group['#final_result'] = increase_condition & liquidity_condition

        group['#priority'] = group['스토캐스틱_slow'] - group['스토캐스틱_fast']

        group = group.set_index('날짜')
        day_price_dict[key] = group

    # Market Timing
    index_day_price['이평선_3'] = sma(index_day_price['종가'], 3)
    index_day_price['이평선_5'] = sma(index_day_price['종가'], 5)
    index_day_price['이평선_10'] = sma(index_day_price['종가'], 10)
    # index_day_price['pct_change_21'] = pct_change(index_day_price['close'], 21)
    index_day_price['#market_timing'] = (index_day_price['종가'] > index_day_price['이평선_3']) | \
                                        (index_day_price['종가'] > index_day_price['이평선_5']) | \
                                        (index_day_price['종가'] > index_day_price['이평선_10'])
    index_day_price = index_day_price.set_index('날짜')

    return day_price_dict, index_day_price


def Buke_S004_buy_list(dir, day):

    path = f"{dir}/trade_list/{day}"

    # 1. 거래일 가져오기
    trading_days_list = read_trading_days(dir, day)

    # 2. 일봉 가져오기
    day_price = read_day_price(dir, day)
    index_day_price = read_index_day_price(dir)

    # 3. 지수 종목 구성 내역 가져오기
    kospi_history, kosdaq_history = read_index_history(dir, day)

    # 4. 매수 조건 및 우선순위 생성
    day_price, index_day_price = add_indicator(day_price, index_day_price)

    # 5. 매수할 종목 확인
    kospi_ticker_list = kospi_history['종목리스트'].loc[trading_days_list[-1]].split(',')
    kosdaq_ticker_list = kosdaq_history['종목리스트'].loc[trading_days_list[-1]].split(',')

    # Market Timing
    try:
        yesterday_market_time = bool(index_day_price['#market_timing'].loc[trading_days_list[-1]])
        print(yesterday_market_time)

    except:

        print("오늘은 매매하기 위험한 날 입니다. 프로그램을 종료합니다.")
        none_list = ["오늘은 매매하기 위험한 날 입니다."]
        df = pd.DataFrame(none_list)
        df.to_csv(f"{path}/buy_4_{str(day)[-5:]}.txt")
        return False

    if yesterday_market_time is False:
        print("오늘은 매매하기 위험한 날 입니다. 프로그램을 종료합니다.")
        none_list = ["오늘은 매매하기 위험한 날 입니다."]
        df = pd.DataFrame(none_list)
        df.to_csv(f"{path}/buy_4_{str(day)[-5:]}.txt")
        return False
    print("종목을 선정중입니다.\n")

    pre_buy_list = []
    for ticker in kospi_ticker_list + kosdaq_ticker_list:

        try:
            yesterday_buy_condition = bool(day_price[ticker]['#final_result'].loc[trading_days_list[-1]])
            if yesterday_buy_condition:
                priority_value = float(day_price[ticker]['#priority'].loc[trading_days_list[-1]])
                ticker_data = (priority_value, ticker)
                pre_buy_list.append(ticker_data)
        except:
            continue

    pre_buy_list.sort(reverse=True)

    pre_buy_list = pre_buy_list[:10]
    print(pre_buy_list)

    basket = {'종목코드': [],'종목명':[], '매수가격1': []}

    for priority_value, ticker in pre_buy_list:

        try:
            yesterday_low = int(day_price[ticker]['저가'].loc[trading_days_list[-1]])
            ticker_name = day_price[ticker]['종목명'].loc[trading_days_list[-1]]

            if ticker in kospi_ticker_list:
                buy_price1 = get_ask_price(yesterday_low * 0.98, Market.kospi)

            else:
                buy_price1 = get_ask_price(yesterday_low * 0.98, Market.kosdaq)


            basket['종목코드'].append(ticker)
            basket['종목명'].append(ticker_name)
            basket['매수가격1'].append(f"{buy_price1}원")

        except:
            continue

    print(basket)

    df = pd.DataFrame(basket)
    df.to_csv(f"{path}/buy_4_{str(day)[-5:]}.txt")