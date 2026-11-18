import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from modules.statistics import numerical_summary,categorical_summary,outliers_iqr


def findings(df):
    items=[]
    lower={c.lower():c for c in df.columns}
    def find(*names):
        for n in names:
            if n in lower: return lower[n]
        return None
    season=find('season'); region=find('region','state'); temp=find('temperature_c','temperature'); veg=find('vegetation_type'); severity=find('severity'); area=find('fire_area_hectares','affected_area','area'); humidity=find('humidity_pct','humidity'); wind=find('wind_speed_kmh','wind_speed')
    if season:
        v=df[season].value_counts(); items.append(f"**{v.index[0]}** records the highest incident frequency with **{int(v.iloc[0]):,}** observations.")
    if region:
        v=df[region].value_counts(); items.append(f"**{v.index[0]}** is the most frequently represented region/state, with **{int(v.iloc[0]):,}** records.")
    if temp:
        items.append(f"The average recorded temperature is **{df[temp].mean():.2f}** in the dataset's units.")
    if veg and area:
        s=df.groupby(veg)[area].mean().sort_values(ascending=False); items.append(f"**{s.index[0]}** has the highest average affected area at **{s.iloc[0]:.2f}**.")
    if humidity and severity:
        tmp=df[[humidity,severity]].dropna(); rel=tmp.groupby(severity)[humidity].mean().sort_values(ascending=False)
        if not rel.empty: items.append(f"The severity category with the highest average humidity is **{rel.index[0]}** ({rel.iloc[0]:.2f}).")
    if wind and area:
        corr=df[[wind,area]].dropna().corr().iloc[0,1]; items.append(f"Wind speed and affected area have a Pearson correlation of **{corr:.3f}**.")
    return items


def render_exploration(df):
    st.markdown('<div class="section-kicker">Section 03</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Exploratory Analysis</h1>', unsafe_allow_html=True)
    st.caption('Descriptive statistics, quality checks and calculated findings')

    num=df.select_dtypes(include=np.number); cat=df.select_dtypes(exclude=[np.number,'datetime64','datetimetz'])
    m1,m2,m3,m4,m5,m6=st.columns(6)
    m1.metric('Observations',f'{len(df):,}'); m2.metric('Features',len(df.columns)); m3.metric('Numerical',len(num.columns)); m4.metric('Categorical',len(cat.columns)); m5.metric('Missing',int(df.isna().sum().sum())); m6.metric('Duplicates',int(df.duplicated().sum()))

    tabs=st.tabs(['Statistics','Data quality','Correlation','Distribution','Findings'])
    with tabs[0]:
        st.subheader('Numerical variables')
        ns=numerical_summary(df)
        st.dataframe(ns,hide_index=True,width='stretch',alt='Numerical descriptive statistics') if not ns.empty else st.info('No numerical columns available.')
        st.subheader('Categorical variables')
        cs=categorical_summary(df)
        st.dataframe(cs,hide_index=True,width='stretch',alt='Categorical descriptive statistics') if not cs.empty else st.info('No categorical columns available.')
    with tabs[1]:
        miss=df.isna().sum().reset_index(); miss.columns=['Column','Missing']; miss=miss[miss.Missing>0].sort_values('Missing',ascending=False)
        if miss.empty: st.success('No missing values in the active dataset.')
        else: st.plotly_chart(px.bar(miss,x='Column',y='Missing',color_discrete_sequence=['#E53935']),width='stretch')
        st.subheader('IQR outliers')
        out=outliers_iqr(df)
        st.dataframe(out,hide_index=True,width='stretch',alt='IQR outlier summary') if not out.empty else st.success('No IQR outliers detected.')
        st.subheader('Data types')
        st.dataframe(pd.DataFrame({'Column':df.columns,'Dtype':[str(x) for x in df.dtypes]}),hide_index=True,width='stretch',alt='Data type analysis')
    with tabs[2]:
        if len(num.columns)>=2:
            method=st.segmented_control('Correlation method',['Pearson','Spearman'],selection_mode='single',default='Pearson')
            corr=num.corr(method=method.lower())
            fig=px.imshow(corr,text_auto='.2f',color_continuous_scale='Reds',zmin=-1,zmax=1,aspect='auto')
            fig.update_layout(template='plotly_dark',height=520,paper_bgcolor='#111111',plot_bgcolor='#171717')
            st.plotly_chart(fig,width='stretch')
            pairs=[]
            for i,a in enumerate(corr.columns):
                for b in corr.columns[i+1:]: pairs.append((a,b,corr.loc[a,b]))
            strong=sorted(pairs,key=lambda z:abs(z[2]),reverse=True)[:8]
            st.dataframe(pd.DataFrame(strong,columns=['Variable 1','Variable 2','Coefficient']),hide_index=True,width='stretch',alt='Strong relationships')
        else: st.info('At least two numerical columns are required.')
    with tabs[3]:
        if len(num.columns):
            col=st.selectbox('Numerical variable',num.columns)
            fig=px.histogram(df,x=col,nbins=30,color_discrete_sequence=['#E53935'])
            fig.update_layout(template='plotly_dark',paper_bgcolor='#111111',plot_bgcolor='#171717',height=420)
            st.plotly_chart(fig,width='stretch')
        if len(cat.columns):
            col=st.selectbox('Categorical variable',cat.columns)
            vc=df[col].value_counts().head(20).reset_index(); vc.columns=[col,'Frequency']
            fig=px.bar(vc,x=col,y='Frequency',color_discrete_sequence=['#E53935'])
            fig.update_layout(template='plotly_dark',paper_bgcolor='#111111',plot_bgcolor='#171717',height=420)
            st.plotly_chart(fig,width='stretch')
    with tabs[4]:
        items=findings(df)
        if items:
            for i,item in enumerate(items,1):
                st.markdown(f'<div class="helper-card"><b>{i:02d}</b>&nbsp;&nbsp;{item}</div>',unsafe_allow_html=True)
        else: st.info('No standard analytical findings could be calculated from the available columns.')
