import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit hiển thị rộng toàn màn hình
st.set_page_config(layout="wide", page_title="Quản lý thiết bị phòng LAB")

# Đọc nội dung file HTML
try:
    with open(r"C:\Users\Admin\Desktop\index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Hiển thị giao diện HTML (tự động bật thanh cuộn nếu nội dung dài)
    components.html(html_content, height=900, scrolling=True)

except FileNotFoundError:
    st.error("Không tìm thấy file 'index.html'. Vui lòng kiểm tra lại cấu trúc thư mục!")
