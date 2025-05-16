import streamlit as st

def run():
    ### 3.🌐Biểu đồ cộng hưởng Schumann Trái Đất trực tuyến
    Nguồn: [Tomsk, Russia – Space Observing System]
    """)
    st.image("https://sosrff.tsu.ru/new/shm.jpg", caption="Schumann Resonance - Live", use_container_width=True)
    
    st.markdown("""
import streamlit as st

def run():
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

