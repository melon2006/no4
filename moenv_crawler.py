import pandas as pd
import xml.etree.ElementTree as ET
import os
import re


# ==================================================
# 從地址字串中擷取「縣市名稱」
# ==================================================
def extract_city(address):
    # 若地址為空，直接回傳空字串
    if not address:
        return ""

    # 統一用字（臺 → 台）
    address = address.replace("臺", "台")

    # 台灣所有縣市清單
    cities = [
        "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
        "基隆市", "新竹市", "嘉義市",
        "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
        "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣",
        "澎湖縣", "金門縣", "連江縣"
    ]

    # 判斷地址是否以縣市名稱開頭
    for city in cities:
        if address.startswith(city):
            return city

    # 若無法判斷則回傳空值
    return ""


# ==================================================
# 從地址中擷取「行政區名稱」
# ==================================================
def extract_district(address, city):
    """
    正確擷取行政區（位於 city 之後）

    範例：
    台北市中正區忠孝西路 → 中正區
    新竹縣竹北市光明路 → 竹北市
    """

    # 若地址或縣市不存在，直接回傳空字串
    if not address or not city:
        return ""

    # 統一用字（臺 → 台）
    address = address.replace("臺", "台")

    # 擷取「縣市名稱之後」的地址內容
    rest = address[len(city):]

    # 使用正則表達式擷取行政區名稱
    # 區 / 鄉 / 鎮 / 市 結尾
    match = re.search(r"^(.+?(區|鄉|鎮|市))", rest)
    if match:
        return match.group(1)

    # 無法判斷行政區時回傳空值
    return ""


# ==================================================
# 爬取並解析環境部 XML 機車排氣檢驗站資料
# ==================================================
def crawl_moenv_xml(file_path="inspection_stations.xml"):

    # 檢查檔案是否存在
    if not os.path.isfile(file_path):
        print(f"❌ 找不到檔案：{file_path}")
        return pd.DataFrame()

    # 解析 XML 檔案
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []

    # 逐筆讀取 XML 中的檢驗站資料
    for item in root:
        station_no = item.findtext("sno", default="").strip()
        station_name = item.findtext("sname", default="").strip()
        tel = item.findtext("tel", default="").strip()
        address = item.findtext("address", default="").strip()
        latitude = item.findtext("latitude", default="").strip()
        longitude = item.findtext("longitude", default="").strip()
        note = item.findtext("note", default="").strip()

        # 從地址擷取縣市與行政區
        city = extract_city(address)
        district = extract_district(address, city)

        # 將資料存成 dict
        data.append({
            "station_no": station_no,
            "station_name": station_name,
            "tel": tel,
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "note": note,
            "city": city,
            "district": district
        })

    # 轉成 DataFrame
    df = pd.DataFrame(data)

    print(f"✅ XML 解析抓到 {len(df)} 筆檢驗站資料")
    return df
