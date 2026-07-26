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

# --- CẤU HÌNH GỬI GOOGLE FORM (THAY CÁC GIÁ TRỊ NÀY BẰNG LINK CỦA BẠN) ---
# Điền link Form phản hồi (Thay từ "/viewform" thành "/formResponse")
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
    """Gửi dữ liệu ẩn lên Google Form bằng phương thức POST"""
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
        # HTTP 200 có nghĩa là dữ liệu đã được đẩy lên Google Form thành công
        return response.status_code == 200
    except Exception:
        return False

# --- QUẢN LÝ DỮ LIỆU CỤC BỘ ---
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

# PHẦN 1: NHẬP DỮ LIỆU MỚI
st.sidebar.header("📝 Thêm Lịch Thay Bình Khí")

# Chọn loại khí ngoài Form để Streamlit bắt sự kiện đổi giao diện lập tức
gas_type = st.sidebar.selectbox("Loại khí", ["Khí Nitơ (N2)", "Khí CO2", "Khí trộn (Trigas)"])

# Tạo ô nhập S/N động
sn_input = "-"
if gas_type == "Khí trộn (Trigas)":
    sn_input = st.sidebar.text_input("Số S/N (Bắt buộc cho Khí trộn)", placeholder="Nhập mã S/N của bình khí trộn")

with st.sidebar.form(key='add_form', clear_on_submit=True):
    date_input = st.date_input("Ngày thay", datetime.date.today())
    branch_input = st.text_input("Nhánh thay (Ví dụ: Nhánh A, Tủ 1...)", placeholder="Nhập vị trí/nhánh")
    quantity_input = st.number_input("Số lượng bình thay", min_value=1, step=1, value=1)
    user_input = st.text_input("Người thực hiện", placeholder="Nhập tên nhân viên")
    
    submit_button = st.form_submit_button(label='Lưu thông tin')

if submit_button:
    # Kiểm tra điều kiện bắt buộc
    if gas_type == "Khí trộn (Trigas)" and (not sn_input or sn_input.strip() == "-"):
        st.sidebar.error("❌ Vui lòng nhập số S/N cho Khí trộn!")
    elif not branch_input.strip() or not user_input.strip():
        st.sidebar.error("❌ Vui lòng điền đầy đủ Nhánh thay và Người thực hiện!")
    else:
        # Làm sạch chuỗi đầu vào
        sn_clean = sn_input.strip()
        branch_clean = branch_input.strip()
        user_clean = user_input.strip()

        # Tạo dòng dữ liệu mới cho bộ nhớ Local
        new_row = pd.DataFrame([{
            "Ngày Thay": date_input,
            "Loại Khí": gas_type,
            "Số S/N (Khí trộn)": sn_clean,
            "Nhánh Thay": branch_clean,
            "Số Lượng Bình": quantity_input,
            "Người Thực Hiện": user_clean
        }])
        
        # Cập nhật session state và lưu file local
        updated_df = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.session_state.data = updated_df
        updated_df.to_csv(DATA_FILE, index=False)
        
        # GỬI DỮ LIỆU SANG GOOGLE FORM (TỰ ĐỘNG LÊN GOOGLE SHEET)
        with st.spinner("🔄 Đang gửi dữ liệu lên Google Sheets..."):
            form_status = send_to_google_form(date_input, gas_type, sn_clean, branch_clean, quantity_input, user_clean)
            
        if form_status:
            st.sidebar.success("🎉 Đã lưu local và đồng bộ Google Sheets thành công!")
        else:
            st.sidebar.warning("⚠️ Đã lưu local nhưng lỗi kết nối Internet (Không thể gửi tới Google Sheet).")
            
        st.rerun()

# PHẦN 2: THỐNG KÊ & BỘ LỌC
st.header("📊 Danh Sách & Bộ Lọc Dữ Liệu")

col1, col2, col3 = st.columns(3)
with col1:
    filter_gas = st.multiselect("Lọc theo loại khí", options=st.session_state.data["Loại Khí"].unique(), default=st.session_state.data["Loại Khí"].unique())
with col2:
    filter_branch = st.multiselect("Lọc theo nhánh", options=st.session_state.data["Nhánh Thay"].unique(), default=st.session_state.data["Nhánh Thay"].unique())
with col3:
    today = datetime.date.today()
    start_of_month = today.replace(day=1)
    date_range = st.date_input("Khoảng thời gian", value=(start_of_month, today))

# Áp dụng bộ lọc vào dataframe
df_filtered = st.session_state.data.copy()

if filter_gas:
    df_filtered = df_filtered[df_filtered["Loại Khí"].isin(filter_gas)]
if filter_branch:
    df_filtered = df_filtered[df_filtered["Nhánh Thay"].isin(filter_branch)]
    
# Sửa lỗi logic lọc khoảng ngày
if isinstance(date_range, tuple) and len(date_range) == 2:
    df_filtered = df_filtered[(df_filtered["Ngày Thay"] >= date_range[0]) & (df_filtered["Ngày Thay"] <= date_range[1])]

# Hiển thị bảng dữ liệu cục bộ
st.dataframe(df_filtered, use_container_width=True)

# PHẦN 3: XUẤT DỮ LIỆU EXCEL / CSV
st.subheader("💾 Xuất báo cáo")

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Lịch Thay Bình Khí')
    return output.getvalue()

col_ex1, col_ex2 = st.columns(2)
with col_ex1:
    st.download_button(
        label="📥 Tải file CSV",
        data=df_filtered.to_csv(index=False).encode('utf-8'),
        file_name=f"lich_thay_binh_khi_{datetime.date.today()}.csv",
        mime="text/csv"
    )
with col_ex2:
    excel_data = to_excel(df_filtered)
    st.download_button(
        label="📥 Tải file Excel",
        data=excel_data,
        file_name=f"lich_thay_binh_khi_{datetime.date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# PHẦN 4: XÓA DỮ LIỆU CỤC BỘ
st.markdown("---")
with st.expander("⚠️ Khu vực quản trị (Xóa dữ liệu cục bộ)"):
    st.warning("Hành động này chỉ xóa dữ liệu lưu tại máy chủ local. Dữ liệu trên Google Sheet (thông qua Google Form) sẽ không bị ảnh hưởng do không có API liên kết ngược.")
    confirm_delete = st.text_input("Nhập chữ 'XOA' để xác nhận", placeholder="XOA")
    if st.button("Xóa toàn bộ dữ liệu"):
        if confirm_delete == "XOA":
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.session_state.data = pd.DataFrame(columns=["Ngày Thay", "Loại Khí", "Số S/N (Khí trộn)", "Nhánh Thay", "Số Lượng Bình", "Người Thực Hiện"])
            st.success("💥 Đã xóa toàn bộ dữ liệu lịch sử cục bộ!")
            st.rerun()
        else:
            st.error("Mã xác nhận không đúng.")
