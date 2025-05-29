import streamlit as st
import swisseph as swe
import pandas as pd
import numpy as np
import pytz
from datetime import datetime, date
import matplotlib.pyplot as plt
import re
import io
import textwrap
def plot_mahadasha_table(df_dasha, title="Bảng Mahadasha (Vimsottari Dasa)"):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.axis('off')
    table = ax.table(
        cellText=df_dasha.values,
        colLabels=df_dasha.columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(True)
    table.set_fontsize(16)
    table.scale(1, 2)  # Tăng chiều cao row
    # Đổi màu header
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_fontsize(18)
            cell.set_facecolor("#ffe299")
            cell.set_text_props(weight='bold')
    ax.set_title(title, fontsize=20, pad=20)
    plt.tight_layout()
    return fig

def plot_detect_yoga_matplotlib(yoga_list, max_width=90):
    if isinstance(yoga_list, str):
        yoga_list = [line.strip("-• ") for line in yoga_list.split("\n") if line.strip() and not line.startswith("####")]

    if not yoga_list or (len(yoga_list) == 1 and "không phát hiện" in yoga_list[0].lower()):
        yoga_list = ["Không phát hiện Yoga/Dosha đặc biệt nổi bật nào."]

    wrapped_yoga = ["\n".join(textwrap.wrap(line, max_width)) for line in yoga_list]

    # Không header, chỉ nội dung
    fig, ax = plt.subplots(figsize=(19, min(1.2 + 0.8*len(wrapped_yoga), 16)))
    ax.axis('off')
    table = ax.table(
        cellText=[[line] for line in wrapped_yoga],
        cellLoc='left',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(24)  # CHỮ TO HẲN
    table.scale(1.45, 1.32)
    for key, cell in table.get_celld().items():
        cell.set_linewidth(0)
        cell.set_facecolor('#ffffff')
        cell.set_height(0.16 + 0.048 * wrapped_yoga[key[0]].count('\n'))
    # Title lớn
    ax.text(0.5, 1.2, 'Cách cục Yoga', ha='center', va='bottom', fontsize=35, fontweight='bold', transform=ax.transAxes)
    plt.tight_layout()
    return fig
def plot_ashtakavarga_table(df_bav):
    import matplotlib.pyplot as plt
    rows = df_bav.index.tolist()
    cols = df_bav.columns.tolist()
    fig, ax = plt.subplots(figsize=(1.4 + 0.5*len(cols), 1.2 + 0.35*len(rows)))
    ax.axis('off')
    table = ax.table(
        cellText=df_bav.values,
        rowLabels=rows,
        colLabels=cols,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.12, 1.17)
    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor('#ffffff')
        cell.set_edgecolor('black')
        cell.set_linewidth(1)
        if row == 0 or col == -1:
            cell.set_text_props(weight='bold', color='navy')
    # Đặt title sát trên bảng (0.98 là sát, 1 là mép trên)
    ax.text(0.5, 0.8, 'Bảng Ashtakavarga', ha='center', va='bottom', fontsize=12, fontweight='bold', transform=ax.transAxes)
    plt.tight_layout()
    return fig
def plot_planet_table(df_planets, user_name=None):
    # Bỏ cột cuối cùng (dù tên là gì)
    df_no_last_col = df_planets.iloc[:, :-1]
    fig, ax = plt.subplots(figsize=(1.6 + 0.7 * df_no_last_col.shape[1], 0.8 + 0.3 * df_no_last_col.shape[0]))
    ax.axis('off')
    table = ax.table(
        cellText=df_no_last_col.values,
        colLabels=df_no_last_col.columns,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.1, 1.2)
    if user_name:
        plt.title(f"Vị trí hành tinh – {user_name}", fontsize=12, pad=12)
    else:
        plt.title("Vị trí hành tinh", fontsize=12, pad=12)
    plt.tight_layout()
    return fig
BAV_BinduMatrix = {
    "Sun":     {"Sun":[1,2,4,7,8,9,10,11], "Moon":[3,6,10,11], "Mars":[1,2,4,7,8,9,10,11], "Mercury":[3,5,6,9,10,11,12], "Jupiter":[5,6,9,11], "Venus":[6,7,12], "Saturn":[1,2,4,7,8,9,10,11], "Ascendant":[3,4,6,10,11,12]},
    "Moon":    {"Sun":[3,6,7,8,10,11], "Moon":[1,3,6,7,10,11], "Mars":[2,3,5,6,9,10,11], "Mercury":[1,3,5,6,9,10,11], "Jupiter":[1,4,7,8,10,11,12], "Venus":[3,4,5,7,9,10,11], "Saturn":[3,5,6,11], "Ascendant":[3,6,10,11]},
    "Mars":    {"Sun":[3,5,6,10,11], "Moon":[3,6,11], "Mars":[1,2,4,7,8,10,11], "Mercury":[3,5,6,11], "Jupiter":[6,10,11,12], "Venus":[6,8,11,12], "Saturn":[1,7,8,9,10,11], "Ascendant":[1,3,6,10,11]},
    "Mercury": {"Sun":[5,6,9,11,12], "Moon":[2,4,6,8,10,11], "Mars":[1,2,4,7,8,9,10,12], "Mercury":[1,3,5,6,9,10,11,12], "Jupiter":[6,8,11,12], "Venus":[1,2,3,4,5,8,9,11], "Saturn":[1,2,4,7,8,9,10,12], "Ascendant":[1,2,4,6,8,10,11]},
    "Jupiter": {"Sun":[1,2,3,4,7,8,9,10,11], "Moon":[2,5,7,9,11], "Mars":[1,2,4,7,8,10,11], "Mercury":[1,2,4,5,6,9,10,11], "Jupiter":[1,2,3,4,7,8,10,11], "Venus":[2,5,6,9,10,11], "Saturn":[3,5,6,12], "Ascendant":[1,2,4,5,6,7,9,10,11]},
    "Venus":   {"Sun":[8,11,12], "Moon":[1,2,3,4,5,8,9,11,12], "Mars":[3,4,6,9,11,12], "Mercury":[3,5,6,9,11], "Jupiter":[5,8,9,10,11], "Venus":[1,2,3,4,5,8,9,10,11], "Saturn":[3,4,5,8,9,10,11], "Ascendant":[1,2,3,4,5,8,9,11]},
    "Saturn":  {"Sun":[1,2,4,7,8,10,11], "Moon":[3,6,11], "Mars":[3,5,6,10,11,12], "Mercury":[6,8,9,10,11,12], "Jupiter":[5,6,11,12], "Venus":[6,11,12], "Saturn":[3,5,6,11], "Ascendant":[1,3,4,10,11]}
}

def compute_ashtakavarga(df_planets):
    # Đảm bảo có mapping planet -> house (số thứ tự nhà), lấy luôn Asc là nhà 1
    planet_houses = {row['Hành tinh']: row['Nhà'] for _, row in df_planets.iterrows()}
    planet_houses['Ascendant'] = 1
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    # Tạo bảng điểm rỗng
    bav_points = {pl: [0]*12 for pl in planets}
    bav_points["Tổng"] = [0]*12

    # Tính điểm cho từng hành tinh
    for planet in planets:
        for ref in BAV_BinduMatrix[planet]:
            if ref not in planet_houses:
                continue
            ref_house = planet_houses[ref]
            for nth in BAV_BinduMatrix[planet][ref]:
                idx = (ref_house + nth - 2) % 12   # python 0-based
                bav_points[planet][idx] += 1

    # Tính tổng
    for i in range(12):
        bav_points["Tổng"][i] = sum(bav_points[pl][i] for pl in planets)

    # Đưa ra dataframe cho đẹp, số cột là 12 nhà (1-12)
    df_bav = pd.DataFrame(bav_points, index=[f"{i+1}" for i in range(12)])
    return df_bav.transpose()
# Hàm chuyển đổi dms (ví dụ "12°30'15\"") thành số độ thập phân
def dms_str_to_float(dms_str):
    match = re.match(r"(\d+)°(\d+)'(\d+)?", dms_str)
    if not match:
        return float(dms_str.replace("°",""))
    d, m, s = [int(x) if x else 0 for x in match.groups()]
    return d + m/60 + s/3600

def navamsa_from_rashi_deg(cung_ten, deg_float):
    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
            "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    def navamsa_from_long(sign, pos_deg, pos_min, pos_sec):
        longi_sec = (((sign - 1) * 30 * 3600) +
                    (pos_deg * 3600) + (pos_min * 60) + pos_sec)
        amsa = ((3 * 3600) + (20 * 60))
        navamsa_index = int(longi_sec // amsa)
        navSign = 1 + navamsa_index % 12
        longi_pending_sec = longi_sec % amsa
        longi_pending_sec_normalized = ((longi_pending_sec * 30 * 3600) / amsa)
        navDeg = int(longi_pending_sec_normalized // 3600)
        navMin = int((longi_pending_sec_normalized % 3600) // 60)
        navSec = round((longi_pending_sec_normalized % 60), 2)
        return (navSign, navDeg, navMin, navSec)
    sign = rashis.index(cung_ten) + 1
    pos_deg = int(deg_float)
    pos_min = int((deg_float - pos_deg) * 60)
    pos_sec = int(round((((deg_float - pos_deg) * 60) - pos_min) * 60))
    navSign, navDeg, navMin, navSec = navamsa_from_long(sign, pos_deg, pos_min, pos_sec)
    nav_cung_ten = rashis[navSign - 1]
    return (nav_cung_ten, navDeg, navMin, navSec)
def build_navamsa_df(df_planets):
    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
              "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    # 1. Lấy vị trí Ascendant trong D1
    asc_row = df_planets[df_planets["Hành tinh"] == "Asc"].iloc[0]
    asc_d1_cung = asc_row["Cung"]
    asc_d1_deg = dms_str_to_float(asc_row["Vị trí"])
    # 2. Tìm cung của Ascendant trong D9 (dùng hàm navamsa_from_rashi_deg)
    asc_d9_cung, _, _, _ = navamsa_from_rashi_deg(asc_d1_cung, asc_d1_deg)
    asc_d9_idx = rashis.index(asc_d9_cung)  # chỉ số bắt đầu

    # 3. Build mapping cung->nhà D9
    cung2nha_d9 = {}
    for i in range(12):
        cung = rashis[(asc_d9_idx + i) % 12]
        cung2nha_d9[cung] = i + 1  # Nhà bắt đầu từ 1

    # 4. Mapping từng hành tinh
    d9_rows = []
    for _, row in df_planets.iterrows():
        deg_float = dms_str_to_float(row["Vị trí"])
        d9_cung, d9_deg, d9_min, d9_sec = navamsa_from_rashi_deg(row["Cung"], deg_float)
        d9_degree_total = d9_deg + d9_min/60 + d9_sec/3600
        # Gán nhà theo mapping từ Asc D9
        d9_nha = cung2nha_d9[d9_cung]
        d9_rows.append({
            "Hành tinh": row["Hành tinh"],
            "D9_Cung": d9_cung,
            "D9_Nhà": d9_nha,
            "D9_Độ": round(d9_degree_total, 2)
        })
    return pd.DataFrame(d9_rows)
def plot_d9_chart(df_d9):
    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
              "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    house_coords = {
        1: (50, 80), 2: (25, 95), 3: (10, 80), 4: (25, 45), 5: (15, 25), 6: (25, 5),
        7: (50, 20), 8: (75, 5), 9: (95, 25), 10: (75, 45), 11: (95, 80), 12: (75, 95)
    }
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    # Vẽ khung
    ax.plot([0, 100, 100, 0, 0], [0, 0, 100, 100, 0], 'k', linewidth=2)
    ax.plot([0, 100], [0, 100], 'k', linewidth=1)
    ax.plot([0, 100], [100, 0], 'k', linewidth=1)
    ax.plot([0, 50], [50, 100], 'k', linewidth=1)
    ax.plot([50, 100], [100, 50], 'k', linewidth=1)
    ax.plot([100, 50], [50, 0], 'k', linewidth=1)
    ax.plot([50, 0], [0, 50], 'k', linewidth=1)
    ax.plot([0, 50, 100, 50, 0], [50, 100, 50, 0, 50], 'k', linewidth=1)
    # Vẽ tên cung
    for i, (x, y) in house_coords.items():
        
       ax.text(x, y + 2, f"{i}", fontsize=6, color='red',weight='bold', ha='center')
    # Vẽ hành tinh
    for i, (x, y) in house_coords.items():
        planets = []
        for _, row in df_d9.iterrows():
            if row["D9_Nhà"] == i:
                name = row["Hành tinh"]
                deg = row["D9_Độ"]
                planets.append(f"{name} ({int(deg)}°)")
        if planets:
            ax.text(x, y, "\n".join(planets), ha='center', va='center', fontsize=7, color='blue')
    ax.set_title("Biểu đồ hậu vận", fontsize=14, pad=10)
    plt.tight_layout()
    plt.show()
    return fig

def trimsamsa_from_rashi_deg(cung_ten, deg_float):
    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
              "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    # Đổi cung sang số thứ tự
    sign = rashis.index(cung_ten) + 1
    pos_deg = int(deg_float)
    pos_min = int((deg_float - pos_deg) * 60)
    pos_sec = int(round((((deg_float - pos_deg) * 60) - pos_min) * 60))
    # Tổng số giây trong cung hiện tại
    longi_sec = (pos_deg * 3600) + (pos_min * 60) + pos_sec
    amsa = 3600  # 1 Trimsamsa = 1 độ = 3600 giây
    # Theo quy tắc Parashara
    if sign % 2 == 0:  # Cung chẵn
        if longi_sec <= 5 * 3600:
            trimsamsa_sign = 2
        elif longi_sec <= 12 * 3600:
            trimsamsa_sign = 6
        elif longi_sec <= 20 * 3600:
            trimsamsa_sign = 12
        elif longi_sec <= 25 * 3600:
            trimsamsa_sign = 10
        else:
            trimsamsa_sign = 8
    else:  # Cung lẻ
        if longi_sec <= 5 * 3600:
            trimsamsa_sign = 1
        elif longi_sec <= 10 * 3600:
            trimsamsa_sign = 11
        elif longi_sec <= 18 * 3600:
            trimsamsa_sign = 9
        elif longi_sec <= 25 * 3600:
            trimsamsa_sign = 3
        else:
            trimsamsa_sign = 7
    # Vị trí trong cung trimsamsa
    longi_pending_sec = (longi_sec % amsa)
    longi_pending_sec_normalized = ((longi_pending_sec * 30 * 3600) / amsa)   # chuẩn hóa sang thang 30°
    d30_deg = int(longi_pending_sec_normalized / 3600)
    longi_pending_sec_normalized = (longi_pending_sec_normalized % 3600)
    d30_min = int(longi_pending_sec_normalized / 60)
    d30_sec = round(longi_pending_sec_normalized % 60, 2)
    trimsamsa_cung_ten = rashis[trimsamsa_sign - 1]
    return (trimsamsa_cung_ten, d30_deg, d30_min, d30_sec)
def build_trimsamsa_df(df_planets):
    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
              "Thiên Bình", "Bọ Cạp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    # Xác định cung trimsamsa của Ascendant
    asc_row = df_planets[df_planets["Hành tinh"] == "Asc"].iloc[0]
    asc_d1_cung = asc_row["Cung"]
    asc_d1_deg = dms_str_to_float(asc_row["Vị trí"])
    asc_d30_cung, _, _, _ = trimsamsa_from_rashi_deg(asc_d1_cung, asc_d1_deg)
    asc_d30_idx = rashis.index(asc_d30_cung)
    # Mapping cung -> nhà D30
    cung2nha_d30 = {}
    for i in range(12):
        cung = rashis[(asc_d30_idx + i) % 12]
        cung2nha_d30[cung] = i + 1  # Nhà bắt đầu từ 1
    # Build bảng
    d30_rows = []
    for _, row in df_planets.iterrows():
        deg_float = dms_str_to_float(row["Vị trí"])
        d30_cung, d30_deg, d30_min, d30_sec = trimsamsa_from_rashi_deg(row["Cung"], deg_float)
        d30_degree_total = d30_deg + d30_min/60 + d30_sec/3600
        d30_nha = cung2nha_d30[d30_cung]
        d30_rows.append({
            "Hành tinh": row["Hành tinh"],
            "D30_Cung": d30_cung,
            "D30_Nhà": d30_nha,
            "D30_Độ": round(d30_degree_total, 2)
        })
    return pd.DataFrame(d30_rows)
def plot_d30_chart(df_d30):
    house_coords = {
        1: (50, 80), 2: (25, 95), 3: (10, 80), 4: (25, 45), 5: (15, 25), 6: (25, 5),
        7: (50, 20), 8: (75, 5), 9: (95, 25), 10: (75, 45), 11: (95, 80), 12: (75, 95)
    }
    fig, ax = plt.subplots(figsize=(3,3))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.plot([0, 100, 100, 0, 0], [0, 0, 100, 100, 0], 'k', linewidth=2)
    ax.plot([0, 100], [0, 100], 'k', linewidth=1)
    ax.plot([0, 100], [100, 0], 'k', linewidth=1)
    ax.plot([0, 50], [50, 100], 'k', linewidth=1)
    ax.plot([50, 100], [100, 50], 'k', linewidth=1)
    ax.plot([100, 50], [50, 0], 'k', linewidth=1)
    ax.plot([50, 0], [0, 50], 'k', linewidth=1)
    ax.plot([0, 50, 100, 50, 0], [50, 100, 50, 0, 50], 'k', linewidth=1)
    # Số nhà
    for i, (x, y) in house_coords.items():
        ax.text(x, y+2, f"{i}", fontsize=6, color='red',weight='bold', ha='center')
    # Hành tinh
    for i, (x, y) in house_coords.items():
        planets = []
        for _, row in df_d30.iterrows():
            if row["D30_Nhà"] == i:
                name = row["Hành tinh"]
                deg = row["D30_Độ"]
                planets.append(f"{name} ({int(deg)}°)")
        if planets:
            ax.text(x, y, "\n".join(planets), ha='center', va='center', fontsize=7, color='blue')
    plt.tight_layout()
    return fig
def detect_yoga_dosha(df_planets):
    """
    Phát hiện các Yoga/Dosha cơ bản từ bảng hành tinh, trả về markdown cho Streamlit.
    """
    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp",
          "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    rashi_rulers = {
        "Bạch Dương": "Mars",        # Aries
        "Kim Ngưu": "Venus",         # Taurus
        "Song Tử": "Mercury",        # Gemini
        "Cự Giải": "Moon",           # Cancer
        "Sư Tử": "Sun",              # Leo
        "Xử Nữ": "Mercury",          # Virgo
        "Thiên Bình": "Venus",       # Libra
        "Bọ Cạp": "Mars",            # Scorpio
        "Nhân Mã": "Jupiter",        # Sagittarius
        "Ma Kết": "Saturn",          # Capricorn
        "Bảo Bình": "Saturn",        # Aquarius
        "Song Ngư": "Jupiter"        # Pisces
    }
    res = []
    
    # Lấy các vị trí nhanh
    def get_planet(name):
        return df_planets[df_planets['Hành tinh'] == name].iloc[0] if name in set(df_planets['Hành tinh']) else None
    
    # === Khai báo các biến hành tinh cần dùng toàn hàm ===
    moon = get_planet("Moon")
    mars = get_planet("Mars")
    jupiter = get_planet("Jupiter")
    mercury = get_planet("Mercury")
    sun = get_planet("Sun")
    venus = get_planet("Venus")
    rahu = get_planet("Rahu")
    ketu = get_planet("Ketu")
    saturn = get_planet("Saturn")

    
    # 1. Pancha Mahapurusha Yoga
    mahapurusha = []
    kendra_houses = [1, 4, 7, 10]
    pmy_data = [
        ("Mars", "Ruchaka", "Mars ở nhà 1,4,7,10 và vượng/tướng"),
        ("Mercury", "Bhadra", "Mercury ở nhà 1,4,7,10 và vượng/tướng"),
        ("Jupiter", "Hamsa", "Jupiter ở nhà 1,4,7,10 và vượng/tướng"),
        ("Venus", "Malavya", "Venus ở nhà 1,4,7,10 và vượng/tướng"),
        ("Saturn", "Shasha", "Saturn ở nhà 1,4,7,10 và vượng/tướng"),
    ]
    for planet, yoga, explain in pmy_data:
        p = get_planet(planet)
        if p is not None and p['Nhà'] in kendra_houses and p['Tính chất'] in ["vượng", "tướng"]:
            res.append(f"- **{yoga} Yoga**: {explain} (đang có hiệu lực)")
       
    # 2. Gaja-Kesari Yoga (Jupiter ở Kendra từ Moon)
    def is_gaja_kerasi(df_planets):
        moon = get_planet("Moon")
        jupiter = get_planet("Jupiter")
        if moon is None or jupiter is None:
            return False, "Thiếu Moon hoặc Jupiter"
    
        moon_house = moon["Nhà"]
        jupiter_house = jupiter["Nhà"]
        kendra_from_moon = [(moon_house - 1 + x) % 12 + 1 for x in [0,3,6,9]]  # 1,4,7,10 từ Moon
    
        if jupiter_house not in kendra_from_moon:
            return False, "Jupiter không ở Kendra từ Moon"
    
        # Không đồng cung với Rahu/Ketu/Saturn
        malefic_names = ["Rahu", "Ketu", "Saturn"]
        for m in malefic_names:
            m_p = get_planet(m)
            if m_p is not None and (m_p["Nhà"] == moon_house or m_p["Nhà"] == jupiter_house):
                return False, f"{m} đồng cung với Moon/Jupiter"
    
        # Không tử/suy yếu
        if moon["Tính chất"] == "tử" or jupiter["Tính chất"] == "tử":
            return False, "Moon hoặc Jupiter bị tử/suy yếu"
    
        return True, "Thỏa mãn các điều kiện mạnh của Gaja-Kesari Yoga.↑"
    is_gk, note = is_gaja_kerasi(df_planets)
    if is_gk:
        res.append(f"- **Gaja-Kesari Yoga**: {note}")
    
    # 3. Chandra-Mangal Yoga (Moon & Mars cùng Kendra tính từ nhau)
    mars = get_planet("Mars")
    if moon is not None and mars is not None:
        moon_house = moon["Nhà"]
        mars_house = mars["Nhà"]
        kendra = [(moon_house + x - 1) % 12 + 1 for x in [0,3,6,9]]
        if mars_house in kendra:
            res.append(
                "- **Chandra-Mangal Yoga**: Mars ở nhà Kendra từ Moon – khả năng kinh doanh, quyết đoán."
            )
             
    
    # 6. Viparita Raja Yoga (phân biệt 3 loại Harsha, Sarala, Vimala)
    vry_types = {6: "Harsha Yoga", 8: "Sarala Yoga", 12: "Vimala Yoga"}
    dusthana = [6, 8, 12]
    vry_shown = set()
    for planet in df_planets.to_dict("records"):
        for ruled_house in planet.get("chủ nhà", []):
            if ruled_house in dusthana and planet["Nhà"] in dusthana:
                # Chỉ hiện 1 lần cho từng hành tinh, từng loại
                key = (planet['Hành tinh'], ruled_house, planet["Nhà"])
                if key in vry_shown:
                    continue
                vry_shown.add(key)
                vry_name = vry_types.get(ruled_house, "Viparita Raja Yoga")
                res.append(
                    f"- **{vry_name}**: {planet['Hành tinh']} là chủ nhà {ruled_house} nằm ở nhà {planet['Nhà']} (Dusthana) – lấy độc trị độc, chuyển hung thành cát."
                )
                break  # Không lặp lại cho cùng hành tinh
    # 7. Neecha Bhanga Raja Yoga (chi tiết cứu giải tử)
    for _, row in df_planets.iterrows():
        if row["Tính chất"] == "tử":
            lord = row["Hành tinh"]
            cung = row["Cung"]
            neecha_ruler = rashi_rulers.get(cung, None)
            ruler_info = get_planet(neecha_ruler) if neecha_ruler else None
            kendra_houses = [1, 4, 7, 10]
            rescue = False
            note = ""
            # Chỉ giữ 2 điều kiện dễ xảy ra nhất
            if ruler_info is not None and ruler_info["Nhà"] in kendra_houses:
                rescue = True
                note = f"Chủ {cung} ({neecha_ruler}) ở Kendra"
            elif ruler_info is not None and ruler_info["Cung"] == cung:
                rescue = True
                note = f"Chủ {cung} ({neecha_ruler}) đồng cung với {lord}"
            if rescue:
                res.append(
                    f"- **Neecha Bhanga Raja Yoga:** {lord} tử ở {cung}, *được cứu giải*: {note}.↑"
                )
        
    # === Raja Yoga: Chủ Kendra và chủ Trikona đồng cung hoặc chiếu nhau ===
    trikona_houses = [1, 5, 9]
    kendra_houses = [1, 4, 7, 10]
    
    # Xác định danh sách hành tinh là chủ các nhà Trikona và Kendra
    trikona_rulers = [p for p in df_planets.to_dict("records") if set(p.get("Chủ tinh của nhà", [])) & set(trikona_houses)]
    kendra_rulers  = [p for p in df_planets.to_dict("records") if set(p.get("Chủ tinh của nhà", [])) & set(kendra_houses)]
    
    for tr in trikona_rulers:
        for kr in kendra_rulers:
            # Loại trừ trường hợp cùng 1 hành tinh là chủ của cả Kendra và Trikona (vd: Lagna lord)
            if tr["Hành tinh"] == kr["Hành tinh"]:
                continue
    
            # 1. Đồng cung
            if tr["Cung"] == kr["Cung"]:
                res.append(
                    f"- **Raja Yoga (Đồng cung):** Chủ Trikona ({tr['Hành tinh']}) và Chủ Kendra ({kr['Hành tinh']}) đồng cung tại {tr['Cung']}."
                )
    
            # 2. Aspect/chiếu nhau (theo Vedic)
            chiếu_tr = [x.strip().split(" ")[0] for x in str(tr.get("Chiếu hành tinh", "")).split(",") if x.strip()]
            chiếu_kr = [x.strip().split(" ")[0] for x in str(kr.get("Chiếu hành tinh", "")).split(",") if x.strip()]
            # Mutual aspect là mạnh nhất, nhưng single aspect cũng ghi nhận
            if (kr["Hành tinh"] in chiếu_tr) and (tr["Hành tinh"] in chiếu_kr):
                res.append(
                    f"- **Raja Yoga (Mutual Aspect):** Chủ Trikona ({tr['Hành tinh']}, {tr['Cung']}) và Chủ Kendra ({kr['Hành tinh']}, {kr['Cung']}) chiếu lẫn nhau."
                )
            elif kr["Hành tinh"] in chiếu_tr:
                res.append(
                    f"- **Raja Yoga (Chiếu):** Chủ Trikona ({tr['Hành tinh']}, {tr['Cung']}) chiếu Chủ Kendra ({kr['Hành tinh']}, {kr['Cung']})."
                )
            elif tr["Hành tinh"] in chiếu_kr:
                res.append(
                    f"- **Raja Yoga (Chiếu):** Chủ Kendra ({kr['Hành tinh']}, {kr['Cung']}) chiếu Chủ Trikona ({tr['Hành tinh']}, {tr['Cung']})."
                )
    
    def check_parivartana(df_planets):
        records = df_planets.to_dict("records")
        exchanges = []
        for p1 in records:
            ruler1 = rashi_rulers.get(p1["Cung"])
            if not ruler1:
                continue
            # Tìm planet đang ở cung của ruler1
            p2 = next((p for p in records if p["Hành tinh"] == ruler1), None)
            # PHẢI kiểm tra hai hành tinh phải khác nhau!
            if p2 and rashi_rulers.get(p2["Cung"]) == p1["Hành tinh"] and p1["Hành tinh"] != p2["Hành tinh"]:
                pair = tuple(sorted([p1["Hành tinh"], p2["Hành tinh"]]))
                if pair not in exchanges:
                    exchanges.append(pair)
        return exchanges
    
    parivartana = check_parivartana(df_planets)
    for p1, p2 in parivartana:
        res.append(f"- **Parivartana Yoga:** {p1} và {p2} hoán đổi cung – sự trợ lực qua lại mạnh mẽ.")




    
    # 8. kal sarpa dosha
    main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    rashi_to_number = {
    "Bạch Dương": 1, "Kim Ngưu": 2, "Song Tử": 3, "Cự Giải": 4,
    "Sư Tử": 5, "Xử Nữ": 6, "Thiên Bình": 7, "Bọ Cạp": 8,
    "Nhân Mã": 9, "Ma Kết": 10, "Bảo Bình": 11, "Song Ngư": 12
}
    def normalize_deg(x):
        return x % 360

    def is_in_arc(x, start, end):
        x = normalize_deg(x)
        start = normalize_deg(start)
        end = normalize_deg(end)
        if start < end:
            return start < x < end
        else:
            return start < x or x < end
    
    main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    def check_kala_sarpa(df_planets):
        rahu = df_planets[df_planets["Hành tinh"] == "Rahu"].iloc[0]
        ketu = df_planets[df_planets["Hành tinh"] == "Ketu"].iloc[0]
        rahu_deg = dms_str_to_float(rahu["Vị trí"]) + 30 * (rashi_to_number[rahu["Cung"]] - 1)
        ketu_deg = dms_str_to_float(ketu["Vị trí"]) + 30 * (rashi_to_number[ketu["Cung"]] - 1)
        rahu_deg = normalize_deg(rahu_deg)
        ketu_deg = normalize_deg(ketu_deg)
        if rahu_deg == ketu_deg:
            ketu_deg = (rahu_deg + 180) % 360
        in_one_arc = True
        for planet in main_planets:
            p = df_planets[df_planets["Hành tinh"] == planet].iloc[0]
            deg = dms_str_to_float(p["Vị trí"]) + 30 * (rashi_to_number[p["Cung"]] - 1)
            if not is_in_arc(deg, rahu_deg, ketu_deg):
                in_one_arc = False
                break
        return in_one_arc
        
        
    # Sử dụng:
    if check_kala_sarpa(df_planets):
        res.append("- **Kala Sarpa Dosha:** Tất cả các hành tinh chính đều nằm giữa trục Rahu-Ketu – Mât cân đối toàn bàn, nhiều thử thách. ↓↓")
    
    
    
    # 11. Paap Kartari Yoga – một cung bị kẹp giữa hai hung tinh
    malefics = ["Mars", "Saturn", "Sun", "Rahu", "Ketu"]
    pk_yoga_shown = set()
    for i, row in df_planets.iterrows():
        curr_house = row["Nhà"]
        if curr_house in pk_yoga_shown:
            continue  # Bỏ qua nếu đã hiện cho nhà này rồi
        prev_house = (curr_house - 2) % 12 + 1
        next_house = curr_house % 12 + 1
        prev_malefic = any(p for p in df_planets.to_dict("records") if p["Nhà"] == prev_house and p["Hành tinh"] in malefics)
        next_malefic = any(p for p in df_planets.to_dict("records") if p["Nhà"] == next_house and p["Hành tinh"] in malefics)
        if prev_malefic and next_malefic:
            res.append(
                f"- **Paap Kartari Yoga:** Nhà {curr_house} bị kẹp giữa hai hung tinh. ↓."
            )
            pk_yoga_shown.add(curr_house)

    # Dhana Yoga: Chủ 2/5/9/11 nằm trong 2/5/9/11 hoặc đồng cung nhau
    dhana_houses = [2,5,9, 11]  # đúng quy tắc 2/5/9/11
    found_dhana = False
    for p in df_planets.to_dict("records"):
        # Chủ của nhà này là gì?
        rulers = p.get("chủ nhà", [])
        if not rulers:
            continue
        for r in rulers:
            if r in dhana_houses and p["Nhà"] in dhana_houses:
                res.append("- **Dhana Yoga**: Chủ tinh nhà tài nằm ở nhà tài. Tài  ↑ .")
                found_dhana = True
                break
        if found_dhana:
            break  # Dừng luôn, chỉ hiển thị 1 lần duy nhất
     # Dhana Yoga:Chủ nhà 6, 8, 12 nằm ở các nhà tài hoặc đồng cung nhà tài.
    daridra_houses = [6, 8, 12]
    for p in df_planets.to_dict("records"):
        if not p.get("chủ nhà", []): continue
        for dh in daridra_houses:
            if dh in p["chủ nhà"] and p["Nhà"] in [2, 11]:
                res.append("- **Daridra Yoga:** Chủ nhà dusthana nằm ở nhà tài. Tài ↓.")

    
    good_houses = [1, 4, 5, 7, 9, 10]
    saraswati_count = 0
    for planet in ["Mercury", "Jupiter", "Venus"]:
        p = get_planet(planet)
        if p is not None and p["Nhà"] in good_houses:
            saraswati_count += 1
    if saraswati_count >= 2 and moon is not None and moon["Nhà"] in good_houses:
        res.append("- **Saraswati Yoga**: Mercury, Jupiter, Venus mạnh ở Kendra/Trikona với Moon mạnh – học vấn, nghệ thuật nổi bật ↑.")   
    house9_ruler_list = []
    for p in df_planets.to_dict("records"):
        if 9 in p.get("chủ nhà", []):
            house9_ruler_list.append(p)
    for p in house9_ruler_list:
        if p["Tính chất"] in ["vượng", "tướng"] and p["Nhà"] in [1, 4, 5, 7, 9, 10]:
            res.append("- **Lakshmi Yoga**: Chủ nhà 9 vượng/tướng ở Kendra/Trikona – thịnh vượng, may mắn ↑.")
            break
    house9_ruler = None
    house10_ruler = None
    for p in df_planets.to_dict("records"):
        if 9 in p.get("chủ nhà", []):
            house9_ruler = p
        if 10 in p.get("chủ nhà", []):
            house10_ruler = p
    if house9_ruler and house10_ruler and house9_ruler["Cung"] == house10_ruler["Cung"]:
        res.append("- **Dharma-Karmadhipati Yoga**: Chủ nhà 9 và 10 đồng cung – sự nghiệp-phúc tăng.")

    # --- Kiểm tra Nabhasa Sankhya Yoga ---
    planets_main = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    signs = [row["Cung"] for row in df_planets.to_dict("records") if row["Hành tinh"] in planets_main]
    unique_signs = set(signs)
    n_signs = len(unique_signs)
    sankhya_map = {
        1: ("Gola", "Cuộc đời tập trung vào một chủ đề chính, số phận thường đơn giản, nhưng thiếu linh hoạt."),
        2: ("Yuga", "Hai thái cực, cuộc đời chia hai mảng lớn rõ rệt."),
        3: ("Shoola", "Tập trung mục tiêu, tiến về một đích lớn, nghị lực mạnh."),
        4: ("Kedara", "Làm nhiều việc cùng lúc, đa năng nhưng dễ phân tán."),
        5: ("Pasa", "Nhiều mối ràng buộc, sống đa chiều, quan hệ rộng."),
        6: ("Dama", "Kiểm soát, ngăn nắp, sống có kỷ luật."),
        7: ("Veena", "Đời sống hài hòa, nghệ thuật, hòa nhập nhiều môi trường.")
    }
    if 1 <= n_signs <= 7:
        name, meaning = sankhya_map[n_signs]
        res.append(f"- **Nabhasa Sankhya Yoga: {name}** – ({n_signs} cung) {meaning}")
    else:
        res.append("Không xác định được Nabhasa Sankhya Yoga.")
    # --- Kiểm tra Kemadruma Yoga ---
    moon = get_planet("Moon")
    if moon is not None:
        moon_house = moon["Nhà"]
        bad_planets = {"Sun", "Rahu", "Ketu", "Moon"}
        houses_around = [((moon_house - 2) % 12) + 1, (moon_house % 12) + 1]
        planets_around = [p for p in df_planets.to_dict("records") if p["Nhà"] in houses_around and p["Hành tinh"] not in bad_planets]
        planets_same = [p for p in df_planets.to_dict("records") if p["Nhà"] == moon_house and p["Hành tinh"] not in bad_planets]
        if len(planets_around) == 0 and len(planets_same) == 0:
            res.append("- **Kemadruma Yoga:** Moon đứng một mình, dễ gặp cô độc, thử thách nội tâm.")
    
    # --- Kiểm tra Adhi Yoga từ Ascendant ---
    benefics = ["Mercury", "Venus", "Jupiter"]
    asc_house = 1  # Theo truyền thống Ascendant (Lagna) luôn ở nhà 1
    houses_6_7_8 = [6, 7, 8]
    found_benefics = [p for p in df_planets.to_dict("records") if p["Hành tinh"] in benefics and p["Nhà"] in houses_6_7_8]
    if len(found_benefics) >= 2:
        res.append("- **Adhi Yoga:** Mercury, Venus, Jupiter chiếm các nhà 6/7/8 từ Ascendant – địa vị, danh vọng, an nhàn.")
      
    
    if not res:
        return "Không phát hiện Yoga/Dosha đặc biệt nổi bật nào."
    else:
        return "#### 📜 **Tổng hợp các cách cục cát/hung nổi bật:**\n\n" + "\n\n".join(res)

    
def astrology_block():
    

    # ==== Setup ====
    swe.set_ephe_path("ephe")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
   

    # Lấy chỉ số timezone mặc định là Việt Nam
    
    vn_tz = pytz.timezone( "Asia/Ho_Chi_Minh")
    now_local = datetime.now(vn_tz)
    decimal_default = now_local.hour + now_local.minute / 60
    
    # Chuyển đổi giờ hiện tại về UTC
    now_utc = now_local.astimezone(pytz.utc)

    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute / 60 + now_utc.second / 3600)

    st.markdown(f"**🕒 Giờ hiện tại (VN)**: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")
    # --- Chọn thời gian và tọa độ ---
    col1, col2 = st.columns([1, 1])

    # Khởi tạo session_state nếu chưa có (chạy 1 lần duy nhất)
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.now().date()
    if "selected_time" not in st.session_state:
        st.session_state.selected_time = datetime.now().time()

    with col1:
        # Giao diện chọn ngày và giờ
        st.session_state.selected_date = st.date_input("📅 Chọn ngày", value=st.session_state.selected_date,min_value=date(1900, 1, 1),
            max_value=date(2100, 12, 31))
        # Nhập giờ kiểu decimal (thập phân)
        if "decimal_hour" not in st.session_state:
            st.session_state.decimal_hour = decimal_default  # float, không phải 12 (int)
    
        decimal_hour = st.number_input(
        "⏰ Nhập giờ(ví dụ: 14.5 = 14h30)",
        min_value=0.0,            # float
        max_value=23.99,          # float
        value=float(st.session_state.decimal_hour), # float
        step=2.0,                # float
        format="%.2f", 
        key="decimal_hour"
    )
        
    
        # Convert về hour, minute
        hour = int(decimal_hour)
        minute = int(round((decimal_hour - hour) * 60))
        st.session_state.selected_time = datetime.now().time().replace(hour=hour, minute=minute, second=0, microsecond=0)
    
        # Gộp lại thành datetime hoàn chỉnh
        selected_datetime = datetime.combine(
            st.session_state.selected_date,
            st.session_state.selected_time
        )
        user_name = st.text_input("Nhập tên")
        user_name = user_name.title().strip()
                
    with col2:
        # Giao diện nhập tọa độ
        latitude = st.number_input("🌐 Vĩ độ", min_value=-90.0, max_value=90.0, value=21.0, step=0.1)
        longitude = st.number_input("🌐 Kinh độ", min_value=-180.0, max_value=180.0, value=105.8, step=0.1)
        tz_options = [
        ("Etc/GMT+12", "Quốc tế đổi ngày", -12),
        ("Pacific/Honolulu", "Hawaii", -10),
        ("America/Anchorage", "Alaska", -9),
        ("America/Los_Angeles", "Los Angeles", -8),
        ("America/Denver", "Denver", -7),
        ("America/Chicago", "Chicago", -6),
        ("America/New_York", "New York", -5),
        ("America/Santiago", "Santiago", -4),
        ("America/Halifax", "Halifax", -3),
        ("America/Sao_Paulo", "Sao Paulo", -3),
        ("Atlantic/Azores", "Azores", -1),
        ("Europe/London", "London", 0),
        ("Europe/Berlin", "Berlin", 1),
        ("Europe/Helsinki", "Helsinki", 2),
        ("Europe/Moscow", "Moscow", 3),
        ("Asia/Dubai", "Dubai", 4),
        ("Asia/Karachi", "Karachi", 5),
        ("Asia/Dhaka", "Dhaka", 6),
        ("Asia/Bangkok", "Bangkok/Hà Nội", 7),
        ("Asia/Ho_Chi_Minh", "TP.HCM", 7),
        ("Asia/Shanghai", "Shanghai/Bắc Kinh", 8),
        ("Asia/Tokyo", "Tokyo", 9),
        ("Australia/Sydney", "Sydney", 10),
        ("Pacific/Noumea", "Noumea", 11),
        ("Pacific/Auckland", "Auckland", 12),
    ]
        tz_labels = [f"UTC{offset:+d} - {city}" for tz, city, offset in tz_options]
        tz_values = [tz for tz, city, offset in tz_options]
        default_tz = "Asia/Ho_Chi_Minh"
        default_index = tz_values.index(default_tz) if default_tz in tz_values else tz_values.index("Asia/Bangkok")
        selected_label = st.selectbox("🌐 Chọn múi giờ đại diện", tz_labels, index=default_index)
        selected_tz = tz_values[tz_labels.index(selected_label)]
        local_tz = pytz.timezone(selected_tz)
    # Button to calculate
    if st.button("Tính Toán"):
        # Gán timezone theo local_tz đã chọn
        if selected_datetime.tzinfo is None:
            selected_datetime_local = local_tz.localize(selected_datetime)
        else:
            selected_datetime_local = selected_datetime.astimezone(local_tz)
    
        selected_utc = selected_datetime_local.astimezone(pytz.utc)
    
        jd = swe.julday(
            selected_utc.year, selected_utc.month, selected_utc.day,
            selected_utc.hour + selected_utc.minute / 60 + selected_utc.second / 3600
        )
    
        st.markdown(f"**Vĩ độ**: {latitude}° **Kinh độ**: {longitude}° ")
        st.markdown(selected_datetime_local)
    rashis = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ", "Thiên Bình", "Bọ Cạp",
              "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
    # Danh sách Nakshatra
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
        "Magha", "P.Phal", "U.Phal", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
        "Jyeshtha", "Mula", "P.Asad", "U.Asad", "Shravana", "Dhanishta", "Shatabhisha",
        "P.Bhad", "U.Bhad", "Revati"
    ]
    planets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE
    }
    dignities = {
        "Sun": {"vượng": "Sư Tử", "tướng": "Bạch Dương", "tù": "Thiên Bình", "tử": "Bảo Bình","bạn bè": {"Cự Giải", "Song Ngư","Nhân mã", "Bọ Cạp" },"địch thủ": {"Kim Ngưu", "Song Tử","Xử Nữ","Ma Kết"  }},
        "Moon": {"vượng": "Cự Giải", "tướng": "Kim Ngưu", "tù": "Bọ Cạp", "tử": "Ma Kết","bạn bè": {"Bạch Dương","Sư Tử", "Song Ngư","Nhân mã" },"địch thủ": {"Thiên Bình", "Song Tử","Xử Nữ","Bảo Bình"  }},
        "Mars": { "vượng": {"Bạch Dương","Bọ Cạp"}, "tướng": "Ma Kết", "tù": "Cự Giải", "tử": {"Kim Ngưu","Thiên Bình"},"bạn bè": {"Sư Tử", "Song Ngư","Nhân mã" },"địch thủ": {"Song Tử","Xử Nữ","Bảo Bình"}},
        "Mercury": {"vượng": {"Song Tử","Xử Nữ"}, "tướng": "Xử Nữ", "tù": "Song Ngư", "tử": "Nhân Mã","bạn bè": {"Kim Ngưu", "Bảo Bình","Thiên Bình" },"địch thủ": {"Bạch Dương", "Bọ Cạp","Cự Giải","Sư Tử"}},
        "Jupiter": {"vượng": {"Nhân Mã","Song Ngư"}, "tướng": "Cự Giải", "tù": "Ma Kết", "tử": {"Song Tử","Xử Nữ"},"bạn bè": {"Sư Tử", "Bạch Dương","Nhân mã" },"địch thủ": {"Kim Ngưu", "Thiên Bình","Bảo Bình"}},
        "Venus": {"vượng": {"Kim Ngưu","Thiên Bình"}, "tướng": "Song Ngư", "tù": "Xử Nữ", "tử": {"Bọ Cạp","Bạch Dương"},"bạn bè": {"Ma Kết","Xử Nữ","Bảo Bình","Song Tử" },"địch thủ": {"Bạch Dương", "Bọ Cạp","Cự Giải","Sư Tử"}},
        "Saturn": {"vượng": {"Ma Kết","Bảo Bình"}, "tướng": "Thiên Bình", "tù": "Bạch Dương", "tử": {"Cự Giải","Sư Tử"},"bạn bè": {"Kim Ngưu","Song Tử","Thiên Bình" },"địch thủ": {"Nhân Mã", "Bọ Cạp","Song Ngư"}},
                  }
    dasha_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
    rashi_to_number = {
        "Bạch Dương": 1, "Kim Ngưu": 2, "Song Tử": 3, "Cự Giải": 4,
        "Sư Tử": 5, "Xử Nữ": 6, "Thiên Bình": 7, "Bọ Cạp": 8,
        "Nhân Mã": 9, "Ma Kết": 10, "Bảo Bình": 11, "Song Ngư": 12
    }
    nakshatra_to_gana = {
        "Ashwini": "Thần", "Bharani": "Nhân", "Krittika": "Quỷ",
        "Rohini": "Nhân", "Mrigashira": "Thần", "Ardra": "Nhân",
        "Punarvasu": "Thần", "Pushya": "Thần", "Ashlesha": "Quỷ",
        "Magha": "Quỷ", "P.Phal": "Nhân", "U.Phal": "Nhân",
        "Hasta": "Thần", "Chitra": "Quỷ", "Swati": "Thần", "Vishakha": "Quỷ",
        "Anuradha": "Thần", "Jyeshtha": "Quỷ", "Mula": "Quỷ",
        "P.Asad": "Nhân", "U.Asad": "Nhân", "Shravana": "Thần",
        "Dhanishta": "Quỷ", "Shatabhisha": "Quỷ", "P.Bhad": "Nhân",
        "U.Bhad": "Nhân", "Revati": "Thần"
    }
    planet_natural_direction = {
    "Sun": "Đ,Lửa",
    "Moon": "TB,Nước",
    "Mars": "N,Lửa",
    "Mercury": "B,Đất",
    "Jupiter": "ĐB,Không",
    "Venus": "TN,Nước",
    "Saturn": "T,Khí",
    "Rahu": "TN,Khí",
    "Ketu": "N,Lửa"
}
    # ==== Hàm phụ ====
    def get_rashi(degree):
        return rashis[int(degree // 30)]
    def get_gana(nakshatra):
        return nakshatra_to_gana.get(nakshatra, "")
    def get_dignity(planet, rashi):
        dign = dignities.get(planet, {})
        # Xử lý vượng, tướng, tù, tử (có thể là chuỗi hoặc set)
        for key in ["vượng", "tướng", "tù", "tử"]:
            val = dign.get(key)
            if isinstance(val, set):
                if rashi in val:
                    return key
            elif isinstance(val, str):
                if rashi == val:
                    return key
        # Xử lý bạn bè, địch thủ
        if rashi in dign.get("bạn bè", set()):
            return "bạn bè"
        if rashi in dign.get("địch thủ", set()):
            return "địch thủ"
        return ""
    def get_nakshatra(degree):
        return nakshatras[int(degree // (360 / 27))]

    def is_combust(planet_name, planet_lon, sun_lon, retrograde=False):
        if planet_name in ["Sun", "Rahu", "Ketu"]:
            return False
        diff = abs((planet_lon - sun_lon + 180) % 360 - 180)
        
        combust_limits = {
            "Moon": 8,
            "Mercury": 4 ,
            "Venus": 6,
            "Mars": 8,
            "Jupiter": 8,
            "Saturn": 8
        }
        limit = combust_limits.get(planet_name, 0)
        return diff < limit
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
        # Nếu sự thay đổi giữa hai ngày có dấu hiệu quay ngược, hành tinh đang retro
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
    asc_gana = get_gana(asc_nak)
    equal_house_cusps = [(asc + i * 30) % 360 for i in range(12)] + [(asc + 360) % 360]
    # Tính toán các hành tinh
    planet_data = []


    # Tính toán ngày trước đó (1 ngày)
    jd_previous = jd - 1  # Giảm 1 ngày để lấy ngày trước đó

    planet_data.append({
        "Hành tinh": "Asc",
        "Vị trí": asc_degree_dms,
        "Cung": asc_rashi,
        "Tú": asc_nak,
        "Pada": asc_pada,
        "Gana": asc_gana,
        "Nhà": 1,
        "Tính chất": "",
        "retro": "",
        "vastu": ""
    })

    for name, code in planets.items():
        # Tính độ của hành tinh ở hiện tại và trước đó
        lon_deg = swe.calc(jd, code, swe.FLG_SIDEREAL)[0][0]
        sun_lon = swe.calc(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
        # Kiểm tra retro với hai ngày
        retrograde_status = "R" if is_retrograde(code, jd, jd_previous) else ""
        is_c = is_combust(name, lon_deg, sun_lon, retrograde=(retrograde_status == "R"))
        status = retrograde_status
        if is_c:
            status += " C"
        # Thêm thông tin hành tinh vào danh sách planet_data
        planet_data.append({
            "Hành tinh": name,
            "Vị trí": deg_to_dms(lon_deg % 30),
            "Cung": get_rashi(lon_deg),
            "Tú": get_nakshatra(lon_deg),
            "Pada": get_pada(lon_deg),
            "Gana": get_gana(get_nakshatra(lon_deg)),
            "Nhà": get_house_for_planet(lon_deg, equal_house_cusps),
            "Tính chất": get_dignity(name, get_rashi(lon_deg)),
            "retro": status,
            "vastu": planet_natural_direction.get(name, "")
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
            "Tú": ketu_nak,
            "Pada": ketu_pada,
            "Gana": get_gana(ketu_nak),
            "Nhà": ketu_bhava,
            "Tính chất": ketu_dignity,
            "retro": "R",  
            "vastu": "N,Lửa",
        })

    selected_datetime_local = None
    if selected_datetime.tzinfo is None:
        selected_datetime_local = local_tz.localize(selected_datetime)
    else:
        selected_datetime_local = selected_datetime.astimezone(local_tz)
    # Hàm vẽ biểu đồ
    def draw_chart(planet_data, user_name=None,selected_datetime_local=None):
        fig, ax = plt.subplots(figsize=(4,4))
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
                    sign = p["Cung"]
                    deg_str = p["Vị trí"].split("°")[0] + "°"
                    # Kiểm tra và gán mũi tên tương ứng
                    dignity = get_dignity(name, sign)
                    if dignity == "vượng" or dignity == "tướng" or dignity == "bạn bè":
                        arrow = " ↑"
                    elif dignity == "tù" or dignity == "tử" or dignity == "địch thủ":
                        arrow = " ↓"
                    else:
                        arrow = ""
                    
                    labels.append(f"{name} ( {deg_str}){arrow}")
            names = "\n".join(labels)
            ax.text(x, y, names, ha='center', va='center', fontsize=7, color='blue')
        for i, (x, y) in house_coords.items():
            cusp_degree = equal_house_cusps[i - 1]
            rashi_name = get_rashi(cusp_degree)
            rashi_number = rashi_to_number[rashi_name]
            ax.text(x-2, y + 2, str(rashi_number), fontsize=5, color='red',weight='bold')
        # Thêm tiêu đề (title) có tên người xem lá số
        if user_name:
            ax.set_title(f"Biểu đồ sinh {user_name}|{selected_datetime_local}", fontsize=8, pad=8)
        else:
            ax.set_title(f"Biểu đồ sinh| {selected_datetime_local}", fontsize=8, pad=8)
        return fig  
        
    fig_d1 = draw_chart(planet_data, user_name,selected_datetime_local)
    
    df_planets = pd.DataFrame(planet_data)



    rashi_rulers = {
        "Bạch Dương": "Mars", "Kim Ngưu": "Venus", "Song Tử": "Mercury", "Cự Giải": "Moon",
        "Sư Tử": "Sun", "Xử Nữ": "Mercury", "Thiên Bình": "Venus", "Bọ Cạp": "Mars",
        "Nhân Mã": "Jupiter", "Ma Kết": "Saturn", "Bảo Bình": "Saturn", "Song Ngư": "Jupiter"
    }

    house_rulers = {
        i + 1: rashi_rulers[get_rashi(cusp)]
        for i, cusp in enumerate(equal_house_cusps[:12])
    }

    planet_to_ruled_houses = {}
    for house, ruler in house_rulers.items():
        planet_to_ruled_houses.setdefault(ruler, []).append(house)

    df_planets["chủ nhà"] = df_planets["Hành tinh"].apply(
        lambda p: planet_to_ruled_houses.get(p, [])
    )
    # === Định nghĩa quy tắc chiếu Vedic ===
    vedic_aspects = {
        "Saturn": [3, 7, 10],
        "Mars": [4, 7, 8],
        "Jupiter": [5, 7, 9],
        "Default": [7]
    }

    # Bản đồ hành tinh -> nhà
    planet_house_map = {p["Hành tinh"]: p["Nhà"] for p in planet_data}

    # Hàm tính hành tinh nào bị chiếu
    def get_aspected_planets(planet_name, current_house):
        if current_house is None:
            return ""
        
        # Lấy danh sách khoảng cách các nhà bị chiếu
        aspect_offsets = vedic_aspects.get(planet_name, vedic_aspects["Default"])
        
        # Tính các nhà bị chiếu
        aspected_houses = [((current_house + offset - 2) % 12) + 1 for offset in aspect_offsets]
        
        # Tìm hành tinh nằm trong các nhà bị chiếu
        result = []
        for other_planet, house in planet_house_map.items():
            if other_planet != planet_name and house in aspected_houses:
                result.append(f"{other_planet} ( {house})")
        return ", ".join(result)

    # Thêm cột vào bảng
    df_planets["Chiếu hành tinh"] = df_planets.apply(
        lambda row: get_aspected_planets(row["Hành tinh"], row["Nhà"]), axis=1
    )
    
    
    # Bảng ánh xạ Nakshatra → Dasha Lord
    nakshatra_to_dasha_lord = {
        "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun",
        "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
        "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
        "Magha": "Ketu", "P.Phal": "Venus", "U.Phal": "Sun",
        "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
        "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshtha": "Mercury",
        "Mula": "Ketu", "P.Asad": "Venus", "U.Asad": "Sun",
        "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
        "P.Bhad": "Jupiter", "U.Bhad": "Saturn", "Revati": "Mercury"
    }

    # Dasha sequence và số năm
    dasha_sequence = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_years = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
                   "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

    # Tính vị trí Mặt Trăng
    moon_longitude = swe.calc(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]

    # Xác định nakshatra
    nakshatra_index = int((moon_longitude % 360) / 13.3333333333)
    nakshatra_fraction = ((moon_longitude % 360) % 13.3333333333) / 13.3333333333
    nakshatra_name = nakshatras[nakshatra_index]
    dasha_lord = nakshatra_to_dasha_lord[nakshatra_name]

    # Số năm còn lại trong Mahadasha hiện tại
    full_years = dasha_years[dasha_lord]
    remain_years = (1 - nakshatra_fraction) * full_years

    # ✅ Giữ ngày kết thúc là hiện tại, tính ngược ra ngày bắt đầu
    end_jd = jd + remain_years * 365.25
    start_jd = end_jd - full_years * 365.25
    curr_jd = start_jd

    # Tạo bảng Mahadasha
    dasha_list = []
    idx = dasha_sequence.index(dasha_lord)
    for i in range(9):
        lord = dasha_sequence[(idx + i) % 9]
        duration = dasha_years[lord]

        start = swe.revjul(curr_jd)
        end_jd = curr_jd + duration * 365.25
        end = swe.revjul(end_jd)

        dasha_list.append({
            "Dasha": lord,
            "Bắt đầu": f"{int(start[2]):02d}-{int(start[1]):02d}-{int(start[0])}",
            "Kết thúc": f"{int(end[2]):02d}-{int(end[1]):02d}-{int(end[0])}",
            "Số năm": round(duration, 2)
        })

        curr_jd = end_jd

    # Hiển thị bảng Mahadasha
    df_dasha = pd.DataFrame(dasha_list)
    


    # Hàm tính Antardasha chuẩn
    def compute_antardasha(mahadasha_lord, start_jd, duration_years):
        antardashas = []
        start_index = dasha_sequence.index(mahadasha_lord)
        jd_pointer = start_jd

        for i in range(9):
            sub_lord = dasha_sequence[(start_index + i) % 9]
            weight = dasha_years[sub_lord] / 120
            sub_duration = duration_years * weight
            end_jd = jd_pointer + sub_duration * 365.25

            start = swe.revjul(jd_pointer)
            end = swe.revjul(end_jd)

            antardashas.append({
                "Antardasha": f"{mahadasha_lord}/{sub_lord}",
                "Bắt đầu": f"{int(start[2]):02d}-{int(start[1]):02d}-{int(start[0])}",
                "Kết thúc": f"{int(end[2]):02d}-{int(end[1]):02d}-{int(end[0])}",
                "Số năm": round(sub_duration, 2)
            })
            jd_pointer = end_jd

        return pd.DataFrame(antardashas)

    all_antardasha = []
    for _, row in df_dasha.iterrows():
        m_lord = row["Dasha"]
        m_start = datetime.strptime(row["Bắt đầu"], "%d-%m-%Y")
        m_start_jd = swe.julday(m_start.year, m_start.month, m_start.day)
        m_years = row["Số năm"]
        all_antardasha += compute_antardasha(m_lord, m_start_jd, m_years).to_dict("records")

    df_all_antar = pd.DataFrame(all_antardasha)
    

    # Quy tắc điểm số theo nhà

    benefic_house_scores = {1:3  ,2:2.5  ,3:-2  ,4:2  ,5:2.5  ,6:-2  ,7:2  ,8:-3  ,9:3  ,10:2  ,11:2.5  ,12:-3 }
    malefic_house_scores = {1:2  ,2:1.5  ,3:0  ,4:1  ,5:2  ,6:0  ,7:2  ,8:-3  ,9:2  ,10:2  ,11:3  ,12:-3 }
    benefics = {"Jupiter", "Venus", "Moon","Mercury"}
    malefics = {"Mars", "Saturn", "Rahu", "Ketu","Sun"}
    def get_house_score(house, planet):
        if planet in benefics:
            return benefic_house_scores.get(house, 0)
        elif planet in malefics:
            return malefic_house_scores.get(house, 0)
        else:
            return 0  # Trung lập hoặc không rõ
    def calc_aspect_and_conj_score(planet, df_planets):
        # 1. Chiếu: lấy từ cột "Chiếu hành tinh"
        chiếu = df_planets.loc[df_planets["Hành tinh"] == planet, "Chiếu hành tinh"].values
        aspected = []
        if len(chiếu) > 0 and chiếu[0]:
            aspected = [x.strip().split(" ")[0] for x in chiếu[0].split(",") if x.strip()]
        # 2. Conjunction: đồng cung với hành tinh nào?
        this_row = df_planets[df_planets["Hành tinh"] == planet]
        conjunction = []
        if not this_row.empty:
            cung = this_row.iloc[0]["Cung"]
            others = df_planets[(df_planets["Cung"] == cung) & (df_planets["Hành tinh"] != planet)]
            conjunction = list(others["Hành tinh"])
        # 3. Tính điểm từng hành tinh chiếu/đồng cung (không double count nếu vừa chiếu vừa đồng cung)
        interacted = set(aspected + conjunction)
        plus03 = {"Jupiter", "Venus", "Moon"}
        minus03 = {"Mars", "Saturn", "Ketu", "Rahu"}
        score = 0
        for asp in interacted:
            if asp in plus03:
                score += 0.3
            elif asp in minus03:
                score -= 0.3
            # Mercury, Sun thì không cộng trừ gì
        # 4. Giới hạn điểm cộng/trừ tối đa ±1.0
        score = max(min(score, 1.0), -1.0)
        return score
    # Tính dữ liệu vẽ biểu đồ
    def build_life_chart(df_dasha, planet_data, birth_jd):
        life_years = []
        life_scores = []
        year_labels = []
        current_year = 0
        birth_offset = None
        
    
        # 2. Tính điểm từng Mahadasha
        for _, m_row in df_dasha.iterrows():
            m_lord = m_row["Dasha"]
            m_start = datetime.strptime(m_row["Bắt đầu"], "%d-%m-%Y")
            m_start_jd = swe.julday(m_start.year, m_start.month, m_start.day)
            m_duration = m_row["Số năm"]

            if birth_offset is None and birth_jd >= m_start_jd:
                birth_offset = (birth_jd - m_start_jd) / 365.25

            # Điểm từ vị trí hiện tại của hành tinh
            m_house = next((p["Nhà"] for p in planet_data if p["Hành tinh"] == m_lord), 0)
            m_score = get_house_score(m_house, m_lord)
            
            m_dignity = next((p["Tính chất"] for p in planet_data if p["Hành tinh"] == m_lord), "")
            if m_dignity in ["vượng", "tướng"]:
                m_score += 1
            elif m_dignity == "bạn bè":
                m_score += 0.5
            elif m_dignity == "địch thủ":
                m_score -= 0.5
            elif m_dignity in ["tù", "tử"]:
                m_score -= 1
            # ✅ Thêm điểm theo tính chất "Cát – Hung" của hành tinh
            if m_lord in ["Jupiter", "Venus", "Moon"]:
                m_score += 0.5
            elif m_lord in ["Mars", "Saturn", "Rahu", "Ketu"]:
                m_score -= 0.5
            m_status = next((p["retro"] for p in planet_data if p["Hành tinh"] == m_lord), "")
            if "R" in m_status and "C" in m_status:
                m_score -= 0.5
            # ✅ Thêm điểm dựa trên các nhà hành tinh đó làm chủ
            ruled_houses = planet_to_ruled_houses.get(m_lord, [])
            rule_bonus = 0
            for rh in ruled_houses:
                if rh in [6, 8, 12]:
                    rule_bonus -= 3.5
                elif rh in [1, 5, 9]:
                    rule_bonus += 3.5
                elif rh in [ 4, 7, 10]:
                    rule_bonus += 1.5
                elif rh in [ 2,11]:
                    rule_bonus += 2.5
            m_score += rule_bonus
            m_gana = next((p["Gana"] for p in planet_data if p["Hành tinh"] == m_lord), "")
            if m_gana == "Thần":
                m_score += 1
            elif m_gana == "Quỷ":
                m_score -= 1
            m_score += calc_aspect_and_conj_score(m_lord, df_planets)
            # Gán nhãn mục tiêu dựa theo nhà
            purpose = ""
            if m_house in [2]:
                purpose = " (tài ↑)"
            elif m_house in [1]:
                purpose = " (mệnh ↑)"
            elif m_house in [ 9]:
                purpose = " (đạo ↑)"
            elif m_house in [5]:
                purpose = " (học ↑)"
            elif m_house in [10]:
                purpose = " (danh ↑)"
            elif m_house in [4]:
                purpose = " (an cư ↑)"
            elif m_house == 7:
                purpose = " (quan hệ ↑)"
            elif m_house == 3:
                purpose = " (thị phi ↓)"
            elif m_house in [8,12]:
                purpose = " (mệnh,tài ↓)"
            elif m_house in [6]:
                purpose = " (mệnh ↓)"
            elif m_house in [11]:
                purpose = " (tài ↑)"
            antars = compute_antardasha(m_lord, m_start_jd, m_duration)
            for _, antar in antars.iterrows():
                a_lord = antar["Antardasha"].split("/")[-1]
                a_years = antar["Số năm"]
                a_house = next((p["Nhà"] for p in planet_data if p["Hành tinh"] == a_lord), 0)
                a_score = get_house_score(a_house, a_lord)*0.5 
                
                # ✅ Thêm điểm từ nhà mà antardasha làm chủ
                ruled_houses_a = planet_to_ruled_houses.get(a_lord, [])
                rule_bonus_a = 0
                for rh in ruled_houses_a:
                    if rh in [6, 8, 12]:
                        rule_bonus_a -= 1
                    elif rh in [1, 5, 9]:
                        rule_bonus_a += 1
                    elif rh in [4, 7, 10]:
                        rule_bonus_a += 0.5
                    elif rh in [ 2,11]:
                        rule_bonus_a += 0.7
                a_score += rule_bonus_a
                
                a_status = next((p["retro"] for p in planet_data if p["Hành tinh"] == a_lord), "")
                if "R" in a_status and "C" in a_status:
                    a_score -= 0.2
                # ✅ Thêm điểm theo dignity (tính chất) của Antardasha lord
                a_dignity = next((p["Tính chất"] for p in planet_data if p["Hành tinh"] == a_lord), "")
                if a_dignity in ["vượng", "tướng"]:
                    a_score += 0.5
                elif a_dignity == "bạn bè":
                    a_score += 0.2
                elif a_dignity == "địch thủ":
                    a_score -= 0.2
                elif a_dignity in ["tù", "tử"]:
                    a_score -= 0.5
                a_gana = next((p["Gana"] for p in planet_data if p["Hành tinh"] == a_lord), "")
                if a_gana == "Thần":
                    a_score += 0.5
                elif a_gana == "Quỷ":
                    a_score -= 0.5    
                # 4️⃣ Điểm từ phân loại Cát/Hung tinh
                if a_lord in ["Jupiter", "Venus", "Moon"]:
                    a_score += 0.2
                elif a_lord in ["Mars", "Saturn", "Rahu", "Ketu"]:
                    a_score -= 0.2
                a_score =a_score+0.5* calc_aspect_and_conj_score(a_lord, df_planets)
                total_score = round(a_score +  m_score, 2)

                life_years.append(current_year)
                life_scores.append(total_score)
                year_labels.append(m_lord + purpose)
                current_year += a_years

        birth_x = round(birth_offset, 2) if birth_offset else 0
        return pd.DataFrame({"Năm": life_years, "Điểm số": life_scores, "Mahadasha": year_labels}), birth_x

    # Sử dụng dữ liệu df_dasha, planet_data và jd ngày sinh
    chart_df, birth_x = build_life_chart(df_dasha, planet_data, jd)
    
    # Vẽ biểu đồ zigzag và đường cong mượt
    chart_df["Năm_mới"] = chart_df["Năm"] - birth_x
    
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(chart_df["Năm_mới"], chart_df["Điểm số"], marker='o')
    ax.hlines(y=0, xmin=0, xmax=115, color='black', linestyle='-', linewidth=2)

    ax.axvspan(0, 70, color='grey', alpha=0.2)  
    ax.spines['left'].set_position('zero')  # Đặt OY đúng tại x=0 mới
    
    ax.set_ylim(-13, 13)

    # Cài đặt chi tiết cho trục hoành
    ax.set_xticks(range(int(chart_df["Năm"].min()), int(chart_df["Năm"].max()) + 1, 5))  # Interval = 5 năm
    shown_mahadashas = set()

    for x, y, label in zip(chart_df["Năm"], chart_df["Điểm số"], chart_df["Mahadasha"]):
        if label not in shown_mahadashas:
            # Lấy đúng tên hành tinh gốc (dù label có thêm text khác)
            base_name = label.split(" ")[0]
            ax.text(x, y , label, fontsize=10, ha='center', va='center')
            shown_mahadashas.add(label)
    df_d9 = build_navamsa_df(df_planets)
    fig_d9=plot_d9_chart(df_d9)
    df_d30=build_trimsamsa_df(df_planets)
    fig_d30=plot_d30_chart(df_d30)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Biểu đồ sinh ")
        
        st.pyplot(fig_d1,use_container_width=False)
    with col2:
        st.markdown("### Biểu đồ hậu vận")
        
        st.pyplot(fig_d9,use_container_width=False)
        #st.markdown("### Biểu đồ lực âm")
        #st.pyplot(fig_d30,use_container_width=False)
    plt.close(fig_d1)
    plt.close(fig_d9)
    ax.tick_params(axis='x')
    filtered_df = chart_df[chart_df["Năm_mới"].between(0, 70)]
    median_score = round(filtered_df["Điểm số"].median(), 2)
    if user_name:
        ax.set_title(f"Biểu đồ đại vận – {user_name}\nĐiểm (Thang từ -10 đến 10): {median_score}")
    else:
        ax.set_title(f"Biểu đồ đại vận/ Điểm (Thang từ -10 đến 10): {median_score}")
    ax.set_xlabel("Tuổi")
    ax.set_ylabel("Điểm số")
    ax.grid(True)
    st.pyplot(fig,use_container_width=False)
    plt.close(fig)
    
    
    fig = plot_planet_table(df_planets, user_name)
    st.pyplot(fig)
    plt.close(fig)
    yoga_markdown = detect_yoga_dosha(df_planets)
    fig_yoga = plot_detect_yoga_matplotlib(yoga_markdown)
    st.pyplot(fig_yoga)
    plt.close(fig_yoga)
    col1, col2 = st.columns([1, 1])
    with col1:
        
        st.pyplot(plot_mahadasha_table(df_dasha))
        plt.close(plot_mahadasha_table(df_dasha))
    with col2:
        if st.checkbox("Antardasha"):
            st.dataframe(df_all_antar, use_container_width=False)       
    
    
    df_bav = compute_ashtakavarga(df_planets)
    fig_bav = plot_ashtakavarga_table(df_bav)
    st.pyplot(fig_bav)
    plt.close(fig_bav)
    
      
   
    st.markdown("""#### 📌 Hướng dẫn
    - Biểu đồ đại vận vimshottari là cách miêu tả hành trình của đời người trong thời mạt pháp, diễn ra trong 120 năm, 
      được tính từ trước thời điểm người đó sinh và cả sau khi người đó chết. 
    - Các đại vận được hiển thị bằng tên các hành tinh; trong đó quan trọng nhất được tô màu xám hiển thị khoảng 70 năm đời người. 
    - Thang điểm từ -10 đến 10, tức điểm 0 được tô đậm là điểm trung bình, điểm >0 được coi là chấp nhận được.
    - Biểu đồ được tính từ các trọng số quan trọng như chủ tinh, vị trí hành tinh, vượng tướng tù tử, đốt cháy hay retro, v.v.
    """)
    pass
