import json
import requests
import pandas as pd
import numpy as np
from datetime import date,timedelta
from time import sleep


def str_to_6str(x) -> str:

    if type(x) == int:
        return "%06d" % x

    else:
        str_len = len(x)
        zero_cnt = 6 - str_len

        for i in range(0, zero_cnt):
            x = '0' + x

        return x


def date_to_str(today):

    str_date = str(today)[:4] + str(today)[5:7] + str(today)[-2:]
    return str_date


def str_to_date(str_date):

    str_date = str_date.replace('-', '')
    year = int(str_date[:4])
    month = int(str_date[4:6])
    day = int(str_date[-2:])
    return date(year,month,day)


def get_day_price(dir, end_date):

    day_price = pd.read_csv(f"{dir}/data_file/전체데이터_2023_to_{end_date.year}.csv", index_col=0)

    return day_price



def generate_stock_list(dir, day):

    day_price = get_day_price(dir, day)

    kospi_date_groupby_df = {'날짜':[], '종목리스트':[]}
    kosdaq_date_groupby_df = {'날짜':[], '종목리스트':[]}
    date_group = day_price.groupby('날짜')

    for date, group in date_group:

        kospi_daily = []
        kosdaq_daily = []

        group['종목코드'] = group['종목코드'].apply(lambda x : str_to_6str(x))

        for i in range(len(group['마켓'])):

            if group['마켓'].iloc[i] == 'KOSPI':
                kospi_daily.append(group['종목코드'].iloc[i])
            else:
                kosdaq_daily.append(group['종목코드'].iloc[i])

        kospi_daily = str(kospi_daily)[1:-1]
        kospi_daily = kospi_daily.replace('\'','').replace(' ','')
        kospi_date_groupby_df['날짜'].append(date)
        kospi_date_groupby_df['종목리스트'].append(kospi_daily)

        kosdaq_daily = str(kosdaq_daily)[1:-1]
        kosdaq_daily = kosdaq_daily.replace('\'', '').replace(' ', '')
        kosdaq_date_groupby_df['날짜'].append(date)
        kosdaq_date_groupby_df['종목리스트'].append(kosdaq_daily)

    df = pd.DataFrame(kospi_date_groupby_df)
    df.to_csv(f"{dir}/data_file/코스피_종목리스트_2023_to_{day.year}.csv")

    df = pd.DataFrame(kosdaq_date_groupby_df)
    df.to_csv(f"{dir}/data_file/코스닥_종목리스트_2023_to_{day.year}.csv")
