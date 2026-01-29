import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
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
    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "指挥员": user,
        "指令": action,
        "目标": target,
        "战力贡献": weight
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全球通讯大脑 V26 (精准路由) ---
def global_comm_router(phone_raw, name_addr, file_name=""):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = (str(name_addr) + " " + str(file_name)).lower()
    
    # Telegram 优先
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", f"TG: +{nums}"

    # 国别强制
    if "vn" in ctx or "vietnam" in ctx or nums.startswith('84') or (len(nums) == 10 and nums.startswith('09')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", f"84-{p}"
    elif "id" in ctx or "indonesia" in ctx or nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", f"62-{p}"
    elif "th" in ctx or "thailand" in ctx or nums.startswith('66'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('66') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", f"66-{p}"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", nums

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V26", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V26.0")
    acc = st.radio("系统入口", ["员工通道", "指挥官中心"], horizontal=True, key="acc26")
    
    if acc == "指挥官中心":
        pwd = st.text_input("创始人密钥", type="password", key="bp26")
        if st.button("激活指挥权限", key="bb26"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui26"), st.text_input("密码", type="password", key="pi26")
            if st.button("进入系统", key="bi26"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("账号未授权或需等待创始人审核")
        with t2:
            nu, np = st.text_input("新账号名", key="nu26"), st.text_input("设置密码", type="password", key="np26")
            if st.button("提交入职申请", key="rb26"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功！请联系指挥官（Founder）在后台批准。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队管理", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("指挥系统", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 全媒体情报中心")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、地址或关键词", key="sq26")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                country, chat_link, tool, info = global_comm_router(phone, name + addr, sel_f)
                
                # 为社媒搜索对店名进行编码
                search_query = urllib.parse.quote(name)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 国家: **{country}**")
                            st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True)
                            st.link_button("📍 地图视觉调研", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write("🌐 **社媒实战探测:**")
                            # 真实的社媒搜索链接
                            s1, s2, s3 = st.columns(3)
                            s1.link_button("FB", f"https://www.facebook.com/search/top/?q={search_query}", use_container_width=True)
                            s2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                            s3.link_button("TK", f"https://www.tiktok.com/search?q={search_query}", use_container_width=True)
                            
                            st.caption(f"📞 号码解析: `{info}`")
                            if st.button(f"标记为今日重点-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, "重点标记", name, 5)

    elif nav == "⚙️ 团队管理":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["🆕 待审名单", "👥 在职名单"])
        
        with t1:
            pnd = load_data("pending")
            if not pnd: st.info("暂无待处理的入职申请")
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"申请人: **{u}** (申请时间: {info['time']})")
                if c2.button("✅ 批准通过", key=f"y_{u}"):
                    users = load_data("users")
                    users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd)
                    add_mission_log("Founder", "批准入职", u, 5)
                    st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()

        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 在职成员: {u}")
                if c2.button("🚫 强行注销", key=f"d_{u}"):
                    del users[u]; save_data("users", users)
                    add_mission_log("Founder", "撤销权限", u, 0)
                    st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 全球指挥审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
