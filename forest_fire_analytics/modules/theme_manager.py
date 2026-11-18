from pathlib import Path
import streamlit as st
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from config import THEMES


def apply_theme(theme_name, accent, density, radius):
    t = THEMES[theme_name].copy()
    t['accent'] = accent
    compact = 'padding: 0.55rem 1rem;' if density == 'Compact' else 'padding: 1rem 1.5rem;'
    radius_px = '8px' if radius == 'Slightly squared' else '14px'
    css = (ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')
    replacements = {
        '{{BG}}': t['bg'], '{{SECONDARY}}': t['secondary'], '{{CARD}}': t['card'],
        '{{SIDEBAR}}': t['sidebar'], '{{TEXT}}': t['text'], '{{MUTED}}': t['muted'],
        '{{BORDER}}': t['border'], '{{ACCENT}}': t['accent'], '{{COMPACT}}': compact,
        '{{RADIUS}}': radius_px,
    }
    for k, v in replacements.items(): css = css.replace(k, v)
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
