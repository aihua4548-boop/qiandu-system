import streamlit as st
import pandas as pd
import os
import json
import urllib.parse
from datetime import datetime

# --- 1. 物理数据库初始化 ---
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
st.set_page_config(page_title="QIANDU Global Command V50", layout="wide")

# --- 3. 登录与注册逻辑 ---
if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V50.0")
    t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
    
    with t1:
        u = st.text_input("账号", key="login_u")
        p = st.text_input("授权密码", type="password", key="login_p")
        if st.button("立即进入系统", use_container_width=True):
            # --- 创始人超级通行证：物理锁死 ---
            if u == "admin" and p == "666888":
                st.session_state.auth_ok = True
                st.session_state.user = "admin"
                st.session_state.role = "boss"
                st.rerun()
            
            # --- 普通员工逻辑 ---
            users = load_json(USER_DB, {})
            if u in users and users[u]["pwd"] == p:
                st.session_state.auth_ok = True
                st.session_state.user = u
                st.session_state.role = "staff"
                st.rerun()
            else:
                st.error("❌ 账号或密码错误，或账号尚未审核通过。")
                
    with t2:
        new_u = st.text_input("拟申请用户名")
        new_p = st.text_input("拟设置密码", type="password")
        if st.button("提交注册申请"):
            if new_u:
                pending = load_json(PENDING_DB, {})
                pending[new_u] = {"pwd": new_p, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
                save_json(PENDING_DB, pending)
                st.success(f"✅ 申请已提交！请通知创始人通过。")

else:
    # --- 4. 内部主系统 ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    
    # 动态功能路由
    menu = ["📊 实战情报中心", "🔍 全域搜索"]
    if st.session_state.role == "boss":
        menu += ["⚙️ 后台审核", "📜 操作日志"]
    
    nav = st.sidebar.radio("系统导航", menu)

    # 1. 情报与搜索模块
    if nav in ["📊 实战情报中心", "🔍 全域搜索"]:
        st.title("📊 QIANDU 全球情报分析矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        
        if not files:
            st.info("💡 请在 GitHub 仓库上传 Excel 数据文件（.xlsx）")
        else:
            sel_f = st.sidebar.selectbox("📂 选择数据库文件", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all')

            # 搜索框：核心优化
            search_q = st.text_input("🔎 搜索店名、电话、地址关键词 (输入后按回车)", placeholder="例如：Wholesale 或 HCM")
            
            if search_q:
                # 全字段模糊匹配
                mask = df.apply(lambda row: row.astype(str).str.contains(search_q, case=False, na=False).any(), axis=1)
                df = df[mask]
            
            st.success(f"找到 {len(df)} 条相关情报")
            
            # 卡片展示
            cols = list(df.columns)
            c_name = st.sidebar.selectbox("🏠 确认【店名】列", cols, index=0)
            c_phone = st.sidebar.selectbox("📞 确认【电话】列", cols, index=min(1, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone = str(row[c_name]), str(row[c_phone])
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        st.write(f"📞 电话: `{phone}`")
                        st.caption(f"📍 地址: {row.get('Address','-')}")
                        
                        # 越南 Zalo 自动适配逻辑
                        raw_p = "".join(filter(str.isdigit, phone))
                        z_p = "84" + raw_p[1:] if raw_p.startswith('0') else raw_p
                        st.link_button("🔵 Zalo 洽谈", f"https://zalo.me/{z_p}")

    # 2. 后台审核 (仅 Boss)
    elif nav == "⚙️ 后台审核":
        st.title("⚙️ 员工账号审批")
        pending = load_json(PENDING_DB, {})
        if not pending:
            st.info("暂无新申请")
        else:
            for u, info in list(pending.items()):
                c1, c2, c3 = st.columns([2,1,1])
                c1.write(f"**{u}** (申请日期: {info['time']})")
                if c2.button("✅ 批准", key=f"y_{u}"):
                    users = load_json(USER_DB, {})
                    users[u] = {"pwd": info["pwd"], "role": "staff", "status": "active"}
                    save_json(USER_DB, users)
                    del pending[u]
                    save_json(PENDING_DB, pending)
                    st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pending[u]
                    save_json(PENDING_DB, pending)
                    st.rerun()

    # 3. 日志 (仅 Boss)
    elif nav == "📜 操作日志":
        st.title("📜 员工行为审计")
        logs = load_json(LOG_DB, [])
        st.table(logs)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.auth_ok = False
        st.rerun()
