import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.stats import median_abs_deviation
from io import BytesIO

st.title("RHEEDノイズ除去アプリ")

st.markdown("""
このアプリでは、RHEED強度データに対して
- Savitzky-Golay フィルタによる平滑化
- スパイクノイズの除去
を行い、グラフ表示とCSVダウンロードができます。
""")

# --- ファイルアップロード ---
uploaded_file = st.file_uploader("RHEEDデータファイル (.txt) をアップロード", type=["txt"])

if uploaded_file is not None:
    # --- ユーザー入力 ---
    total_time = st.number_input("測定にかかった総時間（秒）", value=200.0, step=1.0)
    window_length = st.number_input("Savitzky-Golayフィルタのウィンドウサイズ（奇数）", min_value=3, step=2, value=31)
    polyorder = st.number_input("Savitzky-Golayフィルタの多項式次数", min_value=1, max_value=5, value=3)
    threshold = st.number_input("スパイク除去のしきい値（MAD倍率）", min_value=1.0, max_value=10.0, value=5.0)

    data = pd.read_csv(uploaded_file, sep="\t", header=None, names=["Index", "Intensity"])
    time_axis = np.linspace(0, total_time, len(data))

    # --- Savitzky-Golay 平滑化 ---
    sg_filtered = savgol_filter(data["Intensity"], window_length=window_length, polyorder=polyorder)

    # --- スパイク除去 ---
    median = np.median(sg_filtered)
    mad = median_abs_deviation(sg_filtered)
    denoised = sg_filtered.copy()
    outliers = np.abs(sg_filtered - median) > threshold * mad
    for i in np.where(outliers)[0]:
        if 2 <= i < len(denoised) - 2:
            denoised[i] = np.mean([sg_filtered[i-2], sg_filtered[i-1], sg_filtered[i+1], sg_filtered[i+2]])

    # --- グラフ表示 ---
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(time_axis, data["Intensity"], label="Raw", alpha=0.3)
    ax.plot(time_axis, denoised, label="Denoised", linewidth=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("RHEED Intensity")
    ax.set_title("RHEED Intensity with Noise Removal")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # --- CSV出力用DataFrame ---
    result_df = pd.DataFrame({"Time (s)": time_axis, "Denoised Intensity": denoised})

    # --- CSVダウンロード ---
    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 結果CSVをダウンロード",
        data=csv,
        file_name="rheed_denoised.csv",
        mime="text/csv"
    )
