import streamlit as st
import pandas as pd
import os
import json
import urllib.parse
from datetime import datetime

# --- 1. 数据持久化 ---
USER_DB = "users_data.json"
PENDING_DB = "pending.json"
LOG_DB = "op_logs.json"

def load_json(file, default):
    try:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

# --- 2. 界面配置 ---
st.set_page_config(page_title="QIANDU Global Command V6.0", layout="wide")

# --- 3. 登录逻辑：物理双通道 ---
if "auth_ok" not in st.session_state:
    st.title("🏙️ QIANDU 全球指挥终端 V6.0")
    
    # 物理隔离：创始人 vs 员工
    access_type = st.radio("请选择身份通道", ["👤 员工入口", "🚀 指挥官入口"], horizontal=True)
    
    if access_type == "🚀 指挥官入口":
        st.subheader("创始人专属通道")
        boss_p = st.text_input("指挥官密钥", type="password")
        if st.button("激活指挥权限", use_container_width=True):
            if boss_p == "666888":  # 此处为您设定的唯一密码
                st.session_state.auth_ok = True
                st.session_state.user = "Founder"
                st.session_state.role = "boss"
                st.rerun()
            else:
                st.error("密钥错误")
                
    else:
        tab1, tab2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with tab1:
            u = st.text_input("员工账号")
            p = st.text_input("密码", type="password")
            if st.button("登录"):
                users = load_json(USER_DB, {})
                if u in users and users[u]["pwd"] == p:
                    st.session_state.auth_ok = True
                    st.session_state.user = u
                    st.session_state.role = "staff"
                    st.rerun()
                else:
                    st.error("验证失败，请确认密码或审核状态")
        with tab2:
            new_u = st.text_input("拟用账号")
            new_p = st.text_input("拟用密码", type="password")
            if st.button("提交申请"):
                pending = load_json(PENDING_DB, {})
                pending[new_u] = {"pwd": new_p, "time": datetime.now().strftime("%Y-%m-%d")}
                save_json(PENDING_DB, pending)
                st.success("申请成功！请联系指挥官审核")

else:
    # --- 4. 内部主系统 ---
    st.sidebar.title(f"指挥官: {st.session_state.user}" if st.session_state.role=="boss" else f"员工: {st.session_state.user}")
    
    menu = ["📊 实战情报中心", "🔍 全域搜索"]
    if st.session_state.role == "boss":
        menu += ["⚙️ 后台审核", "📜 操作日志"]
    
    nav = st.sidebar.radio("系统导航", menu)

    # 1. 数据展示与搜索逻辑
    if nav in ["📊 实战情报中心", "🔍 全域搜索"]:
        st.title("📊 QIANDU 情报中心")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        
        if not files:
            st.info("💡 请在 GitHub 上传商户 Excel")
        else:
            sel_f = st.sidebar.selectbox("📂 数据库选择", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all')

            # 搜索增强：针对性匹配
            q = st.text_input("🔎 搜索（输入店名、电话或地址）")
            if q:
                # 解决“不显示文字”的关键：将所有内容转为字符串再搜索
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                # 记录日志
                logs = load_json(LOG_DB, [])
                logs.insert(0, {"时间": datetime.now().strftime("%H:%M:%S"), "用户": st.session_state.user, "搜索": q})
                save_json(LOG_DB, logs[:200])

            st.write(f"共发现 {len(df)} 条记录")
            
            # 卡片排版
            cols = list(df.columns)
            c_n = st.sidebar.selectbox("🏠 店名列", cols, index=0)
            c_p = st.sidebar.selectbox("📞 电话列", cols, index=min(1, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone = str(row[c_n]), str(row[c_p])
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        st.write(f"📞 `{phone}`")
                        raw_p = "".join(filter(str.isdigit, phone))
                        z_p = "84" + raw_p[1:] if raw_p.startswith('0') else raw_p
                        st.link_button("🔵 Zalo 洽谈", f"https://zalo.me/{z_p}")

    # 2. 只有指挥官能看的：后台审核
    elif nav == "⚙️ 后台审核":
        st.title("⚙️ 员工审批")
        pending = load_json(PENDING_DB, {})
        for u, info in list(pending.items()):
            col1, col2 = st.columns([3, 1])
            col1.write(f"申请账号: {u}")
            if col2.button("✅ 批准", key=u):
                users = load_json(USER_DB, {})
                users[u] = {"pwd": info["pwd"]}
                save_json(USER_DB, users)
                del pending[u]
                save_json(PENDING_DB, pending)
                st.rerun()

    # 3. 操作日志
    elif nav == "📜 操作日志":
        st.title("📜 员工行为监控")
        st.table(load_json(LOG_DB, []))

    if st.sidebar.button("🚪 退出"):
        st.session_state.auth_ok = False
        st.rerun()
