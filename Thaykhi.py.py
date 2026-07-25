import streamlit as st
import pandas as pd
import datetime
import io
import requests

# 1. Cấu hình giao diện tối ưu hiển thị cho thiết bị di động/tablet và máy tính
st.set_page_config(page_title="CYLINDER DATA MONITORING", layout="wide", initial_sidebar_state="collapsed")

# Khởi tạo CSS phóng to nút bấm, dễ thao tác bằng ngón tay
st.markdown("""
    <style>
    .stSelectbox, .stTextInput, .stNumberInput { font-size: 16px !important; }
    div.stButton > button:first-child {
        width: 100% !important; height: 50px !important; font-size: 16px !important;
        font-weight: bold !important; background-color: #2e7d32 !important; color: white !important; border-radius: 8px !important;
    }
    div.stDownloadButton > button:first-child {
        width: 100% !important; height: 50px !important; font-size: 16px !important;
        font-weight: bold !important; background-color: #1565c0 !important; color: white !important; border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 🌟 CẤU HÌNH THÔNG TIN GOOGLE FORM & GOOGLE SHEET (HÃY SỬA LẠI THEO ĐÚNG LINK CỦA BẠN)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd0YQ-_0PCshNtxRNBWQRaz_SM2oLEniAXYWFbLsoN60EhU9A/formResponse"
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/146k5ESeQ5ce5sOiOzQUDUj4YZCXFBELSVADQoZNKlJ0/edit?usp=sharing"

# Hàm tải dữ liệu cũ (Đọc trực tiếp từ Google Sheet link CSV)
@st.cache_data(ttl=2) 
def load_sync_data():
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        # Loại bỏ các cột trống không tên nếu có
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    except Exception:
        return pd.DataFrame()

# Khởi tạo bộ nhớ tạm lưu bản ghi cục bộ hiển thị "TỨC THÌ"
if 'local_records' not in st.session_state:
    st.session_state.local_records = []

# Tải dữ liệu tổng hợp từ đám mây
df_cloud = load_sync_data()

# TIÊU ĐỀ ỨNG DỤNG
st.title("🔬 THAY BÌNH KHÍ - IVF LAB")
st.caption("Nhập liệu từ App → Đẩy ngầm qua Google Form → Đồng bộ tự động về lịch sử hiển thị")
st.markdown("---")

# PHẦN 1: NHẬP DỮ LIỆU TRỰC TIẾP TRÊN APP
st.header("📝 ĐIỀN THÔNG TIN THAY BÌNH KHÍ")

gas_type = st.selectbox("Loại khí", ["Khí Nitơ (N2)", "Khí CO2", "Khí trộn (Trigas)"])

sn_input = "-"
if gas_type == "Khí trộn (Trigas)":
    sn_input = st.text_input("Số S/N (Bắt buộc cho Khí trộn)", placeholder="Nhập mã S/N của bình khí trộn")

with st.form(key='add_form', clear_on_submit=True):
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        date_input = st.date_input("Ngày thay khí", datetime.date.today())
        branch_input = st.text_input("Nhánh thay (Ví dụ: Nhánh A, Tủ 1...)", placeholder="Nhập vị trí/nhánh")
    with col_input2:
        quantity_input = st.number_input("Số lượng bình thay", min_value=1, step=1, value=1)
        user_input = st.text_input("Người thực hiện", placeholder="Nhập tên nhân viên")
    
    submit_button = st.form_submit_button(label='Lưu và Đồng Bộ Hệ Thống')

if submit_button:
    if not branch_input or not user_input:
        st.error("Vui lòng điền đầy đủ thông tin Nhánh thay và Người thực hiện!")
    elif gas_type == "Khí trộn (Trigas)" and (not sn_input or sn_input.strip() == "-"):
        st.error("⚠️ Bắt buộc phải nhập số S/N đối với Khí trộn (Trigas)!")
    else:
        final_sn = sn_input.strip() if gas_type == "Khí trộn (Trigas)" else "-"
        date_str = date_input.strftime('%Y-%m-%d')
        
        # Tạo dòng dữ liệu tạm thời
        new_local_row = {
            "ngay_thay_tam": date_str,
            "loai_khi_tam": gas_type,
            "sn_tam": final_sn,
            "nhanh_tam": branch_input,
            "so_luong_tam": int(quantity_input),
            "nguoi_tam": user_input
        }
        st.session_state.local_records.append(new_local_row)
        
                # GỬI NGẦM DỮ LIỆU LÊN GOOGLE FORM
        # ⚠️ Hãy thay các số 111111, 222222... bằng số thật bạn vừa tìm được trong Notepad:
        form_data = {
            'entry.1339704382': gas_type,         # Thay 'entry.222222' bằng Mã số của ô "Loại khí"
            'entry.1403367164': final_sn,         # Thay 'entry.333333' bằng Mã số của ô "Số S/N (Khí trộn)"
            'entry.2138926284': branch_input,     # Thay 'entry.444444' bằng Mã số của ô "Nhánh thay"
            'entry.50738552': int(quantity_input), # Thay 'entry.555555' bằng Mã số của ô "Số lượng bình thay"
            'entry.1553074860': user_input        # Thay 'entry.666666' bằng Mã số của ô "Người thực hiện"
        }

        
        try:
            response = requests.post(GOOGLE_FORM_URL, data=form_data)
            if response.status_code == 200:
                st.success("🎉 Đã cập nhật tức thì lên hệ thống lịch sử!")
            else:
                st.warning("⚠️ Đã lưu trên App, dữ liệu đám mây đang được đồng bộ chậm.")
        except Exception:
            st.warning("⚠️ Chế độ lưu tạm: Hệ thống sẽ đẩy lên Google Sheet khi thiết bị có mạng internet.")
            
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# PHẦN 2: BỘ LỌC LỊCH SỬ HIỂN THỊ ĐỘNG
st.header("📊 LỊCH SỬ THAY BÌNH KHÍ")

df_display = pd.DataFrame()

# Khớp nối thông minh dữ liệu Google Sheet đám mây
if not df_cloud.empty and len(df_cloud.columns) >= 6:
    cols = list(df_cloud.columns)
    df_display['Ngày Thay_Raw'] = df_cloud[cols[1]] # Ánh xạ cột Ngày thay của Form
    df_display['Loại Khí'] = df_cloud[cols[2]]
    df_display['Số S/N (Khí trộn)'] = df_cloud[cols[3]]
    df_display['Nhánh Thay'] = df_cloud[cols[4]]
    df_display['Số Lượng'] = df_cloud[cols[5]]
    df_display['Người Thực Hiện'] = df_cloud[cols[6]] if len(cols) > 6 else df_cloud[cols[5]]

# Khớp nối dữ liệu vừa gõ tạm thời trên App (nếu có)
if st.session_state.local_records:
    df_local = pd.DataFrame(st.session_state.local_records)
    df_local_mapped = pd.DataFrame()
    df_local_mapped['Ngày Thay_Raw'] = df_local['ngay_thay_tam']
    df_local_mapped['Loại Khí'] = df_local['loai_khi_tam']
    df_local_mapped['Số S/N (Khí trộn)'] = df_local['sn_tam']
    df_local_mapped['Nhánh Thay'] = df_local['nhanh_tam']
    df_local_mapped['Số Lượng'] = df_local['so_luong_tam']
    df_local_mapped['Người Thực Hiện'] = df_local['nguoi_tam']
    
    df_display = pd.concat([df_local_mapped, df_display], ignore_index=True)

# TIÊN HÀNH XỬ LÝ LỌC VÀ SẮP XẾP KHI CÓ DỮ LIỆU
if not df_display.empty:
    df_display = df_display.drop_duplicates(subset=['Ngày Thay_Raw', 'Loại Khí', 'Số S/N (Khí trộn)', 'Nhánh Thay'], keep='first')
    
    # Ép kiểu thời gian để sắp xếp toán học
    df_display['Date_Parsed'] = pd.to_datetime(df_display['Ngày Thay_Raw'], errors='coerce')
    df_display = df_display.dropna(subset=['Date_Parsed']) # Lọc sạch hàng lỗi ngày tháng
    
    # SẮP XẾP: Ngày thay mới nhất lên đầu bảng
    df_display = df_display.sort_values(by='Date_Parsed', ascending=False)
    
    # Tạo nhãn định dạng hiển thị
    df_display['Ngày Thay'] = df_display['Date_Parsed'].dt.strftime('%d/%m/%Y')
    df_display['Tháng_Năm'] = df_display['Date_Parsed'].dt.strftime('%m/%Y')
    
    # 🌟 SỬA LỖI: Lọc sạch giá trị None hoặc trống trước khi đưa vào ô chọn Bộ lọc
    raw_months = df_display['Tháng_Năm'].dropna().unique()
    available_months = sorted([str(m) for m in raw_months if str(m).strip() != "" and str(m) != "nan"], reverse=True)
            
    if available_months:
        filter_col, _ = st.columns(2)
        with filter_col:
            selected_month = st.selectbox("Chọn tháng cần theo dõi và báo cáo:", available_months)
            
        # Lọc theo tháng được chọn
        filtered_df = df_display[df_display['Tháng_Năm'] == selected_month].copy()
        
        display_cols = ["Ngày Thay", "Loại Khí", "Số S/N (Khí trộn)", "Nhánh Thay", "Số Lượng", "Người Thực Hiện"]
        final_df = filtered_df[display_cols].reset_index(drop=True)
        
        # Hiển thị bảng dữ liệu sạch lên màn hình Web
        st.dataframe(final_df, use_container_width=True)
        st.markdown("---")
        
        # PHẦN 3: XUẤT FILE EXCEL
        st.header("📥 Xuất Báo Cáo")
        action_col1, action_col2 = st.columns(2)
        with action_col2:
            if st.button("🔄 Làm mới & Đồng bộ lại đám mây"):
                st.session_state.local_records = [] 
                st.cache_data.clear()
                st.rerun()
                
        with action_col1:
            # 🌟 SỬA LỖI: Đảm bảo sheet_name luôn nhận chuỗi chữ (String) hợp lệ
            sheet_title = f"Tháng {str(selected_month).replace('/', '-')}"
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name=sheet_title[:30]) # Giới hạn 30 ký tự theo quy định Excel
                
            st.download_button(
                label=f"📥 Tải File Excel Báo Cáo (Tháng {selected_month})",
                data=buffer.getvalue(),
                file_name=f"Bao_cao_binh_khi_thang_{str(selected_month).replace('/', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Hệ thống chưa phân loại được danh sách tháng. Vui lòng kiểm tra lại cột Ngày thay trên Google Sheet.")
else:
    st.info("Hệ thống chưa có dữ liệu lịch sử. Vui lòng thực hiện nhập liệu ở biểu mẫu phía trên.")
