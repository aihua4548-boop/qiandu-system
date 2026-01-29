import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心架构：时区与数据安全 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7)

DB_FILES = {"users": "users_data.json", "pending": "pending.json", "logs": "op_logs.json", "remarks": "remarks_data.json"}

def load_data(key):
    try:
        if os.path.exists(DB_FILES[key]):
            with open(DB_FILES[key], "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return [] if key == "logs" else {}

def save_data(key, data):
    with open(DB_FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_mission_log(user, action, target="-", score=1):
    logs = load_data("logs")
    current_time = get_local_time()
    risk = "✅ 安全"
    if logs and logs[0].get('操作员') == user:
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1.0:
            risk = "🚨 频率异常"; score = -50
    logs.insert(0, {"时间": current_time.strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "动作": action, "目标": target, "战力分": score, "状态": risk})
    save_data("logs", logs[:5000])

# --- 2. 隐私保护核心：号码脱敏 ---
def mask_phone(phone_raw, role):
    raw = re.sub(r'\D', '', str(phone_raw))
    if role == "boss": return raw 
    return f"{raw[:3]}****{raw[-4:]}" if len(raw) > 7 else "****"

# --- 3. QIANDU 巅峰 AI 决策大脑 V135 (新增产品基因分析) ---
def qiandu_ai_v135(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # 类别识别
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发", "warehouse", "grosir"])
    is_med = any(k in ctx for k in ["spa", "clinic", "pharmacy", "derma", "med"])
    is_prime = any(k in ctx for k in ["district 1", "myeongdong", "sukhumvit", "jakarta pusat"])

    # 产品基因分析逻辑
    if is_ws:
        category = "🏗️ 大宗流通/仓库"
        main_products = "高频快销品、大众面膜、基础清洁 (SNP/Jmella 基础款)"
        strategy = "对方卖的是‘量’。谈判重点：现货周转率、集装箱价格、效期稳定性。"
    elif is_med:
        category = "🏥 专业医美/药妆"
        main_products = "院线修护精华、术后面膜、再生霜 (Leaders 院线款/SNP 医研版)"
        strategy = "对方卖的是‘专业’。谈判重点：成分分析、临床背书、非红海渠道保护。"
    elif is_prime:
        category = "💎 核心地标零售"
        main_products = "高颜值套盒、潮流彩妆、网红引流品 (meloMELI 彩妆/Jmella 香氛系列)"
        strategy = "对方卖的是‘形象’。谈判重点：到店打卡率、视觉陈列架、首发独家权益。"
    else:
        category = "🏪 社区零售/网店"
        main_products = "散单爆款、日化洗护、单片面膜"
        strategy = "对方卖的是‘便利’。谈判重点：补货时效、一件起批、低门槛合作。"

    return {
        "级别": category,
        "主营产品": main_products,
        "经营逻辑": strategy,
        "话术核心": "Chào bạn, mình thấy shop chuyên dòng " + main_products.split('(')[0] + ", bên mình có nguồn tận gốc giá cực tốt..."
    }

# --- 4. 路由系统 ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if nums.startswith('7') or nums.startswith('971') or "moscow" in ctx:
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or "vietnam" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if any(nums.startswith(x) for x in ['81','66','82']) or "japan" in ctx:
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 5. 界面展示层 ---
st.set_page_config(page_title="QIANDU BI V135", layout="wide")

if "auth_ok" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🛡️ QIANDU 全球指挥终端 V135.0</h1>", unsafe_allow_html=True)
    role_tab = st.radio("通道", ["👤 员工入口", "🛰️ 指挥官入口"], horizontal=True, label_visibility="collapsed")
    if role_tab == "🛰️ 指挥官入口":
        pwd = st.text_input("创始人密钥", type="password", key="b_pwd")
        if st.button("激活权限", use_container_width=True):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"}); st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="u"), st.text_input("密码", type="password", key="p")
            if st.button("登录指挥中心", use_container_width=True):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"}); add_mission_log(u, "登录"); st.rerun()
        with t2:
            nu, np = st.text_input("新账号", key="nu"), st.text_input("新密码", type="password", key="np")
            if st.button("提交申请", use_container_width=True):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功，待审核。")
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队战力", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("菜单", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度情报矩阵 (产品基因分析版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=2)
            
            q = st.text_input("🔎 搜店名、地址、商圈词（AI 自动扫描经营品类）")
            if q: df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2); remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                intel = qiandu_ai_v135(name, addr)
                d_phone = mask_phone(phone, st.session_state.role)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        cl1, cl2 = st.columns([1, 1.3])
                        with cl1:
                            st.write(f"🌍 区域: **{country}**")
                            st.write(f"📞 电话: `{d_phone}`")
                            st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True)
                            if st.button(f"📑 记入战力-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                        with cl2:
                            st.write(f"🏢 画像: **{intel['级别']}**")
                            st.warning(f"📦 **主营:** {intel['主营产品']}")
                            st.info(f"💡 **逻辑:** {intel['经营逻辑']}")
                            with st.expander("📝 破冰建议话术"): st.code(intel['话术核心'], language="markdown")
                        
                        # 社媒探测
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True)
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True)

                        st.divider(); rem = remarks.get(name, {"text": "暂无进展", "user": "-", "time": "-"})
                        st.success(f"最新进展: {rem['text']} ({rem['user']})")
                        n_note = st.text_input("更新跟进进展", key=f"ni_{idx}")
                        if st.button("保存备注", key=f"nb_{idx}"):
                            if n_note:
                                remarks[name] = {"text": n_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队战力":
        st.title("⚙️ QIANDU 战力与审核")
        t1, t2 = st.tabs(["待审名单", "战力排行"])
        with t1:
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u} ({info['time']})")
                if c2.button("批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            ldf = pd.DataFrame(load_data("logs"))
            if not ldf.empty:
                st.bar_chart(ldf.groupby("操作员")["战力分"].sum().sort_values(ascending=False))
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"注销权限: {u}", key=f"d_{u}"): del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 审计日志")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            st.dataframe(ldf.style.applymap(lambda x: 'background-color: #ff4b4b; color: white' if "🚨" in str(x) else '', subset=['状态']), use_container_width=True)

    if st.sidebar.button("安全退出系统"): st.session_state.clear(); st.rerun()
