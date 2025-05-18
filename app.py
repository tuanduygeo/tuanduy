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
import os
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from pyproj import Transformer
import contextily as ctx
from astrology_utils import astrology_block

def main():
    
    st.set_page_config(layout="wide")
    st.markdown("### 1. Chiêm tinh Ấn Độ")
    astrology_block()
    st.markdown("""
    ### 2.PHONG THỦY ĐỊA LÝ – BẢN ĐỒ ĐỊA MẠCH
    """)
    
    # Khởi tạo session state
    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = None
    # Thư mục chứa HTML
    html_dir = "dulieu"
    html_files = sorted([f for f in os.listdir(html_dir) if f.endswith(".html")])
    df = pd.DataFrame({"Tên công trình": html_files})
    # Phân trang
    per_page = 5
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
                components.html(html_content, height=900, scrolling=True)
    
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
                components.html(html_content, height=900, scrolling=True)
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
    ### 3.🌐Biểu đồ cộng hưởng Schumann Trái Đất trực tuyến
    Nguồn: [Tomsk, Russia Space Observing System]
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
    
    # 1. tính ========================
    input_str = st.text_input("x:", value="")

    # Xử lý tách chuỗi thành 2 số thực
    x, y = None, None
    if input_str:
        try:
            parts = [s.strip() for s in input_str.split(",")]
            if len(parts) == 2:
                x = float(parts[0])
                y = float(parts[1])
        except Exception:
            st.warning("⚠️ Cần nhhập định dạng chuẩn")
    
    if x is not None and y is not None:
        st.success(f"Bạn đã nhập: vĩ độ={x}, kinh độ={y}")
    dt = st.number_input("t", min_value=0.001, max_value=0.5, value=0.005, step=0.001, format="%.3f")
    dx=dy=dt
    radius=dt*111320
    # ========================
    # 2. NÚT TÍNH & KIỂM TRA FILE
    # ========================
    if st.button("run"):
        if x is None or y is None:
            st.warning("⚠️ Vui lòng nhập đúng định dạng.")
        else:
            try:
                
                west, east = y - dx, y + dx
                south, north = x - dy, x + dy
    
                lat_tile = int(north)
                lon_tile = int(east)
                tile = f"{'N' if lat_tile >= 0 else 'S'}{abs(lat_tile):02d}{'E' if lon_tile >= 0 else 'W'}{abs(lon_tile):03d}"
    
                srtm_dir = "dulieu"
                hgt_path = os.path.join(srtm_dir, f"{tile}.hgt")
                out_path = os.path.join(srtm_dir, "vietnamcrop.tif")
    
                if not os.path.exists(hgt_path):
                    st.error(f"❌ Không tìm thấy file: `{hgt_path}`.")
                else:
                    # ========================
                    # 3. XỬ LÝ DEM & GHI FILE MỚI
                    # ========================
                    with rasterio.open(hgt_path) as src:
                        window = from_bounds(west, south, east, north, src.transform)
                        dem_crop = src.read(1, window=window, resampling=Resampling.bilinear)
                        transform = src.window_transform(window)
                        profile = src.profile
    
                    profile.update({
                        "driver": "GTiff",
                        "height": dem_crop.shape[0],
                        "width": dem_crop.shape[1],
                        "transform": transform,
                        "nodata": -9999
                    })
    
                    with rasterio.open(out_path, "w", **profile) as dst:
                        dst.write(dem_crop, 1)
    
                    st.success("✅ Đã cắt file thành công.")
                    
    
                    # ========================
                    # 4. CHUYỂN HỆ TỌA ĐỘ EPSG:3857
                    # ========================
                    with rasterio.open(out_path) as data:
                        data_array = data.read(1).astype(np.float64)
                        transform = data.transform
    
                    nrows, ncols = data_array.shape
                    xt = np.arange(ncols) * transform.a + transform.c + transform.a / 2
                    yt = np.arange(nrows) * transform.e + transform.f + transform.e / 2
                    Xx, Yx = np.meshgrid(xt, yt)
    
                    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
                    Xx3857, Yx3857 = transformer.transform(Xx, Yx)
    
                    st.success("📐 Chuyển đổi số liệu thành công.")
                    
    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {e}")
        # 3. HÀM VẼ VÒNG FIBONACCI
        # ========================
    
        def plot_fibonacci_labels_only(ax, x_center, y_center, labels_inner, radius=radius):
            n = len(labels_inner)
            theta = np.linspace(0, 2*np.pi, n, endpoint=False) + np.pi/2
            shift = np.deg2rad(7.5)
        
            # Đường chia
            bold_indices = {1, 4, 7, 10, 13, 16, 19, 22}
            for i, t in enumerate(theta):
                lw = 2 if i in bold_indices else 1
                x0 = x_center + np.cos(t + shift) * radius * 0.85
                y0 = y_center + np.sin(t + shift) * radius * 0.85
                x1 = x_center + np.cos(t + shift) * radius * 0.95
                y1 = y_center + np.sin(t + shift) * radius * 0.95
                ax.plot([x0, x1], [y0, y1], color='white', linewidth=lw)
        
            # Vòng tròn
            for r in [ 0.95, 0.85]:
                circle_theta = np.linspace(0, 2*np.pi, 1000)
                x = x_center + np.cos(-circle_theta) * r * radius
                y = y_center + np.sin(-circle_theta) * r * radius
                ax.plot(x, y, color='white', linewidth=1)
        
            # Nhãn chữ
            for t, label in zip(theta, labels_inner):
                x = x_center + np.cos(t) * radius * 0.9
                y = y_center + np.sin(t) * radius * 0.9
                ax.text(x, y, label, ha='center', va='center', fontsize=13, color='white',fontweight='bold')
            ax.text(x_center, y_center, '+', ha='center', va='center', fontsize=22,color='white', fontweight='bold')
        labels_24 = [
            'Tý', 'Nhâm', 'Hợi', 'Càn', 'Tuất', 'Tân', 'Dậu', 'Canh',
            'Thân', 'Khôn', 'Mùi', 'Đinh', 'Ngọ', 'Bính', 'Tỵ', 'Tốn',
            'Thìn', 'Ất', 'Mão', 'Giáp', 'Dần', 'Cấn', 'Sửu', 'Quý'
        ]
        # 4. VẼ TOÀN BỘ
        # ========================
        fig, ax = plt.subplots(figsize=(12, 12))  # 👉 Tăng kích thước hình vẽ
        
        # Tâm ảnh và góc zoom
        x_center, y_center = transformer.transform(y, x)
        x0, x1 = Xx3857.min(), Xx3857.max()
        y0, y1 = Yx3857.min(), Yx3857.max()
        
        img, ext = ctx.bounds2img(x0, y0, x1, y1, ll=False, source=ctx.providers.Esri.WorldImagery, zoom=18)
        ax.imshow(img, extent=ext, origin="upper")
        
        # Khớp lại giới hạn hiển thị
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        
        # Vẽ contour
        levels = np.linspace(data_array.min(), data_array.max(), 21)
        cf = ax.contourf(Xx3857, Yx3857, data_array, cmap="rainbow", levels=levels, alpha=0)
        contour_lines = ax.contour(Xx3857, Yx3857, data_array, levels=levels, cmap='rainbow', linewidths=1)
        threshold = np.percentile(data_array, 90)
        threshold1 = np.percentile(data_array, 2)
        for level in levels:
        if level >= threshold:
            ax.contour(Xx3857, Yx3857, data_array, levels=[level], cmap='rainbow', linewidths=2.5)
        if level <= threshold1:
            ax.contour(Xx3857, Yx3857, data_array, levels=[level], cmap='rainbow', linewidths=2.5)
        # Vẽ vòng Fibonacci
        plot_fibonacci_labels_only(ax, x_center, y_center, labels_24, radius=radius)
      
        # Slider góc
        #col1, col2 = st.columns([1, 3])  # col1 hẹp hơn
        
       # with col1:
       #     angle_deg = st.slider("🎯 Góc", 0, 359, 0)
        
        
        # Chuyển sang radian: 0° ở Bắc, tăng thuận chiều kim đồng hồ
       # angle_rad = np.deg2rad(-angle_deg + 90)
        
        # ====== VẼ MŨI TÊN ======
       # arrow_length = 500  # 👈 bằng với bán kính vòng
       # x_end = x_center + arrow_length * np.cos(angle_rad)
       # y_end = y_center + arrow_length * np.sin(angle_rad)
        
        # Vẽ trên matplotlib hoặc streamlit.pyplot
        # ax.arrow(x_center, y_center, x_end - x_center, y_end - y_center, head_width=10, head_length=15, fc='black', ec='black')
        
        # Tắt trục và lưu ảnh
        ax.set_axis_off()
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close(fig)
    
    st.markdown("""
    ### 5.MÔ HÌNH LẠC THƯ 3X3 VÀ BẬC CAO VÔ TẬN
    """)
    
    # Nhập bậc của ma phương
    n = st.number_input("Nhập bậc lẻ n (>=3):", min_value=3, step=2, value=9)
    
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
        st.dataframe(df, use_container_width=False)
    
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
            st.success("Ma phương hợp lệ!")
        else:
            st.warning("⚠️ Ma phương này KHÔNG hợp lệ.")
    
        
        # --- BẢNG MODULO 9 ---
        st.markdown("#### Bảng ma phương chia hết cho 9:")  
        df_mod9 = (df % 9).replace(0, 9)
        st.dataframe(df_mod9, use_container_width=False)
       
        tong_cot_dau = df_mod9.iloc[:, 0].sum()
        st.markdown(f"🧾 Tổng mỗi cột: **{tong_cot_dau}**")
    
    except Exception as e:
        st.error(f"Lỗi: {e}")
    
    st.markdown("---\n### Tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng. SĐT&ZALO: 0377442597. DONATE: nguyenduytuan techcombank 19033167089018")

if __name__ == "__main__":
    main()
