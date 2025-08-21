import re

def extract_clean_int(s: str) -> int:
    """
    문자열에서 숫자와 쉼표를 추출하여 정수로 변환합니다.
    처리할 수 없는 경우 0을 반환합니다."""
    if not isinstance(s, str):
        return s
    # 부호 포함 숫자 패턴: + 또는 -가 있을 수 있고, 그 뒤에 숫자와 쉼표
    match = re.search(r'[-+]?\d[\d,]*', s)
    if match:
        num_str = match.group().replace(',', '')  # 쉼표 제거
        return int(num_str)
    return 0

import pandas as pd
import numpy as np
import re

def clean_numeric_string(val: str, percent_mode='float') -> float:
    """
    Cleans and extracts numeric values from strings.
    Handles negative values, commas, backslashes, currency symbols, and percentages.
    """
    if pd.isna(val):
        return val

    val = str(val).strip()
    val = val.replace('\\', '').replace(',', '')

    # Handle percentage
    if '%' in val:
        val = val.replace('%', '')
        try:
            val = float(val)
            return val / 100 if percent_mode == 'float' else val
        except ValueError:
            return np.nan

    # Remove all non-numeric characters except digits, minus, and dot
    val = re.sub(r'[^\d\.-]', '', val)
    try:
        return float(val)
    except ValueError:
        return np.nan

int_cols = []
float_cols = []
date_cols = []
string_cols = [
    '종목코드', 
]
def convert_numeric_columns(
    df: pd.DataFrame,
    force_int_cols=None,
    force_float_cols=None,
    force_date_cols=None,
    force_string_cols=None,
    nan_policy='keep',       # 'keep', 'zero', 'drop'
    percent_mode='float'     # 'float' → 0.724, 'raw' → 72.4
) -> pd.DataFrame:
    force_int_cols = set(force_int_cols or int_cols)
    force_float_cols = set(force_float_cols or float_cols)
    force_date_cols = set(force_date_cols or date_cols)
    force_string_cols = set(force_string_cols or string_cols)

    result_df = df.copy()

    for col in result_df.columns:
        series = result_df[col]

        # Skip string columns
        if col in force_string_cols:
            result_df[col] = series.astype(str)
            continue
        # Step 1: Date columns
        if col in force_date_cols:
            result_df[col] = pd.to_datetime(series, errors='coerce')
            continue

        # Step 2: Numeric-like string cleaning
        if col in force_int_cols or col in force_float_cols:
            cleaned = series.apply(lambda x: clean_numeric_string(x, percent_mode=percent_mode))
        else:
            # Try detecting numeric-like columns (basic heuristic on sample)
            sample = series.dropna().astype(str).head(10)
            if all(re.fullmatch(r'\d{4}[./-]\d{2}[./-]\d{2}', x) for x in sample):
                continue  # 완전한 날짜 패턴이면 스킵
            
            if all(re.search(r'[\d₩%,\\]', x) for x in sample):
                cleaned = series.apply(lambda x: clean_numeric_string(x, percent_mode=percent_mode))
            else:
                continue  # skip non-numeric columns

        # Step 3: NaN policy
        if nan_policy == 'zero':
            cleaned = cleaned.fillna(0)
        elif nan_policy == 'drop':
            cleaned = cleaned.dropna()

        # Step 4: Type decision
        if col in force_int_cols:
            result_df[col] = cleaned.astype('Int64')
        elif col in force_float_cols:
            result_df[col] = cleaned.astype(float)
        else:
            non_na = cleaned.dropna()

            # 소수점 없는 float인지 확인 (정수로 안전하게 변환 가능한지)
            is_integral = non_na.apply(lambda x: float(x).is_integer()).all()
            if is_integral:
                result_df[col] = cleaned.astype('Int64')
            else:
                result_df[col] = cleaned.astype(float)

            # if np.allclose(non_na, non_na.astype(int)):
            #     result_df[col] = cleaned.astype('Int64')
            # else:
            #     result_df[col] = cleaned.astype(float)

    return result_df
