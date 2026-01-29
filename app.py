import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 核心引擎与安全审计 ---
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

def add_mission_log(user, action, target="-", score=1):
    logs = load_data("logs")
    current_time = get_local_time()
    risk = "✅ 安全"
    if logs and logs[0]['操作员'] == user:
        if (current_time - datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")).total_seconds() < 1.0:
            risk = "🚨 频率预警"; score = -30
    logs.insert(0, {"时间": current_time.strftime("%Y-%m-%d %H:%M:%S"), "操作员": user, "指令动作": action, "目标对象": target, "战力值": score, "安全评级": risk})
    save_data("logs", logs[:5000])

# --- 2. 隐私保护核心：号码脱敏 ---
def mask_phone(phone_raw, role):
    raw = re.sub(r'\D', '', str(phone_raw))
    if role == "boss": return raw 
    return f"{raw[:3]}****{raw[-4:]}" if len(raw) > 7 else "****"

# --- 3. QIANDU 深度 AI 决策大脑 V98 (三维推演) ---
def qiandu_ai_v98(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # A. 维度识别
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "批发", "warehouse", "grosir", "distributor"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat", "aeon", "lotte"])
    is_med = any(k in ctx for k in ["spa", "clinic", "pharmacy", "nhà thuốc", "med", "derma"])

    # B. 战略推演逻辑
    if is_ws:
        return {
            "身份": "🏗️ 供应链枢纽 (大宗批发)",
            "核心痛点": "货源稳定性、资金成本、SKU更新速度",
            "谈判筹码": "展示千渡一手韩国报关单。谈‘柜货锁定价’。推 Jmella/SNP 常青款。",
            "话术建议": "Chào anh/chị, em bên QIANDU Hàn Quốc. Bên em sẵn kho Jmella/SNP số lượng lớn, giá container ổn định, đầy đủ COA..."
        }
    elif is_med:
        return {
            "身份": "🏥 专业医美/药妆渠道",
            "核心痛点": "成分安全性、术后修复效果、品牌背书",
            "谈判筹码": "推 Leaders/SNP 修复系列。提供临床报告。谈‘非红海市场保护’。强调高客单价。",
            "话术建议": "Chào chị, bên em có dòng Leaders chuyên biệt cho Clinic, phục hồi sau xâm lấn cực tốt, giấy tờ đầy đủ..."
        }
    elif is_prime:
        return {
            "身份": "💎 核心商圈旗舰 (高租金受压商户)",
            "核心痛点": "高额租金、到店转化率、视觉陈列、独特性",
            "谈判筹码": "推 meloMELI 颜值款。提供韩国原装展示柜支持。谈‘打卡效应’引流，对冲地租压力。",
            "话术建议": "Shop mình ở vị trí cực đẹp, nhập thêm meloMELI sẽ giúp tăng tỷ lệ khách vào cửa và check-in rất tốt..."
        }
    
    return {
        "身份": "🏪 社区灵活零售",
        "核心痛点": "起批门槛、补货时效、爆款响应",
        "谈判筹码": "谈‘一件起批’、‘满额送样’。强调胡志明/雅加达本地仓极速发货。主推当月爆款。",
        "话术建议": "Bên mình có sẵn mẫu hot nhất Hàn Quốc, nhập ít cũng giá sỉ, giao hàng ngay trong ngày..."
    }

# --- 4. 路由系统 ---
def get_comm_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if nums.startswith('7') or nums.startswith('971') or "moscow" in ctx:
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or "vietnam" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if any(nums.startswith(x) for x in ['81','66','82']) or any(k in ctx for k in ["japan", "thailand"]):
        return "Line 🚀", f"https://line.me/R/ti/p/~+{nums}", "Line"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 5. 界面层 ---
st.set_page_config(page_title="QIANDU COMMAND V98", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V98.0")
    acc = st.radio("模式", ["员工通道", "指挥官中心"], horizontal=True)
    if acc == "指挥官中心":
        pwd = st.text_input("创始人密钥", type="password")
        if st.button("激活权限"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"}); st.rerun()
    else:
        u, p = st.text_input("账号"), st.text_input("密码", type="password")
        if st.button("登录"):
            users = load_data("users")
            if u in users and users[u]["pwd"] == p:
                st.session_state.update({"auth_ok": True, "user": u, "role": "staff"}); add_mission_log(u, "登录"); st.rerun()
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报决策矩阵", "⚙️ 团队与审核", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报决策矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报决策矩阵":
        st.title("📊 QIANDU 深度商业情报矩阵 (AI 战略推演版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("数据源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            # 智能映射
            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=2)
            
            q = st.text_input("🔎 搜索商户关键词（AI 自动触发地段与身份扫描）")
            if q: df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            grid = st.columns(2); remarks = load_data("remarks")
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI & 脱敏 & 路由
                intel = qiandu_ai_v98(name, addr)
                display_phone = mask_phone(phone, st.session_state.role)
                country, chat_link, tool = get_comm_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        cl1, cl2 = st.columns([1, 1.3])
                        with cl1:
                            st.write(f"🌍 区域: **{country}**")
                            st.write(f"📞 号码: `{display_phone}`")
                            st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True)
                            if st.button(f"📑 登记战力-{idx}", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系客户({tool})", name, 10)
                        with cl2:
                            st.write(f"🏢 画像: **{intel['身份']}**")
                            st.warning(f"🚩 核心痛点: {intel['核心痛点']}")
                            st.info(f"💡 AI 建议: {intel['谈判筹码']}")
                            with st.expander("📝 破冰话术"): st.code(intel['话术建议'], language="markdown")
                        
                        st.write("🌐 **社媒探测:**")
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}", use_container_width=True)
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/", use_container_width=True)
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}", use_container_width=True)

                        rem = remarks.get(name, {"text": "暂无记录", "user": "-", "time": "-"})
                        st.divider()
                        st.success(f"备注: {rem['text']} ({rem['user']})")
                        new_note = st.text_input("更新记录", key=f"ni_{idx}")
                        if st.button("保存备注", key=f"nb_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks); add_mission_log(st.session_state.user, "更新备注", name, 5); st.rerun()

    elif nav == "⚙️ 团队与审核":
        st.title("⚙️ 团队准入与战力排行")
        # 战力排行图表
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            ldf['战力值'] = pd.to_numeric(ldf['战力值'], errors='coerce').fillna(0)
            st.bar_chart(ldf.groupby("操作员")["战力值"].sum().sort_values(ascending=False))
        # 审核
        st.divider(); pnd = load_data("pending")
        for u, info in list(pnd.items()):
            c1, c2 = st.columns([3, 1])
            c1.write(f"👤 {u} ({info['time']})")
            if c2.button("授权通过", key=f"y_{u}"):
                users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()

    elif nav == "📜 深度审计日志":
        st.title("📜 行动审计日志")
        ldf = pd.DataFrame(load_data("logs"))
        if not ldf.empty:
            st.dataframe(ldf.style.applymap(lambda x: 'background-color: #ff4b4b; color: white' if "🚨" in str(x) else '', subset=['安全评级']), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"): st.session_state.clear(); st.rerun()
