import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import savgol_filter
from scipy.stats import median_abs_deviation
from io import BytesIO

st.set_page_config(layout="wide")
st.title("RHEEDノイズ除去アプリ")

st.markdown("""
このアプリでは、RHEED強度データ（複数ファイル）に対して
- Savitzky-Golay フィルタによる平滑化
- スパイクノイズの除去
を行い、グラフ表示（Plotlyで拡大可能）とCSVダウンロードができます。
""")

# --- ファイルアップロード ---
uploaded_files = st.file_uploader("RHEEDデータファイル (.txt, 複数可) をアップロード", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    total_time = st.number_input("測定にかかった総時間（秒）", value=200.0, step=1.0)
    window_length = st.number_input("Savitzky-Golayフィルタのウィンドウサイズ（奇数）", min_value=3, step=2, value=31)
    polyorder = st.number_input("Savitzky-Golayフィルタの多項式次数", min_value=1, max_value=5, value=3)
    threshold = st.number_input("スパイク除去のしきい値（MAD倍率）", min_value=1.0, max_value=10.0, value=5.0)

    for uploaded_file in uploaded_files:
        st.markdown(f"### ファイル: `{uploaded_file.name}`")
        data = pd.read_csv(uploaded_file, sep="\t", header=None, names=["Index", "Intensity"])
        time_axis = np.linspace(0, total_time, len(data))

        # Savitzky-Golay 平滑化
        sg_filtered = savgol_filter(data["Intensity"], window_length=window_length, polyorder=polyorder)

        # スパイク除去
        median = np.median(sg_filtered)
        mad = median_abs_deviation(sg_filtered)
        denoised = sg_filtered.copy()
        outliers = np.abs(sg_filtered - median) > threshold * mad
        for i in np.where(outliers)[0]:
            if 2 <= i < len(denoised) - 2:
                denoised[i] = np.mean([sg_filtered[i-2], sg_filtered[i-1], sg_filtered[i+1], sg_filtered[i+2]])

        # Plotlyでインタラクティブ表示
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_axis, y=data["Intensity"], mode='lines', name="Raw", line=dict(color='gray', width=1)))
        fig.add_trace(go.Scatter(x=time_axis, y=denoised, mode='lines', name="Denoised", line=dict(color='red', width=2)))
        fig.update_layout(title="RHEED Intensity with Noise Removal", xaxis_title="Time (s)", yaxis_title="Intensity", hovermode="x")
        st.plotly_chart(fig, use_container_width=True)

        # 結果CSV出力
        result_df = pd.DataFrame({"Time (s)": time_axis, "Denoised Intensity": denoised})
        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 `{uploaded_file.name}` の結果CSVをダウンロード",
            data=csv,
            file_name=f"{uploaded_file.name.replace('.txt','')}_denoised.csv",
            mime="text/csv"
        )
