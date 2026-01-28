import streamlit as st
import pandas as pd
import os
import json
import uuid
import urllib.parse
from datetime import datetime

# --- 1. 全球通讯硬路由 (物理锁死) ---
PROTOCOL_MATRIX = {
    "Vietnam (越南)": {"tool": "Zalo", "url": "https://zalo.me/", "icon": "🔵", "code": "84"},
    "Thailand (泰国)": {"tool": "Line", "url": "https://line.me/R/ti/p/~", "icon": "🇹🇭", "code": "66"},
    "Russia (俄罗斯)": {"tool": "Telegram", "url": "https://t.me/+", "icon": "🇷🇺", "code": "7"},
    "Indonesia (印尼)": {"tool": "WhatsApp", "url": "https://wa.me/", "icon": "🇮🇩", "code": "62"},
}

# --- 2. QIANDU 深度 AI 智能推演引擎 ---
def get_advanced_ai_bi(name, addr):
    ctx = (str(name) + str(addr)).lower()
    
    # A. 商业角色判定
    is_ws = any(k in ctx for k in ["wholesale", "distributor", "tổng kho", "sỉ", "опт", "ค้าส่ง", "卸", "grosir"])
    is_chain = any(k in ctx for k in ["chain", "mall", "department", "plaza", "hệ thống"])
    
    if is_ws: p_type, p_tag = "🚀 战略级批发商", "货柜单/大单"
    elif is_chain: p_type, p_tag = "🏢 连锁渠道", "多点铺货"
    else: p_type, p_tag = "🏪 零售门店", "潮玩单品"

    # B. 商圈能级评估 (聚焦胡志明、曼谷、首尔等)
    hot_zones = ["district 1", "quận 1", "district 3", "quận 3", "district 7", "sukhumvit", "myeongdong", "gangnam"]
    is_prime = any(z in ctx for z in hot_zones)
    p_loc = "🔥 黄金商圈" if is_prime else "📍 基础地段"
    
    # C. 千渡专属战术建议
    if is_ws:
        p_rec = "建议：深度面谈【Jmella】月均 18 柜级订单"
    elif is_prime:
        p_rec = f"建议：进驻【meloMELI】展柜，主打爆款洁面"
    else:
        p_rec = "建议：推介新品牌【宫畔 Gōng Pàn】注册样品"
        
    return p_type, p_tag, p_loc, p_rec

# --- 3. 权限持久化管理 ---
AUTH_FILE = "staff_auth.json"
def load_auth():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f: return json.load(f)
    return {}

def save_auth(data):
    with open(AUTH_FILE, "w") as f: json.dump(data, f)

# --- 4. 指挥中心界面 ---
st.set_page_config(page_title="QIANDU V20.0", layout="wide", page_icon="💄")

if "auth_ok" not in st.session_state: st.session_state["auth_ok"] = False

if not st.session_state["auth_ok"]:
    st.title("🛡️ QIANDU 全球指挥终端 V20.0")
    with st.form("gate"):
        u, p = st.text_input("指挥官账号"), st.text_input("授权码", type="password")
        if st.form_submit_button("进入千渡实战系统"):
            if u == "admin" and p == "666888": st.session_state["auth_ok"] = True; st.rerun()
else:
    st.sidebar.title("🌍 千渡全球运营中心")
    nav = st.sidebar.radio("导航系统", ["📊 实战情报库", "🎫 授权管理(人员清除)"])

    if nav == "📊 实战情报库":
        st.title("📊 战略情报分析中心 (AI V2.0)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("📂 选择同步数据集", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all')

            # 字段物理校准
            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 字段物理校准")
            cols = list(df.columns)
            c_name = st.sidebar.selectbox("🏠 确认店名所在列", cols, index=0)
            c_phone = st.sidebar.selectbox("📞 确认电话所在列", cols, index=min(1, len(cols)-1))
            c_addr = st.sidebar.selectbox("📍 确认地址所在列", cols, index=min(2, len(cols)-1))

            q = st.text_input("🔍 搜索关键词 (如: 批发, Quận 1, Jmella)...", "")
            if q: df = df[df.apply(lambda r: q.lower() in str(r).lower(), axis=1)]

            # 仪表盘
            m1, m2, m3 = st.columns(3)
            m1.metric("监测商户", len(df))
            m2.metric("当前数据源", sel_f)
            m3.metric("AI 策略引擎", "深度学习模式")

            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(100).iterrows()):
                name, phone, addr = str(row[c_name]), str(row[c_phone]), str(row.get(c_addr, "-"))
                
                # 通讯协议死锁
                raw_num = "".join(filter(str.isdigit, str(phone)))
                clean_p = "84" + raw_num[1:] if raw_num.startswith('0') and len(raw_num) >= 10 else raw_num
                
                t_conf = {"tool": "WhatsApp", "url": "https://wa.me/", "icon": "🌍"}
                for k, v in PROTOCOL_MATRIX.items():
                    if clean_p.startswith(v["code"]):
                        t_conf = {"tool": v["tool"], "url": v["url"], "icon": v["icon"]}
                        break
                
                p_type, p_tag, p_loc, p_rec = get_advanced_ai_bi(name, addr)

                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {t_conf['icon']} {name}")
                        col_l, col_r = st.columns([1.2, 1])
                        with col_l:
                            st.write(f"📞 **电话:** `{phone}`")
                            st.caption(f"📍 **位置:** {addr}")
                            st.link_button(f"🚀 发起 {t_conf['tool']} 业务洽谈", f"{t_conf['url']}{clean_p}", use_container_width=True, type="primary")
                        with col_r:
                            st.info("💡 **AI 商业情报**")
                            st.markdown(f"🏆 **性质:** `{p_type}`")
                            st.markdown(f"🔥 **地段:** `{p_loc}`")
                            st.markdown(f"📦 **战术:** `{p_rec}`")

                        # 四维嗅探
                        st.divider()
                        enc_n = urllib.parse.quote(name)
                        s1, s2, s3, s4 = st.columns(4)
                        with s1: st.link_button("FB", f"https://www.facebook.com/search/top/?q={enc_n}")
                        with s2: st.link_button("Ins", f"https://www.google.com/search?q={enc_n}+instagram")
                        with s3: st.link_button("TikTok", f"https://www.tiktok.com/search?q={enc_n}")
                        with s4: st.link_button("Map", f"https://www.google.com/maps/search/{enc_n}+{addr}")

    elif nav == "🎫 授权管理(人员清除)":
        st.title("🎫 团队授权与访问控制")
        auth_data = load_auth()
        
        # A. 签发新授权
        with st.expander("✨ 签发新授权码"):
            new_staff = st.text_input("员工姓名/备注")
            if st.button("生成并激活"):
                new_code = str(uuid.uuid4())[:8].upper()
                auth_data[new_code] = {"name": new_staff, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
                save_auth(auth_data)
                st.success(f"授权码已激活: {new_code}")

        # B. 名单管理 (删除离职员工)
        st.subheader("👥 当前有效授权名单")
        if auth_data:
            for code, info in list(auth_data.items()):
                c1, c2, c3 = st.columns([1, 2, 1])
                c1.code(code)
                c2.write(f"👤 {info['name']} (签发于: {info['time']})")
                if c3.button("🔴 吊销权限", key=code):
                    del auth_data[code]
                    save_auth(auth_data)
                    st.rerun()
        else:
            st.info("当前无活跃授权记录")

    if st.sidebar.button("🚪 安全退出"): st.session_state["auth_ok"] = False; st.rerun()
