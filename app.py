import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 时区与深度安全审计 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7) # 越南/印尼/泰国 ICT

DB_FILES = {"users": "users_data.json", "pending": "pending.json", "logs": "op_logs.json"}

def load_data(key):
    try:
        if os.path.exists(DB_FILES[key]):
            with open(DB_FILES[key], "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return [] if key == "logs" else {}

def save_data(key, data):
    with open(DB_FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_mission_log(user, action, target="-", depth=1):
    logs = load_data("logs")
    current_time = get_local_time()
    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "动作": action,
        "目标": target,
        "情报深度": "💎 核心" if depth >= 10 else "📄 基础"
    })
    save_data("logs", logs[:3000])

# --- 2. 核心重构：QIANDU 全球通讯大脑 V23 ---
def global_comm_router(phone_raw, name_addr, file_context=""):
    # 物理清洗数字
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = (str(name_addr) + " " + str(file_context)).lower()
    
    # 【优先级 1】小飞机 (Telegram) 特殊识别
    # 只要包含特定关键词或来自特定地区（如迪拜、俄罗斯等），强制走 TG
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus", "uae", "crypto"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", f"TG: +{nums}"

    # 【优先级 2】国家专属软件逻辑
    
    # 1. 越南 (Zalo) - 84
    if "vietnam" in ctx or "vn" in ctx or "hồ chí minh" in ctx or "hà nội" in ctx or nums.startswith('84'):
        p = nums[2:] if nums.startswith('84') else nums[1:] if nums.startswith('0') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", f"84 {p}"
    
    # 2. 印尼 (WhatsApp) - 62
    elif "indonesia" in ctx or "jakarta" in ctx or "idr" in ctx or nums.startswith('62') or nums.startswith('08'):
        p = nums[2:] if nums.startswith('62') else nums[1:] if nums.startswith('0') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", f"62 {p}"
    
    # 3. 泰国 (Line) - 66
    elif "thailand" in ctx or "bangkok" in ctx or "th" in ctx or nums.startswith('66'):
        p = nums[2:] if nums.startswith('66') else nums[1:] if nums.startswith('0') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", f"+66 {p}"
    
    # 4. 韩国 (Line/Kakao) - 82 (目前系统统一跳 Line 接口)
    elif "korea" in ctx or "seoul" in ctx or "incheon" in ctx or nums.startswith('82') or nums.startswith('010'):
        p = nums[2:] if nums.startswith('82') else nums[1:] if nums.startswith('0') else nums
        return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{p}", "Line", f"+82 {p}"
    
    # 5. 日本 (Line) - 81
    elif "japan" in ctx or "tokyo" in ctx or "osaka" in ctx or nums.startswith('81'):
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", f"+81 {p}"

    # 【优先级 3】通用兜底 (WhatsApp)
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", nums

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU V23", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 指挥终端 V23.0")
    acc = st.radio("入口", ["员工", "指挥官"], horizontal=True)
    if acc == "指挥官":
        pwd = st.text_input("密钥", type="password")
        if st.button("进入"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        u, p = st.text_input("账号"), st.text_input("密码", type="password")
        if st.button("登录"):
            users = load_data("users")
            if u in users and users[u]["pwd"] == p:
                st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                st.rerun()
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    nav = st.sidebar.radio("导航", ["📊 情报矩阵", "📜 审计日志"])

    if nav == "📊 情报矩阵":
        st.title("📊 情报决策矩阵 (多国软件自动适配)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 全局检索关键词 (AI 自动重载路由)")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols, index=0), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # V23 精准路由：结合了店名、地址和文件名进行判断
                country, chat_link, tool, parsed_info = global_comm_router(phone, name + addr, sel_f)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.3])
                        with col1:
                            st.write(f"🌍 **国家:** {country}")
                            st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True)
                            st.caption(f"🆔 系统输出: `{parsed_info}`")
                            st.link_button("📍 Google 地图", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            if st.button(f"记录行动-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                        with col2:
                            # 盈利画像重载
                            if "sỉ" in name.lower() or "wholesale" in name.lower():
                                st.write("🏗️ **画像:** 大宗批发商")
                                st.success("📈 **利润:** 5-10% (高周转)")
                            elif "spa" in name.lower():
                                st.write("🏥 **画像:** 院线/药店")
                                st.success("📈 **利润:** 30-50% (高价值)")
                            else:
                                st.write("🏪 **画像:** 终端零售")
                                st.success("📈 **利润:** 20-30% (稳定)")
                            st.info("💡 **谈判建议:** 优先确认对方是否支持本币结算，推 SNP/JMSolution 爆款。")
