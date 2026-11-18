import pandas as pd
import numpy as np


def clean_dataframe(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()].drop_duplicates()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].replace(r'^\s*$', np.nan, regex=True)
        df[col] = df[col].infer_objects(copy=False)
    for col in df.columns:
        if df[col].dtype == 'object':
            converted = pd.to_datetime(df[col], errors='coerce')
            if converted.notna().mean() >= 0.8:
                df[col] = converted
    return df


def detect_types(df):
    num = df.select_dtypes(include=[np.number]).columns.tolist()
    dt = df.select_dtypes(include=['datetime64', 'datetimetz']).columns.tolist()
    cat = [c for c in df.columns if c not in num and c not in dt]
    geo = [c for c in df.columns if c.lower() in ('latitude','lat','longitude','lon','lng','longitude_deg')]
    return {'numerical': num, 'categorical': cat, 'datetime': dt, 'geographical': geo}


def quality_report(df):
    return {
        'missing': int(df.isna().sum().sum()),
        'duplicates': int(df.duplicated().sum()),
        'missing_by_column': df.isna().sum()[df.isna().sum() > 0].sort_values(ascending=False),
        'rows': len(df), 'columns': len(df.columns)
    }
