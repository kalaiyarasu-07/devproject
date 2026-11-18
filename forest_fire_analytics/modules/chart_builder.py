import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def theme_layout(fig, height, title, palette, legend=True, radius='14px'):
    fig.update_layout(
        template='plotly_dark', title=title, height=height,
        paper_bgcolor='#111111', plot_bgcolor='#171717',
        font=dict(color='#F5F5F5'), legend=dict(orientation='h', y=-0.18, visible=legend),
        margin=dict(l=50,r=30,t=65,b=55), hovermode='closest',
        title_font=dict(size=18, color='#F5F5F5'),
    )
    fig.update_xaxes(gridcolor='#292929', zerolinecolor='#292929', tickfont=dict(color='#A3A3A3'))
    fig.update_yaxes(gridcolor='#292929', zerolinecolor='#292929', tickfont=dict(color='#A3A3A3'))
    return fig


def aggregate(df, x, y, method):
    if not x:
        return pd.DataFrame()
    temp=df[[x] + ([y] if y else [])].dropna()
    if not y:
        return temp.groupby(x, dropna=True).size().rename('Count').reset_index()
    if temp.empty:
        return pd.DataFrame(columns=[x,'Value'])
    ops={'Count':'count','Sum':'sum','Average':'mean','Minimum':'min','Maximum':'max'}
    out=temp.groupby(x,dropna=True)[y].agg(ops.get(method,'mean'))
    return out.rename('Value').reset_index()


def build_chart(df, config, palette):
    kind=config['kind']; height=config['height']; title=config['title']
    x=config.get('x'); y=config.get('y'); color=config.get('color')
    clean=df.copy()
    if kind == 'Bar Chart':
        data=aggregate(clean,x,y,config['agg']); yname='Value' if y else 'Count'
        if data.empty:
            return px.bar(pd.DataFrame({x:[0]}),x=x,y=x)
        fig=px.bar(data,x=x if config['orientation']=='Vertical' else yname,
                   y=yname if config['orientation']=='Vertical' else x,
                   orientation='v' if config['orientation']=='Vertical' else 'h',
                   color=color if color and color in data.columns else None,
                   color_discrete_sequence=palette)
    elif kind == 'Line Chart':
        cols=[c for c in [x,y,color] if c]
        data=clean[cols].dropna()
        if config.get('sort') and x:
            data=data.sort_values(x)
        fig=px.line(data,x=x,y=y,color=color if color else None,markers=True,color_discrete_sequence=palette)
    elif kind == 'Pie / Donut Chart':
        value_col=config.get('value')
        if value_col:
            counts=clean[[x,value_col]].dropna().groupby(x,dropna=True)[value_col].sum().reset_index()
            counts.columns=[config['label_col'],'Count']
        else:
            counts=clean[x].dropna().value_counts(dropna=True).reset_index()
            counts.columns=[config['label_col'],'Count']
        fig=px.pie(counts,names=config['label_col'],values='Count',hole=config['hole'],color_discrete_sequence=palette)
    elif kind == 'Histogram':
        fig=px.histogram(clean,x=x,nbins=config['bins'],color=color if color else None,
                         barmode='overlay',opacity=.78,color_discrete_sequence=palette)
    elif kind == 'Scatter Plot':
        size_col=config.get('size_col')
        fig=px.scatter(clean,x=x,y=y,color=color if color else None,
                       size=size_col if size_col and size_col in clean else None,
                       size_max=config['marker'],color_discrete_sequence=palette,hover_data=None)
    elif kind == 'Correlation Heatmap':
        cols=clean.select_dtypes(include=np.number).columns.tolist()
        corr=clean[cols].corr(method=config['method'].lower())
        fig=px.imshow(corr,text_auto=config['annot'],color_continuous_scale='Reds',aspect='auto',zmin=-1,zmax=1)
    elif kind == 'Area Chart':
        fig=px.area(clean,x=x,y=y,color=color if color else None,color_discrete_sequence=palette)
    elif kind == 'Box Plot':
        fig=px.box(clean,x=color or x,y=y,color=color if color else None,color_discrete_sequence=palette)
    elif kind == 'Violin Plot':
        fig=px.violin(clean,x=color or x,y=y,color=color if color else None,box=True,points='outliers',color_discrete_sequence=palette)
    elif kind == 'Treemap':
        path=[c for c in [x,color] if c]
        fig=px.treemap(clean,path=path,values=y if y else None,
                       color=y if y else None,color_continuous_scale='Reds')
    elif kind == 'Bubble Chart':
        size_col=config.get('size_col')
        fig=px.scatter(clean,x=x,y=y,
                       size=size_col if size_col and size_col in clean else None,
                       color=color if color else None,color_discrete_sequence=palette,
                       size_max=config['marker'],hover_data=None)
    elif kind == 'Density Heatmap':
        fig=px.density_heatmap(clean,x=x,y=y,nbinsx=config['bins'],nbinsy=config['bins'],color_continuous_scale='Reds')
    elif kind == 'Geographic Scatter Map':
        lat=config['lat']; lon=config['lon']
        color_col=color if color else (y if y else None)
        fig=px.scatter_map(clean,lat=lat,lon=lon,
                           color=color_col,size=y if y else None,hover_data=None,
                           color_continuous_scale='Reds')
        fig.update_layout(map_style='carto-darkmatter',margin=dict(l=0,r=0,t=65,b=0),height=height,paper_bgcolor='#111111',plot_bgcolor='#171717',title=title)
        return fig
    else:
        raise ValueError('Unsupported chart type')
    fig=theme_layout(fig,height,title,palette,config.get('legend',True))
    fig.update_layout(xaxis_title=config.get('xlabel') or x or '',yaxis_title=config.get('ylabel') or y or '')
    return fig
