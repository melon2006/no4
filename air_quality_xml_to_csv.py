import pandas as pd
import xml.etree.ElementTree as ET
import os


def xml_to_csv(xml_path="空汙.xml", output_csv="air_quality.csv"):
    """
    將空氣品質 XML 檔案轉換為 CSV 檔案

    參數說明：
    xml_path   : 空氣品質 XML 檔案路徑
    output_csv: 輸出的 CSV 檔案名稱
    """

    # ---------- 檢查 XML 檔案是否存在 ----------
    if not os.path.exists(xml_path):
        print(f"❌ 找不到檔案：{xml_path}")
        return

    # ---------- 讀取並解析 XML ----------
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 用來存放每一筆測站資料
    data = []

    # ---------- 逐一走訪 XML 節點 ----------
    # 使用 iter() 是為了避免 XML 結構層級不固定
    for item in root.iter():

        # 讀取測站名稱與縣市
        sitename = item.findtext("sitename")
        county = item.findtext("county")

        # 若非測站資料，直接跳過
        if sitename is None or county is None:
            continue

        # 將每個測站需要的欄位整理成 dict
        record = {
            "sitename": sitename.strip(),                         # 測站名稱
            "county": county.replace("臺", "台").strip(),        # 縣市（統一為「台」）
            "aqi": item.findtext("aqi"),                          # 空氣品質指標
            "pollutant": item.findtext("pollutant"),              # 主要污染物
            "status": item.findtext("status"),                    # 空氣品質狀態
            "co": item.findtext("co"),                            # 一氧化碳
            "pm2.5": item.findtext("pm2.5"),                      # PM2.5 即時值
            "pm2.5_avg": item.findtext("pm2.5_avg"),              # PM2.5 移動平均
            "nox": item.findtext("nox"),                          # 氮氧化物
        }

        # 將整理好的資料加入清單
        data.append(record)

    # ---------- 建立 DataFrame ----------
    df = pd.DataFrame(data)

    # ---------- 將數值欄位轉為數值型態 ----------
    # 若轉換失敗（例如空值或文字），會自動轉為 NaN
    numeric_cols = ["aqi", "co", "pm2.5", "pm2.5_avg", "nox"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ---------- 輸出為 CSV ----------
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"✅ 已產生 {output_csv}，共 {len(df)} 筆資料")


# ---------- 主程式進入點 ----------
if __name__ == "__main__":
    xml_to_csv()
