import pandas as pd, plotly.express as px, streamlit as st
def auto_chart(df: pd.DataFrame):
    if df.empty: return
    cols = df.columns
    if len(cols) >= 2:
        y = [c for c in cols[1:] if pd.api.types.is_numeric_dtype(df[c])]
        if y: st.plotly_chart(px.bar(df, x=cols[0], y=y[0]), use_container_width=True)
