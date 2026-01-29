import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime

# --- 1. 高级数据持久化与日志架构 ---
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

def add_enhanced_log(user, action, target_shop="-", detail="-"):
    """
    增强版日志系统：记录 操作员 | 动作 | 目标商户 | 详细描述 | 风险权重
    """
    logs = load_data("logs")
    log_entry = {
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "核心动作": action,
        "关联商户": target_shop,
        "详细备注": detail,
        "风险": "⚠️ 频繁" if len([l for l in logs[:10] if l['操作员'] == user]) > 8 else "✅ 正常"
    }
    logs.insert(0, log_entry)
    save_data("logs", logs[:2000]) # 延长日志存储至2000条

# --- 2. QIANDU 全球通讯协议 ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    
    # 逻辑匹配：泰国/日本/韩国/印尼/越南
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('09')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    elif nums.startswith('66') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('66') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line"
    elif nums.startswith('81'):
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    elif nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    elif nums.startswith('82') or nums.startswith('010'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('82') else nums
        return "Korea 🇰🇷", f"https://line.me/R/ti/p/~+82{p}", "Line"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 3. QIANDU AI 深度商业逻辑 3.0 ---
def ai_commander_analysis(name, addr):
    ctx = (str(name) + str(addr)).lower()
    
    # A. 渠道生命周期与规模分析
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "grosir", "supply", "批发", "贸易", "warehouse"])
    
    # B. 地理租金与利润溢价预估 (针对您的核心城市)
    rent_level = "🔴 高 (核心商圈/溢价能力强)" if any(k in ctx for k in ["myeongdong", "district 1", "jakarta pusat", "ginza", "sukhumvit", "第一郡"]) else "🟢 中/低"
    
    # C. 谈判战术模组
    if is_ws:
        identity = "🏛️ 区域总代/大批发商"
        strategy = "【攻坚战】: 重点展示千渡‘韩妆一手货源’证件，谈Jmella/SNP货柜价。这类客户看重稳定性和独家授权。"
        risk = "高收益/高门槛"
    elif "spa" in ctx or "clinic" in ctx or "nhà thuốc" in ctx:
        identity = "🏥 专业/医美渠道"
        strategy = "【专业战】: 推Leaders/SNP医美面膜。这类客户利润高，但需要详细的产品成分表和出口资质。"
        risk = "高回购/低散单"
    else:
        identity = "🏪 终端零售店"
        strategy = "【潮流战】: 推meloMELI等高颜值新品牌。这类客户需要‘小而美’，甚至可以提供代发货服务。"
        risk = "低门槛/易成交"

    return identity, rent_level, strategy, risk

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V14", layout="wide", page_icon="🏢")

if "auth_ok" not in st.session_state:
    st.title("🏙️ QIANDU 全球指挥终端 V14.0")
    access = st.radio("系统入口", ["员工通道", "指挥官通道"], horizontal=True, key="access")
    
    if access == "指挥官通道":
        pwd = st.text_input("指挥官密钥", type="password", key="b_pwd")
        if st.button("激活权限", key="b_btn"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="u_in"), st.text_input("密码", type="password", key="p_in")
            if st.button("登录", key="btn_in"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_enhanced_log(u, "登录系统")
                    st.rerun()
        with t2:
            nu, np = st.text_input("新账号", key="u_reg"), st.text_input("设置密码", type="password", key="p_reg")
            if st.button("提交申请", key="btn_reg"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": datetime.now().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请已提交，请联系指挥官批准")

else:
    # --- 5. 内部系统 ---
    st.sidebar.title(f"👤 状态: {st.session_state.user}")
    menu = ["📊 商业情报矩阵", "⚙️ 团队权限控制", "📜 指挥官审计日志"] if st.session_state.role == "boss" else ["📊 商业情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 商业情报矩阵":
        st.title("📊 QIANDU 深度情报矩阵 (V14.0)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜店名、地址、品类或商圈关键词 (如: 批发, Spa, 第一郡)", key="global_search")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_enhanced_log(st.session_state.user, "执行搜索", "-", f"搜索词: {q}")

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名列", cols, index=0), st.sidebar.selectbox("电话列", cols, index=1), st.sidebar.selectbox("地址列", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 深度分析 V3.0
                ident, rent, strategy, risk = ai_commander_analysis(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            st.write(f"🌍 国家地区: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 洽谈", chat_link, type="primary", use_container_width=True):
                                add_enhanced_log(st.session_state.user, "发起联络", name, f"工具: {tool}")
                            st.link_button(f"✈️ Telegram 备选", f"https://t.me/+{re.sub(r'\D', '', phone)}", use_container_width=True)
                            st.link_button("📍 地图视觉核查", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with c2:
                            st.write(f"🏷️ **身份:** {ident}")
                            st.write(f"🏟️ **商圈溢价:** {rent}")
                            st.write(f"⚖️ **风险:** {risk}")
                            st.info(f"💡 **AI 建议:**\n{strategy}")
                        
                        st.write("🌐 **跨平台影响力验证:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TikTok", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队权限控制":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["待审申请", "在职员工"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 申请人: {u} (时间: {info['time']})")
                if col2.button("批准入职", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd)
                    add_enhanced_log("Founder", "权限审批", u, "准许入职")
                    st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 员工账号: {u}")
                if col2.button("注销并清除", key=f"n_{u}"):
                    del users[u]; save_data("users", users)
                    add_enhanced_log("Founder", "员工注销", u, "清除访问权限")
                    st.rerun()

    elif nav == "📜 指挥官审计日志":
        st.title("📜 全球操作日志监控 (QIANDU BI)")
        log_df = pd.DataFrame(load_data("logs"))
        if not log_df.empty:
            # 自动高亮高风险动作
            st.dataframe(log_df, use_container_width=True, column_config={
                "风险": st.column_config.TextColumn("风险等级", help="自动监控高频访问行为")
            })
        else:
            st.write("暂无日志记录")

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
