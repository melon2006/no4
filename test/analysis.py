import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MaxNLocator, StrMethodFormatter
import seaborn as sns

# ==================================================
# 一、圖表與中文字型設定
# ==================================================
# 指定 Windows 內建的微軟正黑體，避免中文亂碼
font_path = "C:/Windows/Fonts/msjh.ttc"
font_prop = font_manager.FontProperties(fname=font_path)

# 避免負號顯示成方塊
plt.rcParams["axes.unicode_minus"] = False

# 使用 seaborn 美化圖表風格
sns.set(style="whitegrid")


# ==================================================
# 二、合法縣市清單（統一使用「台」）
# ==================================================
# 用來過濾錯誤或非台灣本島的資料
VALID_CITIES = [
    "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
    "宜蘭縣", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
    "嘉義縣", "屏東縣", "台東縣", "花蓮縣", "澎湖縣",
    "基隆市", "新竹市", "嘉義市", "金門縣", "連江縣"
]


# ==================================================
# 三、資料清洗函式
# ==================================================
def clean_data(df):
    """
    資料清洗流程：
    1. 統一縣市與行政區用字（臺 → 台）
    2. 移除 city / district 為空的資料
    3. 只保留合法縣市
    4. 移除行政區為空字串的資料
    5. 移除重複資料
    """

    # 統一用字
    df["city"] = df["city"].str.replace("臺", "台")
    df["district"] = df["district"].str.replace("臺", "台")

    # 移除空值
    df = df.dropna(subset=["city", "district"])

    # 只保留合法縣市
    df = df[df["city"].isin(VALID_CITIES)]

    # 移除行政區為空字串
    df = df[df["district"].str.strip() != ""]

    # 移除重複資料
    df = df.drop_duplicates()

    return df


# ==================================================
# 四、儲存清洗後資料（CSV + SQLite）
# ==================================================
def save_files(df):
    """
    將清洗後的資料：
    1. 存成 CSV（方便報告與 Excel 檢視）
    2. 存入 SQLite（展示資料庫應用）
    """

    # 存成 CSV
    df.to_csv("inspection_stations_clean.csv", index=False, encoding="utf-8-sig")

    # 存入 SQLite 資料庫
    conn = sqlite3.connect("inspection_stations.db")
    df.to_sql("stations", conn, if_exists="replace", index=False)
    conn.close()

    print("✅ 已儲存 CSV 與 SQLite")


# ==================================================
# 五、各縣市檢驗站數量統計（文字分析用）
# ==================================================
def analyze_city_count(df):
    """
    計算每個縣市的檢驗站數量
    回傳依數量由多到少排序的 Series
    """
    return (
        df.groupby("city")
        .size()
        .astype(int)
        .sort_values(ascending=False)
    )


# ==================================================
# 六、單一縣市 → 行政區檢驗站數量長條圖
# ==================================================
def plot_district_bar_by_city(df, city):
    """
    功能說明：
    繪製「指定縣市」各行政區的檢驗站數量長條圖
    """

    # 統一縣市用字
    city = city.replace("臺", "台")

    # 篩選該縣市資料
    data = df[df["city"] == city]

    # 若該縣市沒有資料，直接結束
    if data.empty:
        print(f"⚠️ {city} 無資料")
        return

    # 計算各行政區的檢驗站數量
    summary = (
        data.groupby("district")
        .size()
        .astype(int)
        .sort_values(ascending=False)
    )

    # 建立圖表
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(summary.index, summary.values)

    # 圖表標題與座標軸
    ax.set_title(
        f"{city} 各行政區檢驗站數量",
        fontproperties=font_prop,
        fontsize=15,
        pad=20
    )
    ax.set_xlabel("行政區", fontproperties=font_prop)
    ax.set_ylabel("檢驗站數量", fontproperties=font_prop)

    # X 軸文字旋轉避免重疊
    ax.set_xticklabels(
        summary.index,
        rotation=45,
        ha="right",
        fontproperties=font_prop
    )

    # Y 軸強制使用整數刻度
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))

    # 在每個長條上標示數量
    for bar in bars:
        height = int(bar.get_height())
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height}",
            ha="center",
            va="bottom",
            fontproperties=font_prop,
            fontsize=10
        )

    plt.tight_layout()
    plt.show()


# ==================================================
# 七、分析每個縣市「檢驗站最多的行政區（Top 1）」
# ==================================================
def analyze_top_district_by_city(df):
    """
    計算每個縣市中：
    檢驗站數量最多的行政區（Top 1）
    """

    result = []

    for city in sorted(df["city"].unique()):
        city_df = df[df["city"] == city]

        summary = (
            city_df.groupby("district")
            .size()
            .astype(int)
            .sort_values(ascending=False)
        )

        # 若該縣市有資料，取第一名行政區
        if not summary.empty:
            result.append({
                "city": city,
                "top_district": summary.index[0],
                "station_count": summary.iloc[0]
            })

    return pd.DataFrame(result)


# ==================================================
# 八、繪製「各縣市檢驗站最多行政區」總覽圖
# ==================================================
def plot_top_district_summary(top_df):
    """
    將每個縣市檢驗站最多的行政區
    用一張長條圖進行整體比較
    """

    fig, ax = plt.subplots(figsize=(14, 6))

    bars = ax.bar(
        top_df["city"],
        top_df["station_count"]
    )

    ax.set_title(
        "各縣市檢驗站數量最多之行政區",
        fontproperties=font_prop,
        fontsize=16,
        pad=20
    )

    ax.set_xlabel("縣市", fontproperties=font_prop)
    ax.set_ylabel("檢驗站數量", fontproperties=font_prop)

    ax.set_xticklabels(
        top_df["city"],
        rotation=45,
        ha="right",
        fontproperties=font_prop
    )

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # 在 bar 上顯示「行政區名稱 + 數量」
    for bar, district, count in zip(
        bars,
        top_df["top_district"],
        top_df["station_count"]
    ):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{district}\n{count}",
            ha="center",
            va="bottom",
            fontproperties=font_prop,
            fontsize=9
        )

    plt.tight_layout()
    plt.show()
