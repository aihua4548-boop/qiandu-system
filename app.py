import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 时区与深度安全审计 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7) # 越南/印尼 ICT

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

def add_mission_log(user, action, target="-", depth=1):
    logs = load_data("logs")
    current_time = get_local_time()
    
    # 频率监控兼容逻辑
    risk_tag = "✅ 正常"
    if logs:
        try:
            last_time = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_time).total_seconds() < 1.2:
                risk_tag = "🔴 异常高频"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "动作": action,
        "目标": target,
        "价值": "💎 核心" if depth >= 10 else "📄 常规",
        "状态": risk_tag
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 战术与盈利测算大脑 V22 ---
def qiandu_profit_brain(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # 汇率基准 (模拟 2026 实时汇率)
    RATE_VND = 18.5 # 1 KRW = 18.5 VND
    RATE_IDR = 12.0 # 1 KRW = 12.0 IDR
    
    # 1. 深度属性识别
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "批发"])
    is_spa = any(k in ctx for k in ["spa", "skin", "clinic", "nhà thuốc"])
    
    if is_ws:
        role = "🏗️ 大宗批发大户"
        margin = "5% - 12% (靠走量)"
        chips = "✅ 现货供应、✅ 价格对标、✅ 官方代理"
        suggestion = "谈判重点：【价格与账期】。对方不在乎品牌故事，只在乎能不能赚到那 10% 的差价。"
    elif is_spa:
        role = "🏥 专业医美院线"
        margin = "35% - 50% (高利润)"
        chips = "✅ 成分背书、✅ 修复效果、✅ 避开红海"
        suggestion = "谈判重点：【专业性】。推 Leaders/SNP 医美款，强调单客成交利润高，不打价格战。"
    else:
        role = "🏪 潮流零售/网红"
        margin = "20% - 30% (高周转)"
        chips = "✅ 颜值引流、✅ 爆款支持、✅ 小样赠品"
        suggestion = "谈判重点：【引流】。推 meloMELI 新品，强调‘到店转化率’和‘社交媒体热度’。"

    return role, margin, chips, suggestion

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU COMMAND V22", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥部 V22.0")
    acc = st.radio("通道", ["员工入口", "指挥官进入"], horizontal=True, key="acc_v22")
    if acc == "指挥官进入":
        pwd = st.text_input("密钥", type="password", key="bp_v22")
        if st.button("激活权限", key="bb_v22"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="ui_v22"), st.text_input("密码", type="password", key="pi_v22")
            if st.button("进入系统", key="bi_v22"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录")
                    st.rerun()
        with t2:
            nu, np = st.text_input("申请名", key="nu_v22"), st.text_input("设置密码", type="password", key="np_v22")
            if st.button("提交申请", key="rb_v22"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请成功")
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队战力看板", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 智能情报与利润决策矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、地址、关键词 (AI 自动测算利润)", key="sq_v22")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索情报", q)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 盈利测算 V22
                role, margin, chips, suggestion = qiandu_profit_brain(name, addr)
                
                # 电话路由修正
                nums = re.sub(r'\D', '', phone)
                zalo_link = f"https://zalo.me/84{nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums}"
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.3])
                        with col1:
                            st.link_button("💬 Zalo/WA 谈判", zalo_link, type="primary", use_container_width=True)
                            if st.button(f"记录联络-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, "点击洽谈", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            st.caption(f"📞 号码: {phone}")
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.write(f"📈 **预估毛利:** {margin}")
                            st.write(f"🎭 **谈判筹码:** {chips}")
                            st.info(f"💡 **AI 建议:**\n{suggestion}")
                        
                        st.write("🌐 **社媒搜店:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队战力看板":
        st.title("⚙️ 员工绩效战力排行榜")
        logs = load_data("logs")
        if logs:
            ldf = pd.DataFrame(logs)
            stats = ldf[ldf["情报深度"]=="💎 核心"].groupby("操作员").size().sort_values(ascending=False)
            st.bar_chart(stats)
            st.caption("注：柱状图代表员工实际发起联络（深度开发）的次数")
        
        st.divider()
        users = load_data("users")
        for u in list(users.keys()):
            if st.button(f"移除员工: {u}", key=f"d_{u}"):
                del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度审计日志":
        st.title("📜 全球行动深度审计")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
