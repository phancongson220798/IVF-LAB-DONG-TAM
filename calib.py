import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

# 1. CẤU HÌNH GIAO DIỆN DI ĐỘNG
st.set_page_config(page_title="ĐO VÀ HIỆU CHUẨN THÔNG SỐ", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 50px; font-size: 18px !important; font-weight: bold; border-radius: 10px; }
    .stDownloadButton>button { width: 100%; height: 45px; background-color: #2e7d32 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 ĐO VÀ HIỆU CHUẨN TỦ NUÔI")

# --- CẤU HÌNH GOOGLE FORM (THAY ĐỔI THÔNG TIN CỦA BẠN TẠI ĐY) ---
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeWMkxWJa34E8kapIn5cikjlmKWHM2GUZg7YAHk4-ILZVI9Sw/formResponse"

# Thay thế các mã số entry tương ứng với từng câu hỏi bạn lấy được ở Bước 2
FORM_ENTRIES = {
    "hang_muc": "entry.658339313",      # ID câu hỏi Hạng mục kiểm tra
    "co2_do": "entry.1836243222",        # ID câu hỏi CO2 Đo Được
    "co2_hc": "entry.631609850",        # ID câu hỏi CO2 Hiệu Chuẩn
    "o2_do": "entry.2070218032",         # ID câu hỏi O2 Đo Được
    "o2_hc": "entry.142170793",         # ID câu hỏi O2 Hiệu Chuẩn
    "vocs": "entry.1814404491",          # ID câu hỏi VOCs
    "bui_03": "entry.346284382",        # ID câu hỏi Bụi 0.3
    "bui_05": "entry.1450782344",        # ID câu hỏi Bụi 0.5
    "bui_5": "entry.647928021",         # ID câu hỏi Bụi 5
    "ghi_chu": "entry.67856138"        # ID câu hỏi Ghi chú
}
# --------------------------------------------------------------------

DATA_FILE = "dulieu_thongso_tu.csv"
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Ngày đo", "Hạng mục kiểm tra", "CO2 Đo Được (%)", "CO2 Hiệu Chuẩn (%)", 
        "O2 Đo Được (%)", "O2 Hiệu Chuẩn (%)", "VOCs (PPM)", "Bụi 0.3µm", "Bụi 0.5µm", "Bụi 5µm", "Ghi chú"
    ])
    df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# Phân loại lại danh sách hạng mục
tu_chi_co2 = ["Tủ A1", "Tủ A2", "Tủ A3", "Chamber 1", "Chamber 2"]
tu_co2_va_o2_co_hc = ["Tủ A4", "Tủ A5"]  # Chỉ có tủ A4, A5 mới có hiệu chuẩn O2
hang_muc_khac = ["Tủ BT37/ Geri", "Độ bụi", "VOCs"]
tat_ca_hang_muc = tu_chi_co2 + tu_co2_va_o2_co_hc + hang_muc_khac

st.subheader("📝 Nhập Thông Số")
ngay_do = st.date_input("🗓️ Ngày đo", datetime.now().date())
hang_muc = st.selectbox("🎛️ Chọn tủ / Thông số", tat_ca_hang_muc)

st.markdown("---")

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
        
    # TRƯỜNG HỢP 3: Tủ BT37/ Geri (Đo cả CO2 và O2 nhưng KHÔNG HIỆN HIỆU CHUẨN)
    elif hang_muc == "Tủ BT37/ Geri":
        st.success("📊 THÔNG SỐ TỦ: BT37 / GERI")
        co2_do = st.number_input("Thông số CO2 đo được (%)", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")
        o2_do = st.number_input("Thông số O2 đo được (%)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")
        
    # TRƯỜNG HỢP 4: Các loại tủ nuôi cấy thông thường khác (A1, A2, A3, A4, A5, Chamber 1, Chamber 2)
    else:
        st.success(f"📊 THÔNG SỐ TỦ: {hang_muc.upper()}")
        st.markdown("**[Thông số CO2]**")
        co2_do = st.number_input("CO2 đo được (%)", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")
        co2_hc = st.number_input("CO2 hiệu chuẩn (Nếu có, %) ", min_value=0.0, max_value=20.0, step=0.1, format="%.1f")
        
        if hang_muc in tu_co2_va_o2_co_hc:
            st.markdown("---")
            st.markdown("**[Thông số O2]**")
            o2_do = st.number_input("O2 đo được (%)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")
            o2_hc = st.number_input("O2 hiệu chuẩn (Nếu có, %)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")

    st.markdown("---")
    ghi_chu = st.text_area("📝 Ghi chú thêm (nếu có)", placeholder="Nhập tình trạng thiết bị...")
    submit_button = st.form_submit_button("💾 LƯU DỮ LIỆU")

if submit_button:
    # Chuẩn bị dữ liệu để lưu trữ (Nếu không nhập hiệu chuẩn sẽ tự động điền "Không")
    val_co2_do = str(co2_do) if co2_do is not None else "N/A"
    val_co2_hc = str(co2_hc) if (co2_hc is not None and co2_hc > 0) else ("Không" if co2_hc is not None else "N/A")
    val_o2_do = str(o2_do) if o2_do is not None else "N/A"
    val_o2_hc = str(o2_hc) if (o2_hc is not None and o2_hc > 0) else ("Không" if o2_hc is not None else "N/A")
    val_vocs = str(vocs) if vocs is not None else "N/A"
    val_bui_03 = str(bui_03) if bui_03 is not None else "N/A"
    val_bui_05 = str(bui_05) if bui_05 is not None else "N/A"
    val_bui_5 = str(bui_5) if bui_5 is not None else "N/A"

    # Lưu vào file CSV nội bộ dự phòng
    new_data = {
        "Ngày đo": ngay_do.strftime("%Y-%m-%d"), "Hạng mục kiểm tra": hang_muc,
        "CO2 Đo Được (%)": val_co2_do, "CO2 Hiệu Chuẩn (%)": val_co2_hc,
        "O2 Đo Được (%)": val_o2_do, "O2 Hiệu Chuẩn (%)": val_o2_hc,
        "VOCs (PPM)": val_vocs, "Bụi 0.3µm": val_bui_03, "Bụi 0.5µm": val_bui_05, "Bụi 5µm": val_bui_5,
        "Ghi chú": ghi_chu
    }
    df_old = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df_new = pd.concat([df_old, pd.DataFrame([new_data])], ignore_index=True)
    df_new.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

    # ĐỒNG BỘ LÊN GOOGLE SHEET QUA GOOGLE FORM
    form_data = {
        FORM_ENTRIES["hang_muc"]: f"{ngay_do.strftime('%Y-%m-%d')} | {hang_muc}",
        FORM_ENTRIES["co2_do"]: val_co2_do,
        FORM_ENTRIES["co2_hc"]: val_co2_hc,
        FORM_ENTRIES["o2_do"]: val_o2_do,
        FORM_ENTRIES["o2_hc"]: val_o2_hc,
        FORM_ENTRIES["vocs"]: val_vocs,
        FORM_ENTRIES["bui_03"]: val_bui_03,
        FORM_ENTRIES["bui_05"]: val_bui_05,
        FORM_ENTRIES["bui_5"]: val_bui_5,
        FORM_ENTRIES["ghi_chu"]: ghi_chu
    }
    
    try:
        response = requests.post(GOOGLE_FORM_URL, data=form_data)
        if response.status_code == 200:
            st.success(f"🎉 Đã lưu và đồng bộ lên Google Sheet thành công!")
        else:
            st.warning("⚠️ Đã lưu cục bộ, nhưng đồng bộ Google Sheet thất bại (Lỗi kết nối Form).")
    except Exception as e:
        st.warning(f"⚠️ Đã lưu cục bộ, lỗi đồng bộ Cloud: {e}")
        
    st.rerun()

# --- XEM LỊCH SỬ DỮ LIỆU ---
st.markdown("---")
st.subheader("📊 Lịch Sử Cục Bộ (Máy chủ)")
try:
    df_display = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    if not df_display.empty:
        st.dataframe(df_display.iloc[::-1], use_container_width=True)
except Exception as e:
    st.error(f"Lỗi đọc dữ liệu: {e}")
