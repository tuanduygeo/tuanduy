import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
import math
from datetime import date, timedelta, datetime
import swisseph as swe
import pytz
import matplotlib.pyplot as plt



st.set_page_config(layout="wide")
st.title("🧭 PHONG THỦY ĐỊA LÝ – BẢN ĐỒ ĐỊA MẠCH")

st.markdown("""
### 📌 Hướng dẫn
- Danh sách 200 công trình được thường xuyên thay đổi/ 4900 công trình tâm linh được tác giả thu thập tại Việt Nam.
- Công nghệ: Ứng dụng công nghệ tự động hóa địa không gian để xác định vector các hướng địa mạch tự động tại các công trình.
- Phiên bản: V1.0 phiên bản web ưu tiên số liệu nhẹ, vector hướng mạch mang tính tham khảo- không chính xác tuyệt đối.
- Cách dùng: Các bạn chọn trang → Bấm `Xem` → Bản đồ sẽ hiển thị bên dưới.
""")

# Khởi tạo session state
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = None

# Thư mục chứa HTML
html_dir = "dulieu"
html_files = sorted([f for f in os.listdir(html_dir) if f.endswith(".html")])
df = pd.DataFrame({"Tên công trình": html_files})

# Tìm kiếm
search = st.text_input("🔍 Tìm công trình:", "").lower()
if search:
    df = df[df["Tên công trình"].str.lower().str.contains(search)]
    st.session_state.selected_idx = None  # reset khi tìm

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
        default_html = html_files[0]
        html_path = os.path.join(html_dir, default_html)
        st.subheader(f"📍 Bản đồ mặc định: {default_html}")
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            components.html(html_content, height=800, scrolling=True)

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
            components.html(html_content, height=800, scrolling=True)
else:
    st.warning("Không tìm thấy file HTML nào trong thư mục 'dulieu/'")

# --- SCHUMANN RESONANCE ---
st.markdown("""
### 2.🌐Biểu đồ cộng hưởng Schumann Trái Đất trực tuyến
Nguồn: [Tomsk, Russia – Space Observing System]
""")
st.image("https://sosrff.tsu.ru/new/shm.jpg", caption="Schumann Resonance - Live", use_container_width=True)
# --- ĐỊA TỪ TRẠM PHÚ THỌ (INTERMAGNET) ---
st.markdown("""
### 3.🧲 Dữ liệu địa từ trực tuyến""")
start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')
iframe_url = f"https://imag-data.bgs.ac.uk/GIN_V1/GINForms2?observatoryIagaCode=PHU&publicationState=Best+available&dataStartDate={start_date}&dataDuration=30&samplesPerDay=minute&submitValue=View+%2F+Download&request=DataView"
st.components.v1.iframe(iframe_url, height=1200,scrolling=True)
st.markdown("""
### 4.Chiêm tinh Ấn Độ""")

# ==== Thiết lập ====
swe.set_ephe_path("ephe")
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Tọa độ sinh
latitude = 21.0
longitude = 105.8
timezone = 7

rashis = ["♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer", "♌ Leo", "♍ Virgo", "♎ Libra", "♏ Scorpio",
          "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"]

nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
              "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
              "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
              "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
rashi_number = {
    "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
    "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
    "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
}
planets = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
}

dignities = {
    "Sun": {"vượng": "Leo", "tướng": "Aries", "tù": "Libra", "tử": "Aquarius"},
    "Moon": {"vượng": "Cancer", "tướng": "Taurus", "tù": "Scorpio", "tử": "Capricorn"},
    "Mars": {"vượng": "Aries", "tướng": "Capricorn", "tù": "Cancer", "tử": "Libra"},
    "Mercury": {"vượng": "Gemini", "tướng": "Virgo", "tù": "Pisces", "tử": "Sagittarius"},
    "Jupiter": {"vượng": "Sagittarius", "tướng": "Cancer", "tù": "Capricorn", "tử": "Gemini"},
    "Venus": {"vượng": "Taurus", "tướng": "Pisces", "tù": "Virgo", "tử": "Scorpio"},
    "Saturn": {"vượng": "Capricorn", "tướng": "Libra", "tù": "Aries", "tử": "Cancer"},
}

dasha_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}


# ==== Hàm phụ ====
def get_rashi(degree):
    return rashis[int(degree // 30)]

def get_dignity(planet, rashi):
    dign = dignities.get(planet, {})
    if rashi.split()[-1] == dign.get("vượng"):
        return "vượng"
    elif rashi.split()[-1] == dign.get("tướng"):
        return "tướng"
    elif rashi.split()[-1] == dign.get("tù"):
        return "tù"
    elif rashi.split()[-1] == dign.get("tử"):
        return "tử"
    return ""
def get_nakshatra(degree):
    return nakshatras[int(degree // (360 / 27))]


def get_pada(degree):
    deg_in_nak = degree % (360 / 27)
    return int(deg_in_nak // (13.3333 / 4)) + 1


def compute_ketu(rahu_deg):
    return (rahu_deg + 180.0) % 360.0
def is_retrograde(code):
    res, ret = swe.calc_ut(jd, code)
    return ret < 0
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

vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
now_local = datetime.now(vn_tz)  # giờ VN thực sự
now_utc = now_local - timedelta(hours=timezone)
jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                now_utc.hour + now_utc.minute / 60 + now_utc.second / 3600)

st.markdown(f"**🕒 Giờ hiện tại (VN)**: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown(f"Tọa độ:21,105.8")

houses,ascmc = swe.houses_ex(jd, latitude, longitude, b'W', swe.FLG_SIDEREAL)
asc = houses[0]
ast=ascmc[0]
asc_rashi = get_rashi(ast)
asc_pada = get_pada(ast)
asc_nak = get_nakshatra(ast)
asc_degree_dms = deg_to_dms(ast % 30)
equal_house_cusps = [(asc + i * 30) % 360 for i in range(12)] + [(asc + 360) % 360]



# Hành tinh
st.subheader("🪐 Vị trí Hành Tinh")

planet_data = []
sun_deg = swe.calc(jd, swe.SUN, swe.FLG_SIDEREAL)
planet_data.append({
    "Hành tinh": "Asc",
    "Vị trí": asc_degree_dms,
    "Cung": asc_rashi,
    "Nakshatra": asc_nak,
    "Pada": asc_pada,
    "Nhà": 1,
    "Tính chất": "",
    "Nghịch hành": ""
})
for name, code in planets.items():
    lon_deg = swe.calc(jd, code, swe.FLG_SIDEREAL)[0][0]
    rashi = get_rashi(lon_deg)
    nak = get_nakshatra(lon_deg)
    pada = get_pada(lon_deg)
    sign_deg = deg_to_dms(lon_deg % 30)
    dignity = get_dignity(name, rashi)
    bhava = get_house_for_planet(lon_deg, equal_house_cusps)
    planet_data.append({
        "Hành tinh": name,
        "Vị trí": sign_deg,
        "Cung": rashi,
        "Nakshatra": nak,
        "Pada": pada,
        "Nhà": bhava,
        "Tính chất": dignity,
        "Nghịch hành": "R" if is_retrograde(code) else "",
        
    })

ketu_deg = compute_ketu(swe.calc(jd, swe.MEAN_NODE)[0][0])
planet_data.append({
    "Hành tinh": "Ketu",
    "Vị trí": deg_to_dms(ketu_deg % 30),
    "Cung": get_rashi(ketu_deg),
    "Nakshatra": get_nakshatra(ketu_deg),
    "Pada": get_pada(ketu_deg),
    "Nhà": get_house_for_planet(ketu_deg, equal_house_cusps),
    "Tính chất": "",
    "Nghịch hành": "",
    
})

df_planets = pd.DataFrame(planet_data)
st.dataframe(df_planets, use_container_width=True)
# Hàm vẽ biểu đồ
def draw_chart(planet_data):
    fig, ax = plt.subplots(figsize=(3, 3))
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
                sign = p["Cung"].split()[-1]
                deg_str = p["Vị trí"].split("°")[0] + "°"
                labels.append(f"{name} ({sign} {deg_str})")
        names = "\n".join(labels)
        ax.text(x, y, names, ha='center', va='center', fontsize=5, color='blue')
    for house, (x, y) in house_label_coords.items():
        # Xác định cung tại nhà đó
        cusp_long = equal_house_cusps[house - 1]
        rashi = get_rashi(cusp_long).split()[-1]  # chỉ lấy tên cung
        number = rashi_number[rashi]
        ax.text(x, y, str(number), fontsize=6, color='black', weight='bold', ha='center', va='center')
    return fig  

# Hiển thị biểu đồ
st.markdown("<h3 style='text-align: left;'>BIỂU ĐỒ CHIÊM TINH</h3>", unsafe_allow_html=True)
fig = draw_chart(planet_data)
st.pyplot(fig, use_container_width=False)
# Dasha
st.subheader("🕰️ Vimshottari Dasha (120 năm)")

moon_long = swe.calc(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
nak_index = int(moon_long // (360 / 27))
first_dasha = dasha_sequence[nak_index % 9]
deg_in_nak = moon_long % (360 / 27)
balance_years = dasha_years[first_dasha] * (13.3333 - deg_in_nak) / 13.3333

start_date = now_local
rows = []
total_years = 0
index = 0
ordered_dasha = dasha_sequence[nak_index % 9:] + dasha_sequence[:nak_index % 9]
years_list = [balance_years] + [dasha_years[d] for d in ordered_dasha[1:]]

while total_years < 120:
    dasha = ordered_dasha[index % 9]
    years = years_list[index] if index < len(years_list) else dasha_years[dasha]
    if total_years + years > 120: years = 120 - total_years
    end_date = start_date + timedelta(days=years * 365.25)
    rows.append({
        "Dasha Lord": dasha,
        "Years": round(years, 2),
        "Start": start_date.strftime('%Y-%m-%d'),
        "End": end_date.strftime('%Y-%m-%d')
    })
    start_date = end_date
    total_years += years
    index += 1

st.dataframe(pd.DataFrame(rows), use_container_width=True)


st.caption("📍 Phát triển từ tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng.")

