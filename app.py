import streamlit as st
import os
import pandas as pd
import streamlit.components.v1 as components
import math
from datetime import date, timedelta, datetime
import swisseph as swe
import pytz
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
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
st.set_page_config(layout="wide")
def main():
    
    st.markdown("""
    <div style="background:linear-gradient(90deg,#f9d423,#ff4e50);padding:24px 8px 20px 8px;border-radius:16px;margin-bottom:24px;">
        <h1 style='color:white;text-align:center;margin:0;font-size:36px;'>🔯 ỨNG DỤNG  ĐỊA LÝ & CHIÊM TINH </h1>
        <p style='color:white;text-align:center;font-size:20px;margin:0;'>Kết hợp Chiêm tinh, Địa mạch, số liệu Từ trường</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 1. Chiêm tinh Ấn Độ")
    astrology_block()
     # 1. tính ========================
       # --- Giao diện nhập ---
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        input_str = st.text_input("Nhập x,y", value="")
    with col2:
        dt = st.number_input("dt", min_value=0.001, max_value=0.02, value=0.005, step=0.002, format="%.3f")
    with col4:
        run = st.button("Run", use_container_width=True)
    
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
                
                # --- Hàm vẽ vòng Fibonacci ---
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
                img, ext = ctx.bounds2img(x0, y0, x1, y1, ll=False, source=ctx.providers.Esri.WorldImagery, zoom=18)
                ax.imshow(img, extent=ext, origin="upper")
                ax.set_xlim(x0, x1)
                ax.set_ylim(y0, y1)
                
                # Vẽ contour DEM
                levels = np.linspace(data_array.min(), data_array.max(), 21)
                cmap = cm.get_cmap('rainbow')
                norm = mcolors.Normalize(vmin=np.min(levels), vmax=np.max(levels))
                data_smooth = gaussian_filter(data_array, sigma=1.2)
                ax.contourf(Xx3857, Yx3857, data_smooth, cmap="rainbow", levels=levels, alpha=0)
                ax.contour(Xx3857, Yx3857, data_smooth, levels=levels, cmap='rainbow', linewidths=1)
                threshold = np.percentile(data_array, 90)
                threshold1 = np.percentile(data_array, 2)
                for level in levels:
                    if level >= threshold:
                        color = cmap(norm(level))
                        ax.contour(Xx3857, Yx3857, data_smooth, levels=[level], colors=[color], linewidths=3)
                    if level <= threshold1:
                        color = cmap(norm(level))
                        ax.contour(Xx3857, Yx3857, data_smooth, levels=[level], colors=[color], linewidths=2)
                # Vẽ vòng Fibonacci
                plot_fibonacci_labels_only(ax, x_center, y_center, labels_24, radius=radius)
                
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
                
                # Vẽ arrow từ max về center
                arrow_scale = 2.3  # gấp đôi độ dài gốc, tuỳ bạn

                dx = x_max - x_center_map
                dy = y_max - y_center_map
                # Điểm cuối ngược hướng max (so với center)
                arrow_dx = -arrow_scale * dx
                arrow_dy = -arrow_scale * dy
                
                # Vẽ arrow từ center ra đối diện với max
                ax.arrow(
                    x_center_map, y_center_map,   # Gốc là center
                    arrow_dx, arrow_dy,           # Vector ngược hướng max
                    head_width=10,
                    head_length=5,
                    linewidth=2,
                    color='white',        # Mũi tên trắng, viền đen nổi bật
                    length_includes_head=True,
                    zorder=10
                )
                dlon = lon_max - lon0
                dlat = lat_max - lat0
                bearing1 = (np.degrees(np.arctan2(dlon, dlat)) + 360) % 360
                bearing = (bearing1 + 180) % 360   # Bearing hướng từ max về tâm
                
                st.markdown(f"**Chỉ số Bearing :** `{bearing:.1f}°`")
                if 337.5<=float(bearing)<352.5:
                    n=(" 1.Toạ Bính(-2) Tấn 6 kim khắc xuất hướng Nhâm -1 thuỷ nên là cục toạ Tấn nghi Thoái. Hùng dự Hùng<br>     2. Cửa chính,phụ: Mở ở hướng bính tỵ, Tân, Dậu, Mùi Khôn, Sửu <br>      3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br>       Trong đó sơn Nhâm Hợi(tôn), Cấn(tử), Ất Mão(tử)  sinh xuất, khắc xuất là thoái thần <br>  cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh   <br>   - Với sơn mùi khôn, tân dậu, sửu, bính tỵ sinh khắc nhập nên là tấn thần.<br>Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.<br>    4. Các cung vị thuỷ: là các sơn có số 16. Các sơn tý quý(tôn), thân canh(tử), tuất(tử) sinh khắc xuất là thoái thần. <br>    Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài.<br>     - Các sơn giáp dần, tốn thìn, ngọ đinh, càn sinh khắc nhập là tấn thần. Cần có thủy trong 100m." )
                elif 352.5<=float(bearing)<360:
                    n=(" 1.Toạ Ngọ(-6) Tấn 6 kim khắc xuất hướng Tý 1 thuỷ nên là cục toạ Tấn nghi Thoái. Hùng dự Thư<br>     2. Cửa chính,phụ: Mở ở hướng giáp,dần,thìn tốn,đinh ngọ, càn <br>      3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br>       Trong đó sơn quý tý(tôn), canh thân(tử), tuất(tử) sinh xuất, khắc xuất là thoái thần <br>  cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br>   - Với sơn giáp dần, tốn, đinh ngọ, càn sinh khắc nhập nên là tấn thần. <br>    Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn nhâm hợi(tôn), cấn(tử), ất mão(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn sửu, bính tỵ, mùi khôn, tân dậu sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 0<=float(bearing)<7.5:
                    n=(" 1.Toạ Ngọ(-1) Tấn 6 kim khắc xuất hướng Tý 1 thuỷ nên là cục toạ Tấn nghi Thoái. Hùng dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng giáp,dần,thìn tốn,đinh ngọ, càn <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn quý tý(tôn), canh thân(tử), tuất(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn giáp dần, tốn, đinh ngọ, càn sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn nhâm hợi(tôn), cấn(tử), ất mão(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn sửu, bính tỵ, mùi khôn, tân dậu sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 7.5<=float(bearing)<22.5:
                    n=(" 1.Toạ Đinh(-1) Tấn 6 kim khắc xuất hướng Quý 1 thuỷ nên là cục toạ Tấn nghi Thoái. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng giáp,dần, thìn tốn,đinh ngọ, càn <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn quý tý(tôn), canh thân(tử), tuất(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn giáp dần, tốn, đinh ngọ, càn sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn nhâm hợi(tôn), cấn(tử), ất mão(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn sửu, bính tỵ, mùi khôn, tân dậu sinh khắc nhập là tấn thần.<br>   Các sơn này cần có thủy trong 100m ")
                elif 22.5<=float(bearing)<37.5:
                    n=(" 1.Toạ Mùi(2) Thoái 4 mộc sinh xuất hướng Sửu 9 hoả nên là cục toạ Thoái nghi Thoái. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng sửu, bính,tỵ,khôn<br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn sửu(tử), bính tỵ(tôn), khôn(tôn) khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn nhâm hợi,cấn,ất mão, mùi, dậu tân sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn càn(tử), thìn(tôn), đinh ngọ(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn canh thân, tuất, quý tý, giáp dần, tốn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m  ")
                elif 37.5<=float(bearing)<52.5:
                    n=(" 1.Toạ Khôn(7) Thoái 7 kim sinh xuất hướng Cấn 2 thổ nên là cục toạ Thoái nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng cấn, ất mão, nhâm hợi  <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn nhâm hợi(tôn),cấn(tử),ất mão(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn tân dậu,sửu, mùi khôn, tị bính sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn canh thân(tử), tuất(tử), quý tý(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn càn,giáp dần,tốn, ngọ đinh, thìn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m  ")
                elif 52.5<=float(bearing)<67.5:
                    n=(" 1.Toạ Thân(-6) Tấn 8 thổ khắc xuất hướng Dần 3 mộc nên là cục toạ Tấn nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng càn,thìn,đinh ngọ,thân canh, tuất <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn quý tý(tử), giáp dần(tôn), tốn(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn thìn, đinh ngọ, càn, thân canh, tuất sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn mùi(tôn), nhâm hợi(tử),tân dậu(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>- Các sơn sửu, bính tỵ, khôn, mão ất, cấn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 67.5<=float(bearing)<82.5:
                    n=(" 1.Toạ Canh(-1) Thoái 8 thổ khắc xuất hướng Giáp 3 mộc nên là cục toạ Thoái nghi Thoái. Hùng dự Hùng <br> 2. Cửa chính,phụ: Mở ở hướng Tý Quý, giáp dần, tốn<br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn quý tý(tử), giáp dần(tôn), tốn(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn càn, thìn, đinh ngọ, thân canh, tuất sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn tân dậu(tôn), nhâm hợi(tử), mùi (tôn)sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn sửu,bính tỵ, khôn,ất mão, cấn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 82.5<=float(bearing)<97.5:
                    n=(" 1.Toạ Dậu(-7) Tấn 3 mộc cùng hành hướng Mão 8 thổ nên là cục toạ Tấn nghi Tấn. Hùng dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng nhâm hợi, cấn, ất, mão, dậu tân, mùi  <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn sửu(tử), bính tỵ(tôn), khôn(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn nhâm hợi, cấn, ất mão, dậu tân, mùi sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn càn(tử), thìn(tôn), đinh ngọ(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn tuất, quý tý, canh thân, giáp dần, tuất sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 97.5<=float(bearing)<112.5:
                    n=(" 1.Toạ Tân(-2) Tấn 3 mộc khắc nhập hướng Ất 8 thổ nên là cục toạ Tấn nghi Tấn. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng nhâm hợi, cấn, ất, mão, mùi, dậu tân  <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn sửu(tử), bính tỵ(tôn), khôn(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn nhâm hợi, cấn, ất mão, mùi, dậu tân sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn càn(tử), thìn(tôn), đinh ngọ(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn tuất, quý tý, canh thân,giáp dần, tốn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 112.5<=float(bearing)<127.5:
                    n=(" 1.Toạ Tuất(-6) Thoái 2 thổ sinh nhập hướng Thìn 7 kim nên là cục toạ Thoái nghi Tấn. Hùng dự Hùng <br> 2. Cửa chính,phụ: Mở ở hướng quý tý, giáp dần, tốn  <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn quý tý(tử), giáp dần(tôn), tốn(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn thìn, đinh ngọ, càn, thân canh, tuất sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn nhâm hợi(tử), mùi(tôn), tân dậu(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn sửu, bính tỵ, khôn, cấn, mão ất sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 127.5<=float(bearing)<142.5:
                    n=(" 1.Toạ Càn(-1) Tấn 9 hoả sinh nhập hướng Tốn 4 mộc nên là cục toạ Tấn nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng quý tý, giáp dần, tốn, càn  <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn thìn(tử), đinh ngọ(tử), canh thân(tôn), tuất(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn tý quý, giáp dần, tốn, càn sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn ất mão(tôn), tỵ bính(tử), khôn(tử), cấn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn hợi nhâm, mùi, dậu tân, sửu sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 142.5<=float(bearing)<157.5:
                    n=(" 1.Toạ Hợi(2) Thoái 1 thuỷ khắc nhập hướng Tỵ 6 kim nên là cục toạ Thoái nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng mùi, dậu tân, sửu  <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn mùi(tử), dậu tân(tử), sửu(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn nhâm hợi, cấn ,ất mão, bính tỵ sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn càn(tôn), giáp dần(tử), tốn(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  .<br> - Các sơn đinh ngọ, canh thân, tuất, quý tý, thìn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 157.5<=float(bearing)<172.5:
                    n=(" 1.Toạ Nhâm(7) Tấn 1 thuỷ khắc nhập hướng Bính 6 kim nên là cục toạ Tấn nghi Tấn. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng nhâm,cấn,ất mão, bính tỵ, khôn, nhâm hợi  <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn sửu(tôn), mùi(tử), tân dậu(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn nhâm, cấn, ất mão, bính tỵ, khôn, nhâm hợi sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn giáp dần(tử), tốn(tử), càn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn quý tý, thìn, đinh ngọ, canh thân, tuất sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 172.5<=float(bearing)<187.5:
                    n=(" 1.Toạ Tý(1) Tấn 1 thuỷ khắc nhập hướng Ngọ 6 kim nên là cục toạ Tấn nghi Tấn. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng quý tý, thìn, đinh ngọ, canh thân, tuất  <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn càn(tôn), giáp dần(tử), tốn(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn quý tý, thìn, đinh ngọ, canh thân, tuất sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn sửu(tôn), mùi(tử), tân dậu(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn nhâm, cấn, ất mão, bính tỵ, khôn, nhâm hợi sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 187.5<=float(bearing)<202.5:
                    n=(" 1.Toạ Quý(6) Thoái 1 thuỷ khắc nhập  hướng Đinh 6 kim nên là cục toạ Thoái nghi Tấn. Hùng dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng giáp dần, tốn, càn <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn càn(tôn), giáp dần(tử), tốn(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn quý tý, thìn, đinh ngọ, canh thân, tuất sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn sửu(tôn), mùi(tử), tân dậu(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  .<br> - Các sơn nhâm, cấn, ất mão, bính tỵ, khôn, nhâm hợi sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 202.5<=float(bearing)<217.5:
                    n=(" 1.Toạ Sửu(-7) Tấn 9 hoả sinh nhập hướng Mùi 4 mộc nên là cục toạ Tấn nghi Tấn. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng tân dậu, nhâm hợi, sửu, mùi  <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn khôn(tử), ất mão(tôn), bính tỵ(tử), cấn(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn tân dậu, nhâm hợi, sửu, mùi sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn đinh ngọ(tử), canh thân(tôn), tuất(tôn), thìn(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn càn, quý tý, giáp dần, tốn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 217.5<=float(bearing)<232.5:
                    n=(" 1.Toạ Cấn(-2) Thoái 2 thổ sinh nhập hướng Khôn 7 kim nên là cục toạ Thoái nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng mùi, tân dậu, nhâm hợi <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn mùi(tôn), tân dậu(tôn), nhâm hợi(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn khôn, cấn sửu, ất mão, bính tỵ sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn quý tý(tử), giáp dần(tôn), tốn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br>  - Các sơn đinh ngọ, canh thân, tuất thìn, càn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 232.5<=float(bearing)<247.5:
                    n=(" 1.Toạ Dần(1) Tấn 3 mộc khắc nhập hướng Thân 8 thổ nên là cục toạ Tấn nghi Tấn. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng tuất, quý tý, canh thân, giáp dần, tốn  <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn càn(tử), thìn(tôn), đinh ngọ(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn tuất, quý tý, canh thân, giáp dần, tốn sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn sửu(tử), bính tỵ(tôn), khôn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn nhâm hợi, cấn, ất mão, dậu tân, mùi sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 247.5<=float(bearing)<262.5:
                    n=(" 1.Toạ Giáp(6) Tấn 3 mộc khắc nhập hướng Canh 8 thổ nên là cục toạ Tấn nghi Tấn. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng tuất, quý tý, canh thân, giáp dần, tốn  <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn càn(tử), thìn(tôn), đinh ngọ(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn tuất, quý tý, canh thân, giáp dần, tốn sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn sửu(tử), bính tỵ(tôn), khôn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn nhâm hợi, cấn, ất mão, dậu tân, mùi sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 262.5<=float(bearing)<277.5:
                    n=(" 1.Toạ Mão(2) Thoái 8 thổ khắc xuất hướng Dậu 3 mộc nên là cục toạ Thoái nghi Thoái. Thư dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng mùi, tân dậu, nhâm hợi  <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn mùi(tôn), tân dậu(tôn), nhâm hợi(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn khôn, cấn sửu, ất mão, bính tỵ sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn quý tý(tử), giáp dần(tôn), tốn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn đinh ngọ, canh thân, tuất, thìn, càn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 277.5<=float(bearing)<292.5:
                    n=(" 1.Toạ Ất(7) Tấn 8 thổ khắc xuất hướng Tân 3 mộc nên là cục toạ Tấn nghi Thoái. Hùng dự thư<br> 2. Cửa chính,phụ: Mở ở hướng khôn, cấn sửu, ất mão, bính tỵ <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn mùi(tôn), tân dậu(tôn), nhâm hợi(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn khôn, cấn sửu, ất mão, bính tỵ sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn quý tý(tử), giáp dần(tôn), tốn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn đinh ngọ, canh thân, tuất, thìn, càn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 292.5<=float(bearing)<307.5:
                    n=(" 1.Toạ Thìn(1) Thoái 7 kim sinh xuất hướng Tuất 2 thổ nên là cục toạ Thoái nghi Thoái. Hùng dự Hùng<br> 2. Cửa chính,phụ: Mở ở hướng canh thân, tuất, quý tý  <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn quý tý(tôn), canh thân(tử), tuất(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn càn, giáp dần, đinh ngọ, tốn thìn sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn nhâm hợi(tôn), cấn(tử), ất mão(tử) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn sửu, bính tỵ, mùi khôn, tân dậu sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                elif 307.5<=float(bearing)<322.5:
                    n=(" 1.Toạ Tốn(6) Thoái 4 mộc sinh xuất hướng Càn 9 hỏa nên là cục toạ Thoái nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng càn, thìn, đinh ngọ <br> 3.Cung vị sơn: Vì toạ hướng là 16 nên cần thu sơn 16.<br> Trong đó sơn càn(tử), thìn(tôn), đinh ngọ(tôn) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn tuất, quý tý, canh thân, giáp dần, tốn sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 27. Các sơn sửu(tử), bính tỵ(tôn), khôn(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn nhâm hợi, cấn, ất mão, dậu, tân, mùi sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                else:
                    n=(" 1.Toạ Tỵ(-7) Tấn 6 kim khắc xuất hướng Hợi 1 thuỷ nên là cục toạ Tấn nghi Thoái. Thư dự Thư<br> 2. Cửa chính,phụ: Mở ở hướng mùi khôn, tân dậu, bính tỵ, sửu <br> 3.Cung vị sơn: Vì toạ hướng là 27 nên cần thu sơn 27.<br> Trong đó sơn nhâm hợi(tôn), cấn(tử), ất mão(tử) sinh xuất, khắc xuất là thoái thần <br> cần có núi, nhà cao, nhiều nhà ở xa từ 100 đến 1500m. Nếu ở sơn có thủy thì là phản ngâm chủ bại nhân đinh <br> - Với sơn mùi khôn, tân dậu, bính tý, sửu sinh khắc nhập nên là tấn thần. <br> Các sơn này có núi, nhà cao tầng, nhiều nhà trong 100m trở lại.  <br>4. Các cung vị thuỷ: là các sơn có số 16. Các sơn canh thân(tử), tuất(tử), quý tý(tôn) sinh khắc xuất là thoái thần. <br> Các sơn này có thuỷ, ngã tư đường, công viên bãi đỗ xe từ 100 đến 1500m. Nếu các thủy này lại có sơn là phục ngâm, chủ bại tài   <br> - Các sơn đinh ngọ, càn, giáp dần, tốn thìn sinh khắc nhập là tấn thần.<br> Các sơn này cần có thủy trong 100m ")
                
                
                ax.set_axis_off()
                plt.tight_layout()
                st.pyplot(fig)
                st.markdown(f"**Chú giải phong thủy:**<br>{n}", unsafe_allow_html=True)
                plt.close(fig)
        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {e}")
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
