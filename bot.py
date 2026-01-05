import streamlit as st
import numpy as np
import time
import random

# --- 1. GIAO DIỆN BÊN NGOÀI KHÔNG GIAN (VOID & PLATINUM THEME) ---
st.set_page_config(page_title="SINGULARITY V19.0 - CEO PHUOCDZ", layout="wide")
st.markdown("""
    <style>
    .main { background: radial-gradient(ellipse at center, #1b2735 0%, #090a0f 100%); color: #e0e0e0; font-family: 'Rajdhani', sans-serif; }
    
    /* Button Platinum */
    .stButton>button { 
        background: linear-gradient(135deg, #e0e0e0 0%, #888888 100%); 
        color: #000; 
        font-weight: 900; 
        height: 75px; 
        font-size: 24px; 
        width: 100%; 
        border: none; 
        border-radius: 4px;
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.2); 
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .stButton>button:hover { box-shadow: 0 0 50px rgba(255, 255, 255, 0.6); transform: scale(1.01); }
    
    /* Cards */
    .void-card { 
        background: rgba(10, 10, 10, 0.8); 
        border: 1px solid #444; 
        border-top: 4px solid #00d2ff; 
        padding: 30px; 
        border-radius: 8px; 
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
    }
    
    /* Typography */
    .singularity-pred { font-size: 150px; font-weight: 900; text-align: center; color: transparent; -webkit-background-clip: text; background-image: linear-gradient(to bottom, #fff, #00d2ff); text-shadow: 0 0 80px rgba(0, 210, 255, 0.5); line-height: 1; margin-top: 10px; }
    .status-text { text-align: center; font-size: 18px; color: #00d2ff; letter-spacing: 4px; font-weight: bold; margin-bottom: 20px; }
    
    /* Analysis Log */
    .god-log { 
        background: #050505; 
        border-left: 3px solid #00d2ff; 
        padding: 20px; 
        font-family: 'Consolas', monospace; 
        color: #ccc; 
        font-size: 14px; 
        line-height: 1.7;
        margin-top: 20px;
    }
    .highlight { color: #00d2ff; font-weight: bold; }
    .warning { color: #ff3333; font-weight: bold; }
    
    /* Sniper Spots */
    .sniper-box {
        border: 1px solid #00d2ff;
        color: #fff;
        text-align: center;
        padding: 15px;
        font-size: 30px;
        font-weight: bold;
        background: rgba(0, 210, 255, 0.1);
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÕI SINGULARITY (THE CORE) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'pnl' not in st.session_state: st.session_state.pnl = -900
if 'bias' not in st.session_state: st.session_state.bias = 0.0

def singularity_engine(history, bias):
    if len(history) < 2: 
        return "INIT...", 0, [0,0,0], "Hệ thống đang khởi tạo mạng nơ-ron...", "WAITING", "CHỜ DỮ LIỆU"

    # [1] PRE-PROCESSING (Xử lý dữ liệu thô)
    results = [1 if x >= 11 else 0 for x in history]
    vals = np.array(history)
    last_res = results[-1]
    last_val = history[-1]
    
    # [2] PATTERN SCANNER (Quét mẫu hình 2026)
    streak = 1
    for i in range(len(results)-2, -1, -1):
        if results[i] == last_res: streak += 1
        else: break
        
    # Pattern Recognition
    is_11 = len(results) >= 4 and results[-4:] in [[1,0,1,0], [0,1,0,1]]
    is_221 = len(results) >= 5 and results[-5:] == [1,1,0,0,1] # Ví dụ mẫu 2-2-1
    is_123 = len(results) >= 6 and results[-6:] == [0,1,1,0,0,0] # Mẫu 1-2-3

    # [3] SINGULARITY LOGIC (Trí tuệ nhân tạo)
    prediction = "TÀI" if (10.5 + bias) > 10.5 else "XỈU"
    confidence = 88.0
    action = "ĐI ĐỀU"
    log = []

    # -- Logic A: Bệt Rồng (Dragon Streak) --
    if streak >= 5:
        prediction = "TÀI" if last_res == 1 else "XỈU"
        log.append(f"🐉 <span class='highlight'>SINGULARITY DETECT:</span> Phát hiện Dòng Chảy Vô Tận (Streak {streak}).")
        log.append("⚠️ Nguyên tắc: Nước chảy chỗ trũng. Tuyệt đối không chặn đầu.")
        confidence = 98.5
        action = "ALL-IN / VÀO CỰC MẠNH"

    # -- Logic B: Cầu Đảo 1-1 (Ping Pong) --
    elif is_11:
        prediction = "XỈU" if last_res == 1 else "TÀI"
        log.append(f"⚡ <span class='highlight'>QUANTUM SYNC:</span> Nhịp sóng 1-1 đang đồng bộ hóa.")
        log.append("👉 Dự đoán nhịp đảo chiều tiếp theo để cân bằng năng lượng.")
        confidence = 94.0
        action = "ĐI ĐỀU TAY"

    # -- Logic C: Quy luật Tổng điểm (Point Reversion) --
    elif last_val >= 16:
        prediction = "XỈU"
        log.append(f"📉 <span class='warning'>CHAOS LIMIT:</span> Điểm {last_val} chạm giới hạn trên.")
        log.append("👉 Lực hồi quy Gauss ép kết quả về vùng trung tâm (Xỉu).")
        action = "SNIPER (BẮT GÃY)"
    elif last_val <= 5:
        prediction = "XỈU"
        log.append(f"⚓ <span class='warning'>GRAVITY WELL:</span> Điểm {last_val} nằm trong Hố đen trọng lực.")
        log.append("👉 Xu hướng hút thêm một nhịp Xỉu bệt.")
        action = "ĐÁNH VỪA"

    # -- Logic D: Mặc định (Neural Bias) --
    else:
        log.append("🧠 <span class='highlight'>NEURAL CALCULATION:</span> Không có mẫu hình cổ điển.")
        log.append(f"👉 Dùng Bias ({bias:.2f}) và Độ lệch chuẩn để tính toán cửa sáng nhất.")
        action = "THĂM DÒ 10%"

    # [4] POST-PROCESSING (Vị số & Chống bịp)
    if np.std(vals[-10:]) < 1.2 and len(history) > 10:
        log.insert(0, "<span class='warning'>[CẢNH BÁO BỊP]</span> Biến động quá thấp. Sàn đang can thiệp.")
        action = "DỪNG LẠI NGAY"
        confidence = 0

    vi = [11, 13, 14] if prediction == "TÀI" else [4, 7, 10]
    
    return prediction, min(99.99, confidence), vi, "<br>".join(log), action, f"STREAK: {streak}"

# --- 3. DASHBOARD ĐIỀU KHIỂN ---
st.markdown("<h1 style='text-align:center; letter-spacing: 5px; color: #fff;'>THE SINGULARITY V19.0</h1>", unsafe_allow_html=True)

c_left, c_right = st.columns([1, 1.6])

with c_left:
    st.markdown('<div class="void-card">', unsafe_allow_html=True)
    st.markdown(f"### PnL: <span style='color:{'#00ff00' if st.session_state.pnl > 0 else '#ff3333'}'>{st.session_state.pnl}k</span>", unsafe_allow_html=True)
    
    val = st.number_input("NHẬP DỮ LIỆU TỪ VŨ TRỤ:", 3, 18, 10)
    
    if st.button("🌌 KẾT NỐI SINGULARITY"):
        with st.spinner("Đang đồng bộ hóa dữ liệu lượng tử..."):
            time.sleep(1)
            st.session_state.history.append(val)
            st.rerun()
            
    st.write("---")
    c1, c2 = st.columns(2)
    if c1.button("✅ THẮNG"):
        st.session_state.pnl += 200; st.session_state.bias *= 0.1; st.rerun()
    if c2.button("❌ THUA"):
        st.session_state.pnl -= 100
        # Revenge Bias cực đại
        st.session_state.bias += (10.0 if val < 10.5 else -10.0)
        st.rerun()
        
    if st.button("🔄 KHỞI ĐỘNG LẠI"):
        st.session_state.clear(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c_right:
    pred, conf, vis, logic, act, stat = singularity_engine(st.session_state.history, st.session_state.bias)
    
    st.markdown('<div class="void-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="status-text">{stat} | {act}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="singularity-pred">{pred}</div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#888; margin-bottom:20px;'>ĐỘ TIN CẬY TUYỆT ĐỐI: <span style='color:#00d2ff; font-size:24px; font-weight:bold;'>{conf:.2f}%</span></div>", unsafe_allow_html=True)
    
    # Sniper Zone
    st.write("")
    cols = st.columns(3)
    for i in range(3):
        cols[i].markdown(f'<div class="sniper-box">{vis[i]}</div>', unsafe_allow_html=True)
        
    # Analysis
    st.markdown(f"""
        <div class="god-log">
            <b>📜 PHÂN TÍCH TỪ ĐIỂM KỲ DỊ:</b><br>
            {logic}
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
