import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- 1. 数据持久化 ---
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

def add_log(user, action, detail):
    logs = load_data("logs")
    logs.insert(0, {"时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "动作": action, "详情": detail})
    save_data("logs", logs[:1000])

# --- 2. 增强版 AI 与 通讯适配 V9.0 ---
def get_country_and_tool(phone):
    p = str(phone).strip()
    # 越南
    if p.startswith('84') or p.startswith('0'):
        clean_p = p[1:] if p.startswith('0') else p[2:] if p.startswith('84') else p
        return "Vietnam", f"https://zalo.me/84{clean_p}", "Zalo"
    # 印尼
    if p.startswith('62'):
        return "Indonesia", f"https://wa.me/{p}", "WhatsApp"
    # 韩国
    if p.startswith('82'):
        return "Korea", f"https://line.me/R/ti/p/~{p}", "Line/Kakao"
    return "Global", f"https://wa.me/{p}", "WhatsApp"

def advanced_ai_analysis(name, addr):
    ctx = (str(name) + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "批发", "贸易", "grosir"])
    
    category = "💄 综合美妆"
    if any(k in ctx for k in ["skin", "spa", "care", "da", "derma"]): category = "🧴 护肤医美"
    elif any(k in ctx for k in ["baby", "mom", "mẹ", "bé"]): category = "🍼 母婴用品"
    elif any(k in ctx for k in ["pharmacy", "nhà thuốc", "health"]): category = "💊 药妆渠道"
    
    identity = "🚀 大宗批发商" if is_ws else "🏪 零售门店"
    return identity, category

# --- 3. 页面配置 ---
st.set_page_config(page_title="QIANDU Global V9.0", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🏢 QIANDU 全球企业管理系统 V9.0")
    access = st.radio("入口选择", ["员工通道", "指挥官通道"], horizontal=True)
    
    if access == "指挥官通道":
        pwd = st.text_input("指挥官密钥", type="password")
        if st.button("进入指挥部"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
            else: st.error("密钥错误")
    else:
        tab1, tab2 = st.tabs(["🔐 登录", "📝 申请"])
        with tab1:
            u, p = st.text_input("账号"), st.text_input("密码", type="password")
            if st.button("登录系统"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_log(u, "登录", "进入系统")
                    st.rerun()
                else: st.error("登录失败")
        with tab2:
            nu, np = st.text_input("新账号"), st.text_input("密码", type="password")
            if st.button("提交"):
                pnd = load_data("pending")
                pnd[nu] = {"pwd": np, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd)
                st.success("申请已提交")
else:
    # --- 4. 内部指挥系统 ---
    st.sidebar.title(f"在线: {st.session_state.user}")
    menu = ["📊 业务情报", "⚙️ 员工管理", "📜 日志审计"] if st.session_state.role == "boss" else ["📊 业务情报"]
    nav = st.sidebar.radio("菜单", menu)

    if nav == "📊 业务情报":
        st.title("📊 智能情报矩阵 (多国适配版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')

            q = st.text_input("🔍 全局搜索 (支持店名/地址/品类/国家)")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_log(st.session_state.user, "搜索", f"关键词: {q}")

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, addr, phone = str(row[c_n]), str(row[c_a]), str(row[c_p])
                ident, cate = advanced_ai_analysis(name, addr)
                country, chat_link, tool_name = get_country_and_tool(phone)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.write(f"🚩 国家: **{country}**")
                            st.write(f"📞 `{phone}`")
                            st.link_button(f"💬 通过 {tool_name} 联系", chat_link, type="primary", use_container_width=True)
                            st.caption(f"📍 {addr}")
                        
                        with col2:
                            color = "blue" if "批发" in ident else "green"
                            st.markdown(f":{color}[**{ident}**] | {cate}")
                            
                            st.write("🌐 **社媒快速核查:**")
                            # 社媒搜索逻辑：自动携带店名搜索
                            encoded_name = json.loads(json.dumps(name)) # 简单编码
                            s_col1, s_col2, s_col3 = st.columns(3)
                            s_col1.link_button("FB", f"https://www.facebook.com/search/top/?q={encoded_name}")
                            s_col2.link_button("Ins", f"https://www.instagram.com/explore/tags/{encoded_name.replace(' ','')}/")
                            s_col3.link_button("TK", f"https://www.tiktok.com/search?q={encoded_name}")
                            
                            st.info(f"AI 建议: { '重点谈价格' if '批发' in ident else '推潮流新品' }")

    elif nav == "⚙️ 员工管理":
        st.title("⚙️ 员工权限中心")
        t_app, t_man = st.tabs(["🆕 待审核申请", "👥 现有员工"])
        with t_app:
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"申请人: {u}")
                if c2.button("批准", key=f"app_{u}"):
                    users = load_data("users")
                    users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd)
                    add_log("Founder", "审核", f"通过 {u}")
                    st.rerun()
        with t_man:
            users = load_data("users")
            for u in list(users.keys()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u}")
                if c2.button("注销离职", key=f"del_{u}"):
                    del users[u]; save_data("users", users)
                    add_log("Founder", "注销", f"员工 {u} 离职")
                    st.rerun()

    elif nav == "📜 日志审计":
        st.title("📜 全球操作日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
