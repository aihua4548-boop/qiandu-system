import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 数据架构与时区同步 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7)

DB_FILES = {
    "users": "users_data.json", 
    "pending": "pending.json", 
    "logs": "op_logs.json",
    "remarks": "remarks_data.json"
}

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
        "操作员": user,
        "指令": action,
        "目标": target,
        "情报深度": "💎 核心联络" if weight >= 10 else "📄 基础查阅"
    })
    save_data("logs", logs[:3000])

# --- 2. 核心修正：QIANDU 全球通讯大脑 V41 (国家路由补丁) ---
def get_comm_route(phone_raw, name_addr, file_context=""):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = (str(name_addr) + " " + str(file_context)).lower()
    
    # 优先级 1: Telegram (小飞机) - 针对中东或俄区
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", "小飞机直连"

    # 优先级 2: 越南 (Zalo) - 强力纠错
    # 逻辑：如果区号是84，或者地址含越南关键词，或者号码是以越南常用手机号段开头
    if nums.startswith('84') or any(k in ctx for k in ["vn", "vietnam", "hcm", "hanoi", "hồ chí minh", "thành phố"]) or (len(nums) == 10 and (nums.startswith('09') or nums.startswith('03') or nums.startswith('07') or nums.startswith('08'))):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", "越南 Zalo"

    # 优先级 3: 日本 (Line)
    if nums.startswith('81') or "japan" in ctx or "tokyo" in ctx:
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", "日本 Line"

    # 优先级 4: 泰国 (Line)
    if nums.startswith('66') or "thailand" in ctx or "bangkok" in ctx:
        p = nums[2:] if nums.startswith('66') else nums[1:] if nums.startswith('0') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", "泰国 Line"

    # 优先级 5: 印尼 (WhatsApp)
    if nums.startswith('62') or "indonesia" in ctx or "jakarta" in ctx or nums.startswith('08'):
        p = nums[2:] if nums.startswith('62') else nums[1:] if nums.startswith('0') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", "印尼 WhatsApp"
    
    # 兜底：全球 WhatsApp
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", "通用"

# --- 3. QIANDU AI 深度大脑 ---
def qiandu_ai_v41(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "批发"])
    if is_ws:
        return "🏗️ 批发大户", "5%-12%", "【谈价模式】: 报货柜价格，谈一手货源。推 Jmella 全系列。"
    return "🏪 零售/药妆", "20%-45%", "【推新模式】: 谈 meloMELI 颜值和 SNP 修复背书。送样支持。"

# --- 4. 界面展示 ---
st.set_page_config(page_title="QIANDU BI V41", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V41.0")
    acc = st.radio("模式", ["员工入口", "指挥官中心"], horizontal=True, key="acc41")
    if acc == "指挥官中心":
        pwd = st.text_input("创始人密钥", type="password", key="bp41")
        if st.button("激活权限", key="bb41"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="ui41"), st.text_input("密码", type="password", key="pi41")
            if st.button("登录", key="bi41"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
        with t2:
            nu, np = st.text_input("新账号名", key="nu41"), st.text_input("设置密码", type="password", key="np41")
            if st.button("提交入职申请", key="rb41"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功，请等待指挥官批准。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队与权限", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 情报决策矩阵 (通讯路由修复版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名或商圈 (AI 将锁定对应国家软件)")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            c_n, c_p, c_a = df.columns[0], df.columns[1], df.columns[min(2, len(df.columns)-1)]
            grid = st.columns(2)
            remarks = load_data("remarks")
            
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # V41 修复：根据文件名和地址关键词，锁定 Zalo 或 WhatsApp
                country, chat_link, tool, label = get_comm_route(phone, name + addr, sel_f)
                role, profit, strategy = qiandu_ai_v41(name, addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.3])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.write(f"📈 **预期:** {profit}")
                            st.info(f"💡 **AI 建议:**\n{strategy}")

                        st.divider()
                        curr_rem = remarks.get(name, {"text": "暂无跟进备注", "user": "-", "time": "-"})
                        st.caption(f"📝 备注更新: {curr_rem['time']} ({curr_rem['user']})")
                        st.success(f"内容: {curr_rem['text']}")
                        
                        new_note = st.text_input("更新跟进进展", key=f"n_{idx}")
                        if st.button("保存备注", key=f"b_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks)
                                add_mission_log(st.session_state.user, "更新备注", name, 5)
                                st.rerun()

                        st.write("🌐 **社媒影响力探测:**")
                        search_q = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={search_q}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={search_q}")

    elif nav == "⚙️ 团队与权限":
        st.title("⚙️ 团队管理与入职审核")
        t1, t2 = st.tabs(["🆕 准入审核", "👥 现有员工"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"申请人: **{u}** ({info['time']})")
                if c2.button("✅ 批准通过", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 在职: {u}")
                if c2.button("🚫 注销权限", key=f"d_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 全球指挥审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("安全退出"):
        st.session_state.clear(); st.rerun()
