import streamlit as st
import numpy as np
import pandas as pd
from modules.data_validation import detect_types
from modules.chart_builder import build_chart

PRIMARY=['Bar Chart','Line Chart','Pie / Donut Chart','Histogram','Scatter Plot','Correlation Heatmap']
ADVANCED=['Area Chart','Box Plot','Violin Plot','Treemap','Bubble Chart','Density Heatmap','Geographic Scatter Map']


def render_visualization(df, palette):
    st.markdown('<div class="section-kicker">Section 02</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Visualization Studio</h1>', unsafe_allow_html=True)
    st.caption('Choose a method, configure variables and export the result')

    types=detect_types(df); num=types['numerical']; cat=types['categorical']; dt=types['datetime']; allcols=df.columns.tolist()
    kind=st.segmented_control('Visualization method',PRIMARY+ADVANCED,selection_mode='single',default='Bar Chart')
    if kind is None: kind='Bar Chart'

    config={'kind':kind,'title':kind,'height':430,'legend':True,'xlabel':'','ylabel':'','sort':True,'bins':30,'marker':18,'hole':.55,'annot':True,'agg':'Average','orientation':'Vertical','method':'Pearson'}

    left,right=st.columns([1,2.3],gap='medium')
    with left:
        st.subheader('Chart settings')
        config['title']=st.text_input('Chart title',kind)
        config['height']=st.slider('Chart height',300,800,430,25)
        config['legend']=st.toggle('Show legend',True)
        config['xlabel']=st.text_input('X-axis label','')
        config['ylabel']=st.text_input('Y-axis label','')

        x_options=allcols
        if kind in ('Histogram','Pie / Donut Chart','Correlation Heatmap','Geographic Scatter Map'):
            x_options=num if kind=='Histogram' else cat if kind=='Pie / Donut Chart' else allcols
        def sel(label,options,index=0,disabled=False):
            return st.selectbox(label,options,index=min(index,len(options)-1)) if options else (st.info(f'No suitable column available for {label.lower()}.') or None)

        if kind in ('Correlation Heatmap',):
            config['method']=st.segmented_control('Correlation coefficient',['Pearson','Spearman'],selection_mode='single',default='Pearson') or 'Pearson'
            config['annot']=st.toggle('Show annotations',True)
        elif kind=='Pie / Donut Chart':
            config['x']=sel('Categorical column',cat or allcols)
            config['label_col']=config['x'] or 'Category'
            config['value']=st.selectbox('Numerical value column',[None]+num)
            config['hole']=st.slider('Donut hole',0.0,.8,.55,.05)
        elif kind=='Histogram':
            config['x']=sel('Numerical column',num)
            config['bins']=st.slider('Number of bins',5,100,30,5)
        elif kind=='Geographic Scatter Map':
            lower={c.lower():c for c in allcols}
            lat=next((lower[k] for k in ('latitude','lat') if k in lower),None)
            lon=next((lower[k] for k in ('longitude','lon','lng') if k in lower),None)
            config['lat']=sel('Latitude column',[c for c in allcols if c==lat] or allcols)
            config['lon']=sel('Longitude column',[c for c in allcols if c==lon] or allcols)
            config['color']=st.selectbox('Color column',[None]+allcols)
            config['y']=st.selectbox('Size column',[None]+num)
        else:
            config['x']=sel('X-axis column',dt+num+cat)
            if kind not in ('Treemap',): config['y']=sel('Y-axis column',[None]+num)
            else: config['y']=sel('Value column',[None]+num)
            config['color']=st.selectbox('Color / grouping column',[None]+allcols)
            if kind=='Scatter Plot':
                config['size_col']=st.selectbox('Marker size column',[None]+num)
                config['marker']=st.slider('Maximum marker size',8,40,18,2)
            if kind=='Line Chart':
                config['agg']=st.selectbox('Aggregation',['Average','Sum','Count','Minimum','Maximum'])
                config['sort']=st.toggle('Sort X-axis',True)
            if kind=='Bar Chart':
                config['agg']=st.selectbox('Aggregation',['Sum','Average','Count','Minimum','Maximum'])
                config['orientation']=st.segmented_control('Orientation',['Vertical','Horizontal'],selection_mode='single',default='Vertical') or 'Vertical'
            if kind=='Density Heatmap': config['bins']=st.slider('Bin count',10,100,30,5)

        if st.button('Reset chart settings',width='stretch'):
            st.rerun()

    with right:
        required={
            'Bar Chart': bool(config.get('x')) and bool(config.get('y') or kind=='Bar Chart'),
            'Line Chart': bool(config.get('x') and config.get('y')),
            'Pie / Donut Chart': bool(config.get('x')),
            'Histogram': bool(config.get('x')),
            'Scatter Plot': bool(config.get('x') and config.get('y')),
            'Correlation Heatmap': len(num)>=2,
            'Area Chart': bool(config.get('x') and config.get('y')),
            'Box Plot': bool(config.get('y')),
            'Violin Plot': bool(config.get('y')),
            'Treemap': bool(config.get('x')),
            'Bubble Chart': bool(config.get('x') and config.get('y')),
            'Density Heatmap': bool(config.get('x') and config.get('y')),
            'Geographic Scatter Map': bool(config.get('lat') and config.get('lon')),
        }
        if not required.get(kind,False):
            st.markdown('<div class="warning-card"><b>Chart cannot be generated</b><br>The active dataset needs the required columns for this visualization.</div>',unsafe_allow_html=True)
        else:
            try:
                fig=build_chart(df,config,palette)
                st.plotly_chart(fig,width='stretch',config={'displaylogo':False,'modeBarButtonsToAdd':['downloadImage'],'responsive':True})
                st.download_button('Download chart data',df.to_csv(index=False).encode('utf-8'),file_name='chart_data.csv',mime='text/csv',width='stretch')
            except Exception as exc:
                st.error(f'Unable to render chart: {exc}')
