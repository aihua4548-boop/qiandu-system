import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 时区与深度安全审计架构 ---
def get_local_time():
    # 强制同步胡志明/雅加达时间 (UTC+7)
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
    
    # 异常频率监控 (防刷数据)
    risk_status = "✅ 正常"
    if logs:
        try:
            last_t = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_t).total_seconds() < 1.2: risk_status = "🔴 频率异常"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "指挥员": user,
        "指令动作": action,
        "目标对象": target,
        "情报深度": "💎 核心" if weight >= 10 else "📄 基础",
        "安全监控": risk_status
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全球通讯大脑 V30 (精准适配路由) ---
def global_comm_router(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 优先级 A: Telegram (小飞机)
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus", "uae"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", f"TG: +{nums}"

    # 优先级 B: 国家专属软件
    # 越南 (84) -> Zalo
    if "vn" in ctx or "vietnam" in ctx or nums.startswith('84') or (len(nums) == 10 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", f"84-{p}"
    
    # 印尼 (62) -> WhatsApp
    elif "id" in ctx or "indonesia" in ctx or nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", f"62-{p}"
    
    # 泰国/日本/韩国 -> Line
    elif "th" in ctx or "thailand" in ctx or nums.startswith('66'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('66') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", f"66-{p}"
    elif "jp" in ctx or "japan" in ctx or nums.startswith('81'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('81') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", f"81-{p}"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", nums

# --- 3. QIANDU AI 决策引擎 (一店一策实战建议) ---
def qiandu_ai_v30(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "批发", "distributor"])
    is_spa = any(k in ctx for k in ["spa", "skin", "clinic", "pharmacy", "derma"])
    
    if is_ws:
        return "🏗️ 大宗批发", "📈 利润: 5-12% (走量型)", "【策略】: 报货柜价格，展示韩国直发证件。对方看重现货稳定和单价。"
    elif is_spa:
        return "🏥 专业渠道", "📈 利润: 35-50% (价值型)", "【策略】: 推 Leaders 院线款。强调修复成分和专业培训。不要打价格战。"
    else:
        return "🏪 潮流零售", "📈 利润: 20-30% (引流型)", "【策略】: 推 meloMELI 新品。利用陈列柜和小样吸引客户。谈网红热度。"

# --- 4. 界面展示层 ---
st.set_page_config(page_title="QIANDU BI V30", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V30.0")
    acc = st.radio("模式", ["员工通道", "指挥官进入"], horizontal=True, key="acc30")
    if acc == "指挥官进入":
        pwd = st.text_input("创始人密钥", type="password", key="bp30")
        if st.button("激活权限", key="bb30"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="ui30"), st.text_input("密码", type="password", key="pi30")
            if st.button("进入系统", key="bi30"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("登录失败：账号未批准或密码错误")
        with t2:
            nu, np = st.text_input("新账号名", key="nu30"), st.text_input("设置密码", type="password", key="np30")
            if st.button("提交入职申请", key="rb30"):
                pnd = load_data("pending")
                pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功！请联系指挥官批准入职。")

else:
    # --- 5. 内部主系统 ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报决策矩阵", "⚙️ 团队与权限", "📜 深度日志审计"] if st.session_state.role == "boss" else ["📊 情报决策矩阵"]
    nav = st.sidebar.radio("指挥中心", menu)

    if nav == "📊 情报决策矩阵":
        st.title("📊 QIANDU 深度商业情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、地址、商圈或身份关键词 (AI 自动重载战术)", key="sq30")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 策略与路由
                role, profit, strategy = qiandu_ai_v30(name, addr)
                country, chat_link, tool, parsed_num = global_comm_router(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 国家: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系商户({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.write(f"💵 **预期:** {profit}")
                            st.info(f"💡 **AI 建议:**\n{strategy}")
                        
                        st.write("🌐 **社媒影响力核查:**")
                        search_q = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("Facebook", f"https://www.facebook.com/search/top/?q={search_q}")
                        sc2.link_button("Instagram", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TikTok", f"https://www.tiktok.com/search?q={search_q}")

    elif nav == "⚙️ 团队与权限":
        st.title("⚙️ 团队管理与入职审核")
        t1, t2 = st.tabs(["🆕 待审申请", "👥 现有员工"])
        
        with t1:
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"申请人: **{u}** ({info['time']})")
                if c2.button("✅ 批准通过", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd)
                    add_mission_log("Founder", "批准入职", u, 5); st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()

        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 活跃账号: {u}")
                if c2.button("🚫 注销权限", key=f"d_{u}"):
                    del users[u]; save_data("users", users)
                    add_mission_log("Founder", "撤销权限", u, 0); st.rerun()

    elif nav == "📜 深度日志审计":
        st.title("📜 全球行动深度审计")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出系统"):
        st.session_state.clear(); st.rerun()
