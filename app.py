import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心架构：时区与深度审计 ---
def get_local_time():
    # 锁定胡志明/雅加达/曼谷时间 (UTC+7)
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
    # 风控监控：防止恶意刷分/导出
    if logs and logs[0]['操作员'] == user:
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1.2:
            risk = "🚨 频率预警"
            score = -30
    
    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"), 
        "操作员": user, 
        "指令": action, 
        "目标": target, 
        "战力贡献": score, 
        "评级": risk
    })
    save_data("logs", logs[:5000])

# --- 2. 战略大脑：全球路由与 AI 深度分析 ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    # 俄区/迪拜/中东 Telegram 强制路由
    if nums.startswith('7') or nums.startswith('971') or any(k in ctx for k in ["moscow", "dubai", "rus", "tg", "飞机"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    # 越南 Zalo
    if nums.startswith('84') or any(k in ctx for k in ["vn", "vietnam", "hcm", "hanoi"]):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    # 日本/泰国/韩国 Line
    if any(nums.startswith(x) for x in ['81','66','82']) or any(k in ctx for k in ["japan", "thailand", "korea"]):
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    # 默认 WhatsApp
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

def qiandu_ai_v90(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发", "warehouse", "grosir"])
    is_med = any(k in ctx for k in ["pharmacy", "clinic", "nhà thuốc", "spa", "skin"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat"])

    if is_ws:
        return "🏗️ 大宗流通大户", "5%-12%", "【谈价模式】: 谈柜货价、谈现货稳定性。推 Jmella/SNP 基础款。", "防范被当作比价工具。"
    elif is_med:
        return "🏥 专业医美渠道", "35%-55%", "【专业模式】: 谈成分、谈 Leaders 修复背书。强调非红海渠道。", "开发周期长，利润极稳。"
    elif is_prime:
        return "💎 核心地段旗舰", "25%-45%", "【引流模式】: 谈 meloMELI 颜值与视觉陈列支持。地租贵，需高毛利单品。", "对包装档次要求极高。"
    return "🏪 社区灵活零售", "20%-35%", "【周转模式】: 谈‘一件起批’、‘补货快’。推月度爆款单品。", "注意收款风险。"

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU COMMAND V90", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V90.0")
    acc = st.radio("入口模式", ["员工入口", "指挥官进入"], horizontal=True, key="login_mode")
    if acc == "指挥官进入":
        pwd = st.text_input("创始人密钥", type="password", key="boss_key")
        if st.button("激活权限", key="boss_act"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u = st.text_input("账号", key="staff_u")
            p = st.text_input("密码", type="password", key="staff_p")
            if st.button("进入系统", key="staff_enter"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("登录失败：需等待批准或密码错误")
        with t2:
            nu = st.text_input("新账号名", key="new_u")
            np = st.text_input("设置密码", type="password", key="new_p")
            if st.button("提交入职申请", key="apply_btn"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功！请联系指挥官批准。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队与权限", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("指挥系统导航", menu, key="main_nav")

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度商业情报中心 (V90 修复版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files, key="db_sel")
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            st.sidebar.divider()
            cols = list(df.columns)
            c_n = st.sidebar.selectbox("映射：店名列", cols, index=0, key="map_n")
            c_p = st.sidebar.selectbox("映射：电话列", cols, index=1 if len(cols)>1 else 0, key="map_p")
            c_a = st.sidebar.selectbox("映射：地址列", cols, index=min(2, len(cols)-1), key="map_a")
            
            q = st.text_input("🔎 全局搜索：店名、地址、商圈词 (AI 自动执行战术解析)", key="search_q")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2)
            remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 决策深度逻辑
                role, profit, strategy, trap = qiandu_ai_v90(name, addr)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.3])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            # 核心修复：link_button 不再作为条件，改用组合模式
                            st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True)
                            if st.button(f"📑 记入洽谈日志-{i}", use_container_width=True, help="点击后增加战力积分"):
                                add_mission_log(st.session_state.user, f"发起洽谈({tool})", name, 10)
                            st.link_button("📍 地图视觉分析", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role} ({profit})")
                            st.info(f"💡 **AI 建议:**\n{strategy}")

                        # --- 社媒穿透探测 ---
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True)
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True)
                        
                        st.divider()
                        rem = remarks.get(name, {"text": "暂无历史进展", "user": "-", "time": "-"})
                        st.success(f"备注: {rem['text']} ({rem['user']} {rem['time']})")
                        
                        new_note = st.text_input("更新跟进备注", key=f"note_in_{idx}")
                        if st.button("提交备注内容", key=f"note_btn_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队与权限":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["🆕 待审准入", "🏆 战力贡献榜"])
        with t1:
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 **{u}** (申请时间: {info['time']})")
                if c2.button("授权准入", key=f"approve_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd)
                    add_mission_log("Founder", "批准入职", u, 5); st.rerun()
        with t2:
            logs = load_data("logs")
            if logs:
                ldf = pd.DataFrame(logs)
                # 显式转换数据类型确保绘图正确
                ldf['战力贡献'] = pd.to_numeric(ldf['战力贡献'], errors='coerce').fillna(0)
                stats = ldf.groupby("操作员")["战力贡献"].sum().sort_values(ascending=False)
                st.bar_chart(stats)
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"🚫 永久注销: {u}", key=f"ban_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    if st.sidebar.button("🚪 安全退出", key="logout"):
        st.session_state.clear(); st.rerun()
