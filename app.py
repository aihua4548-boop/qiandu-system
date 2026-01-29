import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 精准时间与审计架构 ---
def get_local_time():
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
        "时间": get_local_time().strftime("%Y-%m-%d %H:%M"),
        "指挥员": user,
        "动作": action,
        "目标": target,
        "价值": "💎" * min(depth, 5)
    })
    save_data("logs", logs[:2000])

# --- 2. 核心：QIANDU AI 动态指纹识别引擎 V18.0 ---
def qiandu_deep_ai_v18(name, addr):
    full_ctx = (str(name) + " " + str(addr)).lower()
    
    # A. 消费力打分 (Location Value)
    prime_spots = ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat", "ginza", "lotte", "aeon"]
    is_prime = any(p in full_ctx for p in prime_spots)
    
    # B. 业务指纹分类
    if any(k in full_ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "warehouse", "grosir", "supply"]):
        role = "🏗️ 大宗流通商"
        pain_point = "价格敏感、库存周转、SKU稳定性"
        strategy = "【Jmella/SNP 货柜级报价】不要谈品牌故事，直接展示韩国出货单据，谈量大后的返点政策。"
        trap = "注意对方是否有多家供应商在比价。"
    elif any(k in full_ctx for k in ["pharmacy", "nhà thuốc", "clinic", "spa", "skin", "derma", "med"]):
        role = "🏥 专业医美/药妆渠道"
        pain_point = "产品成分、出口资质、客户回头率"
        strategy = "【Leaders/SNP 专家策略】提供产品成分表（COA）和韩方临床数据。强调无添加和安全性。"
        trap = "这类客户开发周期长，但一旦合作非常稳固。"
    elif is_prime:
        role = "💎 核心商圈旗舰店"
        pain_point = "地段租金压力、引流、视觉形象"
        strategy = "【meloMELI 潮流形象战】利用高颜值产品协助引流。提供联名展示架支持。谈‘到店转换率’。"
        trap = "对包装档次要求极高，散货没机会。"
    else:
        role = "🏪 社区灵活零售"
        pain_point = "起批门槛低、补货快、代发货"
        strategy = "【小快灵策略】推当月爆款面膜或散单。强调‘一件代发’或‘次日达’，无需压货。"
        trap = "由于规模小，需防范收款风险。"

    return role, pain_point, strategy, trap

# --- 3. 通讯协议 ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('66'): return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{nums[2:]}", "Line"
    if nums.startswith('81'): return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V18", layout="wide", page_icon="💄")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V18.0")
    acc = st.radio("通道", ["员工入口", "指挥官入口"], horizontal=True, key="acc18")
    if acc == "指挥官入口":
        pwd = st.text_input("密钥", type="password", key="bp18")
        if st.button("激活权限", key="bb18"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui18"), st.text_input("密码", type="password", key="pi18")
            if st.button("进入系统", key="bi18"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录")
                    st.rerun()
        with t2:
            nu, np = st.text_input("拟申请账号", key="nu18"), st.text_input("拟申请密码", type="password", key="np18")
            if st.button("提交申请", key="rb18"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请成功")
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 实战情报矩阵", "⚙️ 团队权限控制", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 实战情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 实战情报矩阵":
        st.title("📊 QIANDU 深度商业情报 (一店一策版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、地址、商圈或关键词", key="sq18")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索情报", q)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 核心分析
                role, pain, strat, trap = qiandu_deep_ai_v18(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.3])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系 ({tool})", name, 5)
                            st.link_button("📍 地图实景调研", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **角色画像:** {role}")
                            st.write(f"🚩 **核心痛点:** {pain}")
                            st.info(f"💡 **AI 建议策略:**\n{strat}")
                            st.warning(f"⚠️ **避坑指南:** {trap}")
                        
                        st.write("🌐 **社媒影响力核查:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队权限控制":
        st.title("⚙️ 团队控制中心")
        t1, t2 = st.tabs(["待审名单", "在职员工"])
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
                if c2.button("注销权限", key=f"n_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度审计日志":
        st.title("📜 商业行动日志记录")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
