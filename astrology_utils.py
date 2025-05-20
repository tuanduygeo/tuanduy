import streamlit as st
import swisseph as swe
import pandas as pd
import numpy as np
import pytz
from datetime import datetime, date
import matplotlib.pyplot as plt
import re


def detect_yoga_dosha(df_planets, asc_rashi):
    """
    Phát hiện các Yoga/Dosha cơ bản từ bảng hành tinh, trả về markdown cho Streamlit.
    """
    res = []
    def dms_str_to_float(dms_str):
        match = re.match(r"(\d+)°(\d+)'(\d+)\"", dms_str)
        if not match:
            # Nếu chỉ có số độ, không có phút/giây, ví dụ "12°"
            try:
                return float(dms_str.replace("°",""))
            except:
                return 0.0
        d, m, s = map(int, match.groups())
        return d + m/60 + s/3600
    # Lấy các vị trí nhanh
    def get_planet(name):
        return df_planets[df_planets['Hành tinh'] == name].iloc[0] if name in set(df_planets['Hành tinh']) else None
    
    # 1. Pancha Mahapurusha Yoga
    mahapurusha = []
    kendra_houses = [1, 4, 7, 10]
    pmy_data = [
        ("Mars", "Ruchaka", "Mars ở nhà 1,4,7,10 và vượng/tướng"),
        ("Mercury", "Bhadra", "Mercury ở nhà 1,4,7,10 và vượng/tướng"),
        ("Jupiter", "Hamsa", "Jupiter ở nhà 1,4,7,10 và vượng/tướng"),
        ("Venus", "Malavya", "Venus ở nhà 1,4,7,10 và vượng/tướng"),
        ("Saturn", "Shasha", "Saturn ở nhà 1,4,7,10 và vượng/tướng"),
    ]
    for planet, yoga, explain in pmy_data:
        p = get_planet(planet)
        if p is not None and p['Nhà'] in kendra_houses and p['Tính chất'] in ["vượng", "tướng"]:
            mahapurusha.append(f"- **{yoga} Yoga**: {explain} (đang có hiệu lực)")
    
    # 2. Gaja-Kesari Yoga (Jupiter ở Kendra từ Moon)
    moon = get_planet("Moon")
    jupiter = get_planet("Jupiter")
    if moon is not None and jupiter is not None:
        moon_house = moon["Nhà"]
        jup_house = jupiter["Nhà"]
        if jup_house in [(moon_house + x - 1) % 12 + 1 for x in [1,4,7,10]]:
            res.append(
                "- **Gaja-Kesari Yoga**: Jupiter ở nhà Kendra từ Moon – trí tuệ, quyền lực, nổi bật."
            )
    
    # 3. Chandra-Mangal Yoga (Moon & Mars cùng Kendra tính từ nhau)
    mars = get_planet("Mars")
    if moon is not None and mars is not None:
        moon_house = moon["Nhà"]
        mars_house = mars["Nhà"]
        kendra = [(moon_house + x - 1) % 12 + 1 for x in [1,4,7,10]]
        if mars_house in kendra:
            res.append(
                "- **Chandra-Mangal Yoga**: Mars ở nhà Kendra từ Moon – khả năng kinh doanh, quyết đoán."
            )
    
    # 4. Budha-Aditya Yoga (Sun & Mercury đồng cung)
    sun = get_planet("Sun")
    mercury = get_planet("Mercury")
    if sun is not None and mercury is not None and sun["Cung"] == mercury["Cung"]:
        res.append(
            "- **Budha-Aditya Yoga**: Sun và Mercury đồng cung – thông minh, học hành xuất sắc."
        )
    
    # 5. Parivartana Yoga (Hoán đổi chủ tinh)
    # Ví dụ: Venus ở cung Mercury, Mercury ở cung Venus
    venus = get_planet("Venus")
    if venus is not None and mercury is not None:
        if venus["Cung"] == "Song Tử" and mercury["Cung"] == "Kim Ngưu":
            res.append(
                "- **Parivartana Yoga**: Venus & Mercury hoán đổi cung – kết hợp tài năng, sáng tạo."
            )
        # Có thể mở rộng thêm cho các tổ hợp khác
    
    # 6. Viparita Raja Yoga (Chủ nhà xấu trong nhà xấu khác)
    dusthana = [6, 8, 12]
    for planet in ["Mars", "Saturn", "Rahu", "Ketu"]:
        p = get_planet(planet)
        if p is not None and p["Nhà"] in dusthana and p["Chủ tinh của nhà"] and any(h in dusthana for h in p["Chủ tinh của nhà"]):
            res.append(
                f"- **Viparita Raja Yoga**: {planet} chủ Dusthana nằm trong Dusthana – chuyển hung thành cát, vượt khó."
            )
    
    # 7. Neecha Bhanga Raja Yoga (cứu giải vị trí tử)
    # Nếu một hành tinh ở vị trí "tử" (Neecha) nhưng hành tinh chủ cung đó mạnh hoặc ở Kendra
    for _, row in df_planets.iterrows():
        if row["Tính chất"] == "tử":
            lord = row["Hành tinh"]
            cung = row["Cung"]
            # Kiểm tra các cứu giải thường gặp (ví dụ: chủ tinh cung đó mạnh/vượng, hoặc đồng cung với cát tinh)
            # Ở đây chỉ cảnh báo phát hiện tử thôi, còn cứu giải chi tiết nên mở rộng
            res.append(
                f"- **Neecha Bhanga Raja (Cần kiểm tra cứu giải):** {lord} đang ở vị trí 'tử' ({cung}) – tiềm ẩn thử thách, cần kiểm tra cứu giải."
            )
    
    # 8. Kala Sarpa Dosha (tất cả hành tinh nằm giữa Rahu – Ketu)
    rahu = get_planet("Rahu")
    ketu = get_planet("Ketu")
    if rahu is not None and ketu is not None:
        rahu_deg = dms_str_to_float(rahu["Vị trí"])
        ketu_deg = dms_str_to_float(ketu["Vị trí"])
        deg = dms_str_to_float(p["Vị trí"])
        others = [p for p in df_planets.to_dict("records") if p["Hành tinh"] not in ["Rahu","Ketu"]]
        in_between = True
        for p in others:
            deg = dms_str_to_float(p["Vị trí"])
            if rahu_deg < ketu_deg:
                if not (rahu_deg < deg < ketu_deg):
                    in_between = False
                    break
            else:
                if not (deg > rahu_deg or deg < ketu_deg):
                    in_between = False
                    break
        if in_between:
            res.append(
                "- **Kala Sarpa Dosha:** Toàn bộ các hành tinh nằm giữa trục Rahu–Ketu – nghiệp lực mạnh, nhiều thử thách."
            )
    
    # 9. Kemadruma Dosha (Moon cô độc)
    left = get_planet("Moon")
    if left is not None:
        moon_cung = left["Cung"]
        same_cung = [p for p in df_planets.to_dict("records") if p["Cung"] == moon_cung and p["Hành tinh"] != "Moon"]
        if len(same_cung) == 0:
            res.append(
                "- **Kemadruma Dosha:** Moon cô độc (không có hành tinh nào cùng cung) – dễ bất ổn tâm lý, khó ổn định tình cảm."
            )
    
    # 10. Kuja Dosha (Manglik) – Mars ở 1,4,7,8,12 từ Ascendant
    if mars is not None and mars["Nhà"] in [1,4,7,8,12]:
        res.append(
            "- **Kuja Dosha (Manglik):** Mars ở nhà 1,4,7,8,12 – trắc trở hôn nhân, dễ xung đột vợ chồng."
        )
    
    # 11. Paap Kartari Yoga – một cung bị kẹp giữa hai hung tinh
    malefics = ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]
    for i, row in df_planets.iterrows():
        curr_house = row["Nhà"]
        prev_house = (curr_house - 2) % 12 + 1
        next_house = curr_house % 12 + 1
        prev_malefic = any(p for p in df_planets.to_dict("records") if p["Nhà"] == prev_house and p["Hành tinh"] in malefics)
        next_malefic = any(p for p in df_planets.to_dict("records") if p["Nhà"] == next_house and p["Hành tinh"] in malefics)
        if prev_malefic and next_malefic:
            res.append(
                f"- **Paap Kartari Yoga:** Nhà {curr_house} bị kẹp giữa hai hung tinh – ý nghĩa nhà này dễ gặp trở ngại lớn."
            )

    # Dhana Yoga: Chủ 2/5/9/11 nằm trong 2/5/9/11 hoặc đồng cung nhau
    dhana_houses = [9,2, 11]
    for p in df_planets.to_dict("records"):
        # Chủ của nhà này là gì?
        for house in dhana_houses:
            # Lấy danh sách chủ tinh của nhà này
            rulers = p.get("Chủ tinh của nhà", [])
            if rulers:
                for r in rulers:
                    # Nếu chủ là 2,5,9,11 và ở đúng các nhà tài lộc
                    if r in dhana_houses and p["Nhà"] in dhana_houses:
                        res.append("- **Dhana Yoga**: Chủ nhà tài lộc nằm ở nhà tài lộc – dễ giàu có, giữ tiền tốt.")
                        break
    houses_with_planets = set([p["Nhà"] for p in df_planets.to_dict("records")])
    if all(h in houses_with_planets for h in [1, 4, 7, 10]):
        res.append("- **Chatusagara Yoga**: Có hành tinh ở cả 4 nhà Kendra – nổi tiếng, có tiếng tăm rộng khắp.")
    good_houses = [1, 4, 5, 7, 9, 10]
    saraswati_count = 0
    for planet in ["Mercury", "Jupiter", "Venus"]:
        p = get_planet(planet)
        if p is not None and p["Nhà"] in good_houses:
            saraswati_count += 1
    if saraswati_count >= 2 and moon is not None and moon["Nhà"] in good_houses:
        res.append("- **Saraswati Yoga**: Mercury, Jupiter, Venus mạnh ở Kendra/Trikona với Moon mạnh – học vấn, nghệ thuật nổi bật.")   
    house9_ruler_list = []
    for p in df_planets.to_dict("records"):
        if 9 in p.get("Chủ tinh của nhà", []):
            house9_ruler_list.append(p)
    for p in house9_ruler_list:
        if p["Tính chất"] in ["vượng", "tướng"] and p["Nhà"] in [1, 4, 5, 7, 9, 10]:
            res.append("- **Lakshmi Yoga**: Chủ nhà 9 vượng/tướng ở Kendra/Trikona – thịnh vượng, may mắn.")
            break
    house9_ruler = None
    house10_ruler = None
    for p in df_planets.to_dict("records"):
        if 9 in p.get("Chủ tinh của nhà", []):
            house9_ruler = p
        if 10 in p.get("Chủ tinh của nhà", []):
            house10_ruler = p
    if house9_ruler and house10_ruler and house9_ruler["Cung"] == house10_ruler["Cung"]:
        res.append("- **Dharma-Karmadhipati Yoga**: Chủ nhà 9 và 10 đồng cung – đại thành công sự nghiệp/phúc lộc lớn.")
    # Tổng hợp
    if mahapurusha:
        res.append("**Pancha Mahapurusha Yoga:**\n" + "\n".join(mahapurusha))
    if not res:
        return "Không phát hiện Yoga/Dosha đặc biệt nổi bật nào, hoặc các điều kiện phức tạp hơn cần kiểm tra bằng mắt chuyên gia."
    else:
        return "### 📜 **Tổng hợp các cách cục cát/hung nổi bật:**\n" + "\n".join(res)
def astrology_block():
    

    # ==== Setup ====
    swe.set_ephe_path("ephe")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
   

    # Lấy chỉ số timezone mặc định là Việt Nam
    
    vn_tz = pytz.timezone( "Asia/Ho_Chi_Minh")
    now_local = datetime.now(vn_tz)
    decimal_default = now_local.hour + now_local.minute / 60
    
    # Chuyển đổi giờ hiện tại về UTC
    now_utc = now_local.astimezone(pytz.utc)

    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute / 60 + now_utc.second / 3600)

    st.markdown(f"**🕒 Giờ hiện tại (VN)**: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    # --- Chọn thời gian và tọa độ ---
    col1, col2 = st.columns([1, 1])

    # Khởi tạo session_state nếu chưa có (chạy 1 lần duy nhất)
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.now().date()
    if "selected_time" not in st.session_state:
        st.session_state.selected_time = datetime.now().time()

    with col1:
        # Giao diện chọn ngày và giờ
        st.session_state.selected_date = st.date_input("📅 Chọn ngày", value=st.session_state.selected_date,min_value=date(1900, 1, 1),
            max_value=date(2100, 12, 31))
        # Nhập giờ kiểu decimal (thập phân)
        if "decimal_hour" not in st.session_state:
            st.session_state.decimal_hour = decimal_default  # float, không phải 12 (int)
    
        decimal_hour = st.number_input(
        "⏰ Nhập giờ(ví dụ: 14.5 = 14h30)",
        min_value=0.0,            # float
        max_value=23.99,          # float
        value=float(st.session_state.decimal_hour), # float
        step=2.0,                # float
        format="%.2f", 
        key="decimal_hour"
    )
        
    
        # Convert về hour, minute
        hour = int(decimal_hour)
        minute = int(round((decimal_hour - hour) * 60))
        st.session_state.selected_time = datetime.now().time().replace(hour=hour, minute=minute, second=0, microsecond=0)
    
        # Gộp lại thành datetime hoàn chỉnh
        selected_datetime = datetime.combine(
            st.session_state.selected_date,
            st.session_state.selected_time
        )

    with col2:
        # Giao diện nhập tọa độ
        latitude = st.number_input("🌐 Vĩ độ", min_value=-90.0, max_value=90.0, value=21.0, step=0.1)
        longitude = st.number_input("🌐 Kinh độ", min_value=-180.0, max_value=180.0, value=105.8, step=0.1)
        tz_options = [
        ("Etc/GMT+12", "Quốc tế đổi ngày", -12),
        ("Pacific/Honolulu", "Hawaii", -10),
        ("America/Anchorage", "Alaska", -9),
        ("America/Los_Angeles", "Los Angeles", -8),
        ("America/Denver", "Denver", -7),
        ("America/Chicago", "Chicago", -6),
        ("America/New_York", "New York", -5),
        ("America/Santiago", "Santiago", -4),
        ("America/Halifax", "Halifax", -3),
        ("America/Sao_Paulo", "Sao Paulo", -3),
        ("Atlantic/Azores", "Azores", -1),
        ("Europe/London", "London", 0),
        ("Europe/Berlin", "Berlin", 1),
        ("Europe/Helsinki", "Helsinki", 2),
        ("Europe/Moscow", "Moscow", 3),
        ("Asia/Dubai", "Dubai", 4),
        ("Asia/Karachi", "Karachi", 5),
        ("Asia/Dhaka", "Dhaka", 6),
        ("Asia/Bangkok", "Bangkok/Hà Nội", 7),
        ("Asia/Ho_Chi_Minh", "TP.HCM", 7),
        ("Asia/Shanghai", "Shanghai/Bắc Kinh", 8),
        ("Asia/Tokyo", "Tokyo", 9),
        ("Australia/Sydney", "Sydney", 10),
        ("Pacific/Noumea", "Noumea", 11),
        ("Pacific/Auckland", "Auckland", 12),
    ]
        tz_labels = [f"UTC{offset:+d} - {city}" for tz, city, offset in tz_options]
        tz_values = [tz for tz, city, offset in tz_options]
        default_tz = "Asia/Ho_Chi_Minh"
        default_index = tz_values.index(default_tz) if default_tz in tz_values else tz_values.index("Asia/Bangkok")
        selected_label = st.selectbox("🌐 Chọn múi giờ đại diện", tz_labels, index=default_index)
        selected_tz = tz_values[tz_labels.index(selected_label)]
        local_tz = pytz.timezone(selected_tz)
    # Button to calculate
    if st.button("Tính Toán"):
        # Gán timezone theo local_tz đã chọn
        if selected_datetime.tzinfo is None:
            selected_datetime_local = local_tz.localize(selected_datetime)
        else:
            selected_datetime_local = selected_datetime.astimezone(local_tz)
    
        selected_utc = selected_datetime_local.astimezone(pytz.utc)
    
        jd = swe.julday(
            selected_utc.year, selected_utc.month, selected_utc.day,
            selected_utc.hour + selected_utc.minute / 60 + selected_utc.second / 3600
        )
    
        st.markdown(f"**Vĩ độ**: {latitude}° **Kinh độ**: {longitude}° ")
        st.markdown(
            f"**Năm**: {selected_utc.year} **Tháng**: {selected_utc.month} **Ngày**: {selected_utc.day} "
            f"**Giờ**: {selected_datetime_local.hour:02d}:{selected_datetime_local.minute:02d} (timezone: {selected_tz})"
        )
        

    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp",
              "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    # Danh sách Nakshatra
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
        "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
        "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    planets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
    }
    dignities = {
        "Sun": {"vượng": "Sư Tử", "tướng": "Bạch Dương", "tù": "Thiên Bình", "tử": "Bảo Bình","bạn bè": {"Cự Giải", "Song Ngư","Nhân mã", "Bọ Cạp" },"địch thủ": {"Kim Ngưu", "Song Tử","Xử Nữ","Ma Kết"  }},
        "Moon": {"vượng": "Cự Giải", "tướng": "Kim Ngưu", "tù": "Bọ Cạp", "tử": "Ma Kết","bạn bè": {"Bạch Dương","Sư Tử", "Song Ngư","Nhân mã" },"địch thủ": {"Thiên Bình", "Song Tử","Xử Nữ","Bảo Bình"  }},
        "Mars": { "vượng": {"Bạch Dương","Bọ Cạp"}, "tướng": "Ma Kết", "tù": "Cự Giải", "tử": {"Kim Ngưu","Thiên Bình"},"bạn bè": {"Sư Tử", "Song Ngư","Nhân mã" },"địch thủ": {"Song Tử","Xử Nữ","Bảo Bình"}},
        "Mercury": {"vượng": {"Song Tử","Xử Nữ" }, "tướng": "Xử Nữ", "tù": "Song Ngư", "tử": "Nhân Mã","bạn bè": {"Kim Ngưu", "Bảo Bình","Thiên Bình" },"địch thủ": {"Bạch Dương", "Bọ Cạp","Cự Giải","Sư Tử"}},
        "Jupiter": {"vượng": {"Nhân Mã","Song Ngư" }, "tướng": "Cự Giải", "tù": "Ma Kết", "tử": {"Song Tử","Xử Nữ"},"bạn bè": {"Sư Tử", "Bạch Dương","Nhân mã" },"địch thủ": {"Kim Ngưu", "Thiên Bình","Bảo Bình"}},
        "Venus": {"vượng": {"Kim Ngưu","Thiên Bình" }, "tướng": "Song Ngư", "tù": "Xử Nữ", "tử": {"Bọ Cạp","Bạch Dương"},"bạn bè": {"Ma Kết","Xử Nữ","Bảo Bình","Song Tử" },"địch thủ": {"Bạch Dương", "Bọ Cạp","Cự Giải","Sư Tử"}},
        "Saturn": {"vượng": {"Ma Kết","Bảo Bình" }, "tướng": "Thiên Bình", "tù": "Bạch Dương", "tử": {"Cự Giải","Sư Tử"},"bạn bè": {"Kim Ngưu","Song Tử","Thiên Bình" },"địch thủ": {"Nhân Mã", "Bọ Cạp","Song Ngư"}},
                  }
    dasha_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
    rashi_to_number = {
        "Bạch Dương": 1, "Kim Ngưu": 2, "Song Tử": 3, "Cự Giải": 4,
        "Sư Tử": 5, "Xử Nữ": 6, "Thiên Bình": 7, "Bọ Cạp": 8,
        "Nhân Mã": 9, "Ma Kết": 10, "Bảo Bình": 11, "Song Ngư": 12
    }
    nakshatra_to_gana = {
        "Ashwini": "Thiên thần", "Bharani": "Nhân", "Krittika": "Quỷ thần",
        "Rohini": "Nhân", "Mrigashirsha": "Thiên thần", "Ardra": "Nhân",
        "Punarvasu": "Thiên thần", "Pushya": "Thiên thần", "Ashlesha": "Quỷ thần",
        "Magha": "Quỷ thần", "Purva Phalguni": "Nhân", "Uttara Phalguni": "Nhân",
        "Hasta": "Thiên thần", "Chitra": "Quỷ thần", "Swati": "Thiên thần", "Vishakha": "Quỷ thần",
        "Anuradha": "Thiên thần", "Jyeshtha": "Quỷ thần", "Mula": "Quỷ thần",
        "Purva Ashadha": "Nhân", "Uttara Ashadha": "Nhân", "Shravana": "Thiên thần",
        "Dhanishta": "Quỷ thần", "Shatabhisha": "Quỷ thần", "Purva Bhadrapada": "Nhân",
        "Uttara Bhadrapada": "Nhân", "Revati": "Thiên thần"
    }
    # ==== Hàm phụ ====
    def get_rashi(degree):
        return rashis[int(degree // 30)]
    def get_gana(nakshatra):
        return nakshatra_to_gana.get(nakshatra, "")
    def get_dignity(planet, rashi):
        dign = dignities.get(planet, {})
        if rashi == dign.get("vượng"):
            return "vượng"
        elif rashi == dign.get("tướng"):
            return "tướng"
        elif rashi == dign.get("tù"):
            return "tù"
        elif rashi == dign.get("tử"):
            return "tử"
         # Check for "bạn bè" and "địch thủ" (they are sets)
        elif rashi in dign.get("bạn bè", set()):
            return "bạn bè"
        elif rashi in dign.get("địch thủ", set()):
            return "địch thủ"
        return ""
    def get_nakshatra(degree):
        return nakshatras[int(degree // (360 / 27))]

    def is_combust(planet_name, planet_lon, sun_lon, retrograde=False):
        if planet_name in ["Sun", "Rahu", "Ketu"]:
            return False
        diff = abs((planet_lon - sun_lon + 180) % 360 - 180)
        
        combust_limits = {
            "Moon": 8,
            "Mercury": 4 ,
            "Venus": 6,
            "Mars": 8,
            "Jupiter": 8,
            "Saturn": 8
        }
        limit = combust_limits.get(planet_name, 0)
        return diff < limit
    def get_pada(degree):
        deg_in_nak = degree % (360 / 27)
        return int(deg_in_nak // (13.3333 / 4)) + 1


    def compute_ketu(rahu_deg):
        return (rahu_deg + 180.0) % 360.0

    def deg_to_dms(degree):
        d = int(degree)
        m = int((degree - d) * 60)
        s = int(((degree - d) * 60 - m) * 60)
        return f"{d}°{m:02d}'{s:02d}\""


    def get_house_for_planet(lon, house_cusps):
        for i in range(12):
            start = house_cusps[i]
            end = house_cusps[i + 1]
            if end < start: end += 360
            lon_mod = lon if lon >= start else lon + 360
            if start <= lon_mod < end:
                return i + 1
        return None
    def is_retrograde(code, jd_current, jd_previous):
        # Tính toán vị trí hành tinh tại thời điểm hiện tại
        res_current, _ = swe.calc_ut(jd_current, code)
        lon_deg_current = res_current[0]
        
        # Tính toán vị trí hành tinh tại thời điểm trước đó
        res_previous, _ = swe.calc_ut(jd_previous, code)
        lon_deg_previous = res_previous[0]
        
        # Kiểm tra xem vị trí có thay đổi hướng không
        # Nếu sự thay đổi giữa hai ngày có dấu hiệu quay ngược, hành tinh đang nghịch hành
        if lon_deg_current < lon_deg_previous:
            return True
        return False


    houses,ascmc = swe.houses_ex(jd, latitude, longitude, b'W', swe.FLG_SIDEREAL)
    asc = houses[0]
    ast=ascmc[0]
    asc_rashi = get_rashi(ast)
    asc_pada = get_pada(ast)
    asc_nak = get_nakshatra(ast)
    asc_degree_dms = deg_to_dms(ast % 30)
    asc_gana = get_gana(asc_nak)
    equal_house_cusps = [(asc + i * 30) % 360 for i in range(12)] + [(asc + 360) % 360]
    # Tính toán các hành tinh
    planet_data = []


    # Tính toán ngày trước đó (1 ngày)
    jd_previous = jd - 1  # Giảm 1 ngày để lấy ngày trước đó

    planet_data.append({
        "Hành tinh": "Asc",
        "Vị trí": asc_degree_dms,
        "Cung": asc_rashi,
        "Tú": asc_nak,
        "Pada": asc_pada,
        "Gana": asc_gana,
        "Nhà": 1,
        "Tính chất": "",
        "Nghịch hành": ""
    })

    for name, code in planets.items():
        # Tính độ của hành tinh ở hiện tại và trước đó
        lon_deg = swe.calc(jd, code, swe.FLG_SIDEREAL)[0][0]
        sun_lon = swe.calc(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
        # Kiểm tra nghịch hành với hai ngày
        retrograde_status = "R" if is_retrograde(code, jd, jd_previous) else ""
        is_c = is_combust(name, lon_deg, sun_lon, retrograde=(retrograde_status == "R"))
        status = retrograde_status
        if is_c:
            status += " C"
        # Thêm thông tin hành tinh vào danh sách planet_data
        planet_data.append({
            "Hành tinh": name,
            "Vị trí": deg_to_dms(lon_deg % 30),
            "Cung": get_rashi(lon_deg),
            "Tú": get_nakshatra(lon_deg),
            "Pada": get_pada(lon_deg),
            "Gana": get_gana(get_nakshatra(lon_deg)),
            "Nhà": get_house_for_planet(lon_deg, equal_house_cusps),
            "Tính chất": get_dignity(name, get_rashi(lon_deg)),
            "Nghịch hành": status,
        })
    # Tìm Rahu trong planet_data
    rahu_deg = None
    for planet in planet_data:
        if planet["Hành tinh"] == "Rahu":
            rahu_deg = swe.calc(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)[0][0]
            break

    # Nếu Rahu có giá trị, tính toán Ketu
    if rahu_deg is not None:
        ketu_deg = (rahu_deg + 180) % 360  # Ketu là đối diện của Rahu

        # Tính toán các thông số của Ketu
        ketu_rashi = get_rashi(ketu_deg)
        ketu_nak = get_nakshatra(ketu_deg)
        ketu_pada = get_pada(ketu_deg)
        ketu_sign_deg = deg_to_dms(ketu_deg % 30)
        ketu_dignity = ""  # Ketu không có "tính chất" (vượng, tướng, tù, tử)
        ketu_bhava = get_house_for_planet(ketu_deg, equal_house_cusps)

        # Thêm Ketu vào planet_data
        planet_data.append({
            "Hành tinh": "Ketu",
            "Vị trí": ketu_sign_deg,
            "Cung": ketu_rashi,
            "Tú": ketu_nak,
            "Pada": ketu_pada,
            "Gana": get_gana(ketu_nak),
            "Nhà": ketu_bhava,
            "Tính chất": ketu_dignity,
            "Nghịch hành": "R",  
        })


    # Hàm vẽ biểu đồ
    def draw_chart(planet_data):
        fig, ax = plt.subplots(figsize=(4,4))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")

        # Khung ngoài
        ax.plot([0, 100, 100, 0, 0], [0, 0, 100, 100, 0], 'k', linewidth=2)

        # Các đường chéo
        ax.plot([0, 100], [0, 100], 'k', linewidth=1)
        ax.plot([0, 100], [100, 0], 'k', linewidth=1)

        # Đường từ giữa cạnh đến trung tâm
        ax.plot([0, 50], [50, 100], 'k', linewidth=1)
        ax.plot([50, 100], [100, 50], 'k', linewidth=1)
        ax.plot([100, 50], [50, 0], 'k', linewidth=1)
        ax.plot([50, 0], [0, 50], 'k', linewidth=1)

        # Hình thoi trung tâm
        ax.plot([0, 50, 100, 50, 0], [50, 100, 50, 0, 50], 'k', linewidth=1)
        # Tọa độ tương đối cho từng nhà (x, y)
        house_coords = {
            1: (50, 80),
            2: (25, 95),
            3: (10, 80),
            4: (25, 45),
            5: (15, 25),
            6: (25, 5),
            7: (50, 20),
            8: (75, 5),
            9: (95, 25),
            10: (75, 45),
            11: (95, 80),
            12: (75, 95),
        }   
       
        # Gom nhóm các hành tinh theo nhà
        house_planets = {i: [] for i in range(1, 13)}
        for planet in planet_data:
            house = planet["Nhà"]
            name = planet["Hành tinh"]
            if house:
                house_planets[house].append(name)

        # Vẽ tên hành tinh tại vị trí từng nhà
        for house, (x, y) in house_coords.items():
            labels = []
            for p in planet_data:
                if p["Nhà"] == house:
                    name = p["Hành tinh"]
                    sign = p["Cung"]
                    deg_str = p["Vị trí"].split("°")[0] + "°"
                    # Kiểm tra và gán mũi tên tương ứng
                    dignity = get_dignity(name, sign)
                    if dignity == "vượng" or dignity == "tướng" or dignity == "bạn bè":
                        arrow = " ↑"
                    elif dignity == "tù" or dignity == "tử" or dignity == "địch thủ":
                        arrow = " ↓"
                    else:
                        arrow = ""
                    
                    labels.append(f"{name} ({sign} {deg_str}){arrow}")
            names = "\n".join(labels)
            ax.text(x, y, names, ha='center', va='center', fontsize=5, color='blue')
        for i, (x, y) in house_coords.items():
            cusp_degree = equal_house_cusps[i - 1]
            rashi_name = get_rashi(cusp_degree)
            rashi_number = rashi_to_number[rashi_name]
            ax.text(x-2, y + 3, str(rashi_number), fontsize=5, color='red',weight='bold')
        return fig  
        
    fig = draw_chart(planet_data)
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)
    df_planets = pd.DataFrame(planet_data)



    rashi_rulers = {
        "Bạch Dương": "Mars", "Kim Ngưu": "Venus", "Song Tử": "Mercury", "Cự Giải": "Moon",
        "Sư Tử": "Sun", "Xử Nữ": "Mercury", "Thiên Bình": "Venus", "Bọ Cạp": "Mars",
        "Nhân Mã": "Jupiter", "Ma Kết": "Saturn", "Bảo Bình": "Saturn", "Song Ngư": "Jupiter"
    }

    house_rulers = {
        i + 1: rashi_rulers[get_rashi(cusp)]
        for i, cusp in enumerate(equal_house_cusps[:12])
    }

    planet_to_ruled_houses = {}
    for house, ruler in house_rulers.items():
        planet_to_ruled_houses.setdefault(ruler, []).append(house)

    df_planets["Chủ tinh của nhà"] = df_planets["Hành tinh"].apply(
        lambda p: planet_to_ruled_houses.get(p, [])
    )
    # === Định nghĩa quy tắc chiếu Vedic ===
    vedic_aspects = {
        "Saturn": [3, 7, 10],
        "Mars": [4, 7, 8],
        "Jupiter": [5, 7, 9],
        "Default": [7]
    }

    # Bản đồ hành tinh -> nhà
    planet_house_map = {p["Hành tinh"]: p["Nhà"] for p in planet_data}

    # Hàm tính hành tinh nào bị chiếu
    def get_aspected_planets(planet_name, current_house):
        if current_house is None:
            return ""
        
        # Lấy danh sách khoảng cách các nhà bị chiếu
        aspect_offsets = vedic_aspects.get(planet_name, vedic_aspects["Default"])
        
        # Tính các nhà bị chiếu
        aspected_houses = [((current_house + offset - 2) % 12) + 1 for offset in aspect_offsets]
        
        # Tìm hành tinh nằm trong các nhà bị chiếu
        result = []
        for other_planet, house in planet_house_map.items():
            if other_planet != planet_name and house in aspected_houses:
                result.append(f"{other_planet} ( {house})")
        return ", ".join(result)

    # Thêm cột vào bảng
    df_planets["Chiếu hành tinh"] = df_planets.apply(
        lambda row: get_aspected_planets(row["Hành tinh"], row["Nhà"]), axis=1
    )

    
    # Bảng ánh xạ Nakshatra → Dasha Lord
    nakshatra_to_dasha_lord = {
        "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
        "Rohini": "Moon", "Mrigashirsha": "Mars", "Ardra": "Rahu",
        "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
        "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
        "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
        "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
        "Mula": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
        "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
        "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
    }

    # Dasha sequence và số năm
    dasha_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
                   "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

    # Tính vị trí Mặt Trăng
    moon_longitude = swe.calc(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    # Xác định nakshatra
    nakshatra_index = int((moon_longitude % 360) / 13.3333333333)
    nakshatra_fraction = ((moon_longitude % 360) % 13.3333333333) / 13.3333333333
    nakshatra_name = nakshatras[nakshatra_index]
    dasha_lord = nakshatra_to_dasha_lord[nakshatra_name]

    # Số năm còn lại trong Mahadasha hiện tại
    full_years = dasha_years[dasha_lord]
    remain_years = (1 - nakshatra_fraction) * full_years

    # ✅ Giữ ngày kết thúc là hiện tại, tính ngược ra ngày bắt đầu
    end_jd = jd + remain_years * 365.25
    start_jd = end_jd - full_years * 365.25
    curr_jd = start_jd

    # Tạo bảng Mahadasha
    dasha_list = []
    idx = dasha_sequence.index(dasha_lord)
    for i in range(9):
        lord = dasha_sequence[(idx + i) % 9]
        duration = dasha_years[lord]

        start = swe.revjul(curr_jd)
        end_jd = curr_jd + duration * 365.25
        end = swe.revjul(end_jd)

        dasha_list.append({
            "Dasha": lord,
            "Bắt đầu": f"{int(start[2]):02d}-{int(start[1]):02d}-{int(start[0])}",
            "Kết thúc": f"{int(end[2]):02d}-{int(end[1]):02d}-{int(end[0])}",
            "Số năm": round(duration, 2)
        })

        curr_jd = end_jd

    # Hiển thị bảng Mahadasha
    df_dasha = pd.DataFrame(dasha_list)
    


    # Hàm tính Antardasha chuẩn
    def compute_antardasha(mahadasha_lord, start_jd, duration_years):
        antardashas = []
        start_index = dasha_sequence.index(mahadasha_lord)
        jd_pointer = start_jd

        for i in range(9):
            sub_lord = dasha_sequence[(start_index + i) % 9]
            weight = dasha_years[sub_lord] / 120
            sub_duration = duration_years * weight
            end_jd = jd_pointer + sub_duration * 365.25

            start = swe.revjul(jd_pointer)
            end = swe.revjul(end_jd)

            antardashas.append({
                "Antardasha": f"{mahadasha_lord}/{sub_lord}",
                "Bắt đầu": f"{int(start[2]):02d}-{int(start[1]):02d}-{int(start[0])}",
                "Kết thúc": f"{int(end[2]):02d}-{int(end[1]):02d}-{int(end[0])}",
                "Số năm": round(sub_duration, 2)
            })
            jd_pointer = end_jd

        return pd.DataFrame(antardashas)

    all_antardasha = []
    for _, row in df_dasha.iterrows():
        m_lord = row["Dasha"]
        m_start = datetime.strptime(row["Bắt đầu"], "%d-%m-%Y")
        m_start_jd = swe.julday(m_start.year, m_start.month, m_start.day)
        m_years = row["Số năm"]
        all_antardasha += compute_antardasha(m_lord, m_start_jd, m_years).to_dict("records")

    df_all_antar = pd.DataFrame(all_antardasha)
    

    # Quy tắc điểm số theo nhà

    benefic_house_scores = {1:3  ,2:2.5  ,3:-2  ,4:2  ,5:2.5  ,6:-2  ,7:2  ,8:-3  ,9:3  ,10:2  ,11:2.5  ,12:-3 }
    malefic_house_scores = {1:2  ,2:1.5  ,3:0  ,4:1  ,5:2  ,6:0  ,7:2  ,8:-3  ,9:2  ,10:2  ,11:3  ,12:-3 }
    benefics = {"Jupiter", "Venus", "Moon","Mercury"}
    malefics = {"Mars", "Saturn", "Rahu", "Ketu","Sun"}
    def get_house_score(house, planet):
        if planet in benefics:
            return benefic_house_scores.get(house, 0)
        elif planet in malefics:
            return malefic_house_scores.get(house, 0)
        else:
            return 0  # Trung lập hoặc không rõ
    # Tính dữ liệu vẽ biểu đồ
    def build_life_chart(df_dasha, planet_data, birth_jd):
        life_years = []
        life_scores = []
        year_labels = []
        current_year = 0
        birth_offset = None

        for _, m_row in df_dasha.iterrows():
            m_lord = m_row["Dasha"]
            m_start = datetime.strptime(m_row["Bắt đầu"], "%d-%m-%Y")
            m_start_jd = swe.julday(m_start.year, m_start.month, m_start.day)
            m_duration = m_row["Số năm"]

            if birth_offset is None and birth_jd >= m_start_jd:
                birth_offset = (birth_jd - m_start_jd) / 365.25

            # Điểm từ vị trí hiện tại của hành tinh
            m_house = next((p["Nhà"] for p in planet_data if p["Hành tinh"] == m_lord), 0)
            m_score = get_house_score(m_house, m_lord)
            m_dignity = next((p["Tính chất"] for p in planet_data if p["Hành tinh"] == m_lord), "")
            if m_dignity in ["vượng", "tướng"]:
                m_score += 1
            elif m_dignity == "bạn bè":
                m_score += 0.5
            elif m_dignity == "địch thủ":
                m_score -= 0.5
            elif m_dignity in ["tù", "tử"]:
                m_score -= 1
            # ✅ Thêm điểm theo tính chất "Cát – Hung" của hành tinh
            if m_lord in ["Jupiter", "Venus", "Moon"]:
                m_score += 0.5
            elif m_lord in ["Mars", "Saturn", "Rahu", "Ketu"]:
                m_score -= 0.5
            m_status = next((p["Nghịch hành"] for p in planet_data if p["Hành tinh"] == m_lord), "")
            if "R" in m_status and "C" in m_status:
                m_score -= 0.5
            # ✅ Thêm điểm dựa trên các nhà hành tinh đó làm chủ
            ruled_houses = planet_to_ruled_houses.get(m_lord, [])
            rule_bonus = 0
            for rh in ruled_houses:
                if rh in [6, 8, 12]:
                    rule_bonus -= 3.5
                elif rh in [1, 5, 9]:
                    rule_bonus += 3.5
                elif rh in [ 4, 7, 10]:
                    rule_bonus += 1.5
                elif rh in [ 2,11]:
                    rule_bonus += 2.5
            m_score += rule_bonus
            m_gana = next((p["Gana"] for p in planet_data if p["Hành tinh"] == m_lord), "")
            if m_gana == "Thiên thần":
                m_score += 1
            elif m_gana == "Quỷ thần":
                m_score -= 1
            # Gán nhãn mục tiêu dựa theo nhà
            purpose = ""
            if m_house in [2]:
                purpose = " (tài ↑)"
            elif m_house in [1]:
                purpose = " (bản mệnh ↑)"
            elif m_house in [ 9]:
                purpose = " (đạo ↑)"
            elif m_house in [5]:
                purpose = " (học ↑)"
            elif m_house in [10]:
                purpose = " (danh ↑)"
            elif m_house in [4]:
                purpose = " (An ↑)"
            elif m_house == 7:
                purpose = " (Quan hệ ↑)"
            elif m_house == 3:
                purpose = " (Thị phi ↓)"
            elif m_house in [8,12]:
                purpose = " (họa, thiệt ↓)"
            elif m_house in [6]:
                purpose = " (bệnh ↓)"
            elif m_house in [11]:
                purpose = " (Thuận ↑)"
            antars = compute_antardasha(m_lord, m_start_jd, m_duration)
            for _, antar in antars.iterrows():
                a_lord = antar["Antardasha"].split("/")[-1]
                a_years = antar["Số năm"]
                a_house = next((p["Nhà"] for p in planet_data if p["Hành tinh"] == a_lord), 0)
                a_score = get_house_score(a_house, a_lord) 
                # ✅ Thêm điểm từ nhà mà antardasha làm chủ
                ruled_houses_a = planet_to_ruled_houses.get(a_lord, [])
                rule_bonus_a = 0
                for rh in ruled_houses_a:
                    if rh in [6, 8, 12]:
                        rule_bonus_a -= 1
                    elif rh in [1, 5, 9]:
                        rule_bonus_a += 1
                    elif rh in [2, 4, 7, 10,11]:
                        rule_bonus_a += 0.5
                a_score += rule_bonus_a
                
                a_status = next((p["Nghịch hành"] for p in planet_data if p["Hành tinh"] == a_lord), "")
                if "R" in a_status and "C" in a_status:
                    a_score -= 0.2
                # ✅ Thêm điểm theo dignity (tính chất) của Antardasha lord
                a_dignity = next((p["Tính chất"] for p in planet_data if p["Hành tinh"] == a_lord), "")
                if a_dignity in ["vượng", "tướng"]:
                    a_score += 0.5
                elif a_dignity == "bạn bè":
                    a_score += 0.2
                elif a_dignity == "địch thủ":
                    a_score -= 0.2
                elif a_dignity in ["tù", "tử"]:
                    a_score -= 0.5
                a_gana = next((p["Gana"] for p in planet_data if p["Hành tinh"] == a_lord), "")
                if a_gana == "Thiên thần":
                    a_score += 0.5
                elif a_gana == "Quỷ thần":
                    a_score -= 0.5    
                # 4️⃣ Điểm từ phân loại Cát/Hung tinh
                if a_lord in ["Jupiter", "Venus", "Moon"]:
                    a_score += 0.2
                elif a_lord in ["Mars", "Saturn", "Rahu", "Ketu"]:
                    a_score -= 0.2
                total_score = round(0.5 *a_score +  m_score, 2)

                life_years.append(current_year)
                life_scores.append(total_score)
                year_labels.append(m_lord + purpose)
                current_year += a_years

        birth_x = round(birth_offset, 2) if birth_offset else 0
        return pd.DataFrame({"Năm": life_years, "Điểm số": life_scores, "Mahadasha": year_labels}), birth_x

    # Sử dụng dữ liệu df_dasha, planet_data và jd ngày sinh
    chart_df, birth_x = build_life_chart(df_dasha, planet_data, jd)

    # Vẽ biểu đồ zigzag và đường cong mượt
    chart_df["Năm_mới"] = chart_df["Năm"] - birth_x

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(chart_df["Năm_mới"], chart_df["Điểm số"], marker='o')
    ax.hlines(y=0, xmin=0, xmax=115, color='black', linestyle='-', linewidth=2)

    ax.axvspan(0, 70, color='grey', alpha=0.2)  
    ax.spines['left'].set_position('zero')  # Đặt OY đúng tại x=0 mới
    
    ax.set_ylim(-12, 12)

    # Cài đặt chi tiết cho trục hoành
    ax.set_xticks(range(int(chart_df["Năm"].min()), int(chart_df["Năm"].max()) + 1, 5))  # Interval = 5 năm
    shown_mahadashas = set()

    for x, y, label in zip(chart_df["Năm"], chart_df["Điểm số"], chart_df["Mahadasha"]):
        if label not in shown_mahadashas:
            ax.text(x, y + 0.5, label, fontsize=8,  ha='left', va='bottom')
            shown_mahadashas.add(label)
    ax.tick_params(axis='x')  # Nếu bạn muốn nghiêng các nhãn năm cho dễ đọc
    filtered_df = chart_df[chart_df["Năm_mới"].between(0, 70)]
    median_score = round(filtered_df["Điểm số"].median(), 2)
    ax.set_title(f"Biểu đồ đại vận/ Điểm (Thang từ -10 đến 10): {median_score}")

    ax.set_xlabel("Năm")
    ax.set_ylabel("Điểm số")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown("### Vị trí hành tinh")
    st.dataframe(df_planets, use_container_width=False)
    st.markdown(detect_yoga_dosha(df_planets, asc_rashi), unsafe_allow_html=True)
    # === VIMSHOTTARI DASHA - GIỮ NGÀY KẾT THÚC, TÍNH NGÀY BẮT ĐẦU ===
    st.markdown("### 🕉️ Bảng Đại Vận Vimshottari ")

    st.dataframe(df_dasha, use_container_width=False)
    if st.checkbox("👁️ Hiện toàn bộ Antardasha cho 9 Mahadasha"):
        
        st.dataframe(df_all_antar, use_container_width=False)

    
    st.markdown("""#### 📌 Hướng dẫn
    - Biểu đồ đại vận vimshottari là cách miêu tả hành trình của đời người trong thời mạt pháp, diễn ra trong 120 năm, 
      được tính từ trước thời điểm người đó sinh và cả sau khi người đó chết. 
    - Các đại vận được hiển thị bằng tên các hành tinh; trong đó quan trọng nhất được tô màu xám hiển thị khoảng 70 năm đời người. 
    - Thang điểm từ -10 đến 10, tức điểm 0 được tô đậm là điểm trung bình, điểm >0 được coi là chấp nhận được.
    - Biểu đồ được tính từ các trọng số quan trọng như chủ tinh, vị trí hành tinh, vượng tướng tù tử, đốt cháy hay nghịch hành, v.v.
    """)
    pass

# Thêm các hàm phụ trợ cho Chiêm tinh ở dưới (nếu cần)
