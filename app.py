import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 时区与多维审计引擎 ---
def get_local_time():
    # 适配您的出差路线：越南/印尼/韩国。统一使用 ICT (UTC+7)
    return datetime.utcnow() + timedelta(hours=7)

DB_FILES = {"users": "users_data.json", "pending": "pending.json", "logs": "op_logs.json"}

def load_data(key):
    try:
        if os.path.exists(DB_FILES[key]):
            with open(DB_FILES[key], "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return {} if key != "logs" else []

def save_data(key, data):
    with open(DB_FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_mission_log(user, action, target="-", depth=1):
    logs = load_data("logs")
    logs.insert(0, {
        "时间": get_local_time().strftime("%Y-%m-%d %H:%M"),
        "指挥官": user,
        "行动": action,
        "目标商户": target,
        "战力贡献": depth # 记录操作深度分数
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU AI 决策大脑 V19.0 (多语话术适配) ---
def qiandu_ai_v19(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # 识别核心画像
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "warehouse", "批发"])
    is_spa = any(k in ctx for k in ["spa", "skin", "da", "clinic", "pharmacy"])
    
    if is_ws:
        role, score = "🏛️ 核心批发大户", 95
        script = "【越语话术】Chào anh/chị, em từ QIANDU Hàn Quốc. Bên em chuyên đổ sỉ Jmella/SNP giá gốc container..."
        strategy = "重点谈：韩国直发、价格对标、SKU稳定。"
    elif is_spa:
        role, score = "🏥 专业医美院线", 80
        script = "【越语话术】Chào chị, em có dòng mặt nạ Leaders/SNP chuyên dụng cho Spa, phục hồi da sau liệu trình..."
        strategy = "重点谈：成分安全、高回购、医美背书。"
    else:
        role, score = "🏪 潮流零售/代购", 60
        script = "【越语话术】Chào bạn, shop mình có muốn nhập mẫu meloMELI mới nhất về thu hút khách không?..."
        strategy = "重点谈：小样支持、爆款引流、一件代发。"

    return role, score, strategy, script

# --- 3. 全球通讯协议 ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    
    if nums.startswith('66'): return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{nums[2:]}", "Line"
    if nums.startswith('81'): return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V19", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥中心 V19.0")
    acc = st.radio("系统入口", ["员工通道", "指挥官入口"], horizontal=True, key="acc19")
    if acc == "指挥官入口":
        pwd = st.text_input("指挥官密钥", type="password", key="bp19")
        if st.button("激活权限", key="bb19"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui19"), st.text_input("密码", type="password", key="pi19")
            if st.button("进入系统", key="bi19"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统", "-", 1)
                    st.rerun()
        with t2:
            nu, np = st.text_input("申请账号", key="nu19"), st.text_input("申请密码", type="password", key="np19")
            if st.button("提交申请", key="rb19"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请成功")

else:
    # --- 5. 内部系统 ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队战力管理", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("指挥系统", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 情报决策矩阵 (V19 - 话术增强)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、品类、地段关键词 (一键匹配 AI 话术)", key="sq19")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索情报", q, 2)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI V19 深度画像
                role, score, strategy, script = qiandu_ai_v19(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系 ({tool})", name, 10)
                            st.link_button("📍 地图视觉调研", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **身份:** {role} (价值: {score})")
                            st.info(f"💡 **AI 建议策略:**\n{strategy}")
                            with st.expander("📝 查看/复制开发信模板"):
                                st.code(script, language="markdown")
                        
                        st.write("🌐 **跨平台背景核查:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队战力管理":
        st.title("⚙️ QIANDU HR 指挥中心")
        t1, t2 = st.tabs(["待审名单", "员工战力排行"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 申请: {u}")
                if c2.button("批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            st.subheader("员工本月开发力度统计")
            logs = load_data("logs")
            log_df = pd.DataFrame(logs)
            if not log_df.empty:
                stats = log_df.groupby("指挥官")["战力贡献"].sum().sort_values(ascending=False)
                st.bar_chart(stats)
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"注销员工 {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度审计日志":
        st.title("📜 全球行动审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 退出"):
        st.session_state.clear(); st.rerun()
