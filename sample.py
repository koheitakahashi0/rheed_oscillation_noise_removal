import numpy as np
import pandas as pd

# パラメータ設定
n_points = 1000
time = np.linspace(0, 100, n_points)
decay = np.exp(-time / 50)
oscillation = np.sin(2 * np.pi * time / 10)

# RHEED振動っぽい波形（振幅減衰つき正弦波）+ ノイズ
signal = 300 + 50 * decay * oscillation

# ランダムノイズを加える
noise = np.random.normal(0, 5, n_points)
signal_noisy = signal + noise

# スパイク（強制的な外れ値）を数カ所挿入
for i in np.random.choice(n_points, size=10, replace=False):
    signal_noisy[i] += np.random.choice([80, -80])

# データフレーム化
df = pd.DataFrame({
    "Index": np.arange(n_points),
    "Intensity": signal_noisy
})

# .txtとして保存（タブ区切り）
df.to_csv("sample.txt", sep="\t", index=False, header=False)

print("✅ sample.txt を出力しました")
