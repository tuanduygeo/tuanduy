import streamlit as st
from dem_utils import dem_block
from astrology_utils import astrology_block
from misc_utils import (
    geo_html_block,
    magic_square_block,
    schumann_block,
    kp_index_block
)

def main():
    st.set_page_config(layout="wide")
    st.markdown("### 1. PHONG THỦY ĐỊA LÝ – BẢN ĐỒ ĐỊA MẠCH")
    geo_html_block()

    st.markdown("### 2. Chiêm tinh Ấn Độ")
    astrology_block()

    
    dem_block()

    st.markdown("### 4. Ma phương, Schumann, Kp Index")
    magic_square_block()
    schumann_block()
    kp_index_block()

    st.markdown("---\n### Tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng. SĐT&ZALO: 0377442597. DONATE: nguyenduytuan techcombank 19033167089018")

if __name__ == "__main__":
    main()
