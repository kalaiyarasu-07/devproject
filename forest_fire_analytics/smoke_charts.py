import pandas as pd
from modules.chart_builder import build_chart

df=pd.read_csv('datasets/forest_fire_sample_1000_rows.csv')
pal=['#E53935','#FF625E','#B71C1C']
base={'height':430,'legend':True,'xlabel':'','ylabel':'','title':'Test','color':None,'marker':18}
charts={
'Bar':{'kind':'Bar Chart','x':'season','y':'fire_area_hectares','agg':'Average','orientation':'Vertical'},
'Line':{'kind':'Line Chart','x':'date','y':'temperature_c','sort':True},
'Pie':{'kind':'Pie / Donut Chart','x':'season','label_col':'season','hole':.55,'value':None},
'Histogram':{'kind':'Histogram','x':'temperature_c','bins':30},
'Scatter':{'kind':'Scatter Plot','x':'temperature_c','y':'humidity_pct','size_col':None},
'Heatmap':{'kind':'Correlation Heatmap','method':'Pearson','annot':True},
'Area':{'kind':'Area Chart','x':'date','y':'temperature_c'},
'Box':{'kind':'Box Plot','x':'severity','y':'temperature_c'},
'Violin':{'kind':'Violin Plot','x':'severity','y':'temperature_c'},
'Treemap':{'kind':'Treemap','x':'region','y':'fire_area_hectares'},
'Bubble':{'kind':'Bubble Chart','x':'temperature_c','y':'humidity_pct','size_col':'risk_score'},
'Density':{'kind':'Density Heatmap','x':'temperature_c','y':'humidity_pct','bins':30},
'Map':{'kind':'Geographic Scatter Map','lat':'latitude','lon':'longitude','y':'risk_score','color':'severity'},
}
for name,cfg in charts.items():
    try:
        fig=build_chart(df,{**base,**cfg},pal)
        print(name,'OK',len(fig.data))
    except Exception as exc:
        print(name,'FAIL',type(exc).__name__,exc)
