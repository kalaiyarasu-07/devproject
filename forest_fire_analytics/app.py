from pathlib import Path
import sys
import streamlit as st

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from config import PALETTES, THEMES
from modules.data_loader import read_file
from modules.data_validation import clean_dataframe
from modules.theme_manager import apply_theme
from modules.dataset_upload import render_dataset_upload
from modules.visualization import render_visualization
from modules.exploration import render_exploration

st.set_page_config(page_title='Forest Fire Analytics',page_icon='🔥',layout='wide',initial_sidebar_state='expanded')

if 'df' not in st.session_state:
    sample=ROOT/'datasets'/'forest_fire_sample_1000_rows.csv'
    st.session_state.df=clean_dataframe(read_file(sample,sample.name))
    st.session_state.dataset_name='forest_fire_sample_1000_rows.csv'
    st.session_state.uploaded=False

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">F</div><div><div class="brand-name">FOREST FIRE<br>ANALYTICS</div><div class="brand-sub">INTELLIGENCE PLATFORM</div></div></div>',unsafe_allow_html=True)
    section=st.segmented_control('Navigation',['Dataset Upload','Visualization Studio','Exploratory Analysis'],selection_mode='single',default='Dataset Upload')
    st.divider()
    st.markdown(f'<div><span class="status-dot"></span><b>Dataset active</b></div><div style="color:#A3A3A3;font-size:12px;margin-top:5px">{st.session_state.dataset_name}</div>',unsafe_allow_html=True)
    st.divider()
    with st.expander('Appearance',expanded=False):
        theme=st.selectbox('Visual feel',list(THEMES),key='theme')
        accent=st.color_picker('Primary accent','#E53935',key='accent')
        palette_name=st.selectbox('Chart palette',list(PALETTES),key='palette')
        density=st.segmented_control('Density',['Compact','Comfortable'],selection_mode='single',default='Comfortable',key='density') or 'Comfortable'
        radius=st.segmented_control('Container shape',['Rounded','Slightly squared'],selection_mode='single',default='Rounded',key='radius') or 'Rounded'

apply_theme(st.session_state.theme,st.session_state.accent,st.session_state.density,st.session_state.radius)
df=st.session_state.df
palette=PALETTES[st.session_state.palette]

if section=='Dataset Upload':
    df=render_dataset_upload(df)
elif section=='Visualization Studio':
    render_visualization(df,palette)
else:
    render_exploration(df)
