import streamlit as st
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from pyproj import Transformer
import matplotlib.pyplot as plt
import contextily as ctx

def dem_block():
    # 1. tính ========================
    x = st.number_input("v", value=None, format="%.6f")
    y = st.number_input("k", value=None, format="%.6f")
    dt = st.number_input("t", min_value=0.001, max_value=0.5, value=0.005, step=0.001, format="%.3f")
    dx=dy=dt
    radius=dt*111320
    # ========================
    # 2. NÚT TÍNH & KIỂM TRA FILE
    # ========================
    if st.button("run"):
        if x is None or y is None:
            st.warning("⚠️ Vui lòng nhập đầy đủ vĩ độ và kinh độ.")
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
        
        
            
        
        
        # ========================
        # 4. VẼ TOÀN BỘ
        # ========================
        fig, ax = plt.subplots(figsize=(12, 12))  # 👉 Tăng kích thước hình vẽ
        
        # Tâm ảnh và góc zoom
        x_center, y_center = transformer.transform(y, x)
        x0, x1 = Xx3857.min(), Xx3857.max()
        y0, y1 = Yx3857.min(), Yx3857.max()
        
        img, ext = ctx.bounds2img(x0, y0, x1, y1, ll=False, source=ctx.providers.Esri.WorldImagery, zoom=16)
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
        mask = data_array >= threshold
        mask1= data_array <= threshold1
        ax.contour(Xx3857, Yx3857, mask, levels=[0.5], colors='red', linewidths=3)
        ax.contour(Xx3857, Yx3857, mask1, levels=[0.5], colors='blue', linewidths=3)
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
    pass

# Thêm các hàm phụ trợ cho DEM ở dưới (nếu cần)