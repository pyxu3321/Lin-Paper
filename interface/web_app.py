import sys
import os

# 强制路径修复：将项目根目录添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
from config.settings import settings
from core.agent import LinPaperAgent

st.set_page_config(page_title="Lin-Paper AI 辅导系统", layout="wide")
st.title("Lin-Paper 智能错题管家 🤖")

# 初始化 Agent
if "agent" not in st.session_state:
    st.session_state.agent = LinPaperAgent()
    st.session_state.messages = []

# 显示对话历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 文件上传与聊天输入
uploaded_file = st.sidebar.file_uploader("上传错题图片", type=["png", "jpg", "jpeg"])
user_input = st.chat_input("输入指令（例如：识别图片、保存到错题本、分析题目）")

if user_input or uploaded_file:
    prompt_text = user_input if user_input else "请识别这张图片中的题目内容"
    
    # 处理图片上传逻辑
    if uploaded_file:
        img_path = os.path.join(settings.UPLOADS_DIR, uploaded_file.name)
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        prompt_text += f"\n[系统提示：用户已上传图片，路径为 {img_path}]"
    
    # 在界面显示用户的发言
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)
    
    # 代理大脑运行
    with st.chat_message("assistant"):
        with st.spinner("Lin-Paper 思考中..."):
            response = st.session_state.agent.run(prompt_text)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
