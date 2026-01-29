import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心架构：时区与数据安全 ---
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
    # 频率风控
    if logs and logs[0].get('操作员') == user:
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1.0:
            risk = "🚨 频率异常"; score = -50
    # 统一字段名：战力分
    logs.insert(0, {"时间": current_time.strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "动作": action, "目标": target, "战力分": score, "状态": risk})
    save_data("logs", logs[:5000])

# --- 2. 隐私保护：号码脱敏 ---
def mask_phone(phone_raw, role):
    raw = re.sub(r'\D', '', str(phone_raw))
    if role == "boss": return raw 
    return f"{raw[:3]}****{raw[-4:]}" if len(raw) > 7 else "****"

# --- 3. QIANDU 究极 AI 大脑 (三维博弈) ---
def qiandu_ai_v125(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发", "warehouse"])
    is_med = any(k in ctx for k in ["spa", "clinic", "pharmacy", "med"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit"])

    if is_ws:
        return "🏗️ 流通巨头", "谈货柜锁价、展示一手货源。推 Jmella/SNP。", "Chào bạn, QIANDU sẵn container giá gốc Hàn Quốc..."
    if is_med:
        return "🏥 专业医美", "谈 Leaders 修复背书。避开价格战，谈毛利保护。", "Chào chị, bên em chuyên Leaders Clinic cho Spa..."
    if is_prime:
        return "💎 核心店", "地租贵，谈 meloMELI 颜值引流支持。对冲固定成本。", "Shop ở vị trí đẹp nhập meloMELI sẽ cực hút khách..."
    return "🏪 零售终端", "谈‘一件起批’、‘补货快’。推爆款面膜。", "Bên mình có sẵn mẫu hot, giao ngay trong ngày..."

# --- 4. 全球路由系统 ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if nums.startswith('7') or nums.startswith('971') or "moscow" in ctx:
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or "vietnam" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if any(nums.startswith(x) for x in ['81','66','82']) or "japan" in ctx:
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 5. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V125", layout="wide")

if "auth_ok" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🛡️ QIANDU 全球智慧指挥终端 V125</h1>", unsafe_allow_html=True)
    role_tab = st.radio("访问通道", ["👤 员工入口", "🛰️ 指挥官中心"], horizontal=True, label_visibility="collapsed")
    if role_tab == "🛰️ 指挥官中心":
        pwd = st.text_input("创始人密钥", type="password", key="boss_pwd")
        if st.button("激活权限", use_container_width=True):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"}); st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 新账号申请"])
        with t1:
            u, p = st.text_input("账号", key="l_u"), st.text_input("密码", type="password", key="l_p")
            if st.button("进入系统", use_container_width=True):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"}); add_mission_log(u, "登录"); st.rerun()
        with t2:
            nu, np = st.text_input("拟申请账号", key="r_u"), st.text_input("设置密码", type="password", key="r_p")
            if st.button("提交入职申请", use_container_width=True):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功，请联系指挥官审核。")
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队管理", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度商业情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            st.sidebar.divider(); cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols, index=0), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=2)
            
            q = st.text_input("🔎 搜店名、地址、商圈词")
            if q: df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2); remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                role, suggest, script = qiandu_ai_v125(name, addr)
                d_phone = mask_phone(phone, st.session_state.role)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        cl1, cl2 = st.columns([1, 1.4])
                        with cl1:
                            st.write(f"🌍 区域: **{country}**")
                            st.write(f"📞 号码: `{d_phone}`")
                            st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True)
                            if st.button(f"📑 记入战力-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                        with cl2:
                            st.write(f"🏢 画像: **{role}**")
                            st.info(f"💡 建议: {suggest}")
                            with st.expander("📝 破冰话术"): st.code(script, language="markdown")
                        
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True)
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True)

                        st.divider(); rem = remarks.get(name, {"text": "暂无记录", "user": "-", "time": "-"})
                        st.success(f"备注: {rem['text']} ({rem['user']})")
                        n_note = st.text_input("更新跟进进展", key=f"ni_{idx}")
                        if st.button("保存备注", key=f"nb_{idx}"):
                            if n_note:
                                remarks[name] = {"text": n_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队管理":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["🆕 待审准入", "👥 战力看板"])
        with t1:
            pnd = load_data("pending")
            if not pnd:
                st.info("目前没有待处理的入职申请。")
            else:
                for u, info in list(pnd.items()):
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        c1.write(f"👤 **申请账号:** {u}\n\n⏰ **申请时间:** {info['time']}")
                        if c2.button("✅ 批准入职", key=f"y_{u}"):
                            users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                            save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()

        with t2:
            ldf = pd.DataFrame(load_data("logs"))
            if not ldf.empty:
                # 兼容性修复：动态查找战力相关列
                score_col = next((c for c in ldf.columns if "战力" in c), None)
                if score_col:
                    ldf[score_col] = pd.to_numeric(ldf[score_col], errors='coerce').fillna(0)
                    st.bar_chart(ldf.groupby("操作员")[score_col].sum().sort_values(ascending=False))
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"🚫 注销权限: {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 审计日志":
        st.title("📜 行动审计日志")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            status_col = next((c for c in ldf.columns if "状态" in c or "风险" in c), None)
            if status_col:
                st.dataframe(ldf.style.applymap(lambda x: 'background-color: #ff4b4b; color: white' if "🚨" in str(x) else '', subset=[status_col]), use_container_width=True)
            else: st.dataframe(ldf, use_container_width=True)

    if st.sidebar.button("安全退出系统"): st.session_state.clear(); st.rerun()
