import numpy as np
import pandas as pd


def numerical_summary(df):
    num=df.select_dtypes(include=np.number)
    if num.empty: return pd.DataFrame()
    rows=[]
    for c in num:
        s=num[c].dropna()
        rows.append({'Column':c,'Mean':s.mean(),'Median':s.median(),'Mode':s.mode().iloc[0] if not s.mode().empty else np.nan,
                     'Std Dev':s.std(),'Minimum':s.min(),'Maximum':s.max(),'Q1':s.quantile(.25),
                     'Q3':s.quantile(.75),'Variance':s.var(),'Skewness':s.skew(),'Kurtosis':s.kurt()})
    return pd.DataFrame(rows)


def categorical_summary(df):
    cat=df.select_dtypes(exclude=np.number)
    cat=cat.select_dtypes(exclude=['datetime64','datetimetz'])
    rows=[]
    for c in cat:
        s=df[c].dropna()
        rows.append({'Column':c,'Unique Values':s.nunique(),'Most Frequent':s.mode().iloc[0] if not s.mode().empty else np.nan,
                     'Top Frequency':int(s.value_counts().iloc[0]) if len(s) else 0})
    return pd.DataFrame(rows)


def outliers_iqr(df):
    rows=[]
    for c in df.select_dtypes(include=np.number):
        s=df[c].dropna(); q1=s.quantile(.25); q3=s.quantile(.75); iqr=q3-q1
        lo=q1-1.5*iqr; hi=q3+1.5*iqr
        count=int(((s<lo)|(s>hi)).sum())
        if count: rows.append({'Column':c,'Outliers':count,'Lower Bound':lo,'Upper Bound':hi})
    return pd.DataFrame(rows)
