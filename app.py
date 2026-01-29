import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime

# --- 1. 数据持久化 ---
DB_FILES = {"users": "users_data.json", "pending": "pending.json", "logs": "op_logs.json"}

def load_data(key):
    try:
        if os.path.exists(DB_FILES[key]):
            with open(DB_FILES[key], "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return {} if key != "logs" else []

def save_data(key, data):
    with open(DB_FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_log(user, action, detail):
    logs = load_data("logs")
    logs.insert(0, {"时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "动作": action, "详情": detail})
    save_data("logs", logs[:1000])

# --- 2. QIANDU 全球通讯路由引擎 V13 (含小飞机) ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # A. 俄罗斯/乌克兰/迪拜等 Telegram 核心区
    if any(k in ctx for k in ["russia", "uae", "dubai", "moscow", "tg", "telegram"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    
    # B. 越南 (84) -> Zalo
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('09')) or (len(nums) >= 9 and nums.startswith('03')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    
    # C. 泰国 (66) -> Line
    elif nums.startswith('66') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('66') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line"

    # D. 日本 (81) -> Line
    elif nums.startswith('81') or (len(nums) >= 10 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('81') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line"
    
    # E. 印尼 (62) -> WhatsApp
    elif nums.startswith('62') or (len(nums) >= 10 and nums.startswith('08')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"

    # F. 韩国 (82) -> Line
    elif nums.startswith('82') or (len(nums) >= 9 and nums.startswith('010')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('82') else nums
        return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{p}", "Line"

    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 3. 深度 AI 逻辑 ---
def deep_ai_analysis(name, addr):
    ctx = (str(name) + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "grosir", "supply", "批发", "贸易"])
    cat = "💄 综合美妆"
    if any(k in ctx for k in ["skin", "spa", "da", "clinic"]): cat = "🧴 护肤医美"
    elif any(k in ctx for k in ["baby", "mom", "mẹ", "bé"]): cat = "🍼 母婴用品"
    elif any(k in ctx for k in ["pharmacy", "nhà thuốc", "drug"]): cat = "💊 药妆渠道"
    return "🚀 大宗批发" if is_ws else "🏪 零售门店", cat

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU Global V13", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🏙️ QIANDU 全球指挥终端 V13.0")
    access = st.radio("身份确认", ["员工入口", "指挥官入口"], horizontal=True, key="access_type")
    
    if access == "指挥官入口":
        pwd = st.text_input("指挥官密钥", type="password", key="boss_pwd")
        if st.button("激活权限", key="boss_btn"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        tab1, tab2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with tab1:
            u, p = st.text_input("账号", key="l_u"), st.text_input("密码", type="password", key="l_p")
            if st.button("登录", key="l_b"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_log(u, "登录", "进入系统"); st.rerun()
        with tab2:
            nu, np = st.text_input("新账号", key="r_u"), st.text_input("新密码", type="password", key="r_p")
            if st.button("提交申请", key="r_b"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": datetime.now().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请已提交")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 智能情报矩阵", "⚙️ 员工管理", "📜 操作日志"] if st.session_state.role == "boss" else ["📊 智能情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 智能情报矩阵":
        st.title("📊 QIANDU 全球情报 (V13 - 多端通讯版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、品类、地址或电报关键词", key="sq")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_log(st.session_state.user, "搜索", f"关键词: {q}")

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                ident, cat = deep_ai_analysis(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            st.write(f"🌍 国家: **{country}**")
                            st.link_button(f"💬 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True)
                            # 备选 Telegram 通道
                            clean_nums = re.sub(r'\D', '', phone)
                            st.link_button(f"✈️ Telegram 备选", f"https://t.me/+{clean_nums}", use_container_width=True)
                        with c2:
                            st.markdown(f"**身份:** {ident}")
                            st.markdown(f"**品类:** {cat}")
                            st.write("🌐 **社媒搜店:**")
                            sc1, sc2, sc3 = st.columns(3)
                            sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                            sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                            sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")
                        st.caption(f"📍 地址: {addr}")

    elif nav == "⚙️ 员工管理":
        st.title("⚙️ 团队控制中心")
        t1, t2 = st.tabs(["审核申请", "在职员工"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"申请: {u}")
                if col2.button("批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {u}")
                if col2.button("注销", key=f"n_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 操作日志":
        st.title("📜 实时日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 退出"):
        st.session_state.clear(); st.rerun()
