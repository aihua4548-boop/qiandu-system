import streamlit as st
import pandas as pd
import os
import json
import uuid
import urllib.parse
from datetime import datetime

# --- 1. 全球通讯死锁路由 (针对越南、泰国、俄罗斯实战锁死) ---
COMM_LOCK = {
    "Vietnam (越南)": {"tool": "Zalo", "url": "https://zalo.me/", "icon": "🔵", "code": "84"},
    "Thailand (泰国)": {"tool": "Line", "url": "https://line.me/R/ti/p/~", "icon": "🇹🇭", "code": "66"},
    "Russia (俄罗斯)": {"tool": "Telegram", "url": "https://t.me/+", "icon": "🇷🇺", "code": "7"},
    "Indonesia (印尼)": {"tool": "WhatsApp", "url": "https://wa.me/", "icon": "🇮🇩", "code": "62"},
}

# --- 2. 深度 AI 战略画像 (QIANDU 实战逻辑) ---
def get_ai_intel(name, addr):
    ctx = (str(name) + str(addr)).lower()
    # 批发身份判定
    is_ws = any(k in ctx for k in ["wholesale", "distributor", "卸", "tổng kho", "sỉ", "опт", "ค้าส่ง"])
    p_level = "🚀 战略级批发商" if is_ws else "🏪 零售门店"
    p_star = "⭐⭐⭐⭐⭐" if is_ws else "⭐⭐⭐"
    # 商圈价值评估
    is_prime = any(c in ctx for c in ["hcm", "district 1", "quận 1", "bangkok", "sukhumvit", "myeongdong"])
    p_loc = "🔥 黄金商圈" if is_prime else "📍 普通商圈"
    # 针对性建议
    p_rec = "建议：直接谈【货柜级】Jmella" if is_ws else "建议：进驻 meloMELI 潮玩柜"
    return p_level, p_star, p_loc, p_rec

# --- 3. 权限持久化管理 (离职人员清除逻辑) ---
AUTH_FILE = "staff_auth.json"
def load_auth():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f: return json.load(f)
    return {"666888": {"name": "Founder", "time": "Master"}}

def save_auth(data):
    with open(AUTH_FILE, "w") as f: json.dump(data, f)

# --- 4. 界面展示 ---
st.set_page_config(page_title="QIANDU Global Command", layout="wide", page_icon="🌍")

if "auth_ok" not in st.session_state: st.session_state["auth_ok"] = False

if not st.session_state["auth_ok"]:
    st.title("🛡️ QIANDU 全球指挥终端 V30.0")
    with st.form("gate"):
        u, p = st.text_input("指挥官账号"), st.text_input("授权码", type="password")
        if st.form_submit_button("进入指挥系统"):
            auth_list = load_auth()
            if u == "admin" and (p == "666888" or p in auth_list): 
                st.session_state["auth_ok"] = True; st.rerun()
else:
    st.sidebar.title("🌍 千渡全球运营中心")
    nav = st.sidebar.radio("核心导航", ["📊 实战情报库", "🎫 授权管理(人员清除)"])

    if nav == "📊 实战情报库":
        st.title("📊 战略情报分析中心 (AI V3.0)")
        files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx'))]
        if files:
            sel_f = st.sidebar.selectbox("📂 选择同步数据集", files)
            df = pd.read_excel(sel_f) if sel_f.endswith('.xlsx') else pd.read_csv(sel_f)
            df = df.dropna(how='all')

            st.sidebar.divider()
            st.sidebar.subheader("⚙️ 字段物理校准")
            cols = list(df.columns)
            c_name = st.sidebar.selectbox("🏠 确认哪一列是【店名】", cols, index=0)
            c_phone = st.sidebar.selectbox("📞 确认哪一列是【电话号码】", cols, index=min(1, len(cols)-1))
            c_addr = st.sidebar.selectbox("📍 确认哪一列是【详细地址】", cols, index=min(2, len(cols)-1))

            grid = st.columns(2)
            for i, (idx, row) in enumerate(df.head(150).iterrows()):
                name, phone, addr = str(row[c_name]), str(row[c_phone]), str(row.get(c_addr, "-"))
                
                # 通讯死锁：暴力清洗，补全 0 号段
                raw_p = "".join(filter(str.isdigit, str(phone)))
                clean_p = "84" + raw_p[1:] if raw_p.startswith('0') and len(raw_p) >= 10 else raw_p
                
                t_conf = {"tool": "WhatsApp", "url": "https://wa.me/", "icon": "🌍"}
                for k, v in COMM_LOCK.items():
                    if clean_p.startswith(v["code"]):
                        t_conf = {"tool": v["tool"], "url": v["url"], "icon": v["icon"]}
                        break
                
                p_level, p_star, p_loc, p_rec = get_ai_intel(name, addr)

                with grid[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {t_conf['icon']} {name}")
                        col_l, col_r = st.columns([1.1, 1])
                        with col_l:
                            st.write(f"📞 **电话:** `{phone}`")
                            st.caption(f"📍 **位置:** {addr}")
                            st.link_button(f"🚀 发起 {t_conf['tool']} 洽谈", f"{t_conf['url']}{clean_p}", use_container_width=True, type="primary")
                        with col_r:
                            st.info("💡 **AI 商业情报**")
                            st.markdown(f"🏆 **能级:** `{p_level}`")
                            st.markdown(f"🔥 **地段:** `{p_loc}`")
                            st.markdown(f"📦 **战术:** `{p_rec}`")

                        # 情报矩阵
                        st.divider()
                        enc_n = urllib.parse.quote(name)
                        s1, s2, s3, s4 = st.columns(4)
                        with s1: st.link_button("FB", f"https://www.facebook.com/search/top/?q={enc_n}")
                        with s2: st.link_button("Ins", f"https://www.google.com/search?q={enc_n}+instagram")
                        with s3: st.link_button("TT", f"https://www.tiktok.com/search?q={enc_n}")
                        with s4: st.link_button("Map", f"https://www.google.com/maps/search/{enc_n}")

    elif nav == "🎫 授权管理(人员清除)":
        st.title("🎫 团队权限管理中心")
        auth_data = load_auth()
        
        with st.expander("✨ 为新员工签发授权码"):
            staff_name = st.text_input("员工姓名")
            if st.button("激活并生成"):
                new_code = str(uuid.uuid4())[:8].upper()
                auth_data[new_code] = {"name": staff_name, "time": datetime.now().strftime("%Y-%m-%d")}
                save_auth(auth_data)
                st.success(f"已为 {staff_name} 生成授权码: {new_code}")

        st.subheader("👥 当前活跃员工名单")
        for code, info in list(auth_data.items()):
            if code == "666888": continue
            c1, c2, c3 = st.columns([1, 2, 1])
            c1.code(code)
            c2.write(f"👤 {info['name']} (签发: {info['time']})")
            if c3.button("🔴 吊销权限", key=code):
                del auth_data[code]
                save_auth(auth_data)
                st.rerun()

    if st.sidebar.button("🚪 安全退出"): st.session_state["auth_ok"] = False; st.rerun()
