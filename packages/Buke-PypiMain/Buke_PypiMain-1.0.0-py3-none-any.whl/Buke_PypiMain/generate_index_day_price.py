import yfinance as yf
from datetime import date, datetime, timedelta
import pandas as pd


def str_to_date(trading_day: str):

    year = int(trading_day[:4])
    month = int(trading_day[5:7])
    day = int(trading_day[8:10])
    return date(year, month, day)


def get_trading_days(dir, start_date: date, end_date: date):

    df = pd.read_csv(f"{dir}/data_file/korea_trading_days.csv", index_col=0)
    df['날짜'] = df['날짜'].apply(lambda day: str_to_date(day))
    trading_days = df['날짜'].to_list()
    trading_days = [day for day in trading_days if start_date <= day <= end_date]
    return trading_days


def data_refactor(dir, start_date, end_date, df):

    df2 = {'날짜':[],'시가':[],'고가':[],'저가':[],'종가':[],'거래량':[]}

    now_date = start_date
    while now_date <= end_date:
        df2['날짜'].append(now_date)
        now_date = now_date + timedelta(days=1)

    now_date = start_date
    while now_date <= end_date :

        flag = 0

        try:
            value_exist_check = df['종가'].loc[now_date]
        except:
            flag = 1
            pass

        if flag == 0:
            df2['시가'].append(df['시가'].loc[now_date])
            df2['고가'].append(df['고가'].loc[now_date])
            df2['저가'].append(df['저가'].loc[now_date])
            df2['종가'].append(df['종가'].loc[now_date])
            df2['거래량'].append(df['거래량'].loc[now_date])

        else:
            df2['시가'].append(df2['시가'][-1])
            df2['고가'].append(df2['고가'][-1])
            df2['저가'].append(df2['저가'][-1])
            df2['종가'].append(df2['종가'][-1])
            df2['거래량'].append(df2['거래량'][-1])

        now_date = now_date + timedelta(days=1)

    df2 = pd.DataFrame(df2)
    df2['날짜'] = df2['날짜'].apply(lambda x : str_to_date(str(x)[:10]))

    trading_days = get_trading_days(dir, start_date, end_date)

    df3 = {'날짜':[],'시가':[],'고가':[],'저가':[],'종가':[],'거래량':[]}
    df2 = df2.set_index('날짜')

    for day in trading_days:

        df3['날짜'].append(day)
        df3['시가'].append(df2['시가'].loc[day])
        df3['고가'].append(df2['고가'].loc[day])
        df3['저가'].append(df2['저가'].loc[day])
        df3['종가'].append(df2['종가'].loc[day])
        df3['거래량'].append(df2['거래량'].loc[day])

    return df3


def generate_index_day_price(dir, day):

    # VIX 지수
    df = yf.download('^VIX')
    df = df.reset_index()

    df['날짜'] = df['Date']
    df['날짜'] = df['날짜'].apply(lambda x: str_to_date(str(x)[:10]))
    df['시가'] = round(df['Open'], 3)
    df['고가'] = round(df['High'], 3)
    df['저가'] = round(df['Low'], 3)
    df['종가'] = round(df['Close'], 3)
    df['거래량'] = round(df['Volume'], 3)

    df = df[['날짜', '시가', '고가', '저가', '종가', '거래량']]

    start_date = df['날짜'].iloc[0]
    end_date = df['날짜'].iloc[-1]
    df = df.set_index('날짜')

    df = data_refactor(dir, start_date, end_date, df)

    MSCI_Korea_ETF = pd.DataFrame(df)
    MSCI_Korea_ETF.to_csv(f"{dir}/data_file/VIX_지수.csv")
    print("VIX 지수 수집완료")

# MSCI 한국 ETF
    df = yf.download('EWY')
    df = df.reset_index()

    df['날짜'] = df['Date']
    df['날짜'] = df['날짜'].apply(lambda x: str_to_date(str(x)[:10]))
    df['시가'] = round(df['Open'], 3)
    df['고가'] = round(df['High'], 3)
    df['저가'] = round(df['Low'], 3)
    df['종가'] = round(df['Close'], 3)
    df['거래량'] = round(df['Volume'], 3)

    df = df[['날짜', '시가', '고가', '저가', '종가', '거래량']]

    start_date = df['날짜'].iloc[0]
    end_date = df['날짜'].iloc[-1]
    df = df.set_index('날짜')

    df = data_refactor(dir, start_date, end_date, df)

    MSCI_Korea_ETF = pd.DataFrame(df)
    MSCI_Korea_ETF.to_csv(f"{dir}/data_file/MSCI_한국_ETF.csv")
    print("MSCI 한국 ETF data 수집완료\n")


    trading_days = get_trading_days(dir, start_date, day)
    korea_end_day = trading_days[-1]
    print(f"한국거래일 : {korea_end_day}   미국거래일 : {str(end_date)[:10]}")
