import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ==================================================
# 中文字型設定（避免中文亂碼）
# ==================================================
font_path = "C:/Windows/Fonts/msjh.ttc"
font_prop = font_manager.FontProperties(fname=font_path)

# 避免負號顯示成亂碼
plt.rcParams["axes.unicode_minus"] = False


# ==================================================
# 圖一：空汙程度 × 機車檢測站數量（散佈圖）
# ==================================================
def plot_air_vs_station():
    """
    讀取 city_air_vs_station.csv
    繪製「各縣市平均 PM2.5 與機車檢測站數量」的散佈圖
    """

    # 讀取合併後的縣市資料（空汙 + 檢測站）
    df = pd.read_csv("city_air_vs_station.csv")

    # 建立圖表
    plt.figure(figsize=(10, 7))

    # 繪製散佈圖
    plt.scatter(
        df["station_count"],   # X 軸：檢測站數量
        df["pm2.5"]             # Y 軸：平均 PM2.5
    )

    # 在每個點旁標註縣市名稱
    for _, row in df.iterrows():
        plt.text(
            row["station_count"],
            row["pm2.5"],
            row["city"],
            fontproperties=font_prop,
            fontsize=9,
            ha="right",
            va="bottom"
        )

    # 設定座標軸與標題
    plt.xlabel("機車檢測站數量", fontproperties=font_prop, fontsize=12)
    plt.ylabel("平均 PM2.5", fontproperties=font_prop, fontsize=12)
    plt.title(
        "各縣市 空汙程度 × 機車檢測站密度",
        fontproperties=font_prop,
        fontsize=15,
        pad=15
    )

    # 顯示格線，提升可讀性
    plt.grid(True, linestyle="--", alpha=0.6)

    # 自動調整版面
    plt.tight_layout()
    plt.show()


# ==================================================
# 圖二：高 PM2.5 縣市 → 行政區檢測站分布（長條圖）
# ==================================================
def plot_high_pm25_district():
    """
    針對 PM2.5 較高的縣市，
    繪製其各行政區機車檢測站數量分布圖
    """

    # 讀取高 PM2.5 縣市行政區統計資料
    df = pd.read_csv("high_pm25_city_district_station.csv")

    # 取得所有縣市清單
    cities = df["city"].unique()

    # 逐一為每個縣市畫一張圖
    for city in cities:
        city_df = df[df["city"] == city]

        plt.figure(figsize=(10, 6))

        # 繪製長條圖
        bars = plt.bar(
            city_df["district"],       # X 軸：行政區
            city_df["station_count"]   # Y 軸：檢測站數量
        )

        # 在每個長條上顯示數量（整數）
        for bar in bars:
            height = int(bar.get_height())
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height}",
                ha="center",
                va="bottom",
                fontsize=10
            )

        # 圖表標題與座標軸設定
        plt.title(
            f"{city}｜行政區機車檢測站分布（高 PM2.5 縣市）",
            fontproperties=font_prop,
            fontsize=14,
            pad=15
        )
        plt.xlabel("行政區", fontproperties=font_prop)
        plt.ylabel("檢測站數量", fontproperties=font_prop)
        plt.xticks(rotation=45, ha="right", fontproperties=font_prop)

        # 自動調整版面
        plt.tight_layout()
        plt.show()


# ==================================================
# 主程式執行區
# ==================================================
if __name__ == "__main__":
    print("📈 繪製分析圖表中...")

    # 圖一：空汙 × 檢測站數量
    plot_air_vs_station()

    # 圖二：高 PM2.5 縣市行政區分析
    plot_high_pm25_district()

    print("✅ 圖表繪製完成")
