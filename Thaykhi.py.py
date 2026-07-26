import streamlit as st
import pandas as pd
import datetime
import os
import io
import requests

# Cấu hình trang ứng dụng
st.set_page_config(page_title="Quản Lý Thay Bình Khí - Hỗ Trợ Sinh Sản", layout="wide")

# Đường dẫn file dữ liệu lưu trữ cục bộ
DATA_FILE = "lich_thay_binh_khi.csv"

# --- CẤU HÌNH GOOGLE FORM TRUNG GIAN (THAY CÁC GIÁ TRỊ NÀY BẰNG LINK CỦA BẠN) ---
# Quy tắc: Thay cụm từ "/viewform" ở cuối link Form thành "/formResponse"
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd0YQ-_0PCshNtxRNBWQRaz_SM2oLEniAXYWFbLsoN60EhU9A/formResponse"

# Điền các mã Entry tương ứng với từng câu hỏi trên Google Form của bạn
FORM_ENTRIES = {
    "NgayThay": "entry.1339704382",      # Mã câu hỏi Ngày Thay
    "LoaiKhi": "entry.1451757059",       # Mã câu hỏi Loại Khí
    "SoSN": "entry.1403367164",          # Mã câu hỏi Số S/N
    "NhanhThay": "entry.2138926284",     # Mã câu hỏi Nhánh Thay
    "SoLuong": "entry.50738552",       # Mã câu hỏi Số Lượng
    "NguoiThucHien": "entry.1553074860"  # Mã câu hỏi Người Thực Hiện
}

def send_to_google_form(date_val, gas_val, sn_val, branch_val, qty_val, user_val):
    """Gửi dữ liệu ẩn lên Google Form bằng phương thức POST để đẩy về Google Sheet"""
    payload = {
        FORM_ENTRIES["NgayThay"]: str(date_val),
        FORM_ENTRIES["LoaiKhi"]: str(gas_val),
        FORM_ENTRIES["SoSN"]: str(sn_val),
        FORM_ENTRIES["NhanhThay"]: str(branch_val),
        FORM_ENTRIES["SoLuong"]: str(qty_val),
        FORM_ENTRIES["NguoiThucHien"]: str(user_val)
    }
    try:
        response = requests.post(GOOGLE_FORM_URL, data=payload, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# --- HÀM KHỞI TẠO HOẶC TẢI DỮ LIỆU CŨ ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Ngày Thay'] = pd.to_datetime(df['Ngày Thay']).dt.date
        if "Số S/N (Khí trộn)" not in df.columns:
            df["Số S/N (Khí trộn)"] = "-"
        return df
    else:
        return pd.DataFrame(columns=["Ngày Thay", "Loại Khí", "Số S/N (Khí trộn)", "Nhánh Thay", "Số Lượng Bình", "Người Thực Hiện"])

# Tải dữ liệu vào session state để quản lý
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# TIÊU ĐỀ ỨNG DỤNG
st.title("🔬 HỆ THỐNG GIÁM SÁT THAY BÌNH KHÍ - IVF LAB")
st.markdown("---")

# PHẦN 1: NHẬP DỮ LIỆU MỚI (Đã tối ưu ẩn/hiện S/N)
st.sidebar.header("📝 Thêm Lịch Thay Bình Khí")

# Bước 1: Chọn loại khí trước ở ngoài Form để Streamlit bắt được sự kiện thay đổi lập tức
gas_type = st.sidebar.selectbox("Loại khí", ["Khí Nitơ (N2)", "Khí CO2", "Khí trộn (Trigas)"])

# Bước 2: Tạo ô nhập S/N ĐỘNG (Chỉ xuất hiện khi chọn Khí trộn)
sn_input = "-"
if gas_type == "Khí trộn (Trigas)":
    sn_input = st.sidebar.text_input("Số S/N (Bắt buộc cho Khí trộn)", placeholder="Nhập mã S/N của bình khí trộn")

# Bước 3: Tạo Form cho các thông tin còn lại và nút bấm để gom cụm dữ liệu
with st.sidebar.form(key='add_form', clear_on_submit=True):
    date_input = st.date_input("Ngày thay", datetime.date.today())
    branch_input = st.text_input("Nhánh thay (Ví dụ: Nhánh A, Tủ 1...)", placeholder="Nhập vị trí/nhánh")
    quantity_input = st.number_input("Số lượng bình thay", min_value=1, step=1, value=1)
    user_input = st.text_input("Người thực hiện", placeholder="Nhập tên nhân viên")
    
    submit_button = st.form_submit_button(label='Lưu thông tin')

if submit_button:
    # Kiểm tra điều kiện bắt buộc
    if not branch_input.strip() or not user_input.strip():
        st.sidebar.error("Vui lòng điền đầy đủ thông tin Nhánh thay và Người thực hiện!")
    elif gas_type == "Khí trộn (Trigas)" and (not sn_input or sn_input.strip() == "-"):
        st.sidebar.error("⚠️ Bắt buộc phải nhập số S/N đối với Khí trộn (Trigas)!")
    else:
        # Chuẩn hóa giá trị trước khi lưu
        final_sn = sn_input.strip() if gas_type == "Khí trộn (Trigas)" else "-"
        final_branch = branch_input.strip()
        final_user = user_input.strip()
        
        # Tạo dòng dữ liệu mới
        new_row = {
            "Ngày Thay": date_input,
            "Loại Khí": gas_type,
            "Số S/N (Khí trộn)": final_sn,
            "Nhánh Thay": final_branch,
            "Số Lượng Bình": quantity_input,
            "Người Thực Hiện": final_user
        }
        
        # Cập nhật vào DataFrame cục bộ
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.data.to_csv(DATA_FILE, index=False)
        
        # ĐỒNG BỘ SANG GOOGLE FORM TRUNG GIAN
        with st.spinner("🔄 Đang gửi dữ liệu lên Google Sheets..."):
            form_status = send_to_google_form(date_input, gas_type, final_sn, final_branch, quantity_input, final_user)
            
        if form_status:
            st.sidebar.success("🎉 Đã lưu local và đồng bộ Google Sheets thành công!")
        else:
            st.sidebar.warning("⚠️ Đã lưu local nhưng lỗi kết nối (Không thể gửi tới Google Sheet).")
            
        # Làm mới trang để cập nhật bảng dữ liệu ngay lập tức
        st.rerun()

# PHẦN 2: LỌC VÀ THỐNG KÊ THEO THÁNG
st.header("📊 Bộ Lọc Lịch Sử Theo Tháng")

if not st.session_state.data.empty:
    df_display = st.session_state.data.copy()
    df_display['Ngày Thay'] = pd.to_datetime(df_display['Ngày Thay'])
    
    # SẮP XẾP: Đưa ngày mới thay gần nhất lên đầu bảng
    df_display = df_display.sort_values(by='Ngày Thay', ascending=False)
    
    # Tạo danh sách các Tháng/Năm để lọc
    df_display['Tháng_Năm'] = df_display['Ngày Thay'].dt.strftime('%m/%Y')
    
    # Lấy danh sách tháng duy nhất và giữ nguyên thứ tự thời gian mới nhất
    available_months = []
    for m in df_display['Tháng_Năm']:
        if m not in available_months:
            available_months.append(m)
    
    # Bộ lọc trên giao diện chính
    col1, col2 = st.columns([1, 3])  
    with col1:
        selected_month = st.selectbox("Chọn tháng cần theo dõi:", available_months)
    
    # Lọc dữ liệu theo tháng đã chọn
    filtered_df = df_display[df_display['Tháng_Năm'] == selected_month].copy()
    
    # Định dạng lại ngày hiển thị cho chuẩn Việt Nam (DD/MM/YYYY)
    filtered_df['Ngày Thay'] = filtered_df['Ngày Thay'].dt.strftime('%d/%m/%Y')
    
    # Cấu hình các cột hiển thị
    display_cols = ["Ngày Thay", "Loại Khí", "Số S/N (Khí trộn)", "Nhánh Thay", "Số Lượng Bình", "Người Thực Hiện"]
    final_df = filtered_df[display_cols].reset_index(drop=True)
    
    # Hiển thị bảng dữ liệu
    st.dataframe(final_df, use_container_width=True)
    
    # PHẦN 3: XUẤT FILE EXCEL (Đã sửa đổi engine sang xlsxwriter để tránh lỗi)
    st.markdown("---")
    st.header("📥 Xuất Dữ Liệu")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False, sheet_name=f"Tháng {selected_month.replace('/', '-')}")
    
    st.download_button(
        label=f"📥 Tải File Excel (Tháng {selected_month})",
        data=buffer.getvalue(),
        file_name=f"Lich_thay_binh_khi_{selected_month.replace('/', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Chưa có dữ liệu nào được ghi nhận. Vui lòng nhập dữ liệu ở thanh bên trái.")
