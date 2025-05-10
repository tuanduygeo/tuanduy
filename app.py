import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from datetime import date, timedelta

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
if st.session_state.selected_idx is not None:
    selected_html = df.iloc[st.session_state.selected_idx]['Tên công trình']

    # Nút tiến/lùi phía trên bản đồ
    col1, _, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⬅️ Lùi"):
            if st.session_state.selected_idx > 0:
                st.session_state.selected_idx -= 1
                st.rerun()
    with col3:
        if st.button("Tiến ➡️"):
            if st.session_state.selected_idx < len(df) - 1:
                st.session_state.selected_idx += 1
                st.rerun()
    
    st.markdown("---")
    st.subheader(f"🗺️ Bản đồ: {selected_html}")
    html_path = os.path.join(html_dir, selected_html)
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        components.html(html_content, height=800, scrolling=True)
# --- GIAO DIỆN LÁ SỐ CHIÊM TINH ---
st.markdown("""
---
### 🔮 LÁ SỐ CHIÊM TINH VỆ ĐÀ
""")

ten = st.text_input("🧑 Họ và tên")
nam = st.number_input("Năm sinh", value=2000, step=1)
thang = st.number_input("Tháng sinh", value=1, min_value=1, max_value=12)
ngay = st.number_input("Ngày sinh", value=1, min_value=1, max_value=31)
gio = st.number_input("Giờ sinh (0-23)", value=12, min_value=0, max_value=23)
phut = st.number_input("Phút sinh (0-59)", value=0, min_value=0, max_value=59)
timezone = st.number_input("Timezone (VN = 7)", value=7)
lat = st.number_input("Vĩ độ (lat) – VD Hà Nội: 21", value=21.0)
long = st.number_input("Kinh độ (long) – VD Hà Nội: 105.8", value=105.8)

if st.button("🧭 Vẽ lá số"):
    jday = 367*nam-(7*(nam+((thang+9)//12))//4)+((275*thang)//9)+ngay+(gio+phut/60)/24-730531.5+(-timezone)/24
    centuries = jday/36525
    asm4 = (math.atan2(math.cos(0), -math.sin(0)) * 180 / math.pi) % 360
    ay = -24
    asm5 = asm4 + ay if asm4 + ay >= 0 else asm4 + ay + 360
    hoangdao = (asm5 // 30) * 30
    gocascend = -2 * math.pi * (asm5 + 294) / 360
    singocascend = 10 * math.sin(gocascend)
    cosgocascend = 10 * math.cos(gocascend)

    fig = plt.figure(figsize=(8, 8))
    plt.title(f"LÁ SỐ CHIÊM TINH VỆ ĐÀ: {ten}\n{ngay}/{thang}/{nam}")
    plt.scatter(singocascend, cosgocascend, label="Cung Mọc")
    plt.annotate("Cung Mọc", (singocascend, cosgocascend))
    plt.xlim(-15, 15)
    plt.ylim(-15, 15)
    plt.grid(True)
    plt.legend()
    st.pyplot(fig)

    st.success("🎉 Lá số đã được vẽ thành công! (phiên bản đơn giản hoá)")
st.caption("📍 Phát triển từ tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng.")

