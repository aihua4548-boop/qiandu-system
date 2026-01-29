import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心：精准时区与动态审计 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7) # 锁定 ICT 时区

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

def add_mission_log(user, action, target="-", score=1):
    logs = load_data("logs")
    current_time = get_local_time()
    
    # 异常行为风控：如果 1 秒内连续点击
    risk = "✅ 正常"
    if logs and logs[0]['操作员'] == user:
        try:
            last_t = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_t).total_seconds() < 1: risk = "🔴 频繁抓取风险"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令": action,
        "商户": target,
        "战力分": score,
        "安全状态": risk
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全域通讯路由 V35 (含多语言话术) ---
def get_intel_and_chat(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 国家识别与话术生成
    if "japan" in ctx or nums.startswith('81'):
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", "【日文话术】こんにちは、韓国QIANDU（千渡）です。Jmella/SNPの卸売について..."
    
    if "vietnam" in ctx or "vn" in ctx or nums.startswith('84'):
        p = nums[2:] if nums.startswith('84') else nums[1:] if nums.startswith('0') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", "【越文话术】Chào bạn, mình từ QIANDU Hàn Quốc. Bên mình phân phối sỉ Jmella/SNP..."
    
    if "thailand" in ctx or nums.startswith('66'):
        p = nums[2:] if nums.startswith('66') else nums[1:] if nums.startswith('0') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", "【泰文话术】สวัสดีครับ จาก QIANDU Korea ครับ เราเป็นตัวแทนจำหน่าย SNP/Jmella..."
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", "【通用话术】Hi, this is QIANDU Korea. We provide wholesale for K-beauty brands..."

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V35", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥部 V35.0")
    acc = st.radio("模式", ["员工通道", "指挥官进入"], horizontal=True)
    if acc == "指挥官进入":
        pwd = st.text_input("创始人密钥", type="password")
        if st.button("激活权限"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        u, p = st.text_input("账号"), st.text_input("密码", type="password")
        if st.button("登录"):
            users = load_data("users")
            if u in users and users[u]["pwd"] == p:
                st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                add_mission_log(u, "登录系统", "-", 1)
                st.rerun()
        st.caption("没有账号？请点击上方'注册'或联系负责人批准。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报看板", "⚙️ 团队战力统计", "📜 安全审计"] if st.session_state.role == "boss" else ["📊 情报看板"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报看板":
        st.title("📊 QIANDU 深度情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、商圈或国家关键词 (AI 话术同步生成)")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                country, chat_link, tool, script = get_intel_and_chat(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        c1, c2 = st.columns([1, 1.3])
                        with c1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with c2:
                            st.write(f"🏢 **画像:** {'🏗️ 批发大户' if 'sỉ' in name.lower() or 'wholesale' in name.lower() else '🏪 零售终端'}")
                            with st.expander("📝 查看多语言破冰话术"):
                                st.code(script, language="markdown")
                                st.caption("复制后在聊天应用中直接粘贴发送。")
                        
                        st.write("🌐 **社媒探测:**")
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}")

    elif nav == "⚙️ 团队战力统计":
        st.title("⚙️ QIANDU 员工实战看板")
        logs = load_data("logs")
        if logs:
            ldf = pd.DataFrame(logs)
            st.subheader("🔥 员工开发进度排行 (点击联系客户的次数)")
            stats = ldf[ldf["战力分"] >= 10].groupby("操作员").size().sort_values(ascending=False)
            st.bar_chart(stats)
            
            st.divider()
            st.subheader("🆕 待审核新账号")
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {u} ({info['time']})")
                if col2.button("批准入职", key=f"app_{u}"):
                    users = load_data("users")
                    users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()

    elif nav == "📜 安全审计":
        st.title("📜 全球行动审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
