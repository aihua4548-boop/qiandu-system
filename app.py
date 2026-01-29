import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime

# --- 1. 数据持久化与日志升级 ---
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

def add_smart_log(user, action, target="-", score=0):
    logs = load_data("logs")
    logs.insert(0, {
        "时间": datetime.now().strftime("%m-%d %H:%M"),
        "操作员": user,
        "动作": action,
        "对象": target,
        "动作权重": score # 1-查看，5-联络，10-调研
    })
    save_data("logs", logs[:1500])

# --- 2. QIANDU AI 深度大脑 V15.0 (打分模型) ---
def qiandu_brain_v15(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    score = 0
    
    # A. 身份识别分
    if any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "grosir", "distributor", "批发", "贸易"]): score += 50
    if any(k in ctx for k in ["pharmacy", "nhà thuốc", "drugstore", "clinic", "spa", "da", "skin"]): score += 30
    if any(k in ctx for k in ["mall", "plaza", "center", "lotte", "aeon"]): score += 20
    
    # B. 地段加成
    if any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat"]): score += 15

    # C. 千店千策输出
    if score >= 65:
        identity = "🚀 顶级批发巨头"
        category = "📦 供应链型 (B2B)"
        strategy = "【价格战策略】: 话术重点在于‘千渡一手货源’、‘价格对标韩网’、‘稳定柜货’。建议推 Jmella 全系列和 SNP 大包装。"
    elif 40 <= score < 65:
        identity = "🏥 优质专业渠道"
        category = "🧴 护肤/药妆 (Specially)"
        strategy = "【资质战策略】: 话术重点在于‘医美背书’、‘资质齐全’、‘高毛利回购’。建议推 Leaders/SNP 医美级面膜。"
    elif 20 <= score < 40:
        identity = "💎 高端时尚零售"
        category = "💄 彩妆/潮流 (Retail)"
        strategy = "【颜值战策略】: 话术重点在于‘meloMELI 独家形象柜’、‘ins爆款’、‘柜台支持’。建议推 meloMELI 和最新联名款。"
    else:
        identity = "🏪 社区常规美妆"
        category = "👜 杂货/日化"
        strategy = "【爆款战策略】: 话术重点在于‘低门槛起批’、‘代发货’、‘一件代发’。建议推当月最火爆的散单产品。"

    return identity, category, strategy, score

# --- 3. 全球通讯路由 (泰国、日本、越南、印尼、韩国、电报) ---
def get_global_contact(phone, name_addr):
    nums = re.sub(r'\D', '', str(phone))
    ctx = str(name_addr).lower()
    
    # 强制优先：Telegram
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    
    # 泰国/日本/韩国/越南/印尼 适配
    if nums.startswith('66'): return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{nums[2:]}", "Line"
    if nums.startswith('81'): return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    if nums.startswith('82'): return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{nums[2:]}", "Line"
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('09')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V15", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥部 V15.0")
    access = st.radio("系统通道", ["员工通道", "指挥官专属"], horizontal=True, key="acc")
    if access == "指挥官专属":
        pwd = st.text_input("密钥", type="password", key="bp")
        if st.button("激活权限", key="bb"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui"), st.text_input("密码", type="password", key="pi")
            if st.button("进入系统", key="bi"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_smart_log(u, "成功登录")
                    st.rerun()
        with t2:
            nu, np = st.text_input("新账号", key="ru"), st.text_input("设置密码", type="password", key="rp")
            if st.button("提交申请", key="rb"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": datetime.now().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请成功")

else:
    # --- 5. 内部主系统 ---
    st.sidebar.title(f"👤 状态: {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 权限管理", "📜 深度日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度商业情报 (千店千策版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、品类、地段（如：第一郡、Wholesale）", key="sq")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_smart_log(st.session_state.user, "执行搜索", q, 1)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                ident, cat, strategy, score = qiandu_brain_v15(name, addr)
                country, chat_link, tool = get_global_contact(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 谈单", chat_link, type="primary", use_container_width=True):
                                add_smart_log(st.session_state.user, "点击联络", name, 5)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            st.caption(f"📞 号码: {phone}")
                        with col2:
                            st.write(f"🏢 **画像:** {ident}")
                            st.write(f"📦 **品类:** {cat}")
                            st.write(f"🔥 **价值分:** {score}")
                            st.info(f"💡 **AI 策略:**\n{strategy}")
                        
                        st.write("🌐 **社媒影响力核查:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TikTok", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 权限管理":
        st.title("⚙️ 团队管理中心")
        t1, t2 = st.tabs(["入职审核", "在职管理"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u}")
                if c2.button("批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u}")
                if c2.button("注销离职", key=f"n_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度日志":
        st.title("📜 商业行为审计")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
