import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 物理级时间校准与数据安全 ---
def get_local_time():
    # 锁定东七区 (胡志明/雅加达/曼谷)
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
    
    # 异常频率监控 (反侦察)
    risk = "✅ 正常"
    if logs:
        try:
            last_t = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_t).total_seconds() < 1: risk = "🔴 频繁警告"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "指挥员": user,
        "指令": action,
        "目标": target,
        "战力贡献": weight,
        "安全状态": risk
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全球通讯大脑 V24 (精准路由) ---
def global_comm_router(phone_raw, name_addr, file_name=""):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = (str(name_addr) + " " + str(file_name)).lower()
    
    # 优先级 1: Telegram (小飞机) 特权逻辑
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus", "uae", "crypto"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", f"TG: +{nums}"

    # 优先级 2: 国别强制匹配
    # 越南 (84) -> Zalo
    if "vn" in ctx or "vietnam" in ctx or nums.startswith('84') or (len(nums) == 10 and nums.startswith('09')):
        p = nums[2:] if nums.startswith('84') else nums[1:] if nums.startswith('0') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", f"84-{p}"
    
    # 印尼 (62) -> WhatsApp
    elif "id" in ctx or "indonesia" in ctx or nums.startswith('62') or nums.startswith('08'):
        p = nums[2:] if nums.startswith('62') else nums[1:] if nums.startswith('0') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", f"62-{p}"
    
    # 泰国 (66) / 日本 (81) / 韩国 (82) -> Line
    elif "th" in ctx or "thailand" in ctx or nums.startswith('66'):
        p = nums[2:] if nums.startswith('66') else nums[1:] if nums.startswith('0') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", f"66-{p}"
    elif "jp" in ctx or "japan" in ctx or nums.startswith('81'):
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", f"81-{p}"
    elif "kr" in ctx or "korea" in ctx or nums.startswith('82'):
        p = nums[2:] if nums.startswith('82') else nums[1:] if nums.startswith('0') else nums
        return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{p}", "Line", f"82-{p}"

    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", nums

# --- 3. QIANDU AI 决策引擎 4.0 (战术闭环) ---
def qiandu_ai_v24(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # 深度特征提取
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "warehouse", "批发"])
    is_spa = any(k in ctx for k in ["spa", "skin", "clinic", "pharmacy", "nhà thuốc"])
    
    if is_ws:
        return {
            "角色": "🏗️ 大宗批发巨头",
            "价值": "⭐⭐⭐⭐⭐ (极高)",
            "策略": "【谈价模式】: 该客户只关心利润。直报货柜低价，展示韩国通关单。推 Jmella 全系列、SNP 基础款。",
            "避坑": "防范其拿我方报价去压其他供应商。"
        }
    elif is_spa:
        return {
            "角色": "🏥 专业医美渠道",
            "价值": "⭐⭐⭐⭐ (高)",
            "策略": "【谈背书模式】: 发送 Leaders/SNP 修复临床报告。强调‘非红海渠道’。谈专业，不谈价格。",
            "避坑": "开发周期较长，需专人持续跟进成分咨询。"
        }
    else:
        return {
            "角色": "🏪 终端潮流零售",
            "价值": "⭐⭐⭐ (中)",
            "策略": "【谈引流模式】: 推 meloMELI 潮流款。送陈列架、送小样。强调到店转化率。",
            "避坑": "单次起订量小，优先走散单物流。"
        }

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V24", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V24.0")
    acc = st.radio("系统入口", ["员工通道", "指挥官中心"], horizontal=True, key="acc24")
    if acc == "指挥官中心":
        pwd = st.text_input("密钥", type="password", key="bp24")
        if st.button("激活权限", key="bb24"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui24"), st.text_input("密码", type="password", key="pi24")
            if st.button("进入系统", key="bi24"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "成功登录")
                    st.rerun()
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队战力看板", "📜 深度日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度情报决策中心 (多国适配)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 检索店名、地址、商圈（AI 自动调取战术）", key="sq24")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索", q, 1)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                intel = qiandu_ai_v24(name, addr)
                country, chat_link, tool, info = global_comm_router(phone, name + addr, sel_f)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 国家: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            st.caption(f"🆔 系统输出: `{info}`")
                        with col2:
                            st.write(f"🏢 **画像:** {intel['角色']}")
                            st.write(f"📈 **评估:** {intel['价值']}")
                            st.info(f"💡 **AI 建议:**\n{intel['策略']}")
                            st.warning(f"⚠️ **风险点:** {intel['避坑']}")
                        
                        st.write("🌐 **社媒搜店:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队战力看板":
        st.title("⚙️ QIANDU 团队战力排行 (本月指标)")
        logs = load_data("logs")
        if logs:
            ldf = pd.DataFrame(logs)
            stats = ldf.groupby("指挥员")["战力贡献"].sum().sort_values(ascending=False)
            st.bar_chart(stats)
            st.caption("注：柱状图代表员工执行任务的总贡献值 (搜索=1, 联系=10)")
        
        st.divider()
        users = load_data("users")
        for u in list(users.keys()):
            if st.button(f"撤销员工权限: {u}", key=f"d_{u}"):
                del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度日志":
        st.title("📜 全球指挥审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
