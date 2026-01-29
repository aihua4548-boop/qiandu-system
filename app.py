import streamlit as st
import pandas as pd
import os
import json
import re
import urllib.parse
from datetime import datetime, timedelta

# --- 1. 时区与深度审计引擎 ---
def get_local_time():
    # 锁定东七区 (越南/印尼/泰国) 
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
    
    # 核心风控：异常频率检测
    risk_status = "✅ 正常"
    if logs:
        try:
            last_t = datetime.strptime(logs[0]['时间'], "%Y-%m-%d %H:%M:%S")
            if (current_time - last_t).total_seconds() < 1.1: risk_status = "🔴 频率异常警报"
        except: pass

    logs.insert(0, {
        "时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "操作员": user,
        "指令": action,
        "目标": target,
        "价值": "💎 核心资产访问" if weight >= 10 else "📄 基础信息查阅",
        "风控": risk_status
    })
    save_data("logs", logs[:3000])

# --- 2. QIANDU 全球通讯协议 (V50 路由补丁) ---
def get_comm_route(phone_raw, name_addr, file_context=""):
    nums = re.sub(r'\D', '', str(phone_raw))
    ctx = (str(name_addr) + " " + str(file_context)).lower()
    
    # A. 小飞机优先识别 (针对迪拜/俄区/大宗贸易关键词)
    if any(k in ctx for k in ["tg", "telegram", "飞机", "dubai", "rus", "uae"]):
        return "Global ✈️", f"https://t.me/+{nums}", "Telegram", f"TG: +{nums}"

    # B. 越南 Zalo 专项适配 (强力纠错)
    if nums.startswith('84') or any(k in ctx for k in ["vn", "vietnam", "hcm", "hanoi", "sỉ", "thành phố"]) or (len(nums) == 10 and nums.startswith('09')):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('84') else nums
        return "Vietnam 🇻🇳", f"https://zalo.me/84{p}", "Zalo", f"84-{p}"
    
    # C. 日本/泰国/韩国 Line 适配
    if nums.startswith('81') or "japan" in ctx or "tokyo" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('81') else nums
        return "Japan 🇯🇵", f"https://line.me/R/ti/p/~+81{p}", "Line", f"81-{p}"
    
    if nums.startswith('66') or "thailand" in ctx or "bangkok" in ctx:
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('66') else nums
        return "Thailand 🇹🇭", f"https://line.me/R/ti/p/~+66{p}", "Line", f"66-{p}"

    # D. 印尼 WhatsApp 适配
    if nums.startswith('62') or "indonesia" in ctx or "jakarta" in ctx or nums.startswith('08'):
        p = nums[1:] if nums.startswith('0') else nums[2:] if nums.startswith('62') else nums
        return "Indonesia 🇮🇩", f"https://wa.me/62{p}", "WhatsApp", f"62-{p}"
    
    return "Global 🌐", f"https://wa.me/{nums}", "WhatsApp", nums

# --- 3. QIANDU AI 深度决策大脑 (千店千策) ---
def qiandu_ai_v50(name, addr):
    ctx = (str(name) + " " + str(addr)).lower()
    is_ws = any(k in ctx for k in ["wholesale", "sỉ", "tổng kho", "warehouse", "批发", "grosir", "distributor"])
    is_med = any(k in ctx for k in ["pharmacy", "nhà thuốc", "clinic", "spa", "skin", "derma"])
    is_prime = any(k in ctx for k in ["district 1", "quận 1", "myeongdong", "sukhumvit", "jakarta pusat", "aeon", "lotte"])

    if is_ws:
        return {
            "角色": "🏗️ 大宗批发巨头",
            "预期": "5%-12% (靠量回款)",
            "战术": "【价格截杀】: 报货柜低价，展示韩国直发证件。谈现货稳定。推 Jmella/SNP 基础款。",
            "避坑": "防范拿我方报价去压其他供应商。"
        }
    elif is_med:
        return {
            "角色": "🏥 专业医美渠道",
            "预期": "35%-50% (专业溢价)",
            "战术": "【专业渗透】: 推 Leaders/SNP 修复款。谈成分与背书，不谈价格。谈‘非红海渠道’。",
            "避坑": "决策人多为医师或店主本人，周期较长。"
        }
    elif is_prime:
        return {
            "角色": "💎 旗舰零售店",
            "预期": "25%-40% (品牌引流)",
            "战术": "【形象引流】: 推 meloMELI 潮流款。谈颜值与视觉陈列。提供小样与堆头支持。",
            "避坑": "地租极贵，核心痛点是‘到店转化率’。"
        }
    return {
        "角色": "🏪 常规终端零售",
        "预期": "20%-35% (灵活周转)",
        "战术": "【灵活占位】: 谈‘一件起批’、‘补货快’。推当月最火单品，降低压货风险。",
        "避坑": "信用度参差不齐，防范收款风险。"
    }

# --- 4. 界面展示层 ---
st.set_page_config(page_title="QIANDU COMMAND V50", layout="wide", page_icon="🛡️")

if "auth_ok" not in st.session_state:
    st.title("🛡️ QIANDU 全球智慧指挥终端 V50.0")
    acc = st.radio("系统入口", ["员工通道", "指挥官中心"], horizontal=True, key="acc50")
    if acc == "指挥官中心":
        pwd = st.text_input("创始人密钥", type="password", key="bp50")
        if st.button("激活权限", key="bb50"):
            if pwd == "666888":
                st.session_state.update({"auth_ok": True, "user": "Founder", "role": "boss"})
                st.rerun()
    else:
        t1, t2 = st.tabs(["🔐 员工登录", "📝 账号申请"])
        with t1:
            u, p = st.text_input("账号", key="ui50"), st.text_input("密码", type="password", key="pi50")
            if st.button("进入指挥部", key="bi50"):
                users = load_data("users")
                if u in users and users[u]["pwd"] == p:
                    st.session_state.update({"auth_ok": True, "user": u, "role": "staff"})
                    add_mission_log(u, "登录系统")
                    st.rerun()
                else: st.error("登录失败：账号未批准或密码错误")
        with t2:
            nu, np = st.text_input("新账号名", key="nu50"), st.text_input("设置密码", type="password", key="np50")
            if st.button("提交入职申请", key="rb50"):
                pnd = load_data("pending"); pnd[nu] = {"pwd": np, "time": get_local_time().strftime("%Y-%m-%d %H:%M")}
                save_data("pending", pnd); st.success("申请成功！请联系指挥官批准入职。")

else:
    st.sidebar.title(f"👤 状态: {st.session_state.user}")
    menu = ["📊 情报决策矩阵", "⚙️ 团队与权限管理", "📜 深度审计日志"] if st.session_state.role == "boss" else ["📊 情报决策矩阵"]
    nav = st.sidebar.radio("系统导航", menu)

    if nav == "📊 情报决策矩阵":
        st.title("📊 QIANDU 商业智能情报矩阵 (V50 全能版)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("选择当前情报源", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all').fillna('-')
            
            q = st.text_input("🔎 检索店名、地段、商圈或关键词", key="sq50")
            if q:
                df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().str.cat(), axis=1)]

            c_n, c_p, c_a = df.columns[0], df.columns[1], df.columns[min(2, len(df.columns)-1)]
            grid = st.columns(2)
            remarks = load_data("remarks")
            
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_n]), str(row[c_p]), str(row[c_a])
                intel = qiandu_ai_v50(name, addr)
                country, chat_link, tool, info = get_comm_route(phone, name + addr, sel_f)
                
                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {name}")
                        col1, col2 = st.columns([1, 1.2])
                        with col1:
                            st.write(f"🌍 区域: **{country}**")
                            if st.link_button(f"🚀 发起 {tool} 谈判", chat_link, type="primary", use_container_width=True):
                                add_mission_log(st.session_state.user, f"联系({tool})", name, 10)
                            st.link_button("📍 地图视觉分析", f"https://www.google.com/maps/search/{name}+{addr}", use_container_width=True)
                            st.caption(f"🛡️ 通讯解析: {info}")
                        with col2:
                            st.write(f"🏢 **画像:** {intel['角色']}")
                            st.write(f"💵 **预期:** {intel['预期']}")
                            st.info(f"💡 **AI 策略:**\n{intel['战术']}")
                            st.warning(f"⚠️ **风险提示:** {intel['避坑']}")

                        # 核心模块：备注跟进系统
                        st.divider()
                        curr_rem = remarks.get(name, {"text": "暂无历史备注", "user": "-", "time": "-"})
                        st.caption(f"📝 最后备注: {curr_rem['time']} ({curr_rem['user']})")
                        st.success(f"记录: {curr_rem['text']}")
                        
                        new_note = st.text_input("更新跟进进展", key=f"n_{idx}")
                        if st.button("保存备注", key=f"b_{idx}"):
                            if new_note:
                                remarks[name] = {"text": new_note, "user": st.session_state.user, "time": get_local_time().strftime("%m-%d %H:%M")}
                                save_data("remarks", remarks)
                                add_mission_log(st.session_state.user, "更新备注", name, 5)
                                st.rerun()

                        st.write("🌐 **全媒体矩阵调研:**")
                        sq = urllib.parse.quote(name)
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.link_button("FB", f"https://www.facebook.com/search/top/?q={sq}")
                        sc2.link_button("Ins", f"https://www.instagram.com/explore/tags/{name.replace(' ','')}/")
                        sc3.link_button("TK", f"https://www.tiktok.com/search?q={sq}")

    elif nav == "⚙️ 团队与权限管理":
        st.title("⚙️ QIANDU 团队控制中心")
        t1, t2 = st.tabs(["🆕 待审名单", "👥 在职名单与战力"])
        pnd = load_data("pending")
        with t1:
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
                if st.button(f"🚫 注销权限: {u}", key=f"del_{u}"):
                    del users[u]; save_data("users", users); st.rerun()

    elif nav == "📜 深度日志审计":
        st.title("📜 全球行动审计日志")
        st.dataframe(load_data("logs"), use_container_width=True)

    if st.sidebar.button("安全退出系统"):
        st.session_state.clear(); st.rerun()
