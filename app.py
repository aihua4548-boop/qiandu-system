import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 数据持久化与东七区时间校准 ---
def get_local_time():
    # 锁定胡志明/雅加达时间 (UTC+7)
    return datetime.utcnow() + timedelta(hours=7)

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

def add_mission_log(user, action, target="-", depth=1):
    logs = load_data("logs")
    logs.insert(0, {
        "时间": get_local_time().strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "动作": action,
        "目标": target,
        "情报价值": "⭐⭐⭐ 高" if depth > 5 else "⭐ 基础"
    })
    save_data("logs", logs[:2000])

# --- 2. 全球通讯路由 (精准适配日本、泰国、越南、印尼、韩国、小飞机) ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 强制优先：小飞机 (Telegram) 识别
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai", "global"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    
    # 泰国 (66) & 日本 (81) & 韩国 (82) -> Line
    if nums.startswith('66'): return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{nums[2:]}", "Line"
    if nums.startswith('81'): return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    if nums.startswith('82'): return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{nums[2:]}", "Line"
    
    # 越南 (84) -> Zalo
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    
    # 印尼 (62) -> WhatsApp
    if nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 3. QIANDU AI 战术大脑 5.0 (千店千策) ---
def qiandu_ai_strategic(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # 核心深度识别逻辑
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "warehouse", "批发", "贸易", "grosir"])
    is_expert = any(k in ctx for k in ["pharmacy", "nhà thuốc", "clinic", "spa", "skin", "derma", "med"])
    is_mall = any(k in ctx for k in ["mall", "plaza", "center", "aeon", "lotte", "myeongdong", "sukhumvit"])

    if is_ws:
        return {
            "标签": "🏛️ 大宗档口/一级批发",
            "建议": "【价格战策略】: 话术锁定‘千渡韩国一手货源’、‘价格对标韩网’。直接推 Jmella 全系列和 SNP 大包装。",
            "利润点": "看重库存周转率与价格稳定性。"
        }
    elif is_expert:
        return {
            "标签": "🏥 专业药妆/医美渠道",
            "建议": "【专业战策略】: 话术锁定‘医美级护肤’、‘成分安全’。推 Leaders/SNP 针剂面膜。这类客户回购率高。",
            "利润点": "看重产品资质、背书与单品高毛利。"
        }
    elif is_mall:
        return {
            "标签": "💎 高端零售/商场专柜",
            "建议": "【颜值战策略】: 话术锁定‘meloMELI 潮流形象’、‘联名爆款’。提供小样与柜台支持。地段好，适合推高毛利新品。",
            "利润点": "看重品牌形象与引流能力。"
        }
    else:
        return {
            "标签": "🏪 社区常规美妆店",
            "建议": "【散单战策略】: 话术锁定‘代发货’、‘一件起批’。强调补货时效。这类客户适合推当月最火的散单。",
            "利润点": "看重资金回流速度与补货便利度。"
        }

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V17", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V17.0")
    acc = st.radio("身份通道", ["员工入口", "指挥官入口"], horizontal=True, key="acc_v17")
    if acc == "指挥官入口":
        pwd = st.text_input("指挥官密钥", type="password", key="bp17")
        if st.button("激活权限", key="bb17"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="ui17"), st.text_input("密码", type="password", key="pi17")
            if st.button("进入系统", key="bi17"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "系统登录")
                    st.rerun()
        with t2:
            nu, np = st.text_input("申请名", key="nu17"), st.text_input("设置密码", type="password", key="np17")
            if st.button("提交申请", key="rb17"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请成功")
else:
    st.sidebar.title(f"👤 状态: {st.session_state.user}")
    menu = ["📊 深度情报矩阵", "⚙️ 权限管理", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 深度情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 深度情报矩阵":
        st.title("📊 QIANDU 商业智能情报 (千店千策版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、地址、商圈或关键词", key="sq17")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索情报", q)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                intel = qiandu_ai_strategic(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"发起联络 ({tool})", name, 10)
                            st.link_button("📍 地图实景", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **身份:** {intel['标签']}")
                            st.write(f"💵 **利润驱动:** {intel['利润点']}")
                            st.info(f"💡 **AI 建议策略:**\n{intel['建议']}")
                        
                        st.write("🌐 **社媒快速核查:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 权限管理":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["待审名单", "在职管理"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u}")
                if c2.button("批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u}")
                if c2.button("注销", key=f"n_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 全球行动日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 退出"):
        st.session_state.clear(); st.rerun()
