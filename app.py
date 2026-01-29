import streamlit as st
import pandas as pd
import os
import json
import uuid
import urllib.parse
from datetime import datetime

# --- 1. 物理数据库初始化 (防止数据丢失) ---
USER_DB = "users_data.json"
LOG_DB = "op_logs.json"

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)

# 初始化数据
if 'users' not in st.session_state:
    st.session_state.users = load_json(USER_DB, {"admin": {"pwd": "666888", "role": "boss", "status": "active"}})
if 'pending_users' not in st.session_state:
    st.session_state.pending_users = load_json("pending.json", {})

def add_log(user, action, detail):
    logs = load_json(LOG_DB, [])
    logs.insert(0, {"时间": datetime.now().strftime("%m-%d %H:%M"), "操作员": user, "动作": action, "详情": detail})
    save_json(LOG_DB, logs[:500]) # 保留最近500条

# --- 2. AI 深度画像系统 (针对千渡业务优化) ---
def get_ai_intel(name, addr):
    ctx = (str(name) + str(addr)).lower()
    if any(k in ctx for k in ["wholesale", "tổng kho", "sỉ", "卸"]):
        return "🚀 一级批发商", "⭐⭐⭐⭐⭐", "建议：谈货柜级 Jmella/SNP"
    return "🏪 终端门店", "⭐⭐⭐", "建议：推 meloMELI 爆款单品"

# --- 3. 界面设计 ---
st.set_page_config(page_title="QIANDU Global Command V50", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V50.0")
    t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
    with t1:
        u = st.text_input("账号")
        p = st.text_input("授权密码", type="password")
        if st.button("立即进入"):
            users = load_json(USER_DB, {"admin": {"pwd": "666888"}})
            if u in users and users[u]["pwd"] == p:
                if users[u].get("status") == "active":
                    st.session_state.auth_ok, st.session_state.user = True, u
                    st.session_state.role = users[u].get("role", "staff")
                    add_log(u, "登录", "进入指挥系统")
                    st.rerun()
                else: st.error("❌ 账号审核中，请联系创始人")
            else: st.error("❌ 密码错误")
    with t2:
        new_u = st.text_input("申请用户名")
        new_p = st.text_input("设置密码", type="password")
        if st.button("提交申请"):
            pending = load_json("pending.json", {})
            pending[new_u] = {"pwd": new_p, "time": datetime.now().strftime("%Y-%m-%d")}
            save_json("pending.json", pending)
            st.success("✅ 申请成功！请联系创始人审核。")

else:
    # --- 核心操作区 ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 实战情报", "🔍 深度搜索"]
    if st.session_state.role == "boss": menu += ["⚙️ 后台审核", "📜 操作日志"]
    nav = st.sidebar.radio("导航", menu)

    # 1. 情报中心 (含搜索)
    if nav in ["📊 实战情报", "🔍 深度搜索"]:
        st.title("📊 全球情报分析矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if not files:
            st.warning("⚠️ 请在 GitHub 仓库上传商户 Excel 文件")
        else:
            sel_f = st.sidebar.selectbox("📂 选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all')
            
            # 强化搜索功能
            q = st.text_input("🔍 输入店名、地址或电话关键词进行实时检索", help="支持模糊搜索")
            if q:
                df = df[df.apply(lambda r: q.lower() in str(r.values).lower(), axis=1)]
                add_log(st.session_state.user, "搜索", f"关键词: {q}")

            st.caption(f"已检索到 {len(df)} 条符合条件的情报")
            
            # 字段对齐
            cols = list(df.columns)
            c_n = st.sidebar.selectbox("🏠 店名列", cols, index=0)
            c_p = st.sidebar.selectbox("📞 电话列", cols, index=min(1, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone = str(row[c_n]), str(row[c_p])
                level, star, tip = get_ai_intel(name, row.get('Address',''))
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col_a, col_b = st.columns([1, 1])
                        with col_a:
                            st.write(f"📞 电话: `{phone}`")
                            st.caption(f"📍 地址: {row.get('Address','-')}")
                            # 越南 Zalo 自动适配
                            raw_p = "".join(filter(str.isdigit, phone))
                            z_p = "84" + raw_p[1:] if raw_p.startswith('0') else raw_p
                            st.link_button("🔵 发起 Zalo 洽谈", f"https://zalo.me/{z_p}", type="primary")
                        with col_b:
                            st.success(f"能级: {level}\n\n评分: {star}")
                            st.info(f"💡 AI 策略:\n{tip}")

    # 2. 后台审核
    elif nav == "⚙️ 后台审核":
        st.title("⚙️ 审批中心")
        pending = load_json("pending.json", {})
        if not pending: st.info("目前没有待处理的申请")
        for u, info in list(pending.items()):
            c1, c2, c3 = st.columns([2,1,1])
            c1.write(f"申请人: **{u}** (提交日期: {info['time']})")
            if c2.button("✅ 准许加入", key=f"y_{u}"):
                users = load_json(USER_DB, {})
                users[u] = {"pwd": info["pwd"], "role": "staff", "status": "active"}
                save_json(USER_DB, users)
                del pending[u]
                save_json("pending.json", pending)
                st.rerun()
            if c3.button("❌ 拒绝", key=f"n_{u}"):
                del pending[u]
                save_json("pending.json", pending)
                st.rerun()

    # 3. 操作日志
    elif nav == "📜 操作日志":
        st.title("📜 全球员工操作实时追踪")
        st.table(load_json(LOG_DB, []))

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.auth_ok = False
        st.rerun()
