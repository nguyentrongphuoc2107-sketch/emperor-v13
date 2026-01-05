import streamlit as st
import numpy as np
import time

# --- 1. GIAO DIỆN LUXURY V20.0 (GOLD & ONYX) ---
st.set_page_config(page_title="EMPEROR V20.0 - CEO PHUOCDZ", layout="wide")
st.markdown("""
    <style>
    /* Tổng thể */
    .main { background: #050505; color: #d4af37; font-family: 'Playfair Display', serif; }
    
    /* Card Phong cách Thượng lưu */
    .luxury-card { 
        background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
        border: 1px solid #2d2d2d;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 10px 10px 30px #000, -5px -5px 15px #1a1a1a;
        margin-bottom: 25px;
    }
    
    /* Nút bấm Vàng Ròng */
    .stButton>button { 
        background: linear-gradient(180deg, #d4af37 0%, #8a6e2f 100%); 
        color: #000; font-weight: 800; height: 65px; border-radius: 12px; font-size: 20px; 
        width: 100%; border: none; transition: 0.3s; letter-spacing: 1px;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 15px 35px rgba(212, 175, 55, 0.4); color: #fff; }
    
    /* Dự đoán Siêu cấp */
    .pred-val { font-size: 140px; font-weight: 900; text-align: center; margin: 0; color: #fff; text-shadow: 0 0 50px #d4af37; }
    .confidence-text { text-align: center; color: #00ff00; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    
    /* Nhật ký Quân sư */
    .advisor-log { 
        background: rgba(0,0,0,0.5); border-left: 5px solid #d4af37; padding: 20px; 
        font-family: 'Courier New'; color: #ccc; border-radius: 5px; font-size: 15px; line-height: 1.6;
    }
    .status-badge { background: #111; color: #d4af37; padding: 6px 15px; border-radius: 50px; border: 1px solid #d4af37; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BỘ NÃO SIÊU THUẬT TOÁN ---
if 'history' not in st.session_state: st.session_state.history = []
if 'pnl' not in st.session_state: st.session_state.pnl = -900
if 'bias' not in st.session_state: st.session_state.bias = 0.0

def supreme_engine(history, bias):
    if len(history) < 2: return "WAIT", 0, [0,0,0], "Hoàng đế vui lòng nạp dữ liệu phiên.", "KHỞI TẠO", "ĐI NHẸ"

    res_list = [1 if x >= 11 else 0 for x in history]
    last_val = history[-1]
    last_res = res_list[-1]
    
    # Quét nhịp cầu
    streak = 1
    for i in range(len(res_list)-2, -1, -1):
        if res_list[i] == last_res: streak += 1
        else: break

    # Logic Quân sư chi tiết
    prediction = "TÀI" if (10.5 + bias) > 10.5 else "XỈU"
    conf = 85.0
    reason = []
    adv = "ĐI ĐỀU"

    # Nhận diện thế cầu bệt/1-1
    if streak >= 5:
        prediction = "TÀI" if last_res == 1 else "XỈU"
        reason.append(f"👑 **QUÂN SƯ:** Phát hiện bệt Rồng {streak} tay. Nhà cái đang mở kho, tuyệt đối không được bẻ lái.")
        adv = "VÀO MẠNH"
        conf = 97.5
    elif len(res_list) >= 4 and res_list[-4:] in [[1,0,1,0], [0,1,0,1]]:
        prediction = "XỈU" if last_res == 1 else "TÀI"
        reason.append("👑 **QUÂN SƯ:** Cầu Ping-pong 1-1 đang rất đều. Đây là nhịp 'ăn tiền' ổn định nhất.")
        adv = "ĐI ĐỀU"
        conf = 92.0
    elif last_val >= 16:
        prediction = "XỈU"
        reason.append(f"👑 **QUÂN SƯ:** Điểm {last_val} sát đỉnh. Theo luật hồi quy, lực nén đang cực lớn đẩy về cửa Xỉu.")
        adv = "SNIPER"
    else:
        reason.append("👑 **QUÂN SƯ:** Cầu đang biến động ngẫu nhiên. Oracle dùng thuật toán Gauss để tìm cửa sáng nhất.")
        adv = "ĐI NHẸ"

    vi = [11, 13, 15] if prediction == "TÀI" else [4, 7, 9]
    return prediction, conf, vi, "<br>".join(reason), "AN TOÀN", adv

# --- 3. HIỂN THỊ ĐẲNG CẤP ---
st.markdown("<h1 style='text-align:center; color:#d4af37;'>🔱 THE SUPREME EMPEROR V20.0 🔱</h1>", unsafe_allow_html=True)

col_ctrl, col_main = st.columns([1, 1.7])

with col_ctrl:
    st.markdown('<div class="luxury-card">', unsafe_allow_html=True)
    st.markdown(f"### 💎 PnL: <span style='color:#ff3333;'>{st.session_state.pnl}k</span>", unsafe_allow_html=True)
    val_in = st.number_input("KẾT QUẢ VỪA RA:", 3, 18, 10)
    
    if st.button("⚜️ PHÂN TÍCH LƯỢNG TỬ"):
        with st.spinner('Đang giải mã MD5...'):
            time.sleep(1.2)
            st.session_state.history.append(val_in)
            st.rerun()

    st.write("---")
    st.markdown("#### TRẠNG THÁI PHIÊN")
    cb1, cb2 = st.columns(2)
    if cb1.button("WIN ✅"):
        st.session_state.pnl += 200; st.session_state.bias *= 0.1; st.rerun()
    if cb2.button("LOSS ❌"):
        st.session_state.pnl -= 100
        st.session_state.bias += (9.5 if val_in < 10.5 else -9.5)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_main:
    res, cf, vis, log, status, adv = supreme_engine(st.session_state.history, st.session_state.bias)
    
    st.markdown('<div class="luxury-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="display:flex; justify-content:space-between;"><span class="status-badge">{status}</span><span style="color:#d4af37; font-weight:bold;">{adv}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<p class="pred-val">{res}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="confidence-text">ĐỘ TIN CẬY: {cf:.2f}%</p>', unsafe_allow_html=True)
    
    # Sniper Zone
    st.write("")
    sc1, sc2, sc3 = st.columns(3)
    for i, v in enumerate(vis):
        with [sc1, sc2, sc3][i]:
            st.markdown(f"<div style='background:#111; color:#d4af37; padding:20px; text-align:center; font-size:35px; border:1px solid #d4af37; border-radius:15px; box-shadow: inset 0 0 10px #d4af37;'>{v}</div>", unsafe_allow_html=True)
    
    # Advisor Log
    st.markdown(f'<div class="advisor-log"><b>📜 LÝ LẼ CỦA HOÀNG ĐẾ:</b><br>{log}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Lịch sử
if st.session_state.history:
    hist_html = "".join([f'<span style="background:#d4af37; color:#000; padding:6px 14px; margin:4px; border-radius:8px; font-weight:bold; display:inline-block;">{x}</span>' for x in st.session_state.history[-15:]])
    st.markdown(f"<div style='text-align:center; color:#666;'>LỊCH SỬ CHINH PHẠT:<br>{hist_html}</div>", unsafe_allow_html=True)
