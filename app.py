import streamlit as st
import pandas as pd
import os
import json
import uuid
import urllib.parse
from datetime import datetime

# --- 1. 数据持久化逻辑 (模拟数据库) ---
# 实际生产环境建议对接数据库，这里使用 local session 模拟
def init_storage():
    if 'users' not in st.session_state:
        st.session_state.users = {"admin": {"pwd": "666888", "role": "boss", "status": "active"}}
    if 'pending_users' not in st.session_state:
        st.session_state.pending_users = {}
    if 'logs' not in st.session_state:
        st.session_state.logs = []

def add_log(user, action, detail):
    log_entry = {
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "动作": action,
        "详情": detail
    }
    st.session_state.logs.insert(0, log_entry)

# --- 2. 强化 AI 智能分析逻辑 (V4.0) ---
def enhanced_ai_analysis(name, addr, phone):
    ctx = (str(name) + str(addr)).lower()
    
    # 规模判定
    if any(k in ctx for k in ["wholesale", "distributor", "tổng kho", "sỉ", "опт"]):
        level = "🚀 核心批发商 (一级)"
        strategy = "Jmella 货柜级报价 + 独家区域保护"
    elif any(k in ctx for k in ["mall", "center", "plaza", "myeongdong"]):
        level = "💎 高端零售/旗舰店"
        strategy = "meloMELI 形象柜进驻 + 派样活动"
    else:
        level = "🏪 普通门店/美妆店"
        strategy = "散单拿货 + 满减活动"

    # 风险预警
    risk = "✅ 信用良好" if "district 1" in ctx or "hcm" in ctx else "⚠️ 偏远区域需确认物流"
    
    return level, strategy, risk

# --- 3. 页面配置 ---
st.set_page_config(page_title="QIANDU Enterprise Control", layout="wide", page_icon="🏢")
init_storage()

# --- 4. 登录与注册模块 ---
if "auth_ok" not in st.session_state:
    st.title("🏢 QIANDU 全球指挥终端 - 企业内控版")
    tab1, tab2 = st.tabs(["🔐 员工登录", "📝 新员工注册"])
    
    with tab1:
        with st.form("login"):
            u = st.text_input("账号")
            p = st.text_input("密码", type="password")
            if st.form_submit_button("验证进入"):
                if u in st.session_state.users and st.session_state.users[u]["pwd"] == p:
                    if st.session_state.users[u]["status"] == "active":
                        st.session_state.auth_ok = True
                        st.session_state.current_user = u
                        st.session_state.user_role = st.session_state.users[u]["role"]
                        add_log(u, "登录", "成功进入系统")
                        st.rerun()
                    else:
                        st.error("❌ 账号待审核或已停用，请联系创始人")
                else:
                    st.error("❌ 账号或密码错误")

    with tab2:
        with st.form("register"):
            new_u = st.text_input("申请账号(建议英文名)")
            new_p = st.text_input("设置密码", type="password")
            real_name = st.text_input("真实姓名")
            if st.form_submit_button("提交注册申请"):
                if new_u in st.session_state.users or new_u in st.session_state.pending_users:
                    st.warning("⚠️ 该账号已存在")
                else:
                    st.session_state.pending_users[new_u] = {"pwd": new_p, "name": real_name}
                    st.success("✅ 申请已提交！请等待创始人后台审核。")

else:
    # --- 5. 内部主系统 ---
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    st.sidebar.caption(f"权限角色: {st.session_state.user_role}")
    
    menu = ["📊 实战情报中心", "🔍 全域深度搜索"]
    if st.session_state.user_role == "boss":
        menu += ["⚙️ 后台审核", "📜 操作日志"]
    
    nav = st.sidebar.radio("指挥系统导航", menu)

    # --- 菜单 1: 实战情报中心 ---
    if nav == "📊 实战情报中心":
        st.title("📊 实时商户情报矩阵")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("📂 选择同步数据集", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            
            # 搜索功能
            search_q = st.text_input("🔎 在此数据集内搜索 (输入店名、电话或地址关键字)")
            if search_q:
                df = df[df.apply(lambda row: search_q.lower() in row.astype(str).str.lower().values, axis=1)]
                add_log(st.session_state.current_user, "搜索", f"关键词: {search_q}")

            st.write(f"当前共显示 {len(df)} 条情报")
            
            # ... 此处保留原有的卡片展示逻辑，调用 enhanced_ai_analysis ...
            cols = list(df.columns)
            c_name = st.sidebar.selectbox("店名列", cols, index=0)
            c_phone = st.sidebar.selectbox("电话列", cols, index=min(1, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone = str(row[c_name]), str(row[c_phone])
                level, strategy, risk = enhanced_ai_analysis(name, row.get('Address',''), phone)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.subheader(f"🏬 {name}")
                        st.write(f"📞 电话: `{phone}`")
                        st.markdown(f"**AI 能级:** {level}")
                        st.info(f"💡 **AI 策略:** {strategy}\n\n🚩 **风险:** {risk}")
                        if st.button(f"查看详情 - {idx}"):
                            add_log(st.session_state.current_user, "查看详情", f"查看了商户: {name}")

    # --- 菜单 2: 后台审核 (仅 Boss 可见) ---
    elif nav == "⚙️ 后台审核":
        st.title("⚙️ 员工准入审批中心")
        if not st.session_state.pending_users:
            st.info("目前没有待审核的注册申请")
        else:
            for u, info in list(st.session_state.pending_users.items()):
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 **{info['name']}** (账号: {u})")
                if col2.button("✅ 通过", key=f"app_{u}"):
                    st.session_state.users[u] = {"pwd": info['pwd'], "role": "staff", "status": "active"}
                    del st.session_state.pending_users[u]
                    add_log("admin", "审核通过", f"通过了员工 {u} 的注册")
                    st.rerun()
                if col3.button("❌ 拒绝", key=f"rej_{u}"):
                    del st.session_state.pending_users[u]
                    st.rerun()

    # --- 菜单 3: 操作日志 (仅 Boss 可见) ---
    elif nav == "📜 操作日志":
        st.title("📜 全球员工操作追踪")
        st.table(st.session_state.logs)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.auth_ok = False
        st.rerun()
