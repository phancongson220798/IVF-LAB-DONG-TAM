import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CẤU HÌNH GIAO DIỆN DI ĐỘNG (Dùng giao diện gọn - centered)
st.set_page_config(
    page_title="Lab IVF Input", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Thêm CSS tùy biến để tối ưu nút bấm và khoảng cách trên màn hình điện thoại
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 50px;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 10px;
    }
    .stDownloadButton>button {
        width: 100%;
        height: 45px;
        background-color: #2e7d32 !important;
        color: white !important;
    }
    div[data-testid="stNotification"] {
        padding: 10px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 Nhập Liệu Lab IVF")

# ĐỔI THÀNH FILE CSV (Khắc phục triệt để lỗi thiếu thư viện openpyxl của hệ thống)
DATA_FILE = "dulieu_thongso_tu.csv"

# Khởi tạo file CSV nếu chưa tồn tại
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Ngày đo", "Hạng mục kiểm tra", 
        "CO2 Đo Được (%)", "CO2 Hiệu Chuẩn (%)", 
        "O2 Đo Được (%)", "O2 Hiệu Chuẩn (%)",
        "VOCs (PPM)", "Bụi 0.3µm", "Bụi 0.5µm", "Bụi 5µm", "Ghi chú"
    ])
    # Sử dụng utf-8-sig để khi mở bằng Excel không bị lỗi hiển thị tiếng Việt (lỗi font)
    df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# Phân loại các hạng mục kiểm tra
tu_chi_co2 = ["Tủ A1", "Tủ A2", "Tủ A3", "Chamber 1", "Chamber 2"]
tu_co2_va_o2 = ["Tủ A4", "Tủ A5", "Tủ BT37/ Geri"]
hang_muc_khac = ["Độ bụi", "VOCs"]
tat_ca_hang_muc = tu_chi_co2 + tu_co2_va_o2 + hang_muc_khac

# --- PHẦN GIAO DIỆN NHẬP LIỆU ---
st.subheader("📝 Form Nhập Thông Số")

# Cấu hình ngày và hạng mục nằm dọc để dễ chọn trên mobile
ngay_do = st.date_input("🗓️ Ngày đo", datetime.now().date())
hang_muc = st.selectbox("🎛️ Chọn tủ / Hạng mục đo", tat_ca_hang_muc)

st.markdown("---")

# Khởi tạo form nhập số liệu
with st.form("data_entry_form", clear_on_submit=True):
    co2_do = co2_hc = o2_do = o2_hc = vocs = bui_03 = bui_05 = bui_5 = None
    
    # TRƯỜNG HỢP 1: Chọn đo VOCs
    if hang_muc == "VOCs":
        st.warning("☣️ THÔNG SỐ VOCs KHÔNG KHÍ")
        vocs = st.number_input("Nồng độ VOCs thực tế (PPM)", min_value=0.0, max_value=100.0, step=0.01, format="%.2f")
        
    # TRƯỜNG HỢP 2: Chọn đo Độ bụi
    elif hang_muc == "Độ bụi":
        st.info("🛡️ THÔNG SỐ ĐỘ BỤI PHÒNG LAB")
        bui_03 = st.number_input("Kích thước hạt 0.3 µm", min_value=0, value=0, step=1)
        bui_05 = st.number_input("Kích thước hạt 0.5 µm", min_value=0, value=0, step=1)
        bui_5 = st.number_input("Kích thước hạt 5 µm", min_value=0, value=0, step=1)
            
    # TRƯỜNG HỢP 3: Chọn các loại tủ nuôi cấy
    else:
        st.success(f"📊 THÔNG SỐ TỦ: {hang_muc.upper()}")
        
        st.markdown("**[Thông số CO2]**")
        co2_do = st.number_input("CO2 đo được (%)", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")
        co2_hc = st.number_input("CO2 hiệu chuẩn (Nếu có, %) ", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")
        
        if hang_muc in tu_co2_va_o2:
            st.markdown("---")
            st.markdown("**[Thông số O2]**")
            o2_do = st.number_input("O2 đo được (%)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")
            o2_hc = st.number_input("O2 hiệu chuẩn (Nếu có, %)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")

    st.markdown("---")
    ghi_chu = st.text_area("📝 Ghi chú thêm (nếu có)", placeholder="Nhập tình trạng thiết bị...")
    
    submit_button = st.form_submit_button("💾 LƯU DỮ LIỆU")

# Xử lý dữ liệu sau khi bấm Lưu
if submit_button:
    new_data = {
        "Ngày đo": ngay_do.strftime("%Y-%m-%d"),
        "Hạng mục kiểm tra": hang_muc,
        "CO2 Đo Được (%)": co2_do if co2_do is not None else "N/A",
        "CO2 Hiệu Chuẩn (%)": co2_hc if (co2_hc is not None and co2_hc > 0) else ("Không" if co2_hc is not None else "N/A"),
        "O2 Đo Được (%)": o2_do if o2_do is not None else "N/A",
        "O2 Hiệu Chuẩn (%)": o2_hc if (o2_hc is not None and o2_hc > 0) else ("Không" if o2_hc is not None else "N/A"),
        "VOCs (PPM)": vocs if vocs is not None else "N/A",
        "Bụi 0.3µm": bui_03 if bui_03 is not None else "N/A",
        "Bụi 0.5µm": bui_05 if bui_05 is not None else "N/A",
        "Bụi 5µm": bui_5 if bui_5 is not None else "N/A",
        "Ghi chú": ghi_chu
    }
    
    # Đọc và ghi bằng định dạng CSV mã hóa utf-8-sig
    df_old = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df_new = pd.concat([df_old, pd.DataFrame([new_data])], ignore_index=True)
    df_new.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    
    st.success(f"🎉 Đã lưu dữ liệu {hang_muc} thành công!")
    st.rerun()

# --- XEM LỊCH SỬ DỮ LIỆU ---
st.markdown("---")
st.subheader("📊 Lịch Sử Đã Nhập")

try:
    df_display = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    if not df_display.empty:
        st.dataframe(df_display.iloc[::-1], use_container_width=True)
        
        st.markdown("---")
        # Nút tải file CSV tương thích tốt nhất với Excel
        with open(DATA_FILE, "rb") as f:
            st.download_button(
                label="📥 TẢI FILE DỮ LIỆU (.CSV / EXCEL)",
                data=f,
                file_name=f"IVF_Lab_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Chưa có dữ liệu nào được ghi nhận.")
except Exception as e:
    st.error(f"Lỗi đọc dữ liệu: {e}")
