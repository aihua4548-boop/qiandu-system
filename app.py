import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 时区与深度审计 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7)

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

def add_mission_log(user, action, target="-", weight=1):
    logs = load_data("logs")
    current_time = get_local_time()
    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "指挥员": user,
        "指令动作": action,
        "目标对象": target,
        "情报深度": "💎 核心联络" if weight >= 10 else "📄 基础"
    })
    save_data("logs", logs[:3000])

# --- 2. 核心修复：QIANDU 全域通讯路由 V32 ---
def global_comm_router(phone_raw, name_addr):
    # 彻底清洗：只保留数字
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 优先级 1: Telegram (小飞机)
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus", "moscow", "uae"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", f"TG: +{nums}"

    # 优先级 2: 日本 (+81) 强制 Line
    if nums.startswith('81') or "japan" in ctx or "tokyo" in ctx or "osaka" in ctx:
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", f"81-{p}"

    # 优先级 3: 泰国 (+66) 强制 Line
    if nums.startswith('66') or "thailand" in ctx or "bangkok" in ctx:
        p = nums[2:] if nums.startswith('66') else nums[1:] if nums.startswith('0') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", f"66-{p}"

    # 优先级 4: 越南 (+84) 强制 Zalo
    if nums.startswith('84') or "vietnam" in ctx or "vn" in ctx:
        p = nums[2:] if nums.startswith('84') else nums[1:] if nums.startswith('0') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", f"84-{p}"

    # 优先级 5: 印尼 (+62) 强制 WhatsApp
    if nums.startswith('62') or "indonesia" in ctx or "jakarta" in ctx or nums.startswith('08'):
        p = nums[2:] if nums.startswith('62') else nums[1:] if nums.startswith('0') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", f"62-{p}"
    
    # 优先级 6: 韩国 (+82) 强制 Line (通常韩国使用 Kakao，但 Line 也是主流且接口更稳)
    if nums.startswith('82') or "korea" in ctx or "seoul" in ctx:
        p = nums[2:] if nums.startswith('82') else nums[1:] if nums.startswith('0') else nums
        return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{p}", "Line", f"82-{p}"

    # 默认：WhatsApp
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", nums

# --- 3. QIANDU AI 深度大脑 (千店千策) ---
def qiandu_ai_v32(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "批发"])
    is_spa = any(k in ctx for k in ["spa", "skin", "clinic", "pharmacy", "derma"])
    
    if is_ws:
        return "🏛️ 核心批发", "谈货柜价、谈一手货源。推 Jmella 全系列、SNP 大包装。"
    elif is_spa:
        return "🏥 专业药妆", "谈成分、谈 Leaders 医美背书。这类客户回购稳，利润高。"
    return "🏪 潮流门店", "谈颜值、谈引流、谈 meloMELI 潮流款。送陈列架支持。"

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU COMMAND V32", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V32.0")
    acc = st.radio("模式", ["员工入口", "创始人入口"], horizontal=True, key="acc32")
    if acc == "创始人入口":
        pwd = st.text_input("创始人密钥", type="password", key="bp32")
        if st.button("激活权限", key="bb32"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="ui32"), st.text_input("密码", type="password", key="pi32")
            if st.button("进入系统", key="bi32"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("登录失败")
        with t2:
            nu, np = st.text_input("新账号名", key="nu32"), st.text_input("设置密码", type="password", key="np32")
            if st.button("提交申请", key="rb32"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功，等待创始人审核。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队审核", "📜 深度日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 全方位商业情报")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 全局搜索 (AI 自动重载各国通讯软件)", key="sq32")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                country, chat_link, tool, info = global_comm_router(phone, name + addr)
                role, strategy = qiandu_ai_v32(name, addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.info(f"💡 **AI 建议:**\n{strategy}")
                        
                        st.write("🌐 **社媒探测:**")
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}")

    elif nav == "⚙️ 团队审核":
        st.title("⚙️ 员工入职审核中心")
        t1, t2 = st.tabs(["待审名单", "在职员工"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"申请人: **{u}** ({info['time']})")
                if c2.button("✅ 批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 在职: {u}")
                if c2.button("🚫 撤销", key=f"d_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度日志":
        st.title("📜 全球指挥审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 退出"):
        st.session_state.clear(); st.rerun()
