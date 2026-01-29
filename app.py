import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 时区与深度审计引擎 V75 ---
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

def add_mission_log(user, action, target="-", base_score=1):
    logs = load_data("logs")
    current_time = get_local_time()
    
    # 频率风控与战力惩罚逻辑
    risk_level = "✅ 安全"
    final_score = base_score
    if logs and logs[0]['操作员'] == user:
        time_diff = (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds()
        if time_diff < 1.2:
            risk_level = "🚨 高频风险"
            final_score = -50  # 违规操作扣大分

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "动作": action,
        "目标对象": target,
        "战力贡献": final_score,
        "安全评级": risk_level
    })
    save_data("logs", logs[:5000])

# --- 2. QIANDU 全球路由与 AI 画像 (集成前序完美版本) ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    # 俄罗斯/迪拜 Telegram
    if nums.startswith('7') or nums.startswith('971') or any(k in ctx for k in ["moscow", "dubai", "tg", "飞机", "rus"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    # 越南 Zalo
    if nums.startswith('84') or any(k in ctx for k in ["vn", "vietnam", "hcm", "sỉ"]):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    # 日本/泰国 Line
    if nums.startswith('81') or "japan" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('81') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

def qiandu_ai_v75(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发"])
    is_prime = any(k in ctx for k in ["district 1", "myeongdong", "sukhumvit"])
    if is_ws: return "🏗️ 批发巨头", "谈柜货单价，推 Jmella/SNP。", "Chào bạn, bên mình chuyên đổ sỉ giá container..."
    if is_prime: return "💎 核心店", "谈颜值引流，推 meloMELI。", "Shop mình địa điểm đẹp, nhập meloMELI sẽ rất hút khách..."
    return "🏪 终端零售", "谈补货速度与散单价格。", "Bên mình có sẵn hàng, nhập lẻ giá sỉ, giao ngay..."

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V75", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V75.0")
    acc = st.radio("模式", ["员工入口", "指挥官进入"], horizontal=True)
    if acc == "指挥官进入":
        pwd = st.text_input("密钥", type="password")
        if st.button("激活权限"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号"), st.text_input("密码", type="password")
            if st.button("登录"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
        with t2:
            nu, np = st.text_input("拟申请账号"), st.text_input("拟设置密码", type="password")
            if st.button("提交申请"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功，等待审核。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队战力与审核", "📜 行动审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            # 列名智能映射
            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols, index=0), st.sidebar.selectbox("电话列", cols, index=1 if len(cols)>1 else 0), st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1))
            
            q = st.text_input("🔎 搜店名、地址、商圈或关键词")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2)
            remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                country, chat_link, tool = get_comm_route(phone, name + addr)
                role, strat, script = qiandu_ai_v75(name, addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.info(f"💡 **AI 建议:** {strat}")
                            with st.expander("📝 破冰话术"): st.code(script, language="markdown")
                        
                        st.divider()
                        rem = remarks.get(name, {"text": "暂无进展", "user": "-", "time": "-"})
                        st.success(f"备注: {rem['text']} ({rem['user']} {rem['time']})")
                        new_note = st.text_input("跟进进展", key=f"n_{idx}")
                        if st.button("保存备注", key=f"b_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队战力与审核":
        st.title("⚙️ QIANDU 团队控制中心 (管理版)")
        t1, t2 = st.tabs(["🆕 待审准入", "👥 实时战力排行"])
        
        with t1:
            pnd = load_data("pending")
            if not pnd: st.info("目前没有待审核的账号申请")
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 **申请人:** {u} (时间: {info['time']})")
                if c2.button("✅ 批准入职", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd)
                    add_mission_log("Founder", "批准通过", u, 5); st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()
        
        with t2:
            st.subheader("🔥 员工战力贡献榜")
            logs = load_data("logs")
            if logs:
                ldf = pd.DataFrame(logs)
                # 使用战力贡献分累计进行图表展示
                ldf['战力贡献'] = pd.to_numeric(ldf['战力贡献'], errors='coerce').fillna(0)
                stats = ldf.groupby("操作员")["战力贡献"].sum().sort_values(ascending=False)
                st.bar_chart(stats)
            
            st.divider()
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 在职员工: {u}")
                if c2.button("🚫 撤销权限", key=f"d_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 行动审计日志":
        st.title("📜 全球行动审计日志 (V75 高精度版)")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            # 风险高亮处理
            def highlight_risk(val):
                color = 'red' if '🚨' in str(val) else 'white'
                return f'color: {color}'
            st.dataframe(ldf.style.applymap(highlight_risk, subset=['安全评级']), use_container_width=True)

    if st.sidebar.button("安全退出系统"):
        st.session_state.clear(); st.rerun()
