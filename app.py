import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
import math
from datetime import date, timedelta, datetime
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
# --- SCHUMANN RESONANCE ---
st.markdown("""
### 🌐 Trực tiếp Schumann Resonance (Biểu đồ cộng hưởng Trái Đất)
Nguồn: [Tomsk, Russia – Space Observing System]
""")
st.image("https://sosrff.tsu.ru/new/shm.jpg", caption="Schumann Resonance - Live", use_column_width=True)

st.caption("📍 Phát triển từ tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng.")

