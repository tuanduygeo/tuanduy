import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
import math

st.set_page_config(layout="wide")
st.title("🧭 PHONG THỦY ĐỊA LÝ – Danh sách công trình")

st.markdown("""
### 📌 Hướng dẫn
- Danh sách hơn **4900 công trình tâm linh** từ `lakinhnet.py`.
- Gõ tên để lọc → Chọn trang → Bấm `Xem` → Bản đồ sẽ hiển thị bên dưới.
""")

# Thư mục chứa HTML
html_dir = "dulieu"
html_files = sorted([f for f in os.listdir(html_dir) if f.endswith(".html")])
df = pd.DataFrame({"Tên công trình": html_files})

# Tìm kiếm
search = st.text_input("🔍 Tìm công trình:", "").lower()
if search:
    df = df[df["Tên công trình"].str.lower().str.contains(search)]

# Phân trang
per_page = 30
total_pages = math.ceil(len(df) / per_page)
page = st.number_input(f"📄 Trang (1–{total_pages}):", min_value=1, max_value=total_pages, value=1, step=1)

start_idx = (page - 1) * per_page
end_idx = start_idx + per_page
df_page = df.iloc[start_idx:end_idx]

# Biến lưu tên file được chọn
selected_html = None

# Hiển thị danh sách từng trang
for _, row in df_page.iterrows():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"🔸 **{row['Tên công trình']}**")
    with col2:
        if st.button("Xem", key=row['Tên công trình']):
            selected_html = row['Tên công trình']

# Hiển thị bản đồ nếu đã chọn
if selected_html:
    html_path = os.path.join(html_dir, selected_html)
    st.markdown("---")
    st.subheader(f"🗺️ Bản đồ: {selected_html}")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        components.html(html_content, height=800, scrolling=True)

st.markdown("---")
st.caption("📍 Phát triển từ lakinhnet.py – phụng sự cộng đồng và học thuật.")
