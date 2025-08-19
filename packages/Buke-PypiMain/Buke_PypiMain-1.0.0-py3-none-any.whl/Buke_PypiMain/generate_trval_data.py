from datetime import datetime, date
import numpy as np
import pandas as pd
from pandas import DataFrame
import math


def str_to_date(trading_day: str) -> date:
    return date(int(trading_day[:4]), int(trading_day[5:7]), int(trading_day[8:]))


def int_to_str(x: int) -> str:
    return "%06d" % x


def read_day_price(dir, end_date: date):

    df = pd.read_csv(f"{dir}/data_file/전체데이터_2023_to_{end_date.year}.csv", index_col=0)
    df['날짜'] = df['날짜'].apply(lambda day: str_to_date(day))
    # df['종목코드'] = df['종목코드'].apply(lambda x: int_to_str(x))
    return df


def add_indicator(dir, day_price: DataFrame) -> DataFrame:

    group_list = []
    기관_sum = {'날짜':[], '종가':[]}
    외인_sum = {'날짜':[], '종가':[]}

    grouped = day_price.groupby('날짜')
    for key, group in grouped:
        group = group.reset_index(drop=True)

        기관_ts_sum = sum(group['기관순거래대금'])
        기관_sum['날짜'].append(key)
        기관_sum['종가'].append(기관_ts_sum)

        외인_ts_sum = sum(group['외국인순거래대금'])
        외인_sum['날짜'].append(key)
        외인_sum['종가'].append(외인_ts_sum)

        group_list.append(group)

    기관_sum = pd.DataFrame(기관_sum)
    기관_sum.to_csv(f"{dir}/data_file/기관순거래대금합.csv")

    외인_sum = pd.DataFrame(외인_sum)
    외인_sum.to_csv(f"{dir}/data_file/외인순거래대금합.csv")

def generate_trval_data(dir, day):


    # 1. 일봉 가져오기
    day_price = read_day_price(dir, day)

    # 2. 매수 조건 및 우선순위 생성
    add_indicator(dir, day_price)