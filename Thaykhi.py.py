import streamlit as st
import pandas as pd
import datetime
import os
import io

# 1. Cấu hình giao diện chuẩn hóa rộng hết cỡ, tối ưu hiển thị cho thiết bị di động/tablet
st.set_page_config(
    page_title="Giám Sát Bình Khí IVF", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Ẩn thanh bên để dành toàn bộ không gian cho màn hình nhỏ
)

# Khởi tạo CSS tùy biến để nút bấm to, rõ ràng, dễ chạm trên màn hình cảm ứng
st.markdown("""
    <style>
    .stSelectbox, .stTextInput, .stNumberInput {
        font-size: 16px !important;
    }
    div.stButton > button:first-child {
        width: 100% !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    div.stDownloadButton > button:first-child {
        width: 100% !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        background-color: #1565c0 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ĐƯỜNG DẪN FILE EXCEL LƯU TRỮ NỘI BỘ
DATA_FILE = "lich_thay_binh_khi_goc.xlsx"

# Hàm khởi tạo hoặc tải dữ liệu cũ từ file Excel nội bộ
def load_local_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
            # Chuyển đổi cột ngày về đúng định dạng datetime
            df['Ngày Thay'] = pd.to_datetime(df['Ngày Thay']).dt.date
            return df
        except Exception:
            return pd.DataFrame(columns=["Ngày Thay", "Loại Khí", "Số S/N (Khí trộn)", "Nhánh Thay", "Số Lượng Bình", "Người Thực Hiện"])
    else:
        return pd.DataFrame(columns=["Ngày Thay", "Loại Khí", "Số S/N (Khí trộn)", "Nhánh Thay", "Số Lượng Bình", "Người Thực Hiện"])

# Tải dữ liệu vào bộ nhớ tạm session state
if 'data' not in st.session_state:
    st.session_state.data = load_local_data()

# TIÊU ĐỀ ỨNG DỤNG NỘI BỘ
st.title("🔬 HỆ THỐNG GIÁM SÁT THAY BÌNH KHÍ - IVF LAB")
st.caption("Ứng dụng quản lý lưu trữ nội bộ (Offline)")
st.markdown("---")

# PHẦN 1: NHẬP DỮ LIỆU MỚI (TẬP TRUNG GIAO DIỆN CHÍNH, XẾP DỌC TRÊN ĐIỆN THOẠI)
st.header("📝 Ghi Nhận Lịch Thay Bình Khí Mới")

gas_type = st.selectbox("Loại khí", ["Khí Nitơ (N2)", "Khí CO2", "Khí trộn (Trigas)"])

# Ẩn/Hiện ô nhập S/N thông minh theo loại khí trực tiếp trên giao diện
sn_input = "-"
if gas_type == "Khí trộn (Trigas)":
    sn_input = st.text_input("Số S/N (Bắt buộc cho Khí trộn)", placeholder="Nhập mã S/N của bình khí trộn")

with st.form(key='add_form', clear_on_submit=True):
    # Chia cột linh hoạt: Trên PC xếp ngang, trên Điện thoại tự xếp chồng thành hàng dọc
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        date_input = st.date_input("Ngày thay", datetime.date.today())
        branch_input = st.text_input("Nhánh thay (Ví dụ: Nhánh A, Tủ 1...)", placeholder="Nhập vị trí/nhánh")
    with col_input2:
        quantity_input = st.number_input("Số lượng bình thay", min_value=1, step=1, value=1)
        user_input = st.text_input("Người thực hiện", placeholder="Nhập tên nhân viên")
    
    submit_button = st.form_submit_button(label='Lưu dữ liệu nội bộ')

if submit_button:
    if not branch_input or not user_input:
        st.error("Vui lòng điền đầy đủ thông tin Nhánh thay và Người thực hiện!")
    elif gas_type == "Khí trộn (Trigas)" and (not sn_input or sn_input.strip() == "-"):
        st.error("⚠️ Bắt buộc phải nhập số S/N đối với Khí trộn (Trigas)!")
    else:
        final_sn = sn_input.strip() if gas_type == "Khí trộn (Trigas)" else "-"
        
        new_row = {
            "Ngày Thay": date_input,
            "Loại Khí": gas_type,
            "Số S/N (Khí trộn)": final_sn,
            "Nhánh Thay": branch_input,
            "Số Lượng Bình": quantity_input,
            "Người Thực Hiện": user_input
        }
        
        # Cập nhật và lưu vào file Excel nội bộ
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.data.to_excel(DATA_FILE, index=False)
        st.success("🎉 Đã lưu dữ liệu vào hệ thống nội bộ thành công!")
        st.rerun()

st.markdown("---")

# PHẦN 2: BỘ LỌC LỊCH SỬ THEO THÁNG & SẮP XẾP NGÀY
st.header("📊 Bộ Lọc Lịch Sử Theo Tháng")

if not st.session_state.data.empty:
    df_display = st.session_state.data.copy()
    df_display['Ngày Thay'] = pd.to_datetime(df_display['Ngày Thay'])
    
    # SẮP XẾP: Luôn đưa lịch sử mới thay gần nhất lên đầu bảng
    df_display = df_display.sort_values(by='Ngày Thay', ascending=False)
    
    # Tạo nhãn Tháng_Năm phục vụ bộ lọc
    df_display['Tháng_Năm'] = df_display['Ngày Thay'].dt.strftime('%m/%Y')
    
    available_months = []
    for m in df_display['Tháng_Năm']:
        if m not in available_months:
            available_months.append(m)
            
    filter_col, _ = st.columns([1, 1])
    with filter_col:
        selected_month = st.selectbox("Chọn tháng cần theo dõi:", available_months)
        
    # Lọc dữ liệu theo tháng đã chọn
    filtered_df = df_display[df_display['Tháng_Năm'] == selected_month].copy()
    
    # Định dạng ngày hiển thị chuẩn Việt Nam (DD/MM/YYYY)
    filtered_df['Ngày Thay'] = filtered_df['Ngày Thay'].dt.strftime('%d/%m/%Y')
    
    # Cấu hình các cột hiển thị sạch sẽ
    display_cols = ["Ngày Thay", "Loại Khí", "Số S/N (Khí trộn)", "Nhánh Thay", "Số Lượng Bình", "Người Thực Hiện"]
    final_df = filtered_df[display_cols].reset_index(drop=True)
    
    # Hiển thị bảng dữ liệu (Cho phép cuộn/vuốt ngang trên màn hình điện thoại)
    st.dataframe(final_df, use_container_width=True)
    
    # PHẦN 3: XUẤT FILE EXCEL BÁO CÁO ĐỘNG
    st.markdown("---")
    st.header("📥 Xuất Báo Cáo")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        final_df.to_excel(writer, index=False, sheet_name=f"Tháng {selected_month.replace('/', '-')}")
        
    st.download_button(
        label=f"📥 Tải File Excel Báo Cáo (Tháng {selected_month})",
        data=buffer.getvalue(),
        file_name=f"Bao_cao_binh_khi_thang_{selected_month.replace('/', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Chưa có dữ liệu nào được ghi nhận. Vui lòng nhập thông tin ở biểu mẫu phía trên.")
