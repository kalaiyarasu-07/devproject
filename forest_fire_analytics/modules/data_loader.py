from pathlib import Path
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def read_file(path_or_bytes, name):
    suffix = Path(str(name)).suffix.lower()
    if isinstance(path_or_bytes, (str, Path)):
        path = Path(path_or_bytes)
        if suffix == '.csv':
            return pd.read_csv(path)
        return pd.read_excel(path)
    if suffix == '.csv':
        return pd.read_csv(path_or_bytes)
    if suffix in ('.xlsx', '.xls'):
        return pd.read_excel(path_or_bytes)
    raise ValueError('Unsupported file type')
