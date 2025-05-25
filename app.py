import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
import math
from datetime import date, timedelta, datetime
import swisseph as swe
import pytz
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle, Circle
import matplotlib.transforms as transforms
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
from scipy.ndimage import gaussian_filter
import re
import geomag
from scipy.stats import norm, gaussian_kde
import streamlit_authenticator as stauth

st.set_page_config(layout="wide")
def plot_parallel_zones(ax, x_center, y_center, radius, bearing_deg=0, d=30, offset_d=0, rotate_angle=0, ratio_red=0.5):
    """
    Vẽ dải song song kín toàn bộ vòng tròn, offset_d dịch chuyển thật sự!
    """
    theta = np.deg2rad(90 - bearing_deg - rotate_angle)
    dx = np.cos(theta)
    dy = np.sin(theta)
    nx = -dy
    ny = dx

    # Độ rộng từng màu
    d_red = d
    d_blue = d * (1 - ratio_red) / ratio_red if ratio_red > 0 else d  # tránh chia 0

    # Vòng tròn clip path
    circle = Circle((x_center, y_center), radius, transform=ax.transData)
    ax.add_patch(circle)
    circle.set_visible(False)

    # Dải phủ kín từ -radius đến +radius, offset_d được cộng cho từng bước
    offset = -radius
    while offset < radius:
        # Cộng offset_d vào từng vị trí
        total_offset = offset + offset_d

        # Dải đỏ
        cx = x_center + nx * total_offset
        cy = y_center + ny * total_offset
        rect_red = Rectangle(
            (-radius, -d_red / 2), 2 * radius, d_red,
            facecolor=(1, 0, 0, 0.14), edgecolor=None, linewidth=0, alpha=0.4)
        t_red = transforms.Affine2D().rotate_around(0, 0, theta).translate(cx, cy) + ax.transData
        rect_red.set_transform(t_red)
        rect_red.set_clip_path(circle)
        ax.add_patch(rect_red)

        offset += d_red

        # Dải xanh
        total_offset = offset + offset_d
        cx = x_center + nx * total_offset
        cy = y_center + ny * total_offset
        rect_blue = Rectangle(
            (-radius, -d_blue / 2), 2 * radius, d_blue,
            facecolor=(0, 0.4, 1, 0.14), edgecolor=None, linewidth=0, alpha=0.4)
        t_blue = transforms.Affine2D().rotate_around(0, 0, theta).translate(cx, cy) + ax.transData
        rect_blue.set_transform(t_blue)
        rect_blue.set_clip_path(circle)
        ax.add_patch(rect_blue)

        offset += d_blue

    # Viền vòng tròn ngoài cho đẹp
    circle_vis = Circle((x_center, y_center), radius, edgecolor='none', facecolor='none', linewidth=1, alpha=0.2, zorder=99)
    ax.add_patch(circle_vis)
def plot_parallel_zones2(ax, x_center, y_center, radius, bearing_deg2=0, d2=30, offset_d2=0, rotate_angle2=0, ratio_red2=0.5):
    """
    Vẽ các dải song song kín toàn bộ vòng tròn, offset_d2 dịch toàn bộ hệ dải (song song với 'plot_parallel_zones')
    """
    theta = np.deg2rad(90 - bearing_deg2 - rotate_angle2)
    dx = np.cos(theta)
    dy = np.sin(theta)
    nx = -dy
    ny = dx

    # Độ rộng từng màu
    d_red = d2
    d_blue = d2 * (1 - ratio_red2) / ratio_red2 if ratio_red2 > 0 else d2  # tránh chia 0

    # Tạo vòng tròn làm clip path
    circle = Circle((x_center, y_center), radius, transform=ax.transData)
    ax.add_patch(circle)
    circle.set_visible(False)

    # offset chạy từ -radius tới +radius, offset_d2 được cộng cho từng dải
    offset = -radius
    while offset < radius:
        # Dải đỏ
        total_offset = offset + offset_d2
        cx = x_center + nx * total_offset
        cy = y_center + ny * total_offset
        rect_red = Rectangle(
            (-radius, -d_red / 2), 2 * radius, d_red,
            facecolor=(1, 0, 0, 0.14), edgecolor=None, linewidth=0, alpha=0.4)
        t_red = transforms.Affine2D().rotate_around(0, 0, theta).translate(cx, cy) + ax.transData
        rect_red.set_transform(t_red)
        rect_red.set_clip_path(circle)
        ax.add_patch(rect_red)

        offset += d_red

        # Dải xanh
        total_offset = offset + offset_d2
        cx = x_center + nx * total_offset
        cy = y_center + ny * total_offset
        rect_blue = Rectangle(
            (-radius, -d_blue / 2), 2 * radius, d_blue,
            facecolor=(0, 0.4, 1, 0.14), edgecolor=None, linewidth=0, alpha=0.4)
        t_blue = transforms.Affine2D().rotate_around(0, 0, theta).translate(cx, cy) + ax.transData
        rect_blue.set_transform(t_blue)
        rect_blue.set_clip_path(circle)
        ax.add_patch(rect_blue)

        offset += d_blue

    # Vẽ viền vòng tròn ngoài cho đẹp
    circle_vis = Circle((x_center, y_center), radius, edgecolor='none', facecolor='none', linewidth=1, alpha=0.2, zorder=99)
    ax.add_patch(circle_vis)

    
@st.cache_data
def load_crop_dem(hgt_path, west, south, east, north):
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.enums import Resampling

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
    return dem_crop, transform, profile
def get_magnetic_declination(lat, lon):
    return geomag.declination(lat, lon)
def extract_phongthuy_data(n_text):
    door_match = re.search(r'Cửa chính,phụ: Mở ở hướng ([^<]*)<br>', n_text)
    doors = [h.strip() for h in door_match.group(1).split(',')] if door_match else []
    son_thoai, son_tan, thuy_thoai, thuy_tan = [], [], [], []

    match_son_thoai = re.search(r'3\.Cung vị sơn:.*?sơn\s+([^<]*)\s+là thoái thần', n_text)
    if match_son_thoai:
        block = match_son_thoai.group(1)
        for ten_loai in block.split(','):
            ten_loai = ten_loai.strip()
            if ten_loai:
                m = re.match(r'([A-Za-zÀ-ỹ\s]+)\((tôn|tử)\)', ten_loai)
                if m:
                    son_thoai.append({'son': m.group(1).strip(), 'loai': m.group(2).strip(), 'group': 'thoái', 'zone': 'cung vị sơn'})
                else:
                    son_thoai.append({'son': ten_loai.strip(), 'loai': None, 'group': 'thoái', 'zone': 'cung vị sơn'})
    match_son_tan = re.search(r'-\s*sơn\s+([^<]*)\s+là tấn thần', n_text)
    if match_son_tan:
        block = match_son_tan.group(1)
        for ten_loai in block.split(','):
            ten_loai = ten_loai.strip()
            if ten_loai:
                m = re.match(r'([A-Za-zÀ-ỹ\s]+)\((tôn|tử)\)', ten_loai)
                if m:
                    son_tan.append({'son': m.group(1).strip(), 'loai': m.group(2).strip(), 'group': 'tấn', 'zone': 'cung vị sơn'})
                else:
                    son_tan.append({'son': ten_loai.strip(), 'loai': None, 'group': 'tấn', 'zone': 'cung vị sơn'})
    match_thuy_thoai = re.search(r'4\. Các cung vị thuỷ:\s*([^<]*)\s+là thoái thần', n_text)
    if match_thuy_thoai:
        block = match_thuy_thoai.group(1)
        for ten_loai in block.split(','):
            ten_loai = ten_loai.strip()
            if ten_loai:
                m = re.match(r'([A-Za-zÀ-ỹ\s]+)\((tôn|tử)\)', ten_loai)
                if m:
                    thuy_thoai.append({'son': m.group(1).strip(), 'loai': m.group(2).strip(), 'group': 'thoái', 'zone': 'cung vị thủy'})
                else:
                    thuy_thoai.append({'son': ten_loai.strip(), 'loai': None, 'group': 'thoái', 'zone': 'cung vị thủy'})
    match_thuy_tan = re.search(r'-\s*Các sơn\s+([^<]*)\s+là tấn thần', n_text)
    if match_thuy_tan:
        block = match_thuy_tan.group(1)
        for ten_loai in block.split(','):
            ten_loai = ten_loai.strip()
            if ten_loai:
                m = re.match(r'([A-Za-zÀ-ỹ\s]+)\((tôn|tử)\)', ten_loai)
                if m:
                    thuy_tan.append({'son': m.group(1).strip(), 'loai': m.group(2).strip(), 'group': 'tấn', 'zone': 'cung vị thủy'})
                else:
                    thuy_tan.append({'son': ten_loai.strip(), 'loai': None, 'group': 'tấn', 'zone': 'cung vị thủy'})

    all_son = son_thoai + son_tan + thuy_thoai + thuy_tan
    df_son = pd.DataFrame(all_son) if all_son else pd.DataFrame()
    return doors, df_son


def main():
    st.markdown("""
    <div style="background:linear-gradient(90deg,#f9d423,#ff4e50);padding:24px 8px 20px 8px;border-radius:16px;margin-bottom:24px;">
        <h1 style='color:white;text-align:center;margin:0;font-size:36px;'>🔯 ỨNG DỤNG  ĐỊA LÝ & CHIÊM TINH </h1>
        <p style='color:white;text-align:center;font-size:20px;margin:0;'>Tác giả: Nguyễn Duy Tuấn</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 1. Địa mạch") 
    # 1. tính ========================
       # --- Giao diện nhập ---
    col1, col2, col3, col4, col5 = st.columns([1 ,1, 1, 1, 1])
    with col1:
        input_str = st.text_input("Nhập x,y", value="")
        run = st.button("Tính toán", use_container_width=True)
        show_main = st.checkbox("Hiện Mạch chính", value=False)
        show_sub = st.checkbox("Hiện Mạch phụ", value=False)
        diachi = st.text_input("địa chỉ", value="")
        
    with col2:
        distance_between_zones = st.number_input("Mạch chính rộng (m)", min_value=1.0, max_value=800.0, value=30.0, step=1.0)
        offset_d = st.number_input("Dịch chuyển ngang-chính (m)", min_value=-500.0, max_value=500.0, value=0.0, step=1.0)
        rotate_angle = st.number_input("Góc lệch mạch-chính (độ)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0)
        ratio_red=st.number_input("tỷ số tốt/xấu- chính", min_value=0.0, max_value=1.0, value=0.5, step=0.2, format="%.1f")
    with col3:
        distance_between_zones2 = st.number_input("Mạch phụ rộng(m)", min_value=1.0, max_value=800.0, value=30.0, step=1.0)
        offset_d2 = st.number_input("Dịch chuyển ngang-phụ (m)", min_value=-500.0, max_value=500.0, value=0.0, step=1.0)
        rotate_angle2 = st.number_input("Góc lệch mạch-phụ (độ)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0)
        ratio_red2=st.number_input("tỷ số tốt/xấu- phụ", min_value=0.0, max_value=1.0, value=0.5, step=0.2, format="%.1f")
    with col4:
        manual_bearing = st.number_input("góc", min_value=0.0, max_value=360.0, value=None, step=1.0, format="%.1f")
        dt = st.number_input("Bán kính", min_value=0.001, max_value=0.02, value=0.005, step=0.002, format="%.3f")
        
        
    
        
        
   
    x = y = None
    if input_str:
        try:
            parts = [s.strip() for s in input_str.split(",")]
            if len(parts) == 2:
                x = float(parts[0])
                y = float(parts[1])
        except Exception:
            st.warning("⚠️ Cần nhập định dạng chuẩn (ví dụ: 10.123, 106.456)")
    
    if run and x is not None and y is not None:
        try:
            dx = dy = dt
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
                dem_crop, transform, profile = load_crop_dem(hgt_path, west, south, east, north)
    
                
    
                with rasterio.open(out_path, "w", **profile) as dst:
                    dst.write(dem_crop, 1)
                with rasterio.open(out_path) as data:
                    data_array = data.read(1).astype(np.float64)
                    transform = data.transform
                
                nrows, ncols = data_array.shape
                xt = np.arange(ncols) * transform.a + transform.c + transform.a / 2
                yt = np.arange(nrows) * transform.e + transform.f + transform.e / 2
                Xx, Yx = np.meshgrid(xt, yt)
                
                transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
                Xx3857, Yx3857 = transformer.transform(Xx, Yx)
                
                x_center, y_center = transformer.transform(y, x)  # x=lat, y=lon
                
                radius = dt * 111320
                
                def plot_bearing_circle(ax, x_center, y_center, radius):
                    # 360 vạch chia, mỗi 1 độ
                    for deg in range(360):
                        angle = np.deg2rad(deg) - np.pi/2  # Đưa 0° ra phía Bắc (trên cùng), thuận chiều kim đồng hồ
                        # Xác định độ dài vạch
                        if deg % 15 == 0:
                            r0 = radius * 0.99  # Vạch dài cho 15°
                            lw = 1.2
                        else:
                            r0 = radius * 0.99  # Vạch ngắn cho từng độ
                            lw = 1
                        r1 = radius * 1.03     # Mép ngoài
                        x0 = x_center + np.cos(angle) * r0
                        y0 = y_center + np.sin(angle) * r0
                        x1 = x_center + np.cos(angle) * r1
                        y1 = y_center + np.sin(angle) * r1
                        ax.plot([x0, x1], [y0, y1], color='white', linewidth=lw, zorder=101)
                        # Hiển thị số độ mỗi 15°
                        if deg % 15 == 0:
                            xt = x_center + np.cos(angle) * (radius * 1.05)
                            yt = y_center - np.sin(angle) * (radius * 1.05)
                            ax.text(xt, yt, f"{deg}", fontsize=9, color='white', ha='center', va='center',  zorder=45)

                def plot_fibonacci_labels_only(ax, x_center, y_center, labels_inner, radius=radius):
                    n = len(labels_inner)
                    theta = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
                    shift = np.deg2rad(7.5)
                    bold_indices = {1, 4, 7, 10, 13, 16, 19, 22}
                    for i, t in enumerate(theta):
                        lw = 2 if i in bold_indices else 1
                        x0 = x_center + np.cos(t + shift) * radius * 0.85
                        y0 = y_center + np.sin(t + shift) * radius * 0.85
                        x1 = x_center + np.cos(t + shift) * radius * 0.95
                        y1 = y_center + np.sin(t + shift) * radius * 0.95
                        ax.plot([x0, x1], [y0, y1], color='white', linewidth=lw)
                    for r in [0.95, 0.85]:
                        circle_theta = np.linspace(0, 2 * np.pi, 1000)
                        x = x_center + np.cos(-circle_theta) * r * radius
                        y = y_center + np.sin(-circle_theta) * r * radius
                        ax.plot(x, y, color='white', linewidth=1)
                    for t, label in zip(theta, labels_inner):
                        x = x_center + np.cos(t) * radius * 0.9
                        y = y_center + np.sin(t) * radius * 0.9
                        ax.text(x, y, label, ha='center', va='center', fontsize=13, color='white', fontweight='bold')
                    ax.text(x_center, y_center, '+', ha='center', va='center', fontsize=22, color='white', fontweight='bold')
                
                labels_24 = [
                    'Tý', 'Nhâm', 'Hợi', 'Càn', 'Tuất', 'Tân', 'Dậu', 'Canh',
                    'Thân', 'Khôn', 'Mùi', 'Đinh', 'Ngọ', 'Bính', 'Tỵ', 'Tốn',
                    'Thìn', 'Ất', 'Mão', 'Giáp', 'Dần', 'Cấn', 'Sửu', 'Quý'
                ]
                
                fig, ax = plt.subplots(figsize=(12, 12))
                x0, x1 = Xx3857.min(), Xx3857.max()
                y0, y1 = Yx3857.min(), Yx3857.max()
                img, ext = ctx.bounds2img(x0, y0, x1, y1, ll=False, source=ctx.providers.Esri.WorldImagery, zoom=17)
                ax.imshow(img, extent=ext, origin="upper")
                ax.set_xlim(x0, x1)
                ax.set_ylim(y0, y1)
                
                # Vẽ contour DEM
                # Tạo 21 levels đều nhau giữa min và max
                z_min, z_max = float(data_array.min()), float(data_array.max())
                if z_min == z_max:
                    # Nếu dữ liệu phẳng (không có biến động)
                    levels = np.linspace(z_min - 1, z_max + 1, 30)
                else:
                    # Nếu khoảng cách quá nhỏ, mở rộng một chút cho đẹp
                    if abs(z_max - z_min) < 1e-3:
                        z_max = z_min + 1e-3
                    levels = np.linspace(z_min, z_max, 30)
                
                
                cmap = matplotlib.colormaps['jet']
                norm1 = mcolors.Normalize(vmin=np.min(levels), vmax=np.max(levels))
                data_smooth = gaussian_filter(data_array, sigma=1.5)
                ax.contourf(Xx3857, Yx3857, data_smooth, cmap="jet", levels=levels, alpha=0)
                ax.contour(Xx3857, Yx3857, data_smooth, levels=levels, cmap='jet', linewidths=1)
                threshold = np.percentile(data_array, 90)
                threshold1 = np.percentile(data_array, 5)
                for level in levels:
                    if level >= threshold:
                        color = cmap(norm1(level))
                        ax.contour(Xx3857, Yx3857, data_smooth, levels=[level], colors=[color], linewidths=4)
                    if level <= threshold1:
                        color = cmap(norm1(level))
                        ax.contour(Xx3857, Yx3857, data_smooth, levels=[level], colors=[color], linewidths=3)
                # Vẽ vòng Fibonacci
                plot_fibonacci_labels_only(ax, x_center, y_center, labels_24, radius=radius*0.7)
                
                # --- Tìm điểm cao nhất trong mask ---
                z = data_array  # <-- Đồng nhất biến!
                rows, cols = z.shape
                i_idx, j_idx = np.indices((rows, cols))
                xs, ys = rasterio.transform.xy(transform, i_idx, j_idx, offset='center')
                xs = np.array(xs)
                ys = np.array(ys)
                lat0 = x
                lon0 = y
                mask = ((ys - lat0) ** 2 + (xs - lon0) ** 2) <= ((dt/2) ** 2)
                z_flat = z.ravel()
                mask_flat = mask.ravel()
                idx_max = np.argmax(z_flat[mask_flat])
                masked_indices = np.nonzero(mask_flat)[0]
                idx_global = masked_indices[idx_max]
                lat_max = ys.ravel()[idx_global]
                lon_max = xs.ravel()[idx_global]
                
                # Chuyển sang EPSG:3857 để vẽ trên ảnh
                x_center_map, y_center_map = transformer.transform(lon0, lat0)
                x_max, y_max = transformer.transform(lon_max, lat_max)
                
               
                # Tính vector hướng từ center đến max
                dx = x_max - x_center_map
                dy = y_max - y_center_map
                length = np.sqrt(dx**2 + dy**2)
                if length == 0:
                    # Tránh chia 0, chọn hướng bất kỳ
                    dir_x, dir_y = 1, 0
                else:
                    dir_x = dx / length
                    dir_y = dy / length
                
              
                arrow_length = radius * 0.75
                if manual_bearing is not None:
                    # Vẽ theo góc nhập tay (màu đỏ)
                    angle_rad = np.deg2rad(90 - manual_bearing)
                    arrow_dx = np.cos(angle_rad) * arrow_length
                    arrow_dy = np.sin(angle_rad) * arrow_length
                    arrow_color = 'white'
                    
                else:
                    # Vẽ theo hướng DEM tự động (màu trắng)
                    arrow_dx = -dir_x * arrow_length
                    arrow_dy = -dir_y * arrow_length
                    arrow_color = 'white'
                
                ax.arrow(
                    x_center_map, y_center_map,
                    arrow_dx, arrow_dy,
                    head_width=4,
                    head_length=4,
                    linewidth=2,
                    color=arrow_color,
                    length_includes_head=True,
                    zorder=15
                )
                dlon = lon_max - lon0
                dlat = lat_max - lat0
                declination = get_magnetic_declination(x, y)
                huong = "E" if declination >= 0 else "W"
                declination_str = f"{abs(declination):.1f}°{huong}"
                if manual_bearing is not None:
                    bearing = manual_bearing
                else:
                    bearing1 = (np.degrees(np.arctan2(dlon, dlat)) + 360) % 360
                    
                    bearing = (bearing1 + 180 - declination) % 360
                st.markdown(f"**Chỉ số Bearing :** `{bearing:.1f}°`")
                if 337.5<=float(bearing)<352.5:
                    n=(" 1.Toạ Bính(-2) Tấn 6 kim khắc xuất hướng Nhâm -1 thuỷ nên là cục toạ Tấn nghi Thoái. Hùng dự Hùng<br>     2. Cửa chính,phụ: Mở ở hướng bính,tỵ, Tân, Dậu, mùi, khôn, Sửu <br>      3.Cung vị sơn:            sơn nhâm, hợi(tôn), Cấn(tử), ất,mão(tử)     là thoái thần <br>  Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh   <br>   -   sơn mùi, khôn, tân, dậu, sửu, bính,tỵ    là tấn thần.<br>Cần cao , xa <100m.<br>    4. Các cung vị thuỷ:    tý quý(tôn), thân canh(tử), tuất(tử)   là thoái thần. <br>    Cần thấp , xa >100m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài.<br>     - Các sơn giáp, dần, tốn,thìn, ngọ,đinh, càn   là tấn thần. Cần có thủy trong 100m." )
                elif 352.5<=float(bearing)<360:
                    n=(" 1.Toạ Ngọ(-6) Tấn 6 kim khắc xuất hướng Tý 1 thuỷ nên là cục toạ Tấn nghi Thoái. Hùng dự Thư<br>     2. Cửa chính,phụ: Mở ở hướng giáp,dần,thìn,tốn,đinh,ngọ, càn <br>      3.Cung vị sơn:          sơn quý, tý(tôn), canh,thân(tử), tuất(tử)    là thoái thần <br>  Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br>   -   sơn giáp, dần, tốn, đinh,ngọ, càn    là tấn thần. <br>    Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   nhâm, hợi(tôn), cấn(tử), ất,mão(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn sửu, bính,tỵ, mùi, khôn, tân, dậu   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 0<=float(bearing)<7.5:
                    n=(" 1.Toạ Ngọ(-1) Tấn 6 kim khắc xuất hướng Tý 1 thuỷ nên là cục toạ Tấn nghi Thoái. Hùng dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng giáp,dần,thìn,tốn,đinh,ngọ, càn <br> 3.Cung vị sơn:    sơn quý, tý(tôn), canh,thân(tử), tuất(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn giáp, dần, tốn, đinh,ngọ, càn    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   nhâm, hợi(tôn), cấn(tử), ất,mão(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn sửu, bính,tỵ, mùi, khôn, tân, dậu   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 7.5<=float(bearing)<22.5:
                    n=(" 1.Toạ Đinh(-1) Tấn 6 kim khắc xuất hướng Quý 1 thuỷ nên là cục toạ Tấn nghi Thoái. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng giáp,dần, thìn,tốn,đinh,ngọ, càn <br> 3.Cung vị sơn:    sơn quý, tý(tôn), canh,thân(tử), tuất(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn giáp, dần, tốn, đinh,ngọ, càn    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   nhâm, hợi(tôn), cấn(tử), ất,mão(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn sửu, bính,tỵ, mùi, khôn, tân, dậu   là tấn thần.<br>   Cần thấp, xa< 100m ")
                elif 22.5<=float(bearing)<37.5:
                    n=(" 1.Toạ Mùi(2) Thoái 4 mộc sinh xuất hướng Sửu 9 hoả nên là cục toạ Thoái nghi Thoái. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng sửu, bính,tỵ,khôn<br> 3.Cung vị sơn:      sơn sửu(tử), bính,tỵ(tôn), khôn(tôn) khắc xuất là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn nhâm, hợi,cấn,ất,mão, mùi, dậu,tân    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    càn(tử), thìn(tôn), đinh,ngọ(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn canh,thân, tuất, quý, tý, giáp, dần, tốn   là tấn thần.<br> Cần thấp, xa< 100m  ")
                elif 37.5<=float(bearing)<52.5:
                    n=(" 1.Toạ Khôn(7) Thoái 7 kim sinh xuất hướng Cấn 2 thổ nên là cục toạ Thoái nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng cấn, ất,mão, nhâm, hợi  <br> 3.Cung vị sơn:      sơn nhâm, hợi(tôn),cấn(tử),ất,mão(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn tân, dậu,sửu, mùi, khôn, tị bính    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    canh,thân(tử), tuất(tử), quý, tý(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn càn,giáp, dần,tốn, ngọ,đinh, thìn   là tấn thần.<br> Cần thấp, xa< 100m  ")
                elif 52.5<=float(bearing)<67.5:
                    n=(" 1.Toạ Thân(-6) Tấn 8 thổ khắc xuất hướng Dần 3 mộc nên là cục toạ Tấn nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng càn,thìn,đinh,ngọ,thân canh, tuất <br> 3.Cung vị sơn:    sơn quý, tý(tử), giáp, dần(tôn), tốn(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn thìn, đinh,ngọ, càn, thân canh, tuất    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   mùi(tôn), nhâm, hợi(tử),tân, dậu(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>- Các sơn sửu, bính,tỵ, khôn, mão, ất, cấn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 67.5<=float(bearing)<82.5:
                    n=(" 1.Toạ Canh(-1) Thoái 8 thổ khắc xuất hướng Giáp 3 mộc nên là cục toạ Thoái nghi Thoái. Hùng dự Hùng <br> 2. Cửa chính,phụ: Mở ở hướng Tý Quý, giáp, dần, tốn<br> 3.Cung vị sơn:    sơn quý, tý(tử), giáp, dần(tôn), tốn(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn càn, thìn, đinh,ngọ, thân canh, tuất    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   tân, dậu(tôn), nhâm, hợi(tử), mùi (tôn)  là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn sửu,bính,tỵ, khôn,ất,mão, cấn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 82.5<=float(bearing)<97.5:
                    n=(" 1.Toạ Dậu(-7) Tấn 3 mộc cùng hành hướng Mão 8 thổ nên là cục toạ Tấn nghi Tấn. Hùng dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng nhâm, hợi, cấn, ất, mão, dậu,tân, mùi  <br> 3.Cung vị sơn:      sơn sửu(tử), bính,tỵ(tôn), khôn(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn nhâm, hợi, cấn, ất,mão, dậu,tân, mùi    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    càn(tử), thìn(tôn), đinh,ngọ(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn tuất, quý, tý, canh,thân, giáp, dần, tuất   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 97.5<=float(bearing)<112.5:
                    n=(" 1.Toạ Tân(-2) Tấn 3 mộc khắc nhập hướng Ất 8 thổ nên là cục toạ Tấn nghi Tấn. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng nhâm, hợi, cấn, ất, mão, mùi, dậu,tân  <br> 3.Cung vị sơn:      sơn sửu(tử), bính,tỵ(tôn), khôn(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn nhâm, hợi, cấn, ất,mão, mùi, dậu,tân    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    càn(tử), thìn(tôn), đinh,ngọ(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn tuất, quý, tý, canh,thân,giáp, dần, tốn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 112.5<=float(bearing)<127.5:
                    n=(" 1.Toạ Tuất(-6) Thoái 2 thổ sinh nhập hướng Thìn 7 kim nên là cục toạ Thoái nghi Tấn. Hùng dự Hùng <br> 2. Cửa chính,phụ: Mở ở hướng quý, tý, giáp, dần, tốn  <br> 3.Cung vị sơn:    sơn quý, tý(tử), giáp, dần(tôn), tốn(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn thìn, đinh,ngọ, càn, thân canh, tuất    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   nhâm, hợi(tử), mùi(tôn), tân, dậu(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn sửu, bính,tỵ, khôn, cấn, mão, ất   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 127.5<=float(bearing)<142.5:
                    n=(" 1.Toạ Càn(-1) Tấn 9 hoả sinh nhập hướng Tốn 4 mộc nên là cục toạ Tấn nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng quý, tý, giáp, dần, tốn, càn  <br> 3.Cung vị sơn:    sơn thìn(tử), đinh,ngọ(tử), canh,thân(tôn), tuất(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn tý quý, giáp, dần, tốn, càn    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   ất,mão(tôn), tỵ bính(tử), khôn(tử), cấn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn hợi nhâm, mùi, dậu,tân, sửu   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 142.5<=float(bearing)<157.5:
                    n=(" 1.Toạ Hợi(2) Thoái 1 thuỷ khắc nhập hướng Tỵ 6 kim nên là cục toạ Thoái nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng mùi, dậu,tân, sửu  <br> 3.Cung vị sơn:      sơn mùi(tử), dậu,tân(tử), sửu(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn nhâm, hợi, cấn ,ất,mão, bính,tỵ    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    càn(tôn), giáp, dần(tử), tốn(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  .<br> - Các sơn đinh,ngọ, canh,thân, tuất, quý, tý, thìn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 157.5<=float(bearing)<172.5:
                    n=(" 1.Toạ Nhâm(7) Tấn 1 thuỷ khắc nhập hướng Bính 6 kim nên là cục toạ Tấn nghi Tấn. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng nhâm,cấn,ất,mão, bính,tỵ, khôn, nhâm, hợi  <br> 3.Cung vị sơn:      sơn sửu(tôn), mùi(tử), tân, dậu(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn nhâm, cấn, ất,mão, bính,tỵ, khôn, nhâm, hợi    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    giáp, dần(tử), tốn(tử), càn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn quý, tý, thìn, đinh,ngọ, canh,thân, tuất   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 172.5<=float(bearing)<187.5:
                    n=(" 1.Toạ Tý(1) Tấn 1 thuỷ khắc nhập hướng Ngọ 6 kim nên là cục toạ Tấn nghi Tấn. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng quý, tý, thìn, đinh,ngọ, canh,thân, tuất  <br> 3.Cung vị sơn:    sơn càn(tôn), giáp, dần(tử), tốn(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn quý, tý, thìn, đinh,ngọ, canh,thân, tuất    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   sửu(tôn), mùi(tử), tân, dậu(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn nhâm, cấn, ất,mão, bính,tỵ, khôn, nhâm, hợi   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 187.5<=float(bearing)<202.5:
                    n=(" 1.Toạ Quý(6) Thoái 1 thuỷ khắc nhập  hướng Đinh 6 kim nên là cục toạ Thoái nghi Tấn. Hùng dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng giáp, dần, tốn, càn <br> 3.Cung vị sơn:    sơn càn(tôn), giáp, dần(tử), tốn(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn quý, tý, thìn, đinh,ngọ, canh,thân, tuất    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   sửu(tôn), mùi(tử), tân, dậu(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  .<br> - Các sơn nhâm, cấn, ất,mão, bính,tỵ, khôn, nhâm, hợi   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 202.5<=float(bearing)<217.5:
                    n=(" 1.Toạ Sửu(-7) Tấn 9 hoả sinh nhập hướng Mùi 4 mộc nên là cục toạ Tấn nghi Tấn. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng tân, dậu, nhâm, hợi, sửu, mùi  <br> 3.Cung vị sơn:      sơn khôn(tử), ất,mão(tôn), bính,tỵ(tử), cấn(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn tân, dậu, nhâm, hợi, sửu, mùi    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    đinh,ngọ(tử), canh,thân(tôn), tuất(tôn), thìn(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn càn, quý, tý, giáp, dần, tốn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 217.5<=float(bearing)<232.5:
                    n=(" 1.Toạ Cấn(-2) Thoái 2 thổ sinh nhập hướng Khôn 7 kim nên là cục toạ Thoái nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng mùi, tân, dậu, nhâm, hợi <br> 3.Cung vị sơn:      sơn mùi(tôn), tân, dậu(tôn), nhâm, hợi(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn khôn, cấn sửu, ất,mão, bính,tỵ    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    quý, tý(tử), giáp, dần(tôn), tốn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br>  - Các sơn đinh,ngọ, canh,thân, tuất, thìn, càn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 232.5<=float(bearing)<247.5:
                    n=(" 1.Toạ Dần(1) Tấn 3 mộc khắc nhập hướng Thân 8 thổ nên là cục toạ Tấn nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng tuất, quý, tý, canh,thân, giáp, dần, tốn  <br> 3.Cung vị sơn:    sơn càn(tử), thìn(tôn), đinh,ngọ(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn tuất, quý, tý, canh,thân, giáp, dần, tốn    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   sửu(tử), bính,tỵ(tôn), khôn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn nhâm, hợi, cấn, ất,mão, dậu,tân, mùi   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 247.5<=float(bearing)<262.5:
                    n=(" 1.Toạ Giáp(6) Tấn 3 mộc khắc nhập hướng Canh 8 thổ nên là cục toạ Tấn nghi Tấn. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng tuất, quý, tý, canh,thân, giáp, dần, tốn  <br> 3.Cung vị sơn:    sơn càn(tử), thìn(tôn), đinh,ngọ(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn tuất, quý, tý, canh,thân, giáp, dần, tốn    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   sửu(tử), bính,tỵ(tôn), khôn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn nhâm, hợi, cấn, ất,mão, dậu,tân, mùi   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 262.5<=float(bearing)<277.5:
                    n=(" 1.Toạ Mão(2) Thoái 8 thổ khắc xuất hướng Dậu 3 mộc nên là cục toạ Thoái nghi Thoái. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng mùi, tân, dậu, nhâm, hợi  <br> 3.Cung vị sơn:      sơn mùi(tôn), tân, dậu(tôn), nhâm, hợi(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn khôn, cấn sửu, ất,mão, bính,tỵ    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    quý, tý(tử), giáp, dần(tôn), tốn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn đinh,ngọ, canh,thân, tuất, thìn, càn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 277.5<=float(bearing)<292.5:
                    n=(" 1.Toạ Ất(7) Tấn 8 thổ khắc xuất hướng Tân 3 mộc nên là cục toạ Tấn nghi Thoái. Hùng dự thư<br> 2. Cửa chính,phụ: Mở ở hướng khôn, cấn sửu, ất,mão, bính,tỵ <br> 3.Cung vị sơn:      sơn mùi(tôn), tân, dậu(tôn), nhâm, hợi(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn khôn, cấn sửu, ất,mão, bính,tỵ    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    quý, tý(tử), giáp, dần(tôn), tốn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn đinh,ngọ, canh,thân, tuất, thìn, càn   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 292.5<=float(bearing)<307.5:
                    n=(" 1.Toạ Thìn(1) Thoái 7 kim sinh xuất hướng Tuất 2 thổ nên là cục toạ Thoái nghi Thoái. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng canh,thân, tuất, quý, tý  <br> 3.Cung vị sơn:    sơn quý, tý(tôn), canh,thân(tử), tuất(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn càn, giáp, dần, đinh,ngọ, tốn,thìn    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   nhâm, hợi(tôn), cấn(tử), ất,mão(tử)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn sửu, bính,tỵ, mùi, khôn, tân, dậu   là tấn thần.<br> Cần thấp, xa< 100m ")
                elif 307.5<=float(bearing)<322.5:
                    n=(" 1.Toạ Tốn(6) Thoái 4 mộc sinh xuất hướng Càn 9 hỏa nên là cục toạ Thoái nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng càn, thìn, đinh,ngọ <br> 3.Cung vị sơn:    sơn càn(tử), thìn(tôn), đinh,ngọ(tôn)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn tuất, quý, tý, canh,thân, giáp, dần, tốn    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:   sửu(tử), bính,tỵ(tôn), khôn(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn nhâm, hợi, cấn, ất,mão, dậu, tân, mùi   là tấn thần.<br> Cần thấp, xa< 100m ")
                else:
                    n=(" 1.Toạ Tỵ(-7) Tấn 6 kim khắc xuất hướng Hợi 1 thuỷ nên là cục toạ Tấn nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng mùi, khôn, tân, dậu, bính,tỵ, sửu <br> 3.Cung vị sơn:      sơn nhâm, hợi(tôn), cấn(tử), ất,mão(tử)    là thoái thần <br> Cần cao, xa> 100m không đáp ứng ảnh hưởng đinh <br> -   sơn mùi, khôn, tân, dậu, bính tý, sửu    là tấn thần. <br> Cần cao , xa <100m.  <br>4. Các cung vị thuỷ:    canh,thân(tử), tuất(tử), quý, tý(tôn)   là thoái thần. <br> Cần thấp , xa >100m. không đáp ứng ảnh hưởng tài<br> - Các sơn đinh,ngọ, càn, giáp, dần, tốn,thìn   là tấn thần.<br> Cần thấp, xa< 100m ")

                doors, df_son = extract_phongthuy_data(n)
                
                def get_label_index(name, labels_24):
                    for i, n in enumerate(labels_24):
                        # Nếu tên cửa nằm trong nhãn (vd: "Bính" trùng "Bính", hoặc "Bính Ngọ" cũng match "Bính")
                        if name.strip() in n:
                            return i
                    return None
                
                radius_icon = radius*0.75
                theta = np.linspace(0, 2*np.pi, len(labels_24), endpoint=False) + np.pi/2
                def chuan_hoa_ten(ten):
                    # Chỉ in hoa ký tự đầu, còn lại thường (tốt nhất cho trường hợp tiếng Việt không dấu)
                    return ten.strip().capitalize()
                
                doors = [chuan_hoa_ten(d) for d in doors]
                for door in doors:
                    idx = get_label_index(door, labels_24)
                    if idx is not None:
                        angle = theta[idx]
                        x_icon = x_center + np.cos(angle)*radius_icon
                        y_icon = y_center + np.sin(angle)*radius_icon
                        ax.text(x_icon, y_icon, "Cửa", ha='center', va='center', fontsize=12, color='purple',fontweight='bold', zorder=99)
                # Chỉ tính diem_chi_tiet khi df_son không rỗng
                if not df_son.empty:
                    df_son['son'] = df_son['son'].apply(chuan_hoa_ten)
                    median_z = np.median(data_array)
                    diem_tong = 0
                    diem_chi_tiet = []
                    for _, row in df_son.iterrows():
                        idx = get_label_index(row['son'], labels_24)
                        if idx is not None:
                            angle = theta[idx]
                            # ... như cũ ...
                            # Tìm vị trí trên DEM
                            px = x_center + np.cos(angle)*radius*0.7
                            py = y_center + np.sin(angle)*radius*0.7
                            lon_px, lat_px = transformer.transform(px, py, direction="INVERSE")
                            i = np.argmin(np.abs(yt - lat_px))
                            j = np.argmin(np.abs(xt - lon_px))
                            value = data_array[i, j]
                            if row['zone'] == "cung vị sơn":
                                diem = 1 if value >= median_z else -1
                            elif row['zone'] == "cung vị thủy":
                                diem = 1 if value <= median_z else -1
                            else:
                                diem = 0
                            diem_tong += diem
                            diem_chi_tiet.append({
                                'son': row['son'],
                                'zone': row['zone'],
                                'group': row['group'],
                                'giatri': value,
                                'median': median_z,
                                'diem': diem
                            })
                
                    # ... Hiển thị điểm tổng/phụ ...
                    st.markdown(f"### `{diem_tong}`")
                
                    for _, row in df_son.iterrows():
                        idx = get_label_index(row['son'], labels_24)
                        if idx is not None:
                            angle = theta[idx]
                            if (row['group'] == "tấn"):
                                r_icon = 100
                            else:
                                r_icon = radius * 0.9
                    
                            x_icon = x_center + np.cos(angle) * r_icon
                            y_icon = y_center + np.sin(angle) * r_icon
                    
                            # Chọn icon & màu sắc
                            if row['zone'] == "cung vị sơn" and row['group'] == "thoái":
                                icon = "Sơn"
                                color = "red"
                                color_score = "red"
                            elif row['zone'] == "cung vị sơn" and row['group'] == "tấn":
                                icon = "S"
                                color = "red"
                                color_score = "red"
                            elif row['zone'] == "cung vị thủy" and row['group'] == "thoái":
                                icon = "Thủy"
                                color = "blue"
                                color_score = "blue"
                            elif row['zone'] == "cung vị thủy" and row['group'] == "tấn":
                                icon = "T"
                                color = "blue"
                                color_score = "blue"
                            else:
                                continue
                    
                            # Vẽ icon
                            ax.text(
                                x_icon, y_icon, icon,
                                ha='center', va='center',
                                fontsize=12,
                                fontweight='bold',
                                zorder=98,
                                color=color
                            )
                            
                            # Vẽ dấu +/-
                            diem_val = None
                            for diem in diem_chi_tiet:
                                if diem['son'] == row['son'] and diem['zone'] == row['zone'] and diem['group'] == row['group']:
                                    diem_val = diem['diem']
                                    break
                            if diem_val is not None:
                                dau = "+" if diem_val > 0 else "-"
                                # Offset nhỏ hơn nếu icon là "S" hoặc "T"
                                if icon in ["S", "T"]:
                                    offset_x = 6   # sát hơn
                                else:
                                    offset_x = 30   # xa hơn
                                ax.text(
                                    x_icon + offset_x, y_icon,
                                    dau,
                                    ha='left', va='center',
                                    fontsize=10,
                                    fontweight='bold',
                                    color=color_score,
                                    zorder=100,
                                    bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.01', alpha=0.8)
                                )
                        
                            
                ax.set_axis_off()
                scale_length = 100  # 100m
                # Chọn vị trí đặt scale bar (ở góc trái dưới)
                x_start = x0 + 10   # cách mép trái 30m cho đẹp, tùy bạn chỉnh
                y_start = y0 + 20   # cách mép dưới 30m cho đẹp, tùy bạn chỉnh
                x_end = x_start + scale_length
                ax.set_title(f"Sơ đồ địa mạch ({diachi} {x:.6f}, {y:.6f})|Hiệu số: {diem_tong}| Từ thiên: {declination_str}°", 
    fontsize=16, fontweight='bold', color='#f9d423', pad=18) 
                
                # Vẽ thanh thước
                ax.plot([x_start, x_end], [y_start, y_start], color='white', linewidth=4, solid_capstyle='round', zorder=20)
                # Vẽ hai gạch đứng ở hai đầu (nếu thích)
                ax.plot([x_start, x_start], [y_start-10, y_start+10], color='white', linewidth=2, zorder=20)
                ax.plot([x_end, x_end], [y_start-10, y_start+10], color='white', linewidth=2, zorder=20)
                # Thêm chú thích "100m"
                ax.text((x_start + x_end)/2, y_start-+5, "100m", color='white', fontsize=14,fontweight='bold', ha='center', va='top', zorder=21)
                plot_bearing_circle(ax, x_center, y_center, radius*0.672)
                # === Vẽ dải Mạch chính ===
                bearing_main = manual_bearing if manual_bearing is not None else bearing
                if show_main:
                    plot_parallel_zones(
                        ax, x_center, y_center,
                        radius=100,
                        bearing_deg=bearing_main,
                        d=distance_between_zones,
                        offset_d=offset_d,
                        rotate_angle=rotate_angle,
                        ratio_red=ratio_red,
                    )
                
                # === Vẽ dải Mạch phụ (vuông góc với mạch chính) ===
                bearing_deg2 = (bearing_main + 90) % 360
                if show_sub:
                    plot_parallel_zones2(
                        ax, x_center, y_center,
                        radius=100,
                        bearing_deg2=bearing_deg2,
                        d2=distance_between_zones2,
                        offset_d2=offset_d2,
                        rotate_angle2=rotate_angle2,
                        ratio_red2=ratio_red2
                    )

                plt.tight_layout()
                st.pyplot(fig)
                st.markdown(f"**Chú giải phong thủy:**<br>{n}", unsafe_allow_html=True)
                # Nếu muốn hiển thị chi tiết:
                df_diem = pd.DataFrame(diem_chi_tiet)
                if not df_diem.empty:
                    st.dataframe(df_diem)
                plt.close(fig)
                
                data = data_array.ravel()
                mean = np.mean(data)
                std = np.std(data)
                median_z = np.median(data)
                p90 = np.percentile(data, 90)
                p5 = np.percentile(data, 5)
                
                fig_hist, ax_hist = plt.subplots(figsize=(6, 3))
                
                # Histogram
                n, bins, patches = ax_hist.hist(data, bins=30, color='gold', alpha=0.75, edgecolor='k', density=True, label='Histogram')
                def detect_outlier_iqr(data, k=1.5):
                    Q1 = np.percentile(data, 25)
                    Q3 = np.percentile(data, 75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - k * IQR
                    upper_bound = Q3 + k * IQR
                    return (data < lower_bound) | (data > upper_bound)
                
                # Tính mask outlier trước đó
                outlier_mask = detect_outlier_iqr(data)
                
                # KDE
                kde = gaussian_kde(data)
                x_kde = np.linspace(data.min(), data.max(), 200)
                ax_hist.plot(x_kde, kde(x_kde), color='green', linewidth=2, label='KDE (Mật độ thực tế)')
                
                # Normal distribution fit
                x_norm = np.linspace(data.min(), data.max(), 200)
                ax_hist.plot(x_norm, norm.pdf(x_norm, mean, std), 'r-', linewidth=2, label='Normal fit (chuẩn)')
                
                # Đánh dấu các outlier lên biểu đồ
                # Lấy tọa độ y cho scatter (đặt ở đáy đồ thị)
                y_min, y_max = ax_hist.get_ylim()
                y_outlier = np.full(np.sum(outlier_mask), y_min + 0.02*(y_max-y_min))  # đặt sát đáy, cao hơn tí cho dễ nhìn
                ax_hist.scatter(data[outlier_mask], y_outlier, color='red', marker='x', s=60, label='Outlier (IQR)')
                
                # Các đường thẳng
                ax_hist.axvline(median_z, color='red', linestyle='--', linewidth=2, label=f'Median: {median_z:.2f}')
                ax_hist.axvline(p90, color='darkorange', linestyle='-', linewidth=2, label=f'90%: {p90:.2f}')
                ax_hist.axvline(p5, color='blue', linestyle='-', linewidth=2, label=f'5%: {p5:.2f}')
                
                ax_hist.set_title('Phân bố dữ liệu')
                ax_hist.set_xlabel('Giá trị')
                ax_hist.set_ylabel('Mật độ xác suất')
                ax_hist.legend(prop={'size': 7})
                ax_hist.grid(True, linestyle='--', alpha=0.5)
                
                outlier_mask = detect_outlier_iqr(data)
                outliers = data[outlier_mask]
                
                diff = kde(x_kde) - norm.pdf(x_kde, mean, std)
                crossings = np.where(np.diff(np.sign(diff)))[0]  # vị trí các điểm giao
                cross_x = x_kde[crossings]
                if len(cross_x) > 0:
                    min_cross = cross_x.min()
                    max_cross = cross_x.max()
                    ax_hist.axvline(min_cross, color='purple', linestyle=':', linewidth=1.5, label=f'Min crossing: {min_cross:.2f}')
                    ax_hist.axvline(max_cross, color='brown', linestyle=':', linewidth=1.5, label=f'Max crossing: {max_cross:.2f}')
                    
                else:
                    st.write("Không tìm thấy điểm giao cắt giữa KDE và normal fit.")
                ax_hist.legend(prop={'size': 7})
                st.pyplot(fig_hist)
                plt.close(fig_hist)
        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {e}")
  
    st.markdown("### 2. Chiêm tinh Ấn Độ")
    astrology_block()
    st.markdown("""
    ### 3.🌐Biểu đồ cộng hưởng Schumann 
    Nguồn: [Tomsk, Russia Space Observing System]
    """)
    st.image("https://sosrff.tsu.ru/new/shm.jpg", caption="Schumann Resonance - Live", use_container_width=True)
    st.markdown("""### Tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng. 
    Dữ liệu code nguồn không sao chép dưới mọi hình thức. 
    SĐT&ZALO: 0377442597. 
    DONATE: nguyenduytuan techcombank 19033167089018
    """)

if __name__ == "__main__":
    main()
