import streamlit as st

def run():
    ### 5.MÔ HÌNH LẠC THƯ 3X3 VÀ BẬC CAO VÔ TẬN
    """)
    
    # Nhập bậc của ma phương
    n = st.number_input("Nhập bậc lẻ n (>=3):", min_value=3, step=2, value=3)
    
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
    
    
    
    
    st.markdown("""
    ### Tác giả Nguyễn Duy Tuấn – với mục đích phụng sự tâm linh và cộng đồng.SĐT&ZALO: 0377442597.DONATE: nguyenduytuan techcombank 19033167089018
    """)
