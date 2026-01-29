import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 时区与数据安全 ---
def get_local_time():
    return datetime.utcnow() + timedelta(hours=7)

DB_FILES = {"users": "users_data.json", "pending": "pending.json", "logs": "op_logs.json", "remarks": "remarks_data.json"}

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
    logs.insert(0, {"时间": get_local_time().strftime("%Y-%m-%d %H:%M"), "操作员": user, "动作": action, "目标": target, "战力": weight})
    save_data("logs", logs[:2000])

# --- 2. 核心：QIANDU AI 深度博弈大脑 V65 ---
def qiandu_deep_ai_v65(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # A. 身份识别
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "warehouse", "distributor", "grosir", "批发"])
    is_med = any(k in ctx for k in ["pharmacy", "clinic", "nhà thuốc", "med", "derma", "spa"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "ginza", "lotte"])
    
    # B. 差异化策略生成
    if is_ws:
        role = "🏗️ 大宗流通商"
        pain_point = "库存周转、资金成本、SKU稳定性"
        strategy = "推 Jmella/SNP 柜货。直接谈韩国直发价格及出货单据，展示供应链实力。"
        script = "Chào anh, em bên QIANDU Hàn Quốc. Bên em chuyên đổ sỉ container Jmella/SNP giá gốc, đầy đủ COA..."
    elif is_med:
        role = "🏥 专业医美药妆"
        pain_point = "产品成分、出口资质、回购率"
        strategy = "推 Leaders/SNP 修复款。提供临床实验数据。谈‘非红海市场’保护，利润稳定。"
        script = "Chào chị, em có dòng Leaders chuyên dụng cho Spa/Clinic, phục hồi da cực tốt, mẫu này đang ít người bán..."
    elif is_prime:
        role = "💎 核心商圈零售"
        pain_point = "高额租金压力、引流、视觉形象"
        strategy = "推 meloMELI 颜值款。协助提供韩国风展示柜支持。强调‘高到店转化率’。"
        script = "Chào bạn, shop mình ở địa điểm đẹp thế này, nhập thêm meloMELI bản Hàn sẽ hút khách check-in lắm..."
    else:
        role = "🏪 常规社区零售"
        pain_point = "起批门槛、补货速度"
        strategy = "推爆款单单。谈‘一件代发’或‘满小额起批’。降低对方压货风险。"
        script = "Shop ơi, bên mình có sẵn các mẫu mặt nạ hot nhất Hàn Quốc, nhập ít cũng giá sỉ, giao hàng ngay..."

    return role, pain_point, strategy, script

# --- 3. 全球通讯协议 ---
def get_comm_route(phone_raw, name_addr, file_context=""):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = (str(name_addr) + " " + str(file_context)).lower()
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('81') or "japan" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('81') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line"
    if nums.startswith('84') or any(k in ctx for k in ["vn", "vietnam", "hcm", "sỉ"]):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if nums.startswith('62') or "indonesia" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 4. 界面展示 ---
st.set_page_config(page_title="QIANDU BI V65", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V65.0")
    acc = st.radio("模式", ["员工入口", "指挥官进入"], horizontal=True)
    if acc == "指挥官进入":
        pwd = st.text_input("密钥", type="password")
        if st.button("激活"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        u, p = st.text_input("账号"), st.text_input("密码", type="password")
        if st.button("登录"):
            users = load_data("users")
            if u in users and users[u]["pwd"] == p:
                st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                add_mission_log(u, "登录系统")
                st.rerun()
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队与战力", "📜 审计日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度商业情报 (AI 战略版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            # 智能映射
            st.sidebar.divider()
            cols = list(df.columns)
            c_n = st.sidebar.selectbox("店名列", cols, index=0)
            c_p = st.sidebar.selectbox("电话列", cols, index=1 if len(cols)>1 else 0)
            c_a = st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1))
            
            q = st.text_input("🔎 搜索店名、商圈或关键词（AI 实时执行战略分析）")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2)
            remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 决策深度逻辑
                role, pain, strategy, script = qiandu_deep_ai_v65(name, addr)
                country, chat_link, tool = get_comm_route(phone, name + addr, sel_f)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉分析", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **画像:** {role}")
                            st.write(f"🚩 **核心痛点:** {pain}")
                            st.info(f"💡 **AI 建议:**\n{strategy}")
                            with st.expander("📝 破冰话术"):
                                st.code(script, language="markdown")
                        
                        st.divider()
                        curr_rem = remarks.get(name, {"text": "暂无记录", "user": "-", "time": "-"})
                        st.success(f"备注: {curr_rem['text']} ({curr_rem['user']} {curr_rem['time']})")
                        
                        new_note = st.text_input("跟进进展", key=f"n_{idx}")
                        if st.button("保存备注", key=f"b_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

                        st.write("🌐 **社媒探测:**")
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}")

    elif nav == "⚙️ 团队与战力":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["待审名单", "战力排行榜"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u} ({info['time']})")
                if c2.button("批准入职", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            logs = load_data("logs")
            if logs:
                ldf = pd.DataFrame(logs)
                st.bar_chart(ldf.groupby("操作员")["战力"].sum().sort_values(ascending=False))
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"🚫 注销账号: {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
