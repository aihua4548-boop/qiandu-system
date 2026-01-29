import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 数据架构与时区同步 ---
def get_local_time():
    # 强制同步越南/印尼/泰国时区 (UTC+7)
    return datetime.utcnow() + timedelta(hours=7)

DB_FILES = {
    "users": "users_data.json", 
    "pending": "pending.json", 
    "logs": "op_logs.json",
    "remarks": "remarks_data.json"
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

def add_mission_log(user, action, target="-", weight=1):
    logs = load_data("logs")
    current_time = get_local_time()
    
    # 异常频率安全监控
    risk_tag = "✅ 正常"
    if logs:
        try:
            last_t = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_t).total_seconds() < 1.2: risk_tag = "🔴 高频异常"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令": action,
        "目标": target,
        "战力贡献": weight,
        "风控": risk_tag
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全球通讯路由与话术 V38 ---
def get_comm_intel(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 国家识别与多语言话术
    if "japan" in ctx or nums.startswith('81'):
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", "【日文】こんにちは、韓国QIANDUです。Jmella/SNPの卸売について..."
    
    if "vietnam" in ctx or "vn" in ctx or nums.startswith('84'):
        p = nums[2:] if nums.startswith('84') else nums[1:] if nums.startswith('0') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", "【越文】Chào bạn, mình từ QIANDU Hàn Quốc. Bên mình phân phối sỉ Jmella/SNP..."
    
    if "thailand" in ctx or nums.startswith('66'):
        p = nums[2:] if nums.startswith('66') else nums[1:] if nums.startswith('0') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", "【泰文】สวัสดีครับ จาก QIANDU Korea ครับ..."
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", "【通用】Hi, this is QIANDU Korea. Wholesale K-beauty..."

# --- 3. QIANDU AI 深度决策大脑 (千店千策) ---
def qiandu_ai_v38(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "批发", "grosir"])
    is_med = any(k in ctx for k in ["pharmacy", "nhà thuốc", "clinic", "spa", "skin", "derma"])
    is_prime = any(k in ctx for k in ["district 1", "myeongdong", "sukhumvit", "jakarta pusat"])

    if is_ws:
        return "🏗️ 大宗批发", "5%-12%", "【战术】: 谈货柜量、展示一手货源单据。推 Jmella/SNP 基础款。", "防范低价比价。"
    elif is_med:
        return "🏥 专业药妆", "35%-50%", "【战术】: 谈成分、谈 Leaders 医美背书。推高端修护系列。", "开发周期较长。"
    elif is_prime:
        return "💎 旗舰零售", "25%-40%", "【战术】: 谈引流、谈 meloMELI 颜值。提供陈列架支持。", "对包装档次敏感。"
    return "🏪 常规门店", "20%-35%", "【战术】: 谈补货速度、谈一件代发。推月度爆款单品。", "防范收款风险。"

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V38", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V38.0")
    acc = st.radio("模式选择", ["员工登录", "指挥官进入"], horizontal=True)
    if acc == "指挥官进入":
        pwd = st.text_input("创始人密钥", type="password")
        if st.button("激活指挥权限"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号"), st.text_input("密码", type="password")
            if st.button("进入系统"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
        with t2:
            nu, np = st.text_input("拟申请账号"), st.text_input("设置密码", type="password")
            if st.button("提交入职申请"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功！请联系指挥官(Founder)审批。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报看板", "⚙️ 团队战力与审核", "📜 安全审计日志"] if st.session_state.role == "boss" else ["📊 情报看板"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报看板":
        st.title("📊 QIANDU 深度情报决策矩阵 (V38)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、地段或关键词")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            c_n, c_p, c_a = df.columns[0], df.columns[1], df.columns[min(2, len(df.columns)-1)]
            grid = st.columns(2)
            remarks = load_data("remarks")
            
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                country, chat_link, tool, script = get_comm_intel(phone, name + addr)
                role, profit, strategy, trap = qiandu_ai_v38(name, addr)
                
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
                            st.write(f"🏢 **画像:** {role} ({profit})")
                            st.info(f"💡 **AI建议:** {strategy}")
                            with st.expander("📝 话术/风险"):
                                st.warning(f"避坑: {trap}")
                                st.code(script, language="markdown")

                        st.write("📝 **客户跟进状态:**")
                        curr_rem = remarks.get(name, {"text": "暂无记录", "user": "-", "time": "-"})
                        st.caption(f"最后更新: {curr_rem['time']} ({curr_rem['user']})")
                        st.success(f"备注: {curr_rem['text']}")
                        
                        new_note = st.text_input("更新记录", key=f"n_{idx}")
                        if st.button("保存备注", key=f"b_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks)
                                add_mission_log(st.session_state.user, "更新备注", name, 5)
                                st.rerun()

                        st.write("🌐 **社媒探测:**")
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}")

    elif nav == "⚙️ 团队战力与审核":
        st.title("⚙️ 团队控制中心")
        t1, t2 = st.tabs(["🆕 入职审批", "👥 战力排行"])
        with t1:
            pnd = load_data("pending")
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 {u} ({info['time']})")
                if c2.button("✅ 批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
                if c3.button("❌ 拒绝", key=f"n_{u}"):
                    del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            logs = load_data("logs")
            if logs:
                ldf = pd.DataFrame(logs)
                st.bar_chart(ldf.groupby("操作员")["战力贡献"].sum().sort_values(ascending=False))
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"注销权限: {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 安全审计日志":
        st.title("📜 指挥官审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("安全退出"):
        st.session_state.clear(); st.rerun()
