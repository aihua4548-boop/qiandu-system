import streamlit as st
import pandas as pd
import os
import json
import re
from datetime import datetime, timedelta

# --- 1. 数据持久化与智能兼容审计引擎 ---
def get_local_time():
    # 适配越南/印尼时区 (UTC+7)
    return datetime.utcnow() + timedelta(hours=7)

DB_FILES = {"users": "users_data.json", "pending": "pending.json", "logs": "op_logs.json"}

def load_data(key):
    try:
        if os.path.exists(DB_FILES[key]):
            with open(DB_FILES[key], "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return [] if key == "logs" else {}

def save_data(key, data):
    with open(DB_FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_mission_log(user, action, target="-", depth=1):
    logs = load_data("logs")
    current_time = get_local_time()
    
    # 异常频率检测 + 格式兼容逻辑
    risk_tag = "✅ 正常"
    if logs:
        try:
            # 兼容处理：尝试多种时间格式，防止旧数据导致崩溃
            last_time_str = logs[0]['时间']
            formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
            last_time = None
            for fmt in formats:
                try:
                    last_time = datetime.strptime(last_time_str, fmt)
                    break
                except: continue
            
            if last_time and (current_time - last_time).total_seconds() < 1.5:
                risk_tag = "🔴 异常高频"
        except:
            pass # 如果解析彻底失败，跳过检测，不影响系统运行

    log_entry = {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令动作": action,
        "目标对象": target,
        "情报价值": "💎 核心资产" if depth >= 10 else "📄 基础",
        "安全监控": risk_tag
    }
    logs.insert(0, log_entry)
    save_data("logs", logs[:3000])

# --- 2. 全球通讯路由 (适配 Zalo/WA/Line/TG) ---
def get_contact_route(phone_raw, name_addr):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = str(name_addr).lower()
    if any(k in ctx for k in ["tg", "telegram", "飞机", "rus", "dubai"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram"
    if nums.startswith('66'): return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{nums[2:]}", "Line"
    if nums.startswith('81'): return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{nums[2:]}", "Line"
    if nums.startswith('84') or (len(nums) >= 9 and nums.startswith('0')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo"
    if nums.startswith('62') or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp"
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp"

# --- 3. QIANDU AI 深度大脑 V21 (千店千策模型) ---
def qiandu_ai_v21(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    
    # 深度特征提取
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "distributor", "warehouse", "批发", "grosir", "supply"])
    is_spa = any(k in ctx for k in ["spa", "skin", "da", "clinic", "pharmacy", "nhà thuốc", "derma"])
    is_mall = any(k in ctx for k in ["mall", "plaza", "center", "aeon", "lotte", "myeongdong", "district 1"])

    if is_ws:
        return {
            "画像": "🏛️ 一级批发巨头",
            "战略": "【价格战】: 强调韩妆一手货源、通关时效。推 Jmella/SNP 大宗采购。",
            "话术": "Chào anh, bên em từ QIANDU Hàn Quốc. Chuyên đổ sỉ Jmella/SNP giá gốc container, đầy đủ giấy tờ..."
        }
    elif is_spa:
        return {
            "画像": "🏥 专业/医美渠道",
            "战略": "【专业战】: 强调 Leaders/SNP 修复成分。这类客户回购稳，谈‘院线专供’。",
            "话术": "Chào chị, bên em có mẫu mặt nạ Leaders chuyên dụng cho Spa, phục hồi da sau liệu trình cực tốt..."
        }
    elif is_mall:
        return {
            "画像": "💎 高端零售/商场店",
            "战略": "【形象战】: 推 meloMELI 新品。谈‘引流形象’与‘小样支持’。地段贵，看重颜值。",
            "话术": "Chào bạn, mẫu meloMELI này bên mình đang hot nhất ở Seoul, shop có muốn làm đại lý trưng bày không?..."
        }
    else:
        return {
            "画像": "🏪 社区常规美妆",
            "战略": "【散单战】: 谈‘一件起批’、‘补货快’。主推当月爆款面膜，降低对方屯货压力。",
            "话术": "Chào shop, bên mình có sẵn các mẫu mặt nạ hot nhất Hàn Quốc, nhập lẻ giá sỉ, giao hàng ngay..."
        }

# --- 4. 界面逻辑 ---
st.set_page_config(page_title="QIANDU BI V21", layout="wide")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球指挥终端 V21.0")
    acc = st.radio("系统通道", ["员工入口", "指挥官进入"], horizontal=True, key="acc_v21")
    if acc == "指挥官进入":
        pwd = st.text_input("指挥官密钥", type="password", key="bp_v21")
        if st.button("激活权限", key="bb_v21"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui_v21"), st.text_input("密码", type="password", key="pi_v21")
            if st.button("进入系统", key="bi_v21"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
        with t2:
            nu, np = st.text_input("申请账号", key="nu_v21"), st.text_input("申请密码", type="password", key="np_v21")
            if st.button("提交申请", key="rb_v21"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d")}
                save_data("pending", pnd); st.success("申请成功")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = ["📊 情报矩阵", "⚙️ 团队管理", "📜 深度日志"] if st.session_state.role == "boss" else ["📊 情报矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报矩阵":
        st.title("📊 QIANDU 深度商业情报 (全能版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择目标数据库", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 搜索店名、商圈或关键词", key="sq_v21")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]
                add_mission_log(st.session_state.user, "检索情报", q)

            cols = list(df.columns)
            c_n, c_p, c_a = st.sidebar.selectbox("店名", cols, index=0), st.sidebar.selectbox("电话", cols, index=1), st.sidebar.selectbox("地址", cols, index=min(2, len(cols)-1))
            
            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                # AI 画像 V21
                intel = qiandu_ai_v21(name, addr)
                country, chat_link, tool = get_contact_route(phone, name + addr)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"💬 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系商户 ({tool})", name, 10)
                            st.link_button("📍 地图视觉验证", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                        with col2:
                            st.write(f"🏢 **角色:** {intel['画像']}")
                            st.info(f"💡 **AI 建议策略:**\n{intel['战略']}")
                            with st.expander("📝 越语/印尼语开发信"):
                                st.code(intel['话术'], language="markdown")
                        
                        st.write("🌐 **社媒搜店:**")
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={name}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={name}")

    elif nav == "⚙️ 团队管理":
        st.title("⚙️ QIANDU HR 中心")
        t1, t2 = st.tabs(["待审名单", "在职管理"])
        pnd = load_data("pending")
        with t1:
            for u, info in list(pnd.items()):
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 {u}")
                if c2.button("批准", key=f"y_{u}"):
                    users = load_data("users"); users[u] = {"pwd": info["pwd"], "status": "active"}
                    save_data("users", users); del pnd[u]; save_data("pending", pnd); st.rerun()
        with t2:
            users = load_data("users")
            for u in list(users.keys()):
                if st.button(f"注销员工: {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度日志":
        st.title("📜 全球行动日志审计")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("🚪 安全退出"):
        st.session_state.clear(); st.rerun()
