import os
import datetime as dt

import pandas as pd
import numpy as np
from tabulate import tabulate

from mystockutil.type_convert import convert_numeric_columns

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(logger=original_logger, extra={'prefix': 'format'})

"""데이터프레임을 보여주거나 출력하기 위한 함수들을 모아놓은 모듈입니다."""

zero_decimal_columns = [
    '매수총액', '매도총액', '매수평균가', '매수액', '매도액', '현매수', '현재가',
    '평가손익', '실현', '평가', '총평가', '손익', '총손익',  '실현손익', 'TR실현손익', '총실현손익', '미기록손익', 
    '예수금', 'D+1예수금', 'D+2예수금', 
    '현예산', '현금', '초기예산', '잔여예산', '현재예산'
    '포지션사이즈', '총수수료',
    '가용예산', '투입예산', '예비예산', '현재예산',
    '수량', '매수수량', '매도수량', '매도가능수량', '매도가능수량_최대',
    '매수금액', '매도금액', '금액', '평가금액'
]
one_decimal_columns = [
    '평균보유일수', '평균보유', '평균포지션', '발생주기',
    '손익비', 'PF',
]
two_decimal_columns = [
    
]
percent_columns = [
    '수익률', '평균수익률', '추정CAGR', '승률', 'CAGR', '변동률',
    '매도비중', '매도비중_fluct', '매도비중_return',
    '평균이익률', '평균손실률',
]

EXCEL_PATH = r'./df_execl'

def myprint(*args, **kwargs):
    """
    print 함수의 wrapper로, DataFrame이나 dict는 엑셀로 저장하고 출력하며,
    그 외 값은 일반 print로 출력합니다.
    """
    if len(args) == 0:
        return

    first_arg, *rest_args = args

    # DataFrame 또는 dict인 경우 별도 처리
    if isinstance(first_arg, pd.DataFrame) or isinstance(first_arg, dict):
        fixed_order = kwargs.pop('fixed_order', False)
        print_df(first_arg, fixed_order=fixed_order)
        if isinstance(first_arg, pd.DataFrame):
            save_df_to_excel_and_csv(first_arg, EXCEL_PATH)
    else:
        print(first_arg)

    # 나머지 인자 재귀 처리
    if rest_args:
        myprint(*rest_args, **kwargs)

def save_df_to_excel_and_csv(df: pd.DataFrame, dirpath: str) -> None:
    """
    DataFrame을 지정된 디렉토리에 엑셀 파일로 저장합니다.
    파일명은 현재 날짜와 시간을 포함하여 생성되며,
    동일한 파일명이 존재할 경우 숫자를 붙여 중복을 방지합니다.
    
    Parameters
    ----------
    df : pd.DataFrame
        저장할 데이터프레임
    dirpath : str
        엑셀 파일을 저장할 디렉토리 경로
    """
    # 디렉토리가 존재하지 않으면 생성
    os.makedirs(dirpath, exist_ok=True)

    # 현재 날짜와 시간으로 기본 파일명 생성
    timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = f'dataframe_{timestamp}.xlsx'
    filepath = os.path.join(dirpath, base_filename)

    # 동일한 파일명이 있으면 숫자 추가
    counter = 1
    while os.path.exists(filepath):
        filename_with_counter = f'dataframe_{timestamp}_{counter}.xlsx'
        filepath = os.path.join(dirpath, filename_with_counter)
        counter += 1

    # DataFrame을 엑셀로 저장
    df.to_excel(filepath, index=False)
    logger.info(f"DataFrame saved to {filepath}")
    # df.to_csv(filepath.replace('.xlsx', '.csv'), index=False, encoding='utf-8-sig')
    # logger.info(f"DataFrame saved to {filepath.replace('.xlsx', '.csv')}")
        
def print_df(df:pd.DataFrame, fixed_order=False)->None:
    if isinstance(df, dict):
        # dict 형태로 들어온 경우 DF로 변환
        df = pd.DataFrame([df])
    if fixed_order:
        print(tabulate(format_df_to_show(df), headers='keys', tablefmt='psql'))
    else:
        print(tabulate(prettify(df), headers='keys', tablefmt='psql'))

def prettify(df:pd.DataFrame)->pd.DataFrame:
    return format_df_to_show(order_df_to_show(df))

def format_df_to_show(df:pd.DataFrame)->pd.DataFrame:
    df = convert_numeric_columns(df)
    cols_to_modify = zero_decimal_columns + one_decimal_columns + two_decimal_columns + percent_columns
    for col in df.columns:
        if col in zero_decimal_columns:
            df[col] = df[col].map('{:,.0f}'.format)
        elif col in one_decimal_columns:
            df[col] = df[col].map('{:,.1f}'.format)
        elif col in two_decimal_columns:
            df[col] = df[col].map('{:,.2f}'.format)
        elif col in percent_columns or any(x in col for x in ['%', '대비', '수익률']):
            df[col] = df[col].apply(
                lambda x: '{:.2%}'.format(x) if isinstance(x, (int, float)) else x
                )
            # df[col] = df[col].map('{:.2%}'.format)
        elif 'cagr' in col.lower():
            if (df[col] <= 1).all():
                # 모든 값이 1 이하일 때 → 100 곱해서 소수점 1자리
                df[col] = (df[col] * 100).map('{:,.1f}%'.format)
            else:
                # 그렇지 않으면 → 그냥 소수점 1자리
                df[col] = df[col].map('{:,.1f}'.format)    
    return df

def order_df_to_show(df:pd.DataFrame)->pd.DataFrame:
    first_order_columns = [
        '종목명', '수량', '매수총액', '평가손익', '실현손익', '수익률'
    ]
    second_order_columns = [
        '매수가', '매수평균가', '매수총액', '매도가', '매도평균가', '매도총액'
    ]
    last_order_columns = [
        '매수일', '매도일', '증권사', '계좌번호'
    ]
    existing_columns = df.columns.copy()
    for cols in [second_order_columns, first_order_columns]:
        cols_to_move = [c for c in cols if c in existing_columns]
        cols_to_stay = [c for c in existing_columns if c not in cols]
        df = df[cols_to_move + cols_to_stay]
    for cols in [last_order_columns]:
        cols_to_move = [c for c in cols if c in existing_columns]
        cols_to_stay = [c for c in existing_columns if c not in cols]
        df = df[cols_to_stay + cols_to_move]
    return df