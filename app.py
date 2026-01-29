import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 数据架构与时区锁定 (东七区) ---
def get_local_time():
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
    
    # 安全监控：频率分析
    risk = "✅ 正常"
    if logs:
        try:
            last_t = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_t).total_seconds() < 1.1: risk = "🔴 频率异常警报"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令": action,
        "目标": target,
        "贡献": "💎 核心" if weight >= 10 else "📄 基础",
        "风控": risk
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 深度战术引擎 (千店千策) ---
def qiandu_ai_v60(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "批发", "grosir", "distributor"])
    is_spa = any(k in ctx for k in ["spa", "skin", "clinic", "pharmacy", "nhà thuốc", "derma"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat", "aeon", "lotte"])

    if is_ws:
        return "🏗️ 大宗批发巨头", "5%-12%", "【策略】: 展示韩国一手货源证件。推 Jmella 全系列、SNP 基础款。谈‘货柜级’价。", "防范拿报价去比价。"
    elif is_spa:
        return "🏥 专业医美药妆", "35%-50%", "【策略】: 谈 Leaders 修复背书。强调成分安全与‘非红海渠道’。谈专业，不谈价。", "开发周期较长。"
    elif is_prime:
        return "💎 核心商圈旗舰", "25%-40%", "【策略】: 推 meloMELI 颜值款。谈引流、视觉支持。针对极高租金压力，强调到店转化。", "对包装极度挑剔。"
    return "🏪 常规零售门店", "20%-35%", "【策略】: 谈‘一件起批’、‘补货快’。推月度爆款单品。降低囤货风险。", "防范收款风险。"

# --- 3. QIANDU 全球通讯大脑 (精准路由) ---
def get_comm_intel(phone_raw, name_addr, file_context=""):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = (str(name_addr) + " " + str(file_context)).lower()
    
    # 优先级 1: Telegram (小飞机)
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus", "uae"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", "【飞机直连】"

    # 优先级 2: 越南 (Zalo) - 强力补丁
    if nums.startswith('84') or any(k in ctx for k in ["vn", "vietnam", "hcm", "sỉ", "hồ chí minh"]) or (len(nums) == 10 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", "Chào bạn, mình từ QIANDU Hàn Quốc..."
    
    # 优先级 3: 日本/泰国 (Line)
    if "japan" in ctx or nums.startswith('81'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('81') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", "こんにちは、韓国QIANDU（千渡）です..."
    
    if "thailand" in ctx or nums.startswith('66'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('66') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", "สวัสดีครับ จาก QIANDU Korea ครับ..."

    # 兜底: WhatsApp
    return "Indonesia/Global 🌐", f"https://wa.me/{nums}", "WhatsApp", "Hi, this is QIANDU Korea..."

# --- 4. 界面展示层 ---
st.set_page_config(page_title="QIANDU COMMAND V60", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V60.0")
    acc = st.radio("模式选择", ["员工登录", "创始人进入"], horizontal=True, key="acc60")
    if acc == "创始人进入":
        pwd = st.text_input("创始人密钥", type="password", key="bp60")
        if st.button("激活指挥权限", key="bb60"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui60"), st.text_input("密码", type="password", key="pi60")
            if st.button("进入指挥部", key="bi60"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("账号未授权或需等待创始人批准")
        with t2:
            nu, np = st.text_input("新账号名", key="nu60"), st.text_input("设置密码", type="password", key="np60")
            if st.button("提交入职申请", key="rb60"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功！请联系指挥官批准入职。")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报决策矩阵", "⚙️ 团队管理与审批", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报决策矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报决策矩阵":
        st.title("📊 QIANDU 旗舰情报决策中心")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 智能列名映射")
            all_cols = list(df.columns)
            name_col = st.sidebar.selectbox("店名所在列", all_cols, index=0)
            phone_col = st.sidebar.selectbox("电话所在列", all_cols, index=min(1, len(all_cols)-1))
            addr_col = st.sidebar.selectbox("地址所在列", all_cols, index=min(2, len(all_cols)-1))
            
            q = st.text_input("🔎 全局检索店名、商圈或关键词")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2)
            remarks = load_data("remarks")
            
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[name_col]), str(row[phone_col]), str(row[addr_col])
                role, profit, strategy, trap = qiandu_ai_v60(name, addr)
                country, chat_link, tool, script = get_comm_intel(phone, name + addr, sel_f)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 国家: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"发起联络({tool})", name, 10)
                            st.link_button("📍 地图实景分析", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.write(f"📈 **预估毛利:** {profit}")
                            st.info(f"💡 **AI 策略:**\n{strategy}")
                            with st.expander("📝 破冰话术/避坑"):
                                st.warning(f"避坑: {trap}")
                                st.code(script, language="markdown")

                        st.divider()
                        curr_rem = remarks.get(name, {"text": "暂无跟进备注", "user": "-", "time": "-"})
                        st.caption(f"🕒 最后跟进: {curr_rem['time']} ({curr_rem['user']})")
                        st.success(f"备注: {curr_rem['text']}")
                        
                        new_note = st.text_input("更新跟进进展", key=f"n_{idx}")
                        if st.button("保存备注", key=f"b_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks)
                                add_mission_log(st.session_state.user, "更新备注", name, 5)
                                st.rerun()

                        st.write("🌐 **社媒全媒体探测:**")
                        search_q = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={search_q}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={search_q}")

    elif nav == "⚙️ 团队管理与审批":
        st.title("⚙️ 员工准入与权限控制")
        t1, t2 = st.tabs(["🆕 待审申请", "👥 战力排行榜"])
        pnd = load_data("pending")
        with t1:
            if not pnd: st.info("目前没有待审核的申请")
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
                st.bar_chart(ldf.groupby("操作员")["指令"].count().sort_values(ascending=False))
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"🚫 注销权限: {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度审计日志":
        st.title("📜 全球指挥审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("安全退出系统"):
        st.session_state.clear(); st.rerun()
