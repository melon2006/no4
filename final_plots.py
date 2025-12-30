import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MaxNLocator, StrMethodFormatter

# ==================================================
# 中文字型設定（避免圖表中文字變成亂碼）
# ==================================================
font_path = "C:/Windows/Fonts/msjh.ttc"   # Windows 常用微軟正黑體
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams["axes.unicode_minus"] = False  # 修正負號顯示問題


def run_final_plots():
    # ==================================================
    # 讀取資料
    # ==================================================
    stations = pd.read_csv("inspection_stations_clean.csv")
    air = pd.read_csv("air_quality.csv")

    # 統一縣市名稱用字（臺 → 台）
    stations["city"] = stations["city"].str.replace("臺", "台")
    air["county"] = air["county"].str.replace("臺", "台")

    # ==================================================
    # 圖一：各縣市「檢測站最多的行政區（Top 1）」
    # X 軸：縣市
    # 長條顯示：行政區名稱 + 檢測站數量
    # ==================================================

    # 計算每個「縣市 × 行政區」的檢測站數量
    district_summary = (
        stations.groupby(["city", "district"])
        .size()
        .reset_index(name="station_count")
    )

    # 每個縣市取檢測站數量最多的行政區（Top 1）
    top_district_by_city = (
        district_summary
        .sort_values(["city", "station_count"], ascending=[True, False])
        .groupby("city")
        .head(1)
        .reset_index(drop=True)
        .sort_values("station_count", ascending=False)
    )

    # 繪製長條圖
    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        top_district_by_city["city"],
        top_district_by_city["station_count"]
    )

    # 在每個長條上顯示「行政區 + 數量」
    for bar, district, count in zip(
        bars,
        top_district_by_city["district"],
        top_district_by_city["station_count"]
    ):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{district}\n{count}",
            ha="center",
            va="bottom",
            fontproperties=font_prop,
            fontsize=9
        )

    # 圖表標題與座標軸說明
    plt.title(
        "各縣市機車排氣檢測站數量最多的行政區（Top 1）",
        fontproperties=font_prop,
        fontsize=14,
        pad=15
    )

    plt.xlabel("縣市", fontproperties=font_prop)
    plt.ylabel("檢測站數量", fontproperties=font_prop)

    # X 軸縣市名稱旋轉，避免重疊
    plt.xticks(rotation=45, ha="right", fontproperties=font_prop)

    # Y 軸強制顯示整數
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()
    plt.show()

    # ==================================================
    # 圖二：空氣污染程度 × 檢測站數量（散佈圖）
    # ==================================================

    # 計算每個縣市的檢測站總數
    station_city = (
        stations.groupby("city")
        .size()
        .reset_index(name="station_count")
    )

    # 計算每個縣市的平均 PM2.5 與 AQI
    air_city = (
        air.groupby("county")[["pm2.5", "aqi"]]
        .mean()
        .reset_index()
    )

    # 合併空氣品質與檢測站資料
    merged = pd.merge(
        station_city,
        air_city,
        left_on="city",
        right_on="county",
        how="inner"
    )

    # 繪製散佈圖（X：檢測站數量，Y：PM2.5）
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(merged["station_count"], merged["pm2.5"])

    # 在每個點旁標示縣市名稱
    for _, row in merged.iterrows():
        ax.text(
            row["station_count"],
            row["pm2.5"],
            row["city"],
            fontproperties=font_prop,
            fontsize=9
        )

    # 圖表標題與座標軸說明
    ax.set_title(
        "各縣市 空汙程度 × 機車檢測站密度",
        fontproperties=font_prop,
        fontsize=14,
        pad=15
    )

    ax.set_xlabel("機車檢測站數量", fontproperties=font_prop)
    ax.set_ylabel("平均 PM2.5", fontproperties=font_prop)

    # X 軸顯示整數，Y 軸顯示一位小數
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.1f}"))

    plt.tight_layout()
    plt.show()
