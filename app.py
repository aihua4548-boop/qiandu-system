import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 时区与深度安全审计架构 ---
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
        "情报深度": "💎 深度联络" if weight >= 10 else "📄 基础查阅"
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 深度战术决策大脑 V31 ---
def qiandu_strategic_brain(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # A. 身份指纹提取
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "grosir", "distributor", "批发", "kho"])
    is_med = any(k in ctx for k in ["pharmacy", "nhà thuốc", "clinic", "spa", "skin", "derma", "med"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat", "aeon", "lotte"])

    # B. 深度战术分析
    if is_ws:
        return {
            "画像": "🏛️ 区域一级批发/档口",
            "生存痛点": "看重库存周转与价格博弈，对品牌忠诚度低。",
            "实战战术": "【价格截杀】直接亮出千渡韩国一手货源证件。推 Jmella 全系列、SNP 基础款。谈‘柜货价格’和‘现货稳定性’。",
            "利润点": "5% - 12% (靠量和返点生存)"
        }
    elif is_med:
        return {
            "画像": "🏥 专业医美/药妆渠道",
            "生存痛点": "看重产品成分、出口资质及售后，客户信任成本高。",
            "实战战术": "【专业渗透】发送 Leaders/SNP 修复系列临床数据。强调‘非红海渠道’。谈‘专业背书’，不纠结价格。",
            "利润点": "35% - 50% (靠专业溢价生存)"
        }
    elif is_prime:
        return {
            "画像": "💎 核心商圈零售/旗舰店",
            "生存痛点": "租金极高，急需高颜值、快引流、高转化的新品。",
            "实战战术": "【形象引流】推 meloMELI 潮流系列。提供品牌陈列展示架支持。谈‘到店转化率’和‘网红打卡效应’。",
            "利润点": "25% - 40% (靠品牌形象生存)"
        }
    else:
        return {
            "画像": "🏪 常规社区美妆/网店",
            "生存痛点": "资金压力大，不愿压货，追求爆款补货速度。",
            "实战战术": "【灵活占位】推单片面膜爆款。谈‘一件起批’或‘满小额送样’。强调补货时效。",
            "利润点": "20% - 35% (靠单品周转生存)"
        }

# --- 3. 全球精准通讯协议 ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if "th" in ctx or "thailand" in ctx or nums.startswith('66'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('66') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line"
    if "vn" in ctx or "vietnam" in ctx or nums.startswith('84') or (len(nums) == 10 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if "id" in ctx or "indonesia" in ctx or nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 4. 界面展示 ---
st.set_page_config(page_title="QIANDU COMMAND V31", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V31.0")
    acc = st.radio("入口", ["员工登录", "创始人进入"], horizontal=True, key="acc31")
    if acc == "创始人进入":
        pwd = st.text_input("创始人密钥", type="password", key="bp31")
        if st.button("激活权限", key="bb31"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui31"), st.text_input("密码", type="password", key="pi31")
            if st.button("进入系统", key="bi31"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
        with t2:
            nu, np = st.text_input("新账号名", key="nu31"), st.text_input("设置密码", type="password", key="np31")
            if st.button("提交入职申请", key="rb31"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请提交成功！请联系指挥官批准入职。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报决策矩阵", "⚙️ 团队管理与审核", "📜 深度日志审计"] if st.session_state.role == "boss" else ["📊 情报决策矩阵"]
    nav = st.sidebar.radio("指挥系统导航", menu)

    if nav == "📊 情报决策矩阵":
        st.title("📊 QIANDU 深度商业情报矩阵 (V31)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、商圈关键词（AI 实时分析策略）", key="sq31")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                intel = qiandu_strategic_brain(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图实景分析", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {intel['画像']}")
                            st.write(f"💵 **预期:** {intel['利润点']}")
                            st.info(f"💡 **AI 指战策:**\n{intel['实战战术']}")
                        
                        st.write("🌐 **社媒影响力探测:**")
                        search_q = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={search_q}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={search_q}")

    elif nav == "⚙️ 团队管理与审核":
        st.title("⚙️ 员工准入与权限控制")
        t1, t2 = st.tabs(["🆕 待审申请", "👥 在职名单"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"申请人: **{u}** ({info['time']})")
                if c2.button("✅ 批准入职", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 在职: {u}")
                if c2.button("🚫 撤销权限", key=f"d_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度日志审计":
        st.title("📜 全球指挥审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
