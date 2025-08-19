import json
import requests
import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

def date_to_str(today):

    str_date = str(today)[:4] + str(today)[5:7] + str(today)[-2:]
    return str_date

def str_to_date(str_date):

    year = int(str_date[:4])
    month = int(str_date[5:7])
    day = int(str_date[-2:])
    return date(year,month,day)

def get_trading_days(dir, start_date: date, end_date: date):

    df = pd.read_csv(f"{dir}/data_file/korea_trading_days.csv", index_col=0)
    df['날짜'] = df['날짜'].apply(lambda day: str_to_date(day))
    trading_days = df['날짜'].to_list()
    trading_days = [day for day in trading_days if start_date <= day <= end_date]
    return trading_days

def get_kospi_price(start_date,end_date):

    str_start_date = date_to_str(start_date)
    str_end_date = date_to_str(end_date)

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT00301',
        'locale': 'ko_KR',
        'tboxindIdx_finder_equidx0_0': '코스닥',
        'indIdx': '2',
        'indIdx2': '001',
        'codeNmindIdx_finder_equidx0_0': '코스닥',
        'param1indIdx_finder_equidx0_0': '',
        'strtDd': str_start_date,
        'endDd': str_end_date,
        'share': '2',
        'money':'3',
        'csvxls_isNo':'false'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd'
    }
    j = json.loads(requests.post(url, data=data, headers=headers).text)

    df = pd.json_normalize(j['output'])

    df = df.replace(',', '', regex=True)
    df = df.drop(['FLUC_TP_CD', 'PRV_DD_CMPR', 'UPDN_RATE'], axis='columns')

    df['TRD_DD'] = df['TRD_DD'].apply(lambda x : str_to_date(x))

    cols_map = {'TRD_DD':'날짜', 'CLSPRC_IDX':'종가', 'OPNPRC_IDX':'시가', 'HGPRC_IDX':'고가',
                'LWPRC_IDX':'저가', 'ACC_TRDVOL':'거래량', 'ACC_TRDVAL':'거래대금', 'MKTCAP':'시가총액'}

    df = df.rename(columns=cols_map)
    df = df[['날짜','종가','시가','고가','저가','거래량','거래대금','시가총액']]
    df = df.sort_values('날짜', ascending=True)

    return df


def generate_kosdaq_price(dir, today):

    end_date = today

    bef_df = pd.read_csv(f"{dir}/data_file/Kosdaq_Price.csv")
    bef_df['날짜'] = bef_df['날짜'].apply(lambda x : str_to_date(x))
    start_date = bef_df['날짜'].iloc[-1] + timedelta(days=1)

    if start_date > end_date:
        print("수집할 코스닥 INDEX가 없습니다")

    trading_days = get_trading_days(dir, start_date, end_date)

    if len(trading_days) > 0:

        aft_df = get_kospi_price(start_date,end_date)
        df = pd.concat([bef_df, aft_df])
        df = df[['날짜','종가','시가','고가','저가','거래량','거래대금','시가총액']]

        df.index = np.arange(len(df))

        df.to_csv(f"{dir}/data_file/Kosdaq_Price.csv")
        print("코스닥 INDEX 수집완료")
