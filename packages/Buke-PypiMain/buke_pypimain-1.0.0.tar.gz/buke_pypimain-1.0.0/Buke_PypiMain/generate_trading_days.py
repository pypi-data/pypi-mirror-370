from datetime import date, timedelta
import pandas as pd
import json
import requests
import os
import numpy as np


def date_to_str(today):

    str_date = str(today)[:4] + str(today)[5:7] + str(today)[-2:]
    return str_date


def str_to_date(trading_day: str):
    year = int(trading_day[:4])
    month = int(trading_day[5:7])
    day = int(trading_day[-2:])
    return date(year, month, day)


def get_trading_days(dir):
    df = pd.read_csv(f"{dir}/data_file/korea_trading_days.csv", index_col=0)
    df['날짜'] = df['날짜'].apply(lambda day: str_to_date(day))
    return df


def generate_trading_days(dir, day):

    try:
        os.makedirs(f"{dir}/data_file")
    except OSError:
        if not os.path.isdir(f"{dir}/data_file"):
            raise

    bef_trading_days = get_trading_days(dir)
    start_date = bef_trading_days['날짜'].iloc[-1]
    start_date = start_date + timedelta(days=1)

    end_date = day

    if start_date > end_date :

        print("수집할 거래일이 없습니다")

    else :

        str_start_date = date_to_str(start_date)
        str_end_date = date_to_str(end_date)

        try:

            url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
            data = {
                'bld': 'dbms/MDC/STAT/standard/MDCSTAT01701',
                'tboxisuCd_finder_stkisu0_5': '005930/삼성전자',
                'isuCd': 'KR7005930003',
                'isuCd2': 'KR7005930003',
                'codeNmisuCd_finder_stkisu0_5': '삼성전자',
                'param1isuCd_finder_stkisu0_5': 'ALL',
                'strtDd': str_start_date,
                'endDd': str_end_date,
                'share': '1',
                'money': '1',
                'csvxls_isNo': 'false',
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd'
            }

            j = json.loads(requests.post(url, data=data, headers=headers).text)

            df = pd.json_normalize(j['output'])
            df = df.replace(',', '', regex=True)

            df['TRD_DD'] = df['TRD_DD'].apply(lambda x: str_to_date(x))
            date_list = df['TRD_DD'].tolist()
            date_list.sort(reverse=False)
            aft_trading_days = pd.DataFrame({"날짜": date_list})

            df = pd.concat([bef_trading_days, aft_trading_days])
            df.index = np.arange(len(df))

            df.to_csv(f"{dir}/data_file/korea_trading_days.csv")

        except:

            print("(EXCEPT) 수집할 거래일이 없습니다.")


