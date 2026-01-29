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

# --- 2. QIANDU 深度商业智能引擎 V11.0 ---
def deep_business_analysis(name, addr):
    ctx = (str(name) + str(addr)).lower()
    
    # A. 渠道深度鉴定
    if any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "grosir", "supply", "trade"]):
        biz_type = "🏛️ 大宗贸易型 (High Volume)"
        power = "💰 极强 (货柜级采购潜力)"
        focus = "Jmella / SNP 基础款"
    elif any(k in ctx for k in ["mall", "plaza", "center", "aeon", "lotte", "myeongdong"]):
        biz_type = "💎 品牌零售型 (Brand Image)"
        power = "💵 中高 (高扣率/高形象要求)"
        focus = "meloMELI / 联名限定款"
    elif any(k in ctx for k in ["spa", "skin", "clinic", "derma", "nhà thuốc", "pharmacy"]):
        biz_type = "🏥 专业渠道 (Professional)"
        power = "💳 中等 (高忠诚度/高回购)"
        focus = "Leaders / 医美级护肤"
    else:
        biz_type = "🏪 常规美妆店 (General Retail)"
        power = "🪙 较弱 (散单为主)"
        focus = "爆款引流品"

    # B. 品类渗透分析
    tags = []
    if any(k in ctx for k in ["lip", "color", "make", "son"]): tags.append("💄 彩妆")
    if any(k in ctx for k in ["mask", "skin", "da", "mặt"]): tags.append("🧴 面膜/护肤")
    if any(k in ctx for k in ["hair", "body", "tắm"]): tags.append("🛁 洗护")
    if not tags: tags = ["📦 综合美妆"]

    # C. 谈判难度与策略
    risk = "🔴 高 (需创始人亲自谈)" if "wholesale" in ctx else "🟢 中 (员工可跟进)"
    strategy = f"建议优先谈 {focus}，利用千渡韩国一手货源优势，强调‘零中间商’。"

    return biz_type, power, tags, strategy, risk

def get_contact_route(phone_raw):
    nums = re.sub(r'\D', '', str(phone_raw))
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    elif nums.startswith('62') or (len(nums) >= 10 and nums.startswith('08')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/{p}", "WhatsApp"
    elif nums.startswith('82') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('82') else nums
        return "Korea 🇰🇷", f"https://line.me/R/ti/p/~82{p}", "Line/Contact"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V11", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🏙️ QIANDU 全球指挥终端 V11.0")
    access = st.radio("身份确认", ["员工入口", "指挥官入口"], horizontal=True)
    if access == "指挥官入口":
        pwd = st.text_input("指挥官密钥", type="password")
        if st.button("激活权限"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号"), st.text_input("密码", type="password")
            if st.button("登录"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_log(u, "登录", "进入系统")
                    st.rerun()
        with t2:
            nu, np = st.text_input("新账号"), st.text_input("密码", type="password")
            if st.button("提交申请"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": datetime.now().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请已提交")
else:
    # --- 4. 内部核心模块 ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 智能情报矩阵", "⚙️ 员工权限", "📜 日志审计"] if st.session_state.role == "boss" else ["📊 智能情报矩阵"]
    nav = st.sidebar.radio("指挥系统", menu)

    if nav == "📊 智能情报矩阵":
        st.title("📊 QIANDU 商业智能情报 (Deep Analysis)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')

            q = st.text_input("🔎 深度检索（店名、区号、品类、身份）")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_log(st.session_state.user, "搜索", f"关键词: {q}")

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # 深度分析
                biz_type, power, tags, strategy, risk = deep_business_analysis(name, addr)
                country, chat_link, tool = get_contact_route(phone)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 国家: **{country}**")
                            st.link_button(f"💬 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True)
                            st.link_button("📍 Google 地图实景", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            st.caption(f"📞 原始号码: {phone}")
                        with col2:
                            st.write(f"🏢 **渠道:** {biz_type}")
                            st.write(f"💰 **采购力:** {power}")
                            st.write(f"📦 **核心品类:** {', '.join(tags)}")
                            st.write(f"⚖️ **跟进风险:** {risk}")
                            st.info(f"💡 **战略建议:**\n{strategy}")
                        
                        st.write("🌐 **社媒影响力核查:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("Facebook", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Instagram", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TikTok", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 员工权限":
        st.title("⚙️ QIANDU HR 管理中心")
        t1, t2 = st.tabs(["待审核申请", "在职名单"])
        # ... 此处保留原有的审核与注销逻辑 ...
        pnd = load_data("pending")
        for u, info in list(pnd.items()):
            c1, c2 = st.columns([3, 1])
            c1.write(f"申请: {u}")
            if c2.button("批准", key=f"y_{u}"):
                users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        users = load_data("users")
        for u in list(users.keys()):
            c1, c2 = st.columns([3, 1])
            c1.write(f"👤 {u}")
            if c2.button("强制注销", key=f"n_{u}"):
                del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 日志审计":
        st.title("📜 全球操作日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
