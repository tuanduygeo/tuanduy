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

# Create sliders for user input for time and coordinates
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    year = st.slider("Chọn Năm", min_value=1900, max_value=2100, value=2025, step=1)
    month = st.slider("Chọn Tháng", min_value=1, max_value=12, value=5, step=1)
    day = st.slider("Chọn Ngày", min_value=1, max_value=31, value=11, step=1)
with col2:
    hour = st.slider("Chọn Giờ", min_value=0, max_value=23, value=13, step=1)
    minute = st.slider("Chọn Phút", min_value=0, max_value=59, value=26, step=1)
with col3:

    latitude = st.slider("Chọn Vĩ độ", min_value=-90.0, max_value=90.0, value=21.0, step=0.1)
    longitude = st.slider("Chọn Kinh độ", min_value=-180.0, max_value=180.0, value=105.8, step=0.1)
# Button to calculate
if st.button("Tính Toán"):
    selected_datetime = datetime(year, month, day, hour, minute)

    if selected_datetime.tzinfo is None:
        selected_datetime_vn = vn_tz.localize(selected_datetime)
    else:
        selected_datetime_vn = selected_datetime.astimezone(vn_tz)

    selected_utc = selected_datetime_vn.astimezone(pytz.utc)  # Convert to UTC

    jd = swe.julday(selected_utc.year, selected_utc.month, selected_utc.day,
                    selected_utc.hour + selected_utc.minute / 60 + selected_utc.second / 3600)

    st.markdown(f"**Vĩ độ**: {latitude}° **Kinh độ**: {longitude}° **Múi giờ**: GMT{timezone}")
    st.markdown(f"**Năm**: {selected_utc.year} **Tháng**: {selected_utc.month} **Ngày**: {selected_utc.day}")



rashis = ["♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer", "♌ Leo", "♍ Virgo", "♎ Libra", "♏ Scorpio",
          "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"]

nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
              "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
              "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
              "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

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
equal_house_cusps = [(asc + i * 30) % 360 for i in range(12)] + [(asc + 360) % 360]

# Tính toán các hành tinh
planet_data = []

# Tính toán ngày trước đó (1 ngày)
jd_previous = jd - 1  # Giảm 1 ngày để lấy ngày trước đó
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
    # Tính độ của hành tinh ở hiện tại và trước đó
    lon_deg = swe.calc(jd, code, swe.FLG_SIDEREAL)[0][0]
    
    # Kiểm tra nghịch hành với hai ngày
    retrograde_status = "R" if is_retrograde(code, jd, jd_previous) else ""

    # Thêm thông tin hành tinh vào danh sách planet_data
    planet_data.append({
        "Hành tinh": name,
        "Vị trí": deg_to_dms(lon_deg % 30),
        "Cung": get_rashi(lon_deg),
        "Nakshatra": get_nakshatra(lon_deg),
        "Pada": get_pada(lon_deg),
        "Nhà": get_house_for_planet(lon_deg, equal_house_cusps),
        "Tính chất": get_dignity(name, get_rashi(lon_deg)),
        "Nghịch hành": retrograde_status,
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
        "Nakshatra": ketu_nak,
        "Pada": ketu_pada,
        "Nhà": ketu_bhava,
        "Tính chất": ketu_dignity,
        "Nghịch hành": "R",  
    })


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
    
    return fig  
fig = draw_chart(planet_data)
st.pyplot(fig, use_container_width=False)

df_planets = pd.DataFrame(planet_data)
st.dataframe(df_planets, use_container_width=True)


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
st.components.v1.iframe(iframe_url, height=1200,scrolling=True)
st.caption("📍 Phát triển từ tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng.")
