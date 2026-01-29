import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 数据持久化与安全审计引擎 ---
def get_local_time():
    # 适配越南、印尼时区 (UTC+7)
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
    """
    集成异常监控逻辑：
    depth=1: 常规查阅
    depth=10: 核心资产联络
    """
    logs = load_data("logs")
    current_time = get_local_time()
    
    # 异常行为检测 (防爬虫/防刷数据)
    risk_tag = "✅ 正常"
    if len(logs) > 0:
        last_log_time = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
        if (current_time - last_log_time).total_seconds() < 1.2:
            risk_tag = "🔴 异常高频"

    log_entry = {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令动作": action,
        "关联目标": target,
        "情报深度": "💎 核心资产访问" if depth >= 10 else "📄 基础查阅",
        "安全状态": risk_tag
    }
    logs.insert(0, log_entry)
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全球通讯路由 (精准适配) ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 优先识别 Telegram
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    
    # 国别识别
    if nums.startswith('66'): return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{nums[2:]}", "Line"
    if nums.startswith('81'): return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    if nums.startswith('82'): return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{nums[2:]}", "Line"
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 3. QIANDU AI 深度大脑 (一店一策) ---
def qiandu_ai_logic(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "warehouse", "批发", "grosir"])
    is_spa = any(k in ctx for k in ["spa", "skin", "da", "clinic", "pharmacy", "nhà thuốc"])
    
    if is_ws:
        return "🏛️ 核心批发巨头", "【批发战术】: 谈货柜价格与返点，推 Jmella/SNP。", "Chào anh, bên em chuyên đổ sỉ Jmella/SNP giá gốc Hàn Quốc..."
    elif is_spa:
        return "🏥 专业医美渠道", "【专业战术】: 谈成分与修护，推 Leaders 针剂面膜。", "Chào chị, em có dòng mặt nạ Leaders chuyên dụng cho Spa..."
    else:
        return "🏪 潮流零售/代购", "【引流战术】: 谈爆款与小样，推 meloMELI 新品。", "Chào bạn, mẫu meloMELI mới này đang rất hot, shop có muốn thử không?..."

# --- 4. 界面展示 ---
st.set_page_config(page_title="QIANDU BI V20", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥部 V20.0")
    acc = st.radio("通道选择", ["员工登录", "指挥官进入"], horizontal=True, key="acc_v20")
    if acc == "指挥官进入":
        pwd = st.text_input("指挥官密钥", type="password", key="boss_v20")
        if st.button("激活权限", key="btn_v20"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="u_v20"), st.text_input("密码", type="password", key="p_v20")
            if st.button("进入系统", key="bin_v20"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "系统登录", "-", 1)
                    st.rerun()
        with t2:
            nu, np = st.text_input("申请账号", key="nu_v20"), st.text_input("密码", type="password", key="np_v20")
            if st.button("提交申请", key="rb_v20"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请成功")

else:
    # --- 5. 内部系统 ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队战力管理", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("指挥中心导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度商业情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、商圈或品类 (AI 自动匹配战术)", key="sq_v20")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索情报", q, 2)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 画像
                role, strategy, script = qiandu_ai_logic(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系商户 ({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.info(f"💡 **AI 建议策略:**\n{strategy}")
                            with st.expander("📝 话术模板"):
                                st.code(script, language="markdown")
                        
                        st.write("🌐 **社媒影响力核查:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队战力管理":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["待审名单", "员工战力排行"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u}")
                if c2.button("批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            st.subheader("本月开发战力贡献榜")
            logs = load_data("logs")
            if logs:
                log_df = pd.DataFrame(logs)
                stats = log_df.groupby("操作员")["指令动作"].count().sort_values(ascending=False)
                st.bar_chart(stats)
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"注销权限 {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度审计日志":
        st.title("📜 全球行动深度审计")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
