import streamlit as st
import pandas as pd
import datetime
import requests
import os

# 1. Cấu hình giao diện dashboard
st.set_page_config(
    page_title="DATA MONITORING",
    page_icon="🔬",
    layout="wide"
)

# =====================================================================
# CẤU HÌNH THÔNG TIN BIỂU MẪU GOOGLE FORMS CỦA BẠN TẠI ĐÂY
# =====================================================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdzPIpDVuHudnDQpNL39iODQdjZCWRGpI__Y5tI3qRw-aDpOw/formResponse"

ENTRY_THOI_GIAN = "entry.354649550"
ENTRY_THIET_BI = "entry.839283793"
ENTRY_THONG_SO = "entry.1493359847"
ENTRY_GIA_TRI = "entry.1654406867"
ENTRY_CHUYEN_VIEN = "entry.2134976502"
ENTRY_GHI_CHU = "entry.1315883282"

# Link xuất file dạng CSV của Google Sheets (Nhớ đổi đuôi thành /export?format=csv)
URL_GOOGLE_SHEET = "https://google.com"

# 2. ĐỊNH NGHĨA CẤU HÌNH CHI TIẾT CÁC THIẾT BỊ
CHAMBER_FIELDS = {
    "Cài đặt: Nhiệt trái (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt phải (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt giữa (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt trung tâm (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: Nhiệt khí (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Cài đặt: CO2 (%)": {"type": "number", "default": 6.0, "step": 0.1, "format": "%.1f"},
    
    "Thực tế: Nhiệt trái (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt phải (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt giữa (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt trung tâm (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: Nhiệt khí (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
    "Thực tế: CO2 (%)": {"type": "number", "default": 6.0, "step": 0.1, "format": "%.1f"}
}

DEVICE_CONFIGS = {
    "Tủ A1": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 6.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A2": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 6.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A3": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 6.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A4": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 6.0, "step": 0.1, "format": "%.1f"},
        "O2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Tủ A5": {
        "Nhiệt độ (°C)": {"type": "number", "default": 37.0, "step": 0.1, "format": "%.1f"},
        "CO2 (%)": {"type": "number", "default": 6.0, "step": 0.1, "format": "%.1f"},
        "O2 (%)": {"type": "number", "default": 5.0, "step": 0.1, "format": "%.1f"},
        "Sục khí": {"type": "checkbox", "default": False}
    },
    "Chamber 1": CHAMBER_FIELDS,
    "Chamber 2": CHAMBER_FIELDS,
    "BT37 1": {
        "Nhiệt độ (°C)": {"type": "number", "default": 375.0, "step": 0.1, "format": "%.1f"},
        "Flow (mL/min)": {"type": "number", "default": 30.0, "step": 1.0, "format": "%.0f"}
    },
    "BT37 2": {
        "Nhiệt độ (°C)": {"type": "number", "default": 35.0, "step": 0.1, "format": "%.1f"},
        "Flow (mL/min)": {"type": "number", "default": 30.0, "step": 1.0, "format": "%.0f"}
    },
    "BT37 3": {
        "Nhiệt độ (°C)": {"type": "number", "default": 35.0, "step": 0.1, "format": "%.1f"},
        "Flow (mL/min)": {"type": "number", "default": 30.0, "step": 1.0, "format": "%.0f"}
    },
    "BT37 4": {
        "Nhiệt độ (°C)": {"type": "number", "default": 35.0, "step": 0.1, "format": "%.1f"},
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

# 3. LOGIC KHỞI TẠO BỘ NHỚ ĐỆM TẠM THỜI (SESSION STATE) ĐỂ HIỂN THỊ TỨC THÌ
if "local_data" not in st.session_state:
    try:
        # Lần đầu mở app, tải lịch sử từ Google Sheets xuống
        cache_buster = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        url_clear_cache = f"{URL_GOOGLE_SHEET}&cache={cache_buster}"
        df_init = pd.read_csv(url_clear_cache)
        df_init = df_init.dropna(subset=["Thời gian"])
        st.session_state.local_data = df_init
    except Exception:
        # Nếu Sheets trống hoặc lỗi mạng, tạo bảng dữ liệu rỗng tạm thời
        st.session_state.local_data = pd.DataFrame(columns=["Thời gian", "Thiết bị", "Thông số", "Giá trị", "Chuyên viên", "Ghi chú"])

# Đảm bảo đồng bộ kiểu dữ liệu chuỗi để phục vụ bộ lọc thời gian
st.session_state.local_data["Thời gian"] = st.session_state.local_data["Thời gian"].astype(str)
st.session_state.local_data["Ngày_Phụ"] = st.session_state.local_data["Thời gian"].str.slice(0, 10)

if "inspector_name" not in st.session_state:
    st.session_state.inspector_name = ""

st.title("🔬 THEO DÕI THIẾT BỊ LABO")

# --- THÔNG TIN PHIÊN LÀM VIỆC ---
st.markdown("### 👤 Thông tin phiên làm việc")
st.session_state.inspector_name = st.text_input(
    "Người thực hiện:",
    value=st.session_state.inspector_name
)

st.markdown("---")

col_left, col_right = st.columns(2)

# ----------------- BÊN TRÁI: FORM NHẬP LIỆU ĐỘNG -----------------
with col_left:
    st.subheader("📥 Tổng hợp thiết bị trong LAB")
    
    selected_device = st.selectbox("Chọn thiết bị:", list(DEVICE_CONFIGS.keys()))
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
                new_entries_local = []
                success_count = 0

                for field_name, value in input_values.items():
                    if isinstance(value, bool):
                        display_value = "Có (Đang bật)" if value else "Không"
                    else:
                        display_value = value
                    
                    # 1. Tạo bản ghi đẩy trực tiếp vào bộ nhớ hiển thị của ứng dụng (Tức thì)
                    new_entries_local.append({
                        "Thời gian": now_str,
                        "Thiết bị": selected_device,
                        "Thông số": field_name,
                        "Giá trị": str(display_value),
                        "Chuyên viên": st.session_state.inspector_name,
                        "Ghi chú": note,
                        "Ngày_Phụ": now_str[0:10]
                    })
                    
                    # 2. Tạo gói tin đẩy ngầm lên mạng Google Form trực tuyến
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
                
                # Cập nhật trực tiếp danh sách mới vào bộ nhớ màn hình
                new_df_local = pd.DataFrame(new_entries_local)
                st.session_state.local_data = pd.concat([st.session_state.local_data, new_df_local], ignore_index=True)
                
                st.success(f"🎉 Đã lưu thành công dữ liệu cho {selected_device} và hiển thị tức thì!")
                st.rerun()

# ----------------- BÊN PHẢI: XEM NHẬT KÝ LỊCH SỬ CẬP NHẬT TỨC THÌ -----------------
with col_right:
    st.subheader("📋 Lịch sử theo dõi trực tuyến")
    
    if st.session_state.local_data.empty:
        st.info("Chưa có thông số nào được ghi lại trên hệ thống.")
    else:
        st.markdown("🔍 **Bộ lọc tìm kiếm nhật ký**")
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            filter_device = st.selectbox("1. Xem theo thiết bị:", ["Tất cả"] + list(DEVICE_CONFIGS.keys()))
        
        with filter_col2:
            available_days = sorted(list(st.session_state.local_data["Ngày_Phụ"].dropna().unique()), reverse=True)
            if not available_days:
                available_days = [str(datetime.date.today())]
            selected_day = st.selectbox("2. Chọn ngày trong tháng:", available_days)
        
        # Tiến hành lọc dữ liệu từ bộ nhớ cục bộ cập nhật nhanh
        df_filtered = st.session_state.local_data[st.session_state.local_data["Ngày_Phụ"] == selected_day]
        
        if filter_device != "Tất cả":
            df_filtered = df_filtered[df_filtered["Thiết bị"] == filter_device]
            
        st.markdown(f"📅 Kết quả ngày **{selected_day}** | Thiết bị: **{filter_device}** ({len(df_filtered)} bản ghi)")
        
        if df_filtered.empty:
            st.warning("Không có dữ liệu ghi nhận nào khớp với bộ lọc đã chọn.")
        else:
            df_display = df_filtered.drop(columns=["Ngày_Phụ"])
            st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)
