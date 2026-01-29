import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心底座：数据安全与时区 ---
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
    # 风控：检测 1 秒内重复点击
    if logs and logs[0]['操作员'] == user:
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1.0:
            risk = "🚨 频率异常"; score = -50
    logs.insert(0, {"时间": current_time.strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "动作": action, "目标": target, "战力分": score, "状态": risk})
    save_data("logs", logs[:5000])

# --- 2. 核心算法：AI 战略画像与脱敏 ---
def mask_phone(phone_raw, role):
    raw = re.sub(r'\D', '', str(phone_raw))
    if role == "boss": return raw 
    return f"{raw[:3]}****{raw[-4:]}" if len(raw) > 7 else "****"

def qiandu_ai_v100(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发", "warehouse"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat"])
    is_med = any(k in ctx for k in ["spa", "clinic", "pharmacy", "nhà thuốc", "med", "derma"])

    if is_ws:
        return "🏗️ 批发巨头", "谈货柜锁价，推 Jmella/SNP。", "Chào bạn, bên mình sỉ container giá gốc Hàn..."
    if is_med:
        return "🏥 医美院线", "谈 Leaders 修复报告。不打价格战。", "Chào chị, bên em có dòng Leaders phục hồi da chuyên sâu..."
    if is_prime:
        return "💎 核心旗舰", "谈 meloMELI 颜值引流，对冲地租。", "Shop ở vị trí đẹp nhập meloMELI sẽ tăng khách check-in..."
    return "🏪 常规零售", "谈补货快、一件起批。", "Bên mình có sẵn hàng hot nhất, giao ngay..."

# --- 3. 全球路由系统 ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if nums.startswith('7') or nums.startswith('971') or "moscow" in ctx:
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or "vietnam" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if any(nums.startswith(x) for x in ['81','66','82']) or any(k in ctx for k in ["japan", "thailand"]):
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 4. 界面逻辑：双向导视验证网关 ---
st.set_page_config(page_title="QIANDU COMMAND V100", layout="wide")

if "auth_ok" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🛡️ QIANDU 全球指挥终端 V100.0</h1>", unsafe_allow_html=True)
    
    # 顶部身份选择器
    role_tab = st.radio("请选择访问通道：", ["👤 员工入口", "🛰️ 指挥官中心"], horizontal=True, label_visibility="collapsed")
    
    if role_tab == "🛰️ 指挥官中心":
        with st.container(border=True):
            st.subheader("创始人最高权限验证")
            boss_pwd = st.text_input("请输入密钥", type="password", key="boss_key")
            if st.button("激活权限", use_container_width=True):
                if boss_pwd == "666888":
                    st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                    st.rerun()
                else: st.error("密钥错误")
    
    else:
        # 核心修复：在这里提供 登录/申请 的明确入口
        tab_login, tab_reg = st.tabs(["🔐 员工登录", "📝 新账号申请"])
        
        with tab_login:
            u = st.text_input("账号", key="login_u")
            p = st.text_input("密码", type="password", key="login_p")
            if st.button("进入系统", use_container_width=True, key="login_btn"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统", score=0)
                    st.rerun()
                else: st.error("登录失败：需等待批准或账号密码有误")
        
        with tab_reg:
            st.info("入职申请提交后，请联系指挥官（Founder）在管理后台手动批准。")
            nu = st.text_input("拟申请账号名", key="reg_u")
            np = st.text_input("拟设置密码", type="password", key="reg_p")
            if st.button("提交申请", use_container_width=True, key="reg_btn"):
                pnd = load_data("pending")
                pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd)
                st.success(f"申请已提交！账号名：{nu}。请等待审核。")

else:
    # --- 5. 内部情报决策矩阵 ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    if st.session_state.role == "boss":
        st.sidebar.divider()
        pnd_count = len(load_data("pending"))
        if pnd_count > 0: st.sidebar.warning(f"🔔 有 {pnd_count} 个新申请待审核")
    
    menu = ["📊 情报矩阵", "⚙️ 团队战力", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度商业情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            # 列映射
            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols, index=0), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=2)
            
            q = st.text_input("🔎 搜店名、地址、商圈词")
            if q: df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2); remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI、脱敏、路由
                role, suggest, script = qiandu_ai_v100(name, addr)
                d_phone = mask_phone(phone, st.session_state.role)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        cl1, cl2 = st.columns([1, 1.3])
                        with cl1:
                            st.write(f"🌍 区域: **{country}**")
                            st.write(f"📞 号码: `{d_phone}`")
                            st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True)
                            if st.button(f"📑 记入战力-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, f"发起联系({tool})", name, 10)
                        with cl2:
                            st.write(f"🏢 画像: **{role}**")
                            st.info(f"💡 AI策略: {suggest}")
                            with st.expander("📝 破冰话术"): st.code(script, language="markdown")
                        
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True)
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True)

                        # 备注
                        st.divider()
                        rem = remarks.get(name, {"text": "暂无进展", "user": "-", "time": "-"})
                        st.success(f"最新进展: {rem['text']} ({rem['user']})")
                        n_note = st.text_input("更新跟进进展", key=f"ni_{idx}")
                        if st.button("保存备注", key=f"nb_{idx}"):
                            if n_note:
                                remarks[name] = {"text": n_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队战力":
        st.title("⚙️ 团队实战看板")
        # 战力图
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            ldf['战力分'] = pd.to_numeric(ldf['战力分'], errors='coerce').fillna(0)
            st.bar_chart(ldf.groupby("操作员")["战力分"].sum().sort_values(ascending=False))
        # 审核
        st.divider(); pnd = load_data("pending")
        for u, info in list(pnd.items()):
            c1, c2 = st.columns([3, 1])
            c1.write(f"👤 {u} (申请时间: {info['time']})")
            if c2.button("批准准入", key=f"y_{u}"):
                users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 深度行动日志")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            def risk_color(x): return 'background-color: #ff4b4b; color: white' if "🚨" in str(x) else ''
            st.dataframe(ldf.style.applymap(risk_color, subset=['状态']), use_container_width=True)

    if st.sidebar.button("🚪 安全退出系统"): st.session_state.clear(); st.rerun()
