import streamlit as st
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import swisseph as swe
import datetime
import os
import math
import pytz
import requests
import streamlit.components.v1 as components
from map_viewer import run as run_map
from indian_astrology import run as run_astro
from schumann import run as run_schumann
from magic_square import run as run_magic
import sys
import os
sys.path.append(os.path.dirname(__file__))
st.set_page_config(layout="wide")

# Sidebar menu
st.sidebar.title("📂 Menu")
section = st.sidebar.selectbox(
    "Chọn chuyên mục:",
    [
        "1. Bản đồ Địa Mạch",
        "2. Chiêm tinh Ấn Độ",
        "3. Biểu đồ Schumann",
        "4. Dữ liệu địa từ",
        "5. Ma phương Lạc Thư"
    ]
)

# Route to each section
if section.startswith("1"):
    run_map()
elif section.startswith("2"):
    run_astro()
elif section.startswith("3"):
    run_schumann()

elif section.startswith("5"):
    run_magic()
