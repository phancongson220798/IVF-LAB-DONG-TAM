import streamlit as st
import streamlit.components.v1 as components
import os
import glob
st.set_page_config(layout="wide")
current_dir = os.path.dirname(os.path.abspath(__file__))
found_files = glob.glob(os.path.join(current_dir, "*quan-ly-bao-tri*"))
if not found_files:
    st.error("Khong tim thay file HTML")
    st.write(os.listdir(current_dir))
else:
    with open(found_files[0], "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=900, scrolling=True)
