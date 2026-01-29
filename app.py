import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心底座：高精度审计引擎 ---
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
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    hour = current_time.hour
    
    # 智能风控与价值判定
    risk = "✅ 正常"
    if hour < 7 or hour > 23: risk = "🌙 深夜操作"
    
    if logs and logs[0]['操作员'] == user:
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1.0:
            risk = "🚨 高频风险"
            score = -50 # 恶意操作扣重分
    
    logs.insert(0, {
        "时间": time_str, 
        "操作员": user, 
        "指令动作": action, 
        "目标对象": target, 
        "战力值": score, 
        "安全评级": risk
    })
    save_data("logs", logs[:5000])

# --- 2. 战略路由与 AI 决策逻辑 (集成前序版本精华) ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if nums.startswith('7') or nums.startswith('971') or any(k in ctx for k in ["moscow", "dubai", "tg"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or any(k in ctx for k in ["vn", "vietnam", "hcm"]):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if any(nums.startswith(x) for x in ['81','66','82']) or any(k in ctx for k in ["japan", "thailand", "korea"]):
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

def qiandu_ai_v95(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发", "warehouse"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit"])
    if is_ws: return "🏗️ 批发巨头", "谈价模式：报货柜单价。推 Jmella/SNP。", "5-12%"
    if is_prime: return "💎 核心店", "引流模式：谈 meloMELI 颜值支持。地租贵，需高毛利。", "25-45%"
    return "🏪 终端零售", "周转模式：谈补货快、一件起批。推爆款单品。", "20-35%"

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU COMMAND V95", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V95.0")
    acc = st.radio("入口", ["员工通道", "指挥官中心"], horizontal=True, key="entry_mode")
    if acc == "指挥官中心":
        pwd = st.text_input("密钥", type="password", key="boss_in")
        if st.button("激活权限", key="boss_go"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 入职申请"])
        with t1:
            u, p = st.text_input("账号", key="u_in"), st.text_input("密码", type="password", key="p_in")
            if st.button("登录", key="log_btn"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统", score=0)
                    st.rerun()
        with t2:
            nu, np = st.text_input("拟用账号", key="nu_in"), st.text_input("密码设置", type="password", key="np_in")
            if st.button("提交申请", key="app_btn"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请已送达指挥官。")

else:
    # 侧边栏老板全局视窗
    st.sidebar.title(f"👤 {st.session_state.user}")
    if st.session_state.role == "boss":
        st.sidebar.divider()
        st.sidebar.subheader("📈 系统实时快报")
        logs_all = load_data("logs")
        st.sidebar.metric("今日操作总数", len([l for l in logs_all if l['时间'].startswith(get_local_time().strftime("%Y-%m-%d"))]))
        st.sidebar.metric("待审核申请", len(load_data("pending")))
    
    menu = ["📊 情报矩阵", "⚙️ 团队与战力", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("导航系统", menu, key="main_nav")

    if nav == "📊 情报矩阵":
        st.title("📊 情报与决策矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files, key="f_sel")
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            # 列映射与搜索逻辑 (保持 V90 的稳定性)
            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols, key="c1"), st.sidebar.selectbox("电话列", cols, index=1, key="c2"), st.sidebar.selectbox("地址列", cols, index=2, key="c3")
            
            q = st.text_input("🔎 搜索店名、商圈或关键词", key="q_in")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2)
            remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                role, strat, profit = qiandu_ai_v95(name, addr)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        cl1, cl2 = st.columns([1, 1.2])
                        with cl1:
                            st.write(f"🌍 区域: **{country}**")
                            st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True)
                            if st.button(f"📑 登记洽谈战力", key=f"log_{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, f"发起洽谈({tool})", name, 10)
                        with cl2:
                            st.write(f"🏢 画像: **{role}**")
                            st.info(f"💡 建议: {strat}")
                        
                        # 社媒矩阵
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True)
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True)

                        rem = remarks.get(name, {"text": "暂无记录", "user": "-", "time": "-"})
                        st.divider()
                        st.success(f"最新进展: {rem['text']} ({rem['user']})")
                        new_note = st.text_input("更新记录", key=f"ni_{idx}")
                        if st.button("保存备注", key=f"nb_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队与战力":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["🆕 待审准入", "🏆 战力排行图"])
        with t1:
            pnd = load_data("pending")
            if not pnd: st.info("目前没有待审核的入职申请。")
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 **{u}** (申请于: {info['time']})")
                if c2.button("批准准入", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
                if c3.button("拒绝申请", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            st.subheader("🔥 员工战力贡献榜 (分值加权)")
            ldf = pd.DataFrame(load_data("logs"))
            if not ldf.empty:
                ldf['战力值'] = pd.to_numeric(ldf['战力值'], errors='coerce').fillna(0)
                stats = ldf.groupby("操作员")["战力值"].sum().sort_values(ascending=False)
                st.bar_chart(stats)
                
                st.divider()
                st.subheader("👥 团队在线清单")
                users = load_data("users")
                for u in list(users.keys()):
                    cc1, cc2 = st.columns([3, 1])
                    cc1.write(f"👤 在职成员: **{u}**")
                    if cc2.button("吊销权限", key=f"ban_{u}"):
                        del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度审计日志":
        st.title("📜 行动审计雷达 (全量日志)")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            # 自动高亮风险项
            def color_risk(val):
                if "🚨" in str(val): return 'background-color: #ff4b4b; color: white'
                if "🌙" in str(val): return 'background-color: #f0f2f6; color: #ffa500'
                return ''
            st.dataframe(ldf.style.applymap(color_risk, subset=['安全评级']), use_container_width=True)

    if st.sidebar.button("🚪 安全退出系统", key="out"):
        st.session_state.clear(); st.rerun()
