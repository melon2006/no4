from moenv_crawler import crawl_moenv_xml
import analysis
import pandas as pd
import final_plots


def main():
    print("=== 空汙 × 機車排氣檢測站 大數據分析專案 ===")

    # ==================================================
    # 1️⃣ 讀取機車排氣檢測站 XML 資料
    #    資料來源：環境部（原環保署）公開資料
    # ==================================================
    station_df = crawl_moenv_xml("機車排氣定檢站資料.xml")

    # 若資料為空，代表 XML 讀取失敗或檔案有問題
    if station_df.empty:
        print("❌ 機車檢測站資料為空，專案結束")
        return

    # 清理資料（縣市名稱統一、去除空值與重複值）
    station_df = analysis.clean_data(station_df)

    # 將整理後資料儲存為 CSV 與 SQLite
    analysis.save_files(station_df)

    # ==================================================
    # 2️⃣ 讀取空氣品質資料（PM2.5、AQI）
    # ==================================================
    try:
        air_df = pd.read_csv("air_quality.csv")
    except FileNotFoundError:
        print("❌ 找不到 air_quality.csv")
        return

    # 統一縣市名稱用字（臺 → 台），方便後續資料合併
    air_df["county"] = air_df["county"].str.replace("臺", "台")
    print("✅ 成功載入空汙資料")

    # ==================================================
    # 3️⃣ 各縣市「空汙程度 × 檢測站數量」分析
    #    目的：比較空氣污染程度與檢測站設置密度
    # ==================================================

    # 計算每個縣市的機車檢測站總數
    station_count = (
        station_df.groupby("city")
        .size()
        .reset_index(name="station_count")
    )

    # 計算各縣市平均 PM2.5 與 AQI
    air_summary = (
        air_df.groupby("county")[["pm2.5", "aqi"]]
        .mean()
        .reset_index()
    )

    # 合併「檢測站數量」與「空氣品質」資料
    merged_city_df = pd.merge(
        station_count,
        air_summary,
        left_on="city",
        right_on="county",
        how="inner"
    ).drop(columns=["county"])

    # 輸出分析結果供報告或後續使用
    merged_city_df.to_csv(
        "city_air_vs_station.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("✅ 已產生 city_air_vs_station.csv")

    # ==================================================
    # 4️⃣ 高 PM2.5 縣市的行政區檢測站分布分析
    #    目的：找出空汙嚴重縣市中，檢測站集中在哪些行政區
    # ==================================================

    # 取 PM2.5 平均值最高的前 5 名縣市
    top_pm25_cities = (
        merged_city_df
        .sort_values("pm2.5", ascending=False)
        .head(5)["city"]
        .tolist()
    )

    # 篩選出這些高空汙縣市的檢測站資料
    high_pm25_df = station_df[station_df["city"].isin(top_pm25_cities)]

    # 計算「縣市 × 行政區」的檢測站數量
    district_summary = (
        high_pm25_df
        .groupby(["city", "district"])
        .size()
        .reset_index(name="station_count")
    )

    # 儲存高 PM2.5 縣市行政區分析結果
    district_summary.to_csv(
        "high_pm25_city_district_station.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("✅ 已產生 high_pm25_city_district_station.csv")

    # ==================================================
    # 5️⃣ ⭐ 自動產生最終分析圖表（報告重點）
    # ==================================================
    print("\n📈 自動繪製最終分析圖表...")
    final_plots.run_final_plots()

    print("\n=== 專案分析完成 ===")


# Python 程式進入點
# 確保此檔案是「直接執行」時才會執行 main()
if __name__ == "__main__":
    main()
