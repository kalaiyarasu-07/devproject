import streamlit as st
import pandas as pd
from modules.data_loader import read_file
from modules.data_validation import clean_dataframe, quality_report, detect_types


def render_dataset_upload(df):
    st.markdown('<div class="section-kicker">Section 01</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Dataset Upload</h1>', unsafe_allow_html=True)
    st.caption('Load, inspect and prepare data for analysis')

    uploaded=st.file_uploader('Upload CSV or Excel',type=['csv','xlsx','xls'],help='Replace the active dataset')
    if uploaded:
        try:
            raw=read_file(uploaded,uploaded.name)
            df=clean_dataframe(raw)
            st.session_state.df=df
            st.session_state.dataset_name=uploaded.name
            st.session_state.uploaded=True
            st.success(f'Loaded {uploaded.name}',icon=':material/check_circle:')
        except Exception as exc:
            st.error(f'Could not load dataset: {exc}')

    c1,c2,c3=st.columns(3)
    c1.metric('Dataset',st.session_state.dataset_name[:28])
    c2.metric('Observations',f'{len(df):,}')
    c3.metric('Features',len(df.columns))

    types=detect_types(df); report=quality_report(df)
    st.divider()
    tabs=st.tabs(['Preview','Column types','Data quality'])
    with tabs[0]:
        if df.empty:
            st.info('The active dataset contains no rows.')
        else:
            page_size=st.selectbox('Rows per page',[10,25,50,100],index=1)
            pages=max(1,(len(df)-1)//page_size+1)
            page=st.number_input('Page',1,pages,1)
            start=(page-1)*page_size
            st.dataframe(df.iloc[start:start+page_size],hide_index=True,width='stretch',alt='Dataset preview')
    with tabs[1]:
        type_rows=[]
        for col in df.columns:
            dtype='Numerical' if col in types['numerical'] else 'Datetime' if col in types['datetime'] else 'Categorical'
            if col in types['geographical']: dtype='Geographical'
            type_rows.append({'Column':col,'Detected type':dtype,'Dtype':str(df[col].dtype),'Missing':int(df[col].isna().sum())})
        st.dataframe(pd.DataFrame(type_rows),hide_index=True,width='stretch',alt='Detected column types')
    with tabs[2]:
        q1,q2,q3=st.columns(3)
        q1.metric('Missing values',report['missing'])
        q2.metric('Duplicate records',report['duplicates'])
        q3.metric('Memory usage',f'{df.memory_usage(deep=True).sum()/1024:.1f} KB')
        if not report['missing_by_column'].empty:
            st.bar_chart(report['missing_by_column'],color='#E53935',height=260)
        else: st.success('No missing values detected')

    csv=df.to_csv(index=False).encode('utf-8')
    st.download_button('Download cleaned dataset',csv,file_name='cleaned_dataset.csv',mime='text/csv',width='stretch')
    return df
