import json
import requests
import pandas as pd
import numpy as np
from datetime import date,timedelta
from time import sleep


def int_to_str(x: int) -> str:
    return "%06d" % x


def date_to_str(today):

    str_date = str(today)[:4] + str(today)[5:7] + str(today)[-2:]
    return str_date


def str_to_date(str_date):

    str_date = str_date.replace('-', '')
    year = int(str_date[:4])
    month = int(str_date[4:6])
    day = int(str_date[-2:])
    return date(year,month,day)


def get_trading_day(dir, start_date, end_date):

    trading_days = pd.read_csv(f"{dir}/data_file/korea_trading_days.csv")
    trading_days['날짜'] = trading_days['날짜'].apply(lambda x: str_to_date(x))
    trading_days = trading_days['날짜'].to_list()
    trading_days = [day for day in trading_days if start_date <= day <= end_date]
    return trading_days


def get_supply_day_price(today):

    print(today)

     # 코스피 일봉 수집
    # 인데 -> 거래일 리스트를 생성해야함 (삼성전자 데이터 수집)

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
        'mktId': 'STK',
        'trdDd': str(today),
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd'
    }

    j = json.loads(requests.post(url, headers=headers, data=data).text)
    df = pd.json_normalize(j['OutBlock_1'])
    df = df.replace(',', '', regex=True)
    df = df.drop(['SECT_TP_NM','MKT_ID','FLUC_TP_CD','CMPPREVDD_PRC','FLUC_RT'],axis='columns')

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
        'mktId': 'KSQ',
        'trdDd': str(today),
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd'
    }

    j = json.loads(requests.post(url, headers=headers, data=data).text)
    df2 = pd.json_normalize(j['OutBlock_1'])
    df2 = df2.replace(',', '', regex=True)
    df2 = df2.drop(['SECT_TP_NM', 'MKT_ID', 'FLUC_TP_CD', 'CMPPREVDD_PRC', 'FLUC_RT'], axis='columns')

    df = pd.concat([df,df2])

    date_index = str_to_date(today)
    df['날짜'] = date_index

    cols_map = {'ISU_SRT_CD':'종목코드', 'ISU_ABBRV':'종목명', 'MKT_NM':'마켓', '날짜':'날짜',
                'TDD_CLSPRC':'종가', 'TDD_OPNPRC':'시가', 'TDD_HGPRC':'고가', 'TDD_LWPRC':'저가',
                'ACC_TRDVOL':'거래량', 'ACC_TRDVAL':'거래대금', 'MKTCAP':'시가총액', 'LIST_SHRS':'상장주식수'
    }

    df = df.rename(columns=cols_map)
    df = df[['종목코드','종목명','날짜','마켓','종가','시가','고가','저가','거래량','거래대금','시가총액','상장주식수']]

    per_df = pd.DataFrame()
    per_df[['종목코드', 'EPS', 'PER', 'BPS', 'PBR', '주당배당금', '배당수익률']] = 0.

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT03501',
        'locale': 'ko_KR',
        'searchType': '1',
        'mktId': 'ALL',
        'trdDd': str(today),
        'tboxisuCd_finder_stkisu0_4': '005930/삼성전자',
        'isuCd': 'KR7005930003',
        'isuCd2': 'KR7005930003',
        'codeNmisuCd_finder_stkisu0_4': '삼성전자',
        'param1isuCd_finder_stkisu0_4': 'ALL',
        'strtDd': str(today),
        'endDd': str(today),
        'csvxls_isNo': 'false'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd'
    }
    j = json.loads(requests.post(url, headers=headers, data=data).text)
    per_df2 = pd.json_normalize(j['output'])
    per_df2 = per_df2.replace(',', '', regex=True)

    per_df['종목코드'] = per_df2['ISU_SRT_CD']
    per_df['EPS'] = per_df2['EPS']
    per_df['PER'] = per_df2['PER']
    per_df['BPS'] = per_df2['BPS']
    per_df['PBR'] = per_df2['PBR']
    per_df['주당배당금'] = per_df2['DPS']
    per_df['배당수익률'] = per_df2['DVD_YLD']

    all_df = pd.merge(df, per_df, on='종목코드', how='inner')

    # b의 컬럼에 있는 NaN 값을 0으로 채움
    all_df = all_df.replace('-', 0)
    all_df = all_df.fillna(0)

    all_df['시가총액'] = pd.to_numeric(all_df['시가총액'], errors = 'coerce')
    all_df.sort_values('시가총액', ascending=False, inplace=True)

    df = pd.DataFrame()

    dic_code = {'1000': '금융투자', '2000': '보험', '3000': '투신', '4000': '은행', '5000': '기타금융', '6000': '연기금', \
                '7050': '기관', '7100': '기타법인', '8000': '개인', '9000': '외국인', '9001': '기타외국인'}


    for code in dic_code:

        url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
        data = {
            'bld': 'dbms/MDC/STAT/standard/MDCSTAT02401',
            'locale': 'ko_KR',
            'mktId': 'ALL',
            'invstTpCd': code,
            'strtDd': str(today),
            'endDd': str(today),
            'share': '1',
            'money':'1',
            'csvxls_isNo':'false'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd'
        }
        j = json.loads(requests.post(url, headers=headers, data=data).text)
        local_df = pd.json_normalize(j['output'])
        local_df = local_df.replace(',', '', regex=True)

        local_df = local_df[['ISU_SRT_CD', 'ISU_NM', 'NETBID_TRDVOL', 'NETBID_TRDVAL']]

        df2 = pd.DataFrame()
        df2['종목코드'] = local_df['ISU_SRT_CD']
        df2[f'{dic_code[code]}순매수'] = local_df['NETBID_TRDVOL']
        df2[f'{dic_code[code]}순거래대금'] = local_df['NETBID_TRDVAL']

        if code == '1000':

            df['종목코드'] = local_df['ISU_SRT_CD']
            df[f'{dic_code[code]}순매수'] = local_df['NETBID_TRDVOL']
            df[f'{dic_code[code]}순거래대금'] = local_df['NETBID_TRDVAL']

        else :
            df = pd.merge(df, df2, on='종목코드', how='left')
            df = df.replace('-', 0)
            df = df.fillna(0)


    all_df = pd.merge(all_df, df, on='종목코드', how='left')

    # b의 컬럼에 있는 NaN 값을 0으로 채움
    all_df = all_df.replace('-', 0)
    all_df = all_df.fillna(0)


    for_df = pd.DataFrame()
    for_df[['종목코드', '외국인보유수량', '외국인지분율']] = 0.

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
    data = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT03701',
        'locale': 'ko_KR',
        'searchType': '1',
        'mktId': 'ALL',
        'trdDd': str(today),
        'tboxisuCd_finder_stkisu0_4': '005930/삼성전자',
        'isuCd': 'KR7005930003',
        'isuCd2': 'KR7005930003',
        'codeNmisuCd_finder_stkisu0_5': '삼성전자',
        'param1isuCd_finder_stkisu0_5': 'ALL',
        'strtDd': str(today),
        'endDd': str(today),
        'share':'1',
        'csvxls_isNo': 'false'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd'
    }
    j = json.loads(requests.post(url, headers=headers, data=data).text)
    for_df2 = pd.json_normalize(j['output'])
    for_df2 = for_df2.replace(',', '', regex=True)

    for_df['종목코드'] = for_df2['ISU_SRT_CD']
    for_df['외국인보유수량'] = for_df2['FORN_HD_QTY']
    for_df['외국인지분율'] = for_df2['FORN_LMT_EXHST_RT']

    all_df = pd.merge(all_df, for_df, on='종목코드', how='left')
    df = all_df.reset_index()

    return df


def generate_day_price(dir, day):

    bef_day_price = pd.read_csv(f"{dir}/data_file/전체데이터_2023_to_{day.year}.csv", index_col=0)

    try:
        bef_day_price['날짜'] = bef_day_price['날짜'].apply(lambda day: str_to_date(day))
        bef_day_price['종목코드'] = bef_day_price['종목코드'].apply(lambda x: int_to_str(x))
    except:
        pass

    start_date = bef_day_price['날짜'].iloc[-1]
    start_date = start_date + timedelta(days=1)

    end_date = day

    if start_date > end_date:
        print("수집할 가격데이터가 없습니다")

    trading_days = get_trading_day(dir, start_date, end_date)


    if len(trading_days) == 0:

        print("수집할 가격데이터가 없습니다")

    else:

        trading_days = [date_to_str(day) for day in trading_days]

        aft_day_price = get_supply_day_price(trading_days[0])

        for i,now_day in enumerate(trading_days):

            if i == 0:
                continue

            df2 = get_supply_day_price(now_day)
            aft_day_price = pd.concat([aft_day_price,df2])

        try:
            day_price = pd.concat([bef_day_price, aft_day_price])
            day_price = day_price.reset_index()
        except:
            pass
        # ,level_0,index,종목코드,종목명,날짜,마켓,종가,시가,고가,저가,거래량,거래대금,시가총액,상장주식수,금융투자순매수,금융투자순거래대금,보험순매수,보험순거래대금,투신순매수,투신순거래대금,은행순매수,은행순거래대금,기타금융순매수,기타금융순거래대금,연기금순매수,연기금순거래대금,기관순매수,기관순거래대금,기타법인순매수,기타법인순거래대금,개인순매수,개인순거래대금,외국인순매수,외국인순거래대금,기타외국인순매수,기타외국인순거래대금

        day_price = day_price[['종목코드','종목명','날짜','마켓','종가','시가','고가','저가','거래량','거래대금','시가총액'\
            ,'상장주식수','금융투자순매수','금융투자순거래대금','보험순매수','보험순거래대금','투신순매수','투신순거래대금','은행순매수'\
            ,'은행순거래대금','기타금융순매수','기타금융순거래대금','연기금순매수','연기금순거래대금','기관순매수','기관순거래대금'\
            ,'기타법인순매수','기타법인순거래대금','개인순매수','개인순거래대금','외국인순매수','외국인순거래대금','기타외국인순매수','기타외국인순거래대금'\
            ,'EPS','PER','BPS','PBR','주당배당금','배당수익률','외국인보유수량','외국인지분율']]

        day_price.to_csv(f"{dir}/data_file/전체데이터_2023_to_{day.year}.csv")