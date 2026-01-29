import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心引擎 ---
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
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1.0:
            risk = "🚨 高频风险"; score = -50
    logs.insert(0, {"时间": current_time.strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "指令动作": action, "目标对象": target, "战力值": score, "安全评级": risk})
    save_data("logs", logs[:5000])

# --- 2. 核心算法：号码脱敏处理 ---
def mask_phone(phone_raw, role):
    raw = re.sub(r'\D', '', str(phone_raw))
    if role == "boss": return raw # 指挥官看全局
    if len(raw) > 7:
        return f"{raw[:3]}****{raw[-4:]}" # 员工看脱敏版
    return "****"

# --- 3. 战略路由与 AI ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if nums.startswith('7') or nums.startswith('971') or "moscow" in ctx or "dubai" in ctx:
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or "vietnam" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if any(nums.startswith(x) for x in ['81','66','82']) or any(k in ctx for k in ["japan", "thailand"]):
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

def qiandu_ai_v96(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    if any(k in ctx for k in ["wholesale", "sỉ", "批发"]): return "🏗️ 批发巨头", "谈柜货价，推 Jmella/SNP。", "5-12%"
    if any(k in ctx for k in ["district 1", "myeongdong"]): return "💎 核心店", "谈颜值引流，推 meloMELI。", "25-45%"
    return "🏪 终端零售", "谈补货快。推爆款。", "20-35%"

# --- 4. 界面展示 ---
st.set_page_config(page_title="QIANDU COMMAND V96", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V96.0")
    acc = st.radio("入口", ["员工通道", "指挥官中心"], horizontal=True)
    if acc == "指挥官中心":
        pwd = st.text_input("密钥", type="password")
        if st.button("激活"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"}); st.rerun()
    else:
        u, p = st.text_input("账号"), st.text_input("密码", type="password")
        if st.button("登录"):
            users = load_data("users")
            if u in users and users[u]["pwd"] == p:
                st.session_state.update({"auth_ok": True, "user": u, "role": "staff"}); add_mission_log(u, "登录"); st.rerun()
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队战力", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 深度情报矩阵 (数据脱敏保护版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=2)
            
            q = st.text_input("🔎 搜索商户关键词")
            if q: df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2); remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # 脱敏处理
                display_phone = mask_phone(phone, st.session_state.role)
                role, strat, profit = qiandu_ai_v96(name, addr)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        cl1, cl2 = st.columns([1, 1.2])
                        with cl1:
                            st.write(f"🌍 区域: **{country}**")
                            st.write(f"📞 号码: `{display_phone}`")
                            st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True)
                            if st.button(f"📑 登记战力-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系客户({tool})", name, 10)
                        with cl2:
                            st.write(f"🏢 画像: **{role}**")
                            st.info(f"💡 建议: {strat}")
                        
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True)
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True)

                        rem = remarks.get(name, {"text": "暂无记录", "user": "-", "time": "-"})
                        st.divider()
                        st.success(f"备注: {rem['text']} ({rem['user']})")
                        new_note = st.text_input("更新记录", key=f"ni_{idx}")
                        if st.button("保存备注", key=f"nb_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队战力":
        st.title("⚙️ QIANDU 战力排行图")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            ldf['战力值'] = pd.to_numeric(ldf['战力值'], errors='coerce').fillna(0)
            st.bar_chart(ldf.groupby("操作员")["战力值"].sum().sort_values(ascending=False))
        # 审核板块
        st.divider()
        st.subheader("🆕 待审准入")
        pnd = load_data("pending")
        for u, info in list(pnd.items()):
            c1, c2 = st.columns([3, 1])
            c1.write(f"👤 {u} ({info['time']})")
            if c2.button("通过", key=f"y_{u}"):
                users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 行动审计日志")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            def color_risk(val): return 'background-color: #ff4b4b; color: white' if "🚨" in str(val) else ''
            st.dataframe(ldf.style.applymap(color_risk, subset=['安全评级']), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"): st.session_state.clear(); st.rerun()
