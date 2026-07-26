import streamlit as st
import pandas as pd
import datetime
import os
import requests

# --- 1. CẤU HÌNH ĐƯỜNG DẪN GOOGLE (BẮT BUỘC ĐỂ Ở ĐẦU FILE, KHÔNG ĐỔI TÊN BIẾN) ---
# Quy tắc: Thay cụm từ "/viewform" ở cuối link Form thành "/formResponse"
GOOGLE_FORM_URL = "https://google.com"

# Link xem dữ liệu trên Web: Dán link trang Google Sheet hiển thị kết quả của bạn vào đây
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

# Cấu hình trang ứng dụng (Dùng centered để gom cụm nội dung vừa màn hình dọc mobile)
st.set_page_config(page_title="IVF Gas Management", layout="centered")

# Đường dẫn file dữ liệu lưu trữ cục bộ trên máy chủ Web
DATA_FILE = "lich_thay_binh_khi.csv"

def send_to_google_form(date_val, gas_val, sn_val, branch_val, qty_val, user_val):
    """Gửi dữ liệu ẩn lên Google Form bằng phương thức POST để tự động ghi vào Google Sheet"""
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

# TIÊU ĐỀ ỨNG DỤNG TỐI ƯU GỌN GÀNG CHO ĐIỆN THOẠI
st.markdown("<h2 style='text-align: center; color: #0073e6;'>🔬 GIÁM SÁT THAY BÌNH KHÍ</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; color: gray;'>Hệ thống quản lý IVF LAB trực tuyến</p>", unsafe_allow_html=True)
st.markdown("---")

# PHẦN 1: NHẬP DỮ LIỆU MỚI (Đưa ra màn hình chính, thiết kế dạng thẻ cuộn dọc mobile)
st.markdown("### 📝 Cập Nhật Lịch Thay Khí")

# Ô chọn loại khí (để bắt sự kiện ẩn hiện S/N lập tức trên mobile)
gas_type = st.selectbox("Loại khí", ["Khí Nitơ (N2)", "Khí CO2", "Khí trộn (Trigas)"])

# Tạo ô nhập S/N ĐỘNG (Chỉ xuất hiện khi chọn Khí trộn)
sn_input = "-"
if gas_type == "Khí trộn (Trigas)":
    sn_input = st.text_input("Số S/N (Bắt buộc)", placeholder="Nhập mã S/N bình khí trộn")

# Gom cụm các thông tin còn lại vào Form chính để giảm tải render trên điện thoại
with st.form(key='mobile_add_form', clear_on_submit=True):
    date_input = st.date_input("Ngày thay", datetime.date.today())
    branch_input = st.text_input("Nhánh thay / Vị trí tủ", placeholder="Ví dụ: Nhánh A, Tủ 1...")
    quantity_input = st.number_input("Số lượng bình", min_value=1, step=1, value=1)
    user_input = st.text_input("Người thực hiện", placeholder="Tên nhân viên")
    
    # Nút bấm lưu thiết kế lớn, nổi bật dễ bấm bằng ngón tay
    submit_button = st.form_submit_button(label='💾 LƯU THÔNG TIN', use_container_width=True)

if submit_button:
    if not branch_input.strip() or not user_input.strip():
        st.error("❌ Vui lòng điền đầy đủ Nhánh thay và Người thực hiện!")
    elif gas_type == "Khí trộn (Trigas)" and (not sn_input or sn_input.strip() == "-"):
        st.error("⚠️ Bắt buộc nhập số S/N đối với Khí trộn (Trigas)!")
    else:
        final_sn = sn_input.strip() if gas_type == "Khí trộn (Trigas)" else "-"
        final_branch = branch_input.strip()
        final_user = user_input.strip()
        
        new_row = {
            "Ngày Thay": date_input,
            "Loại Khí": gas_type,
            "Số S/N (Khí trộn)": final_sn,
            "Nhánh Thay": final_branch,
            "Số Lượng Bình": quantity_input,
            "Người Thực Hiện": final_user
        }
        
        # Cập nhật local
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.data.to_csv(DATA_FILE, index=False)
        
        # Gửi Google Form trực tuyến
        with st.status("🔄 Đang đồng bộ lên hệ thống...", expanded=False) as status:
            form_status = send_to_google_form(date_input, gas_type, final_sn, final_branch, quantity_input, final_user)
            if form_status:
                status.update(label="🎉 Thành công!", state="complete")
            else:
                status.update(label="⚠️ Lỗi mạng, chưa đồng bộ!", state="error")
        
        st.rerun()

st.markdown("---")

# PHẦN 2: TRA CỨU NHANH TRÊN MOBILE
st.markdown("### 📊 Tra Cứu Lịch Sử")

if not st.session_state.data.empty:
    df_display = st.session_state.data.copy()
    df_display['Ngày Thay'] = pd.to_datetime(df_display['Ngày Thay'])
    df_display = df_display.sort_values(by='Ngày Thay', ascending=False)
    df_display['Tháng_Năm'] = df_display['Ngày Thay'].dt.strftime('%m/%Y')
    
    available_months = []
    for m in df_display['Tháng_Năm']:
        if m not in available_months:
            available_months.append(m)
            
    # Bộ lọc tháng tối giản chiếm trọn chiều ngang màn hình điện thoại
    selected_month = st.selectbox("Xem dữ liệu theo tháng:", available_months)
    
    filtered_df = df_display[df_display['Tháng_Năm'] == selected_month].copy()
    filtered_df['Ngày Thay'] = filtered_df['Ngày Thay'].dt.strftime('%d/%m') # Rút ngắn thành DD/MM để vừa màn hình dọc di động
    
    # Định dạng lại bảng hiển thị rút gọn cột cho Mobile đỡ bị tràn ngang
    display_cols = ["Ngày Thay", "Loại Khí", "Nhánh Thay", "Số Lượng Bình"]
    final_df = filtered_df[display_cols].reset_index(drop=True)
    
    # Hiển thị bảng dạng cuộn ngang tối ưu di động
    st.dataframe(final_df, use_container_width=True)
    
    # PHẦN 3: GIẢI PHÁP NÚT BẤM HTML THUẦN (Đã sửa lỗi xung đột dấu ngoặc nhọn f-string)
    st.markdown(" ")
    
    # Sử dụng nối chuỗi bằng dấu cộng (+) thay vì f-string để tránh lỗi cú pháp dấu ngoặc nhọn của CSS
    html_button = '<a href="' + GOOGLE_SHEET_URL + '" target="_blank" style="text-decoration: none;">' + """
        <div style="
            background-color: #0073e6;
            color: white;
            padding: 12px 20px;
            text-align: center;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        ">
            📈 XEM BÁO CÁO & IN ẤN (GOOGLE SHEET)
        </div>
    </a>
    """
    st.markdown(html_button, unsafe_allow_html=True)


else:
    st.info("Chưa có dữ liệu. Hãy nhập thông tin ở form phía trên.")
