import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
import math
from datetime import date, timedelta, datetime
import swisseph as swe
import pytz
import matplotlib.pyplot as plt
import random
import numpy as np
import requests

st.set_page_config(layout="wide")
st.markdown("""
### 1.PHONG THỦY ĐỊA LÝ – BẢN ĐỒ ĐỊA MẠCH
""")

# Khởi tạo session state
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = None
# Thư mục chứa HTML
html_dir = "dulieu"
html_files = sorted([f for f in os.listdir(html_dir) if f.endswith(".html")])
df = pd.DataFrame({"Tên công trình": html_files})

# Phân trang
per_page = 10
total_pages = math.ceil(len(df) / per_page)
page = st.number_input(f"📄 Trang (1–{total_pages}):", min_value=1, max_value=total_pages, value=1, step=1)

start_idx = (page - 1) * per_page
end_idx = start_idx + per_page
df_page = df.iloc[start_idx:end_idx]

# Hiển thị danh sách từng trang
for i, (_, row) in enumerate(df_page.iterrows()):
    idx = start_idx + i
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"🔸 **{row['Tên công trình']}**")
    with col2:
        if st.button("Xem", key=row['Tên công trình']):
            st.session_state.selected_idx = idx

# Hiển thị bản đồ
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = None

# Nếu có danh sách HTML
if html_files:
    df = pd.DataFrame({"Tên công trình": html_files})

    # Nếu chưa chọn gì → hiển thị mặc định bản đồ đầu tiên
    if st.session_state.selected_idx is None:
        default_html = random.choice(html_files)
        html_path = os.path.join(html_dir, default_html)
        st.subheader(f"📍 Bản đồ mặc định: {default_html}")
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            components.html(html_content, height=1100, scrolling=True)

    # Nếu đã chọn → hiển thị bản đồ có nút tiến lùi
    else:
        selected_html = df.iloc[st.session_state.selected_idx]['Tên công trình']

        col1, _, col3 = st.columns([1, 6, 1])
        with col1:
            if st.button("⬅️ Lùi") and st.session_state.selected_idx > 0:
                st.session_state.selected_idx -= 1
                st.rerun()
        with col3:
            if st.button("Tiến ➡️") and st.session_state.selected_idx < len(df) - 1:
                st.session_state.selected_idx += 1
                st.rerun()

        st.markdown("---")
        st.subheader(f"🗺️ Bản đồ: {selected_html}")
        html_path = os.path.join(html_dir, selected_html)
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            components.html(html_content, height=1100, scrolling=True)
else:
    st.warning("Không tìm thấy file HTML nào trong thư mục 'dulieu/'")

st.markdown("""
### 📌 Hướng dẫn
- Danh sách 200 công trình được thường xuyên thay đổi/ 4900 công trình tâm linh được tác giả thu thập tại Việt Nam.
- Công nghệ: Ứng dụng công nghệ tự động hóa địa không gian để xác định vector các hướng địa mạch tự động tại các công trình.
- Phiên bản: V1.0 phiên bản web ưu tiên số liệu nhẹ, vector hướng mạch mang tính tham khảo- không chính xác tuyệt đối.
- Cách dùng: Các bạn chọn trang → Bấm `Xem` → Bản đồ sẽ hiển thị bên dưới.
""")

st.markdown("""
### 2.Chiêm tinh Ấn Độ""")

# ==== Setup ====
swe.set_ephe_path("ephe")
swe.set_sid_mode(swe.SIDM_LAHIRI)
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
# Lấy giờ hiện tại ở múi giờ Việt Nam
now_local = datetime.now(vn_tz)

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
    st.session_state.selected_time = st.time_input("⏰ Chọn giờ", value=st.session_state.selected_time)

    # Gộp lại thành datetime hoàn chỉnh
    selected_datetime = datetime.combine(
        st.session_state.selected_date,
        st.session_state.selected_time
    )

with col2:
    # Giao diện nhập tọa độ
    latitude = st.number_input("🌐 Vĩ độ", min_value=-90.0, max_value=90.0, value=21.0, step=0.1)
    longitude = st.number_input("🌐 Kinh độ", min_value=-180.0, max_value=180.0, value=105.8, step=0.1)
# Button to calculate
if st.button("Tính Toán"):
    if selected_datetime.tzinfo is None:
        selected_datetime_vn = vn_tz.localize(selected_datetime)
    else:
        selected_datetime_vn = selected_datetime.astimezone(vn_tz)

    selected_utc = selected_datetime_vn.astimezone(pytz.utc)

    jd = swe.julday(selected_utc.year, selected_utc.month, selected_utc.day,
                    selected_utc.hour + selected_utc.minute / 60 + selected_utc.second / 3600)

    st.markdown(f"**Vĩ độ**: {latitude}° **Kinh độ**: {longitude}° ")
    st.markdown(f"**Năm**: {selected_utc.year} **Tháng**: {selected_utc.month} **Ngày**: {selected_utc.day} **Giờ**: {selected_utc.hour+7}")


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
    "Rohini": "Nhân", "Mrigashirsha": "Thiên thần", "Ardra": "Quỷ thần",
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

st.markdown("### Vị trí hành tinh")
st.dataframe(df_planets, use_container_width=True)
# === VIMSHOTTARI DASHA - GIỮ NGÀY KẾT THÚC, TÍNH NGÀY BẮT ĐẦU ===
st.markdown("### 🕉️ Bảng Đại Vận Vimshottari ")

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
st.dataframe(df_dasha, use_container_width=True)


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

if st.checkbox("👁️ Hiện toàn bộ Antardasha cho 9 Mahadasha"):
    
    st.dataframe(df_all_antar, use_container_width=True)

# Quy tắc điểm số theo nhà

benefic_house_scores = {1:3  ,2:2  ,3:-2  ,4:2  ,5:3  ,6:-2  ,7:2  ,8:-3  ,9:3  ,10:2  ,11:2  ,12:-3 }
malefic_house_scores = {1:2  ,2:2  ,3:0  ,4:1  ,5:2  ,6:0  ,7:2  ,8:-3  ,9:2  ,10:2  ,11:3  ,12:-3 }
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
            m_score += 0.7
        elif m_lord in ["Mars", "Saturn", "Rahu", "Ketu"]:
            m_score -= 0.7
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
            elif rh in [2, 4, 7, 10,11]:
                rule_bonus += 1.5
        
        m_score += rule_bonus
        # Gán nhãn mục tiêu dựa theo nhà
        purpose = ""
        if m_house in [2, 11]:
            purpose = " (tài ↑)"
        elif m_house in [1]:
            purpose = " (mệnh ↑)"
        elif m_house in [ 9]:
            purpose = " (đạo ↑)"
        elif m_house in [5]:
            purpose = " (học ↑)"
        elif m_house in [10]:
            purpose = " (danh ↑)"
        elif m_house == 7:
            purpose = " (Quan hệ ↑)"
        elif m_house == 3:
            purpose = " (Thị phi ↓)"
        elif m_house in [6,8,12]:
            purpose = " (tài,mệnh ↓)"
            
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
                # 4️⃣ Điểm từ phân loại Cát/Hung tinh
            if a_lord in ["Jupiter", "Venus", "Moon"]:
                a_score += 0.2
            elif a_lord in ["Mars", "Saturn", "Rahu", "Ketu"]:
                a_score -= 0.2
            total_score = round(0.33 *a_score +  m_score, 2)

            life_years.append(current_year)
            life_scores.append(total_score)
            year_labels.append(m_lord + purpose)
            current_year += a_years

    birth_x = round(birth_offset, 2) if birth_offset else 0
    return pd.DataFrame({"Năm": life_years, "Điểm số": life_scores, "Mahadasha": year_labels}), birth_x

# Sử dụng dữ liệu df_dasha, planet_data và jd ngày sinh
chart_df, birth_x = build_life_chart(df_dasha, planet_data, jd)

# Vẽ biểu đồ zigzag và đường cong mượt
fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(chart_df["Năm"], chart_df["Điểm số"], marker='o')
# Đường kẻ ngang tại 0 (trục điểm)
ax.axhline(y=0, color='black', linestyle='-', linewidth=2)
# Phủ vùng từ năm 80 đến 120 bằng lớp mờ
ax.axvspan(0, 70, color='grey', alpha=0.2)
# Đánh dấu thời điểm sinh
ax.axvline(x=birth_x, color='purple', linestyle=':', linewidth=2)
ax.text(birth_x, min(chart_df["Điểm số"]) - 5, "Sinh", rotation=90, color='purple', ha='center', va='bottom')
ax.set_ylim(-11, 11)

# Cài đặt chi tiết cho trục hoành
ax.set_xticks(range(int(chart_df["Năm"].min()), int(chart_df["Năm"].max()) + 1, 5))  # Interval = 5 năm
shown_mahadashas = set()

for x, y, label in zip(chart_df["Năm"], chart_df["Điểm số"], chart_df["Mahadasha"]):
    if label not in shown_mahadashas:
        ax.text(x, y + 0.5, label, fontsize=8,  ha='left', va='bottom')
        shown_mahadashas.add(label)
ax.tick_params(axis='x')  # Nếu bạn muốn nghiêng các nhãn năm cho dễ đọc
ax.set_title("Biểu đồ đại vận (tham khảo)")

ax.set_xlabel("Năm")
ax.set_ylabel("Điểm số")
ax.grid(True)
ax.legend()
st.pyplot(fig)
filtered_df = chart_df[chart_df["Năm"].between(0, 70)]
median_score = round(filtered_df["Điểm số"].median(), 2)
st.subheader(f"**Điểm(Thang từ -10 đến 10):** `{median_score}`")

st.markdown("""
### 3.🌐Biểu đồ cộng hưởng Schumann Trái Đất trực tuyến
Nguồn: [Tomsk, Russia – Space Observing System]
""")
st.image("https://sosrff.tsu.ru/new/shm.jpg", caption="Schumann Resonance - Live", use_container_width=True)

st.markdown("""
### 4.🧲 Dữ liệu địa từ trực tuyến""")
start_date = (datetime.today() - timedelta(days=15)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')
iframe_url = f"https://imag-data.bgs.ac.uk/GIN_V1/GINForms2?" \
             f"observatoryIagaCode=PHU&publicationState=Best+available" \
             f"&dataStartDate={start_date}&dataDuration=30" \
             f"&samplesPerDay=minute&submitValue=View+%2F+Download&request=DataView"
# Hiển thị trong Streamlit
st.components.v1.iframe(iframe_url, height=1000,scrolling=True)

st.markdown("""
###  Chỉ số Kp – Cảnh báo Bão Từ
""")

kp_url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"

def interpret_kp(kp):
    if kp <= 2:
        return "🟢 Rất an toàn"
    elif kp == 3:
        return "🟢 An toàn"
    elif kp == 4:
        return "🟡 Trung bình – chú ý nhẹ"
    elif kp == 5:
        return "🟠 Cảnh báo nhẹ – Bão từ cấp G1"
    elif kp == 6:
        return "🔴 Cảnh báo – Bão từ cấp G2"
    elif kp == 7:
        return "🔴 Nguy hiểm – Bão từ cấp G3"
    elif kp == 8:
        return "🔴 Rất nguy hiểm – G4"
    else:
        return "🚨 Cực kỳ nguy hiểm – G5"

try:
    kp_data = requests.get(kp_url).json()
    df_kp = pd.DataFrame(kp_data)

    if 'kp_index' in df_kp.columns and not df_kp.empty:
        df_kp['time_tag'] = pd.to_datetime(df_kp['time_tag'])
        df_kp.set_index('time_tag', inplace=True)

        latest_kp = df_kp['kp_index'].iloc[-1]
        st.metric("🌐 Kp Index (hiện tại)", f"{latest_kp}", delta=interpret_kp(latest_kp))

        # Hiển thị biểu đồ 3 ngày gần nhất
        df_kp['date'] = df_kp.index.date
        last_3_days = sorted(df_kp['date'].unique())[-3:]
        df_plot = df_kp[df_kp['date'].isin(last_3_days)]
        st.line_chart(df_plot['kp_index'])

    else:
        st.warning("⚠️ Không tìm thấy cột 'kp_index' trong dữ liệu.")
except Exception as e:
    st.error("❌ Lỗi khi tải dữ liệu Kp Index.")
    st.text(str(e))

st.markdown("""
### 5.MÔ HÌNH LẠC THƯ 3X3 VÀ BẬC CAO VÔ TẬN
""")

# Nhập bậc của ma phương
n = st.number_input("Nhập bậc lẻ n (>=3):", min_value=3, step=2, value=3)

def generate_magic_square_southeast(n):
    if n % 2 == 0:
        raise ValueError("Chỉ hỗ trợ ma phương bậc lẻ.")

    square = np.zeros((n, n), dtype=int)
    
    # Bắt đầu từ vị trí gần tâm: (tâm hàng + 1, tâm cột)
    i, j = n // 2 + 1, n // 2

    for num in range(1, n * n + 1):
        square[i % n, j % n] = num
        
        # Vị trí kế tiếp theo hướng Đông Nam
        new_i, new_j = (i + 1) % n, (j + 1) % n

        if square[new_i, new_j] != 0:
            # Nếu bị trùng, thì nhảy xuống thêm 1 hàng
            i = (i + 2) % n
        else:
            i, j = new_i, new_j

    return square
# Xác định hàng và cột trung tâm
center_index = n // 2

# Hàm tô màu các ô thuộc hàng/cột trung tâm
def highlight_center(row_or_col, axis='row'):
    return ['background-color: orange' if (i == center_index if axis == 'row' else row_or_col.name == center_index) else '' for i in range(len(row_or_col))]

# --- MAIN ---
try:
    square = generate_magic_square_southeast(n)
    df = pd.DataFrame(square)

   # 👉 Hiển thị bảng ma phương với tô màu trung tâm
    st.markdown(f"#### Ma phương {n}x{n}:") 
    styled_df = df.style.format("{:d}") \
        .apply(highlight_center, axis=1) \
        .apply(highlight_center, axis=0)
    st.dataframe(styled_df)

    # --- Kiểm tra tổng ---
    
    row_sums = df.sum(axis=1)
    col_sums = df.sum(axis=0)
    diag1 = np.trace(square)
    diag2 = np.trace(np.fliplr(square))
    magic_const = n * (n ** 2 + 1) // 2

    st.markdown(f"- Tổng chuẩn (magic constant): **{magic_const}**")
    st.markdown(f"- Tổng hàng: **{row_sums.iloc[0]}**")
    st.markdown(f"- Tổng cột: **{col_sums.iloc[0]}**")
    st.markdown(f"- Tổng đường chéo chính: {diag1}")
    st.markdown(f"- Tổng đường chéo phụ: {diag2}")

    if (
        all(row_sums == magic_const)
        and all(col_sums == magic_const)
        and diag1 == magic_const
        and diag2 == magic_const
    ):
        st.success("🎉 Đây là ma phương chuẩn hợp lệ!")
    else:
        st.warning("⚠️ Ma phương này KHÔNG hợp lệ.")

    
    # --- BẢNG MODULO 9 ---
    st.markdown("#### Bảng ma phương chia hết cho 9:")  
    df_mod9 = df % 9
    
    # Áp dụng highlight cho cả hàng và cột trung tâm
    styled_mod9 = df_mod9.style.format("{:d}") \
        .apply(highlight_center, axis=1) \
        .apply(highlight_center, axis=0)
    
    st.dataframe(styled_mod9)
    tong_cot_dau = df_mod9.iloc[:, 0].sum()
    st.markdown(f"🧾 Tổng mỗi cột: **{tong_cot_dau}**")

except Exception as e:
    st.error(f"Lỗi: {e}")

def fibonacci_mod(mod, length):
    seq = [0, 1]
    for _ in range(length - 2):
        seq.append((seq[-1] + seq[-2]) % mod)
    return seq

def plot_fibonacci_triple_circle(values_outer, values_middle, labels_inner):
    n_outer = len(values_outer)
    n_middle = len(values_middle)
    n_inner = len(labels_inner)

    theta_outer = -np.linspace(0, 2*np.pi, n_outer, endpoint=False)
    theta_middle = -np.linspace(0, 2*np.pi, n_middle, endpoint=False)
    theta_inner = -np.linspace(0, 2*np.pi, n_inner, endpoint=False)
    theta_lines = -np.linspace(0, 2*np.pi, 24, endpoint=False)

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.spines['polar'].set_visible(False)
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)
    
    # Vẽ các đường chia
    bold_indices = {2, 5, 8, 11, 14, 17, 20, 23}
    shift = np.deg2rad(7.5)
    for i, t in enumerate(theta_lines):
        linewidth = 2 if i in bold_indices else 1
        ax.plot([t + shift, t + shift], [0.75, 1.05], color='black', linewidth=linewidth)

    # Vẽ các vòng tròn
    for r in [1.05, 0.95, 0.85, 0.75]:
        circle_theta = np.linspace(0, 2 * np.pi, 1000)
        ax.plot(-circle_theta, [r] * len(circle_theta), color='black', linewidth=1)

    # Các lớp dữ liệu
    for t, num in zip(theta_outer, values_outer):
        ax.text(t, 0.9, str(num), ha='center', va='center', fontsize=8)
    for t, num in zip(theta_middle, values_middle):
        ax.text(t, 1.0, str(num), ha='center', va='center', fontsize=8, color='darkblue')
    for t, label in zip(theta_inner, labels_inner):
        ax.text(t, 0.8, label, ha='center', va='center', fontsize=8, color='darkred')

    ax.text(0, 0, '+', ha='center', va='center', fontsize=12, fontweight='bold')

    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.grid(False)
    plt.title("Fibonacci mod 9 & mod 10 + 24 phân cung (Tý, Nhâm,...)", va='bottom')

    # ✅ Hiển thị trong Streamlit
    st.pyplot(fig)

# Dữ liệu
fib_mod9 = fibonacci_mod(9, 24)
fib_mod10 = fibonacci_mod(10, 60)
labels_24 = [
    'Tý', 'Nhâm', 'Hợi', 'Càn', 'Tuất', 'Tân', 'Dậu', 'Canh',
    'Thân', 'Khôn', 'Mùi', 'Đinh', 'Ngọ', 'Bính', 'Tỵ', 'Tốn',
    'Thìn', 'Ất', 'Mão', 'Giáp', 'Dần', 'Cấn', 'Sửu', 'Quý'
]

# Streamlit layout
st.set_page_config(layout="wide")
st.title("🔄 Biểu đồ vòng tròn Fibonacci mod 9 + mod 10")
plot_fibonacci_triple_circle(fib_mod9, fib_mod10, labels_24)


st.markdown("""
### Tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng.SĐT&ZALO: 0377442597.DONATE: nguyenduytuan techcombank 19033167089018
""")
