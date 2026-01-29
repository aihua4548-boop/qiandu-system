import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 数据架构与时区同步 ---
def get_local_time():
    # 锁定胡志明/雅加达/曼谷时间 (UTC+7)
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
    
    # 核心安全监控：异常频率拦截
    risk_tag = "✅ 正常"
    if logs:
        try:
            last_t = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_t).total_seconds() < 1.2: risk_tag = "🔴 频率异常警报"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令动作": action,
        "目标对象": target,
        "情报深度": "💎 核心联络" if weight >= 10 else "📄 基础查阅",
        "安全监控": risk_tag
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全球通讯协议 (V40 精准修正版) ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 优先级 1: Telegram (小飞机)
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus", "uae"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", f"TG: +{nums}"

    # 优先级 2: 国别精准匹配
    if "japan" in ctx or "tokyo" in ctx or nums.startswith('81'):
        p = nums[2:] if nums.startswith('81') else nums[1:] if nums.startswith('0') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", "【日文破冰】"
    
    if "thailand" in ctx or "bangkok" in ctx or nums.startswith('66'):
        p = nums[2:] if nums.startswith('66') else nums[1:] if nums.startswith('0') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", "【泰文破冰】"

    if "vietnam" in ctx or "vn" in ctx or nums.startswith('84') or (len(nums) == 10 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", "【越文破冰】"

    if "indonesia" in ctx or "jakarta" in ctx or nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", "【印尼文破冰】"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", "【通用开发信】"

# --- 3. QIANDU AI 决策引擎 (战略指纹识别) ---
def qiandu_ai_v40(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "批发", "grosir", "distributor"])
    is_med = any(k in ctx for k in ["pharmacy", "nhà thuốc", "clinic", "spa", "skin", "derma"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat", "aeon", "lotte"])

    if is_ws:
        return "🏗️ 大宗批发巨头", "5%-12%", "报货柜低价，展示韩国直发证件。对方看重现货稳定和单价。", "注意多方比价。"
    elif is_med:
        return "🏥 专业医美渠道", "35%-50%", "推 Leaders 院线款。强调成分、修护与专业背书。不要谈低价。", "开发周期较长。"
    elif is_prime:
        return "💎 核心商圈旗舰", "25%-40%", "推 meloMELI 颜值款。谈引流、谈视觉陈列支持。地段贵，需高毛利。", "对包装极敏感。"
    return "🏪 常规零售门店", "20%-35%", "谈补货速度、谈一件代发。推当月最火单品。降低囤货压力。", "防范收款风险。"

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V40", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V40.0")
    acc = st.radio("模式", ["员工入口", "指挥官中心"], horizontal=True, key="acc40")
    if acc == "指挥官中心":
        pwd = st.text_input("创始人密钥", type="password", key="bp40")
        if st.button("激活权限", key="bb40"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 登录", "📝 申请"])
        with t1:
            u, p = st.text_input("账号", key="ui40"), st.text_input("密码", type="password", key="pi40")
            if st.button("进入系统", key="bi40"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("登录失败：账号未批准或密码错误")
        with t2:
            nu, np = st.text_input("新账号名", key="nu40"), st.text_input("设置密码", type="password", key="np40")
            if st.button("提交入职申请", key="rb40"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功！请联系指挥官(Founder)批准。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报决策矩阵", "⚙️ 团队与权限管理", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报决策矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报决策矩阵":
        st.title("📊 QIANDU 深度商业情报矩阵 (V40)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、商圈或关键词")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            c_n, c_p, c_a = df.columns[0], df.columns[1], df.columns[min(2, len(df.columns)-1)]
            grid = st.columns(2)
            remarks = load_data("remarks")
            
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 与 通讯逻辑
                role, profit, strategy, trap = qiandu_ai_v40(name, addr)
                country, chat_link, tool, script_label = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.3])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"发起联络({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            st.caption(f"🛡️ 风控识别: {tool}")
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.write(f"📈 **预期:** {profit}")
                            st.info(f"💡 **AI 建议:**\n{strategy}")
                            st.warning(f"⚠️ **风险点:** {trap}")

                        # 核心功能：备注跟进
                        st.divider()
                        curr_rem = remarks.get(name, {"text": "暂无跟进备注", "user": "-", "time": "-"})
                        st.caption(f"🕒 最后更新: {curr_rem['time']} ({curr_rem['user']})")
                        st.success(f"备注内容: {curr_rem['text']}")
                        
                        new_note = st.text_input("更新跟进进展", key=f"n_{idx}")
                        if st.button("保存备注", key=f"b_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks)
                                add_mission_log(st.session_state.user, "更新备注", name, 5)
                                st.rerun()

                        st.write("🌐 **全媒体矩阵调研:**")
                        search_q = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={search_q}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={search_q}")

    elif nav == "⚙️ 团队与权限管理":
        st.title("⚙️ 团队审核与战力排行")
        t1, t2 = st.tabs(["🆕 准入审核", "🏆 战力排行"])
        with t1:
            pnd = load_data("pending")
            if not pnd: st.info("目前没有待审核的入职申请")
            for u, info in list(pnd.items()):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"申请人: **{u}** ({info['time']})")
                if c2.button("✅ 批准入职", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd)
                    add_mission_log("Founder", "批准入职", u, 5); st.rerun()
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

    elif nav == "📜 深度日志审计":
        st.title("📜 全球行动审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("安全退出系统"):
        st.session_state.clear(); st.rerun()
