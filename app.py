import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 数据架构与多端同步 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7)

DB_FILES = {
    "users": "users_data.json", 
    "pending": "pending.json", 
    "logs": "op_logs.json",
    "remarks": "remarks_data.json" # 核心：跟进备注仓
}

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
    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令": action,
        "商户": target,
        "战力分": score
    })
    save_data("logs", logs[:3000])

# --- 2. 核心逻辑：通讯路由与话术 ---
def get_intel_and_chat(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if "japan" in ctx or nums.startswith('81'):
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", "【日文】こんにちは、韓国QIANDU（千渡）です..."
    if "vietnam" in ctx or "vn" in ctx or nums.startswith('84'):
        p = nums[2:] if nums.startswith('84') else nums[1:] if nums.startswith('0') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", "【越文】Chào bạn, mình từ QIANDU Hàn Quốc..."
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", "【通用】Hi, this is QIANDU Korea..."

# --- 3. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V36", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥部 V36.0")
    acc = st.radio("模式", ["员工入口", "指挥官入口"], horizontal=True)
    if acc == "指挥官入口":
        pwd = st.text_input("创始人密钥", type="password")
        if st.button("激活权限"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        u, p = st.text_input("账号"), st.text_input("密码", type="password")
        if st.button("登录系统"):
            users = load_data("users")
            if u in users and users[u]["pwd"] == p:
                st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                add_mission_log(u, "登录系统", "-", 1)
                st.rerun()

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报看板", "⚙️ 团队战力统计", "📜 安全审计"] if st.session_state.role == "boss" else ["📊 情报看板"]
    nav = st.sidebar.radio("指挥中心导航", menu)

    if nav == "📊 情报看板":
        st.title("📊 QIANDU 深度情报矩阵 (含跟进备注)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、商圈或地址")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            c_n, c_p, c_a = df.columns[0], df.columns[1], df.columns[min(2, len(df.columns)-1)]
            
            grid = st.columns(2)
            remarks = load_data("remarks")
            
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                country, chat_link, tool, script = get_intel_and_chat(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        c1, c2 = st.columns([1, 1.2])
                        with c1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with c2:
                            # 备注展示与输入
                            current_remark = remarks.get(name, {"text": "暂无跟进记录", "user": "-", "time": "-"})
                            st.caption(f"🕒 最后跟进: {current_remark['time']} ({current_remark['user']})")
                            st.info(f"📝 {current_remark['text']}")
                            
                            new_note = st.text_input("更新备注", placeholder="如：已寄样、嫌贵、负责人不在...", key=f"note_{idx}")
                            if st.button("保存备注", key=f"btn_{idx}"):
                                if new_note:
                                    remarks[name] = {
                                        "text": new_note,
                                        "user": st.session_state.user,
                                        "time": get_local_time().strftime("%m-%d %H:%M")
                                    }
                                    save_data("remarks", remarks)
                                    add_mission_log(st.session_state.user, "更新备注", name, 5)
                                    st.rerun()

                        st.write("🌐 **全媒体探测:**")
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}")

    elif nav == "⚙️ 团队战力统计":
        st.title("⚙️ 员工实战看板")
        logs = load_data("logs")
        if logs:
            ldf = pd.DataFrame(logs)
            st.subheader("🔥 员工战力排行 (综合联络与备注贡献)")
            stats = ldf.groupby("操作员")["战力分"].sum().sort_values(ascending=False)
            st.bar_chart(stats)
            
            st.divider()
            st.subheader("🆕 待审核新员工")
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {u} (申请时间: {info['time']})")
                if col2.button("批准入职", key=f"app_{u}"):
                    users = load_data("users")
                    users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()

    elif nav == "📜 安全审计":
        st.title("📜 全球行动审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
