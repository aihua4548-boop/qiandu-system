import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 核心：精准时间与数据持久化 ---
def get_local_time():
    # 强制修正为东七区时间 (胡志明/雅加达)
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

def add_mission_log(user, action, target="-", depth=0):
    logs = load_data("logs")
    logs.insert(0, {
        "时间": get_local_time().strftime("%Y-%m-%d %H:%M:%S"),
        "指挥员": user,
        "指令动作": action,
        "目标对象": target,
        "情报深度": "💎 深度" if depth > 5 else "📄 基础"
    })
    save_data("logs", logs[:2000])

# --- 2. QIANDU AI 深度决策引擎 V16.0 ---
def qiandu_strategic_intel(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # A. 核心资产鉴定
    is_big_fish = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "grosir", "distributor", "warehouse"])
    is_high_end = any(k in ctx for k in ["mall", "plaza", "district 1", "myeongdong", "sukhumvit", "aeon"])
    is_med_expert = any(k in ctx for k in ["pharmacy", "nhà thuốc", "clinic", "spa", "skin", "derma"])

    # B. 差异化话术与盈利点 (拒绝雷同)
    if is_big_fish:
        intel = {
            "身份": "🏛️ 区域一级批发/档口",
            "生存状态": "靠‘走量’生存，对价格敏感度极高，追求货源稳定。",
            "实战战术": "【价格截杀】: 直接报柜货底价，强调千渡在韩国的通关能力。不用谈品牌故事，只谈‘利润差’和‘现货量’。",
            "推荐": "Jmella 大桶装 / SNP 基础款 / 韩国本土免税大包"
        }
    elif is_med_expert:
        intel = {
            "身份": "🏥 医美/专业渠道",
            "生存状态": "靠‘信任’生存，客户忠诚度高，毛利空间大。",
            "实战战术": "【专业渗透】: 发送 SNP/Leaders 的成分报告和医美诊所背书。谈‘皮肤修复逻辑’，而非价格。",
            "推荐": "Leaders 针剂面膜 / SNP 积雪草系列 / 医美级精华"
        }
    elif is_high_end:
        intel = {
            "身份": "💎 高端零售旗舰",
            "生存状态": "靠‘形象’生存，地段租金极高，急需潮流新品引流。",
            "实战战术": "【潮流引领】: 推 meloMELI 联名款。提供高颜值陈列架支持，谈‘独家性’和‘到店流量’。",
            "推荐": "meloMELI 潮流彩妆 / 联名限定周边"
        }
    else:
        intel = {
            "身份": "🏪 社区灵活终端",
            "生存状态": "靠‘便利’生存，资金回笼快，单次采购量小。",
            "实战战术": "【快速周转】: 谈‘一件代发’或‘满小额起批’。强调补货速度，支持员工直接送货上门。",
            "推荐": "单片面膜 / 爆款洗面奶 / 护手霜"
        }
    return intel

# --- 3. 多国通讯协议与地图 ---
def get_global_contact(phone, name_addr):
    nums = re.sub(r'\D', '', str(phone))
    ctx = str(name_addr).lower()
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    
    if nums.startswith('66'): return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{nums[2:]}", "Line"
    if nums.startswith('81'): return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    if nums.startswith('82'): return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{nums[2:]}", "Line"
    if nums.startswith('84') or (len(nums) >= 9 and (nums.startswith('09') or nums.startswith('03'))):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU COMMAND V16", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V16.0")
    acc = st.radio("身份通道", ["员工入口", "指挥官入口"], horizontal=True, key="acc_v16")
    if acc == "指挥官入口":
        pwd = st.text_input("指挥官密钥", type="password", key="boss_v16")
        if st.button("激活权限", key="btn_boss"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="u16"), st.text_input("密码", type="password", key="p16")
            if st.button("进入系统", key="b16"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "系统登录")
                    st.rerun()
        with t2:
            nu, np = st.text_input("申请账号", key="nu16"), st.text_input("设置密码", type="password", key="np16")
            if st.button("提交申请", key="nr16"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请已提交")

else:
    st.sidebar.title(f"👤 指挥官: {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队管理", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 情报决策矩阵 (V16 - 深度实战)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、地址、商圈或身份关键词", key="sq16")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索情报", q)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                intel = qiandu_strategic_intel(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        c1, c2 = st.columns([1, 1.2])
                        with c1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系商户 ({tool})", name, 10)
                            st.link_button("📍 地图视觉核实", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            st.caption(f"📞 号码: {phone}")
                        with col2:
                            st.markdown(f"**身份:** {intel['身份']}")
                            st.markdown(f"**经营:** {intel['生存状态']}")
                            st.info(f"💡 **实战战术:**\n{intel['实战战术']}")
                            st.warning(f"📦 **核心力推:** {intel['推荐']}")
                        
                        st.write("🌐 **社媒影响力核查:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队管理":
        st.title("⚙️ QIANDU HR 控制中心")
        t1, t2 = st.tabs(["待审名单", "在职员工"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {u} (申请时间: {info['time']})")
                if col2.button("通过", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 账号: {u}")
                if col2.button("注销", key=f"n_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 全球行动日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
