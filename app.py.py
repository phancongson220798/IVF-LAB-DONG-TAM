import streamlit as st
import pandas as pd
import datetime
import requests
import os

# 1. Cấu hình giao diện dashboard
st.set_page_config(
    page_title="IVF Lab Parameter Input",
    page_icon="🔬",
    layout="wide"
)

# =====================================================================
# CẤU HÌNH THÔNG TIN BIỂU MẪU GOOGLE FORMS CỦA BẠN TẠI ĐÂY
# Bạn cần thay thế link Form và các mã entry tương ứng ở đây để app hoạt động
# =====================================================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdyYeaBLuWBHQkA-0S6LD_UkLabCmuOLhBPZdgRCF4KxRjUWw/formResponse"

ENTRY_THOI_GIAN = "entry.1208343403"
ENTRY_THIET_BI = "entry.708086797"
ENTRY_THONG_SO = "entry.1303762242"
ENTRY_GIA_TRI = "entry.594501047"
ENTRY_CHUYEN_VIEN = "entry.666373778"
ENTRY_GHI_CHU = "entry.1130830415"

# Đường link Google Sheets của bạn ở chế độ công khai (Bất kỳ ai có liên kết đều có thể xem)
# Hãy giữ nguyên đoạn đuôi '/gviz/tq?tqx=out:csv' để app tự ép file thành dạng CSV khi đọc
URL_GOOGLE_SHEET = "https://google.com"

# 2. ĐỊNH NGHĨA CẤU HÌNH CHI TIẾT CÁC THIẾT BỊ
CHAMBER_FIELDS = {
    "Cài đặt: Nhiệt trái (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt phải (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt giữa (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt trung tâm (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt khí (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: CO2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
    
    "Thực tế: Nhiệt trái (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt phải (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt giữa (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt trung tâm (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt khí (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: CO2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"}
}

DEVICE_CONFIGS = {
    "Tủ A1": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A2": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A3": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A4": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "O2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A5": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "O2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Chamber 1": CHAMBER_FIELDS,
    "Chamber 2": CHAMBER_FIELDS,
    "BT37 1": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Flow (mL/min)": {"type": "number", "default": 30.0, "step": 1.0, "format": "%.0f"}
    },
    "BT37 2": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Flow (mL/min)": {"type": "number", "default": 30.0, "step": 1.0, "format": "%.0f"}
    },
    "BT37 3": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Flow (mL/min)": {"type": "number", "default": 30.0, "step": 1.0, "format": "%.0f"}
    },
    "BT37 4": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Flow (mL/min)": {"type": "number", "default": 30.0, "step": 1.0, "format": "%.0f"}
    },
    "Tủ ấm LAB": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"}
    },
    "Tủ ấm phòng TT": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"}
    },
    "Tủ ấm LS1": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"}
    },
    "Tủ ấm LS2": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"}
    },
    "WorkStation CH": {
        "Nhiệt trái (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Nhiệt phải (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Nhiệt kính (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"}
    },
    "WorkStation Đ-R": {
        "Nhiệt trái (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Nhiệt phải (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "Nhiệt kính (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"}
    },
    "Điều áp 1": {
        "Áp suất (PSI)": {"type": "number", "default": 15.0, "step": 0.1, "format": "%.1f"}
    },
    "Điều áp 2": {
        "Áp suất (PSI)": {"type": "number", "default": 15.0, "step": 0.1, "format": "%.1f"}
    },
    "Điều áp 3": {
        "Áp suất (PSI)": {"type": "number", "default": 15.0, "step": 0.1, "format": "%.1f"}
    }
}

# 3. ĐỌC DỮ LIỆU LỊCH SỬ TỪ LINK GOOGLE SHEETS
try:
    df_history = pd.read_csv(URL_GOOGLE_SHEET)
    df_history = df_history.dropna(subset=["Thời gian"])
except Exception:
    df_history = pd.DataFrame(columns=["Thời gian", "Thiết bị", "Thông số", "Giá trị", "Chuyên viên", "Ghi chú"])

# Tạo cột phụ Ngày phục vụ bộ lọc
if not df_history.empty:
    df_history["Thời gian"] = df_history["Thời gian"].astype(str)
    df_history["Ngày_Phụ"] = df_history["Thời gian"].str.slice(0, 10)
else:
    df_history["Ngày_Phụ"] = pd.Series(dtype='str')

if "inspector_name" not in st.session_state:
    st.session_state.inspector_name = ""

st.title("🔬 Hệ Thống Nhập Thông Số Labo IVF (Cloud Forms)")

# --- THÔNG TIN PHIÊN LÀM VIỆC ---
st.markdown("### 👤 Thông tin phiên làm việc")
st.session_state.inspector_name = st.text_input(
    "Nhập tên Chuyên viên kiểm tra (Chỉ cần điền 1 lần khi mở app):",
    value=st.session_state.inspector_name
)

st.markdown("---")

col_left, col_right = st.columns(2)

# ----------------- BÊN TRÁI: FORM NHẬP LIỆU ĐỘNG -----------------
with col_left:
    st.subheader("📥 Form điền thông số")
    
    selected_device = st.selectbox("Chọn thiết bị kiểm tra:", list(DEVICE_CONFIGS.keys()))
    current_fields = DEVICE_CONFIGS[selected_device]
    
    with st.form("ivf_dynamic_form", clear_on_submit=False):
        st.markdown(f"✍️ *Đang ghi nhận cho:* **{selected_device}**")
        if st.session_state.inspector_name:
            st.caption(f"👤 Người thực hiện hiện tại: **{st.session_state.inspector_name}**")
        else:
            st.caption("⚠️ *Lưu ý: Bạn chưa điền tên Chuyên viên ở phía trên cùng.*")
            
        has_printed_setting_header = False
        has_printed_actual_header = False
        
        input_values = {}
        for field_name, config in current_fields.items():
            if field_name.startswith("Cài đặt:"):
                if not has_printed_setting_header:
                    st.markdown("---")
                    st.markdown("⚙️ **THÔNG SỐ CÀI ĐẶT**")
                    has_printed_setting_header = True
                clean_label = field_name.replace("Cài đặt: ", "")
            elif field_name.startswith("Thực tế:"):
                if not has_printed_actual_header:
                    st.markdown("---")
                    st.markdown("📊 **THÔNG SỐ THỰC TẾ**")
                    has_printed_actual_header = True
                clean_label = field_name.replace("Thực tế: ", "")
            else:
                clean_label = field_name

            if config["type"] == "number":
                input_values[field_name] = st.number_input(
                    label=clean_label,
                    value=config["default"],
                    step=config["step"],
                    format=config["format"],
                    key=f"num_{selected_device}_{field_name}"
                )
            elif config["type"] == "checkbox":
                input_values[field_name] = st.checkbox(
                    label=clean_label,
                    value=config["default"],
                    key=f"chk_{selected_device}_{field_name}"
                )
        
        st.markdown("---")        
        note = st.text_area("Ghi chú / Trạng thái bất thường (Nếu có):", height=70)
        
        submit_btn = st.form_submit_button("💾 XÁC NHẬN LƯU VÀO HỆ THỐNG")
        
        if submit_btn:
            if not st.session_state.inspector_name.strip():
                st.error("⚠️ Lỗi: Vui lòng kéo lên đầu trang và điền tên Chuyên viên kiểm tra trước!")
            else:
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                success_count = 0
                success_count = 0
                # Lặp gửi từng hàng thông số sang Google Form trực tuyến
                for field_name, value in input_values.items():
                    if isinstance(value, bool):
                        display_value = "Có (Đang bật)" if value else "Không"
                    else:
                        display_value = value
                    
                    form_data = {
                        ENTRY_THOI_GIAN: now_str,
                        ENTRY_THIET_BI: selected_device,
                        ENTRY_THONG_SO: field_name,
                        ENTRY_GIA_TRI: str(display_value),
                        ENTRY_CHUYEN_VIEN: st.session_state.inspector_name,
                        ENTRY_GHI_CHU: note
                    }
                    
                    try:
                        res = requests.post(FORM_URL, data=form_data)
                        if res.status_code == 200:
                            success_count += 1
                    except Exception:
                        pass
                
                if success_count > 0:
                    st.success(f"🎉 Đã lưu thành công dữ liệu cho {selected_device} vào hệ thống!")
                    st.rerun()
                else:
                    st.error("❌ Lỗi kết nối internet! Không thể đẩy dữ liệu lên Cloud.")

# ----------------- BÊN PHẢI: XEM NHẬT KÝ LỊCH SỬ TỪ GOOGLE SHEETS -----------------
with col_right:
    st.subheader("📋 Nhật ký lịch sử trực tuyến")
    
    if df_history.empty:
        st.info("Chưa có thông số nào được ghi lại trên Trang tính.")
    else:
        st.markdown("🔍 **Bộ lọc tìm kiếm nhật ký**")
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            filter_device = st.selectbox("1. Xem theo thiết bị:", ["Tất cả"] + list(DEVICE_CONFIGS.keys()))
        
        with filter_col2:
            available_days = sorted(list(df_history["Ngày_Phụ"].dropna().unique()), reverse=True)
            if not available_days:
                available_days = [str(datetime.date.today())]
            selected_day = st.selectbox("2. Chọn ngày trong tháng:", available_days)
        
        df_filtered = df_history[df_history["Ngày_Phụ"] == selected_day]
        
        if filter_device != "Tất cả":
            df_filtered = df_filtered[df_filtered["Thiết bị"] == filter_device]
            
        st.markdown(f"📅 Kết quả ngày **{selected_day}** | Thiết bị: **{filter_device}** ({len(df_filtered)} bản ghi)")
        
        if df_filtered.empty:
            st.warning("Không có dữ liệu ghi nhận nào khớp với bộ lọc đã chọn.")
        else:
            df_display = df_filtered.drop(columns=["Ngày_Phụ"])
            st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)
