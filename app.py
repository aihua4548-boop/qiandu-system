import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心架构：时区与深度审计 ---
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
    if logs and logs[0]['操作员'] == user:
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1:
            risk = "🚨 频率预警"
            score = -10
    
    logs.insert(0, {"时间": current_time.strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "指令": action, "目标": target, "战力": score, "评级": risk})
    save_data("logs", logs[:5000])

# --- 2. 战略大脑：全球路由与 AI 画像 ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if nums.startswith('7') or nums.startswith('971') or "moscow" in ctx or "dubai" in ctx:
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or "vietnam" in ctx or "vn" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if any(nums.startswith(x) for x in ['81','66','82']) or any(k in ctx for k in ["japan", "thailand", "korea"]):
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

def qiandu_ai_v85(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发", "warehouse"])
    is_med = any(k in ctx for k in ["pharmacy", "clinic", "nhà thuốc", "spa"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "aeon"])

    if is_ws:
        return "🏗️ 流通大户", "报货柜价。推 Jmella/SNP 基础款。谈现货稳定。", "5-12%"
    elif is_med:
        return "🏥 专业医美/药妆", "推 Leaders 修复系列。谈临床数据与背书，避开价格战。", "35-55%"
    elif is_prime:
        return "💎 核心商圈旗舰", "地租极贵！谈 meloMELI 颜值与引流陈列支持。强调转化率。", "25-45%"
    return "🏪 终端零售", "谈‘一件代发’与‘补货快’。推月度爆款单品。", "20-35%"

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V85", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V85.0")
    acc = st.radio("系统模式", ["员工通道", "指挥官中心"], horizontal=True, key="main_mode")
    if acc == "指挥官中心":
        pwd = st.text_input("创始人密钥", type="password", key="boss_pwd_input")
        if st.button("激活权限", key="boss_login_btn"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u = st.text_input("账号", key="staff_login_user")
            p = st.text_input("密码", type="password", key="staff_login_pwd")
            if st.button("进入系统", key="staff_login_btn"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("登录失败：账号未批准或密码错误")
        with t2:
            nu = st.text_input("拟申请账号名", key="reg_user")
            np = st.text_input("拟设置密码", type="password", key="reg_pwd")
            if st.button("提交入职申请", key="reg_btn"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功，请联系指挥官批准。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队与审核", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu, key="nav_sidebar")

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度情报与 AI 决策中心")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源文件", files, key="file_select")
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            st.sidebar.divider()
            cols = list(df.columns)
            c_n = st.sidebar.selectbox("店名列", cols, index=0, key="col_n")
            c_p = st.sidebar.selectbox("电话列", cols, index=1 if len(cols)>1 else 0, key="col_p")
            c_a = st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1), key="col_a")
            
            q = st.text_input("🔎 搜店名、商圈或关键词（AI 自动重载各国路由）", key="search_bar")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2)
            remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                role, strat, profit = qiandu_ai_v85(name, addr)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.3])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True, key=f"chat_{idx}"):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True, key=f"map_{idx}")
                        with col2:
                            st.write(f"🏢 **画像:** {role} ({profit})")
                            st.info(f"💡 **AI 建议:**\n{strat}")

                        # --- 社媒探测 ---
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True, key=f"fb_{idx}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True, key=f"ins_{idx}")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True, key=f"tk_{idx}")
                        
                        st.divider()
                        rem = remarks.get(name, {"text": "暂无进展", "user": "-", "time": "-"})
                        st.success(f"备注: {rem['text']} ({rem['user']} {rem['time']})")
                        new_note = st.text_input("更新跟进备注", key=f"note_input_{idx}")
                        if st.button("保存记录", key=f"note_btn_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队与审核":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["🆕 入职审批", "👥 战力看板"])
        with t1:
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 **{u}** (申请时间: {info['time']})")
                if c2.button("通过审批", key=f"approve_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            logs = load_data("logs")
            if logs:
                ldf = pd.DataFrame(logs)
                st.bar_chart(ldf.groupby("操作员")["战力"].sum().sort_values(ascending=False))
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"注销权限: {u}", key=f"del_user_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    if st.sidebar.button("🚪 安全退出", key="logout_btn"):
        st.session_state.clear(); st.rerun()
