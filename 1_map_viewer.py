import streamlit as st

def run():
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
    # --- SCHUMANN RESONANCE ---
    
    st.markdown("""
