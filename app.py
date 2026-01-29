import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- 1. 核心数据库逻辑 ---
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

# --- 2. 增强版 AI 智能分析引擎 V8.0 ---
def advanced_ai_analysis(name, addr):
    ctx = (str(name) + str(addr)).lower()
    
    # A. 身份与品类判定
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "批发", "贸易"])
    
    category = "💄 综合美妆"
    if any(k in ctx for k in ["skin", "spa", "care", "da", "derma"]): category = "🧴 专业护肤/医美"
    elif any(k in ctx for k in ["baby", "mom", "mẹ", "bé"]): category = "🍼 母婴用品"
    elif any(k in ctx for k in ["pharmacy", "nhà thuốc", "health"]): category = "💊 药妆渠道"
    elif any(k in ctx for k in ["perfume", "nước hoa"]): category = "✨ 香水香氛"

    # B. 经营建议
    if is_ws:
        identity = "🚀 大宗批发商"
        strategy = "重点推 Jmella 货柜政策，SNP 批量报价。"
    else:
        identity = "🏪 零售门店"
        strategy = "推 meloMELI 潮流单品，利用小样引流。"
        
    return identity, category, strategy

# --- 3. 页面配置 ---
st.set_page_config(page_title="QIANDU Enterprise V8", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🏢 QIANDU 全球企业管理系统 V8.0")
    access = st.radio("入口选择", ["员工通道", "指挥官通道"], horizontal=True)
    
    if access == "指挥官通道":
        pwd = st.text_input("指挥官密钥", type="password")
        if st.button("进入指挥部"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
            else: st.error("密钥错误")
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号"), st.text_input("密码", type="password")
            if st.button("登录系统"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p and users[u].get("status") == "active":
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_log(u, "登录", "进入系统")
                    st.rerun()
                else: st.error("账号未激活或密码错误")
        with t2:
            nu, np = st.text_input("新账号"), st.text_input("设置密码", type="password")
            if st.button("提交"):
                pnd = load_data("pending")
                pnd[nu] = {"pwd": np, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd)
                st.success("申请已外发，等待指挥官审批")

else:
    # --- 4. 内部指挥系统 ---
    st.sidebar.title(f"在线: {st.session_state.user}")
    menu = ["📊 业务情报", "⚙️ 员工管理", "📜 日志审计"] if st.session_state.role == "boss" else ["📊 业务情报"]
    nav = st.sidebar.radio("菜单", menu)

    # A. 业务情报 (含 AI 增强搜索)
    if nav == "📊 业务情报":
        st.title("📊 智能情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')

            q = st.text_input("🔍 全局搜索 (支持店名/地址/品类关键词)")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_log(st.session_state.user, "搜索", f"关键词: {q}")

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, addr, phone = str(row[c_n]), str(row[c_a]), str(row[c_p])
                ident, cate, strat = advanced_ai_analysis(name, addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            st.write(f"📞 `{phone}`")
                            st.caption(f"📍 {addr}")
                            raw_p = "".join(filter(str.isdigit, phone))
                            z_p = "84" + raw_p[1:] if raw_p.startswith('0') else raw_p
                            st.link_button("🔵 Zalo 洽谈", f"https://zalo.me/{z_p}", use_container_width=True)
                        with c2:
                            color = "blue" if "批发" in ident else "green"
                            st.markdown(f":{color}[**{ident}**]")
                            st.markdown(f"**品类:** {cate}")
                            st.info(f"💡 {strat}")

    # B. 员工管理 (入职、离职、审核)
    elif nav == "⚙️ 员工管理":
        st.title("⚙️ 企业人力资源控制台")
        t_app, t_man = st.tabs(["🆕 待审核申请", "👥 现有员工名单"])
        
        with t_app:
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"申请人: {u} (时间: {info['time']})")
                if col2.button("批准入职", key=f"app_{u}"):
                    users = load_data("users")
                    users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users)
                    del pnd[u]
                    save_data("pending", pnd)
                    add_log("Founder", "审核", f"批准员工 {u} 入职")
                    st.rerun()

        with t_man:
            users = load_data("users")
            for u, info in list(users.items()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 员工账号: {u}")
                if col2.button("🚫 办理离职", key=f"del_{u}"):
                    del users[u]
                    save_data("users", users)
                    add_log("Founder", "离职", f"注销员工 {u} 账号")
                    st.rerun()

    # C. 全面日志审计
    elif nav == "📜 日志审计":
        st.title("📜 全球操作实时监控")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear()
        st.rerun()
