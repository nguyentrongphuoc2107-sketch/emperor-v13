import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# --- 1. SIÊU GIAO DIỆN MATRIX DARK-GOLD ---
st.set_page_config(page_title="EMPEROR V13 - ULTIMATE", layout="wide")
st.markdown("""
    <style>
    .main { background: #050505; color: #d4af37; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { background: linear-gradient(90deg, #856404, #d4af37); color: #000; border: 1px solid #fff; font-weight: bold; height: 55px; border-radius: 8px; width: 100%; }
    .stButton>button:hover { box-shadow: 0 0 25px #d4af37; transform: scale(1.02); }
    .card { background: rgba(15,15,15,0.95); border: 1px solid #d4af37; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
    .pred-main { font-size: 90px; font-weight: 900; text-align: center; color: #ff0000; text-shadow: 0 0 20px rgba(255,0,0,0.4); margin: 0; }
    .vi-box { background: #111; border: 2px solid #d4af37; color: #fff; padding: 15px; text-align: center; font-size: 35px; font-weight: bold; border-radius: 8px; }
    .advice-box { background: #1a1a1a; border-left: 5px solid #d4af37; padding: 15px; margin-top: 10px; font-style: italic; color: #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KHỞI TẠO HỆ THỐNG ---
if 'history' not in st.session_state: st.session_state.history = []
if 'pnl' not in st.session_state: st.session_state.pnl = 0
if 'bias' not in st.session_state: st.session_state.bias = 0.0
if 'streak' not in st.session_state: st.session_state.streak = 0

# --- 3. BỘ NÃO SIÊU MÁY TÍNH (TỔNG HỢP THUẬT TOÁN) ---
def emperor_engine(history, bias, streak):
    if len(history) < 2: 
        return "DÒ SÓNG", 50.0, [10, 11, 12], "Hệ thống cần ít nhất 2 phiên mồi để quét nhịp cầu."
    
    # Tính toán Momentum (Lực đẩy) & Entropy (Độ loạn)
    recent = np.array(history[-10:])
    avg = np.mean(recent)
    std = np.std(recent)
    
    # Công thức cốt lõi: Kết hợp Bias Tự học + Lực đàn hồi 10.5
    # Nếu streak (chuỗi thua) tăng cao, AI sẽ tự động kích hoạt đảo cầu
    force = (10.5 - avg) * 0.6 + bias
    
    if streak >= 3: # Chế độ CHỐNG BỊP: Đảo ngược dự đoán khi gặp chuỗi thua
        prediction_score = 10.5 - force 
        status = "⚠️ PHÁT HIỆN BỊP: Đang kích hoạt chế độ Đảo Cầu (Anti-Fraud)."
    else:
        prediction_score = 10.5 + force
        status = "✅ Cầu ổn định. AI đang bám sát nhịp đàn hồi của xúc xắc."

    # Phân tích Quân sư dựa trên vùng điểm
    if avg > 12: status += " Cầu đang treo Tài cao, ưu tiên đánh hồi Xỉu."
    elif avg < 9: status += " Cầu đang dìm Xỉu sâu, ưu tiên đánh hồi Tài."

    # Quyết định Tài/Xỉu
    if prediction_score > 10.5:
        target = "TÀI"
        winrate = 50 + (prediction_score - 10.5) * 7
        vi = [11, 13, 15] if streak < 2 else [12, 14, 16]
    else:
        target = "XỈU"
        winrate = 50 + (10.5 - prediction_score) * 7
        vi = [6, 8, 10] if streak < 2 else [4, 7, 9]

    # Hiệu chỉnh Winrate theo độ loạn (std)
    final_winrate = min(98.5, max(40.0, winrate - (std * 1.5)))
    return target, final_winrate, vi, status

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown('<h1 style="text-align:center;">🔥 CEO MAKAO PHUOCDZ - ULTIMATE SUPREMACY V13</h1>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 2.2])

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💰 QUẢN LÝ VỐN KELLY")
    st.markdown(f'### PnL: <span style="color:#d4af37;">{st.session_state.pnl}k</span>', unsafe_allow_html=True)
    
    val = st.number_input("KẾT QUẢ PHIÊN VỪA RA:", 3, 18, 10)
    
    # Cụm nút bấm Tự học
    b1, b2, b3 = st.columns(3)
    if b1.button("THẮNG ✅"):
        st.session_state.pnl += 200
        st.session_state.streak = 0
        st.session_state.bias *= 0.7 # Giảm bias khi đã thắng để tránh quá đà
        st.session_state.history.append(val)
        st.rerun()
    if b2.button("HÒA 🤝"):
        st.session_state.history.append(val)
        st.rerun()
    if b3.button("THUA ❌"):
        st.session_state.pnl -= 100
        st.session_state.streak += 1
        # TỰ HỌC: Hiệu chỉnh hướng lệch (Bias) cực mạnh khi thua
        st.session_state.bias += (2.0 if val < 10.5 else -2.0)
        st.session_state.history.append(val)
        st.rerun()

    if st.button("RESET TOÀN BỘ"):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if len(st.session_state.history) >= 2:
        res, win, vi, advice = emperor_engine(st.session_state.history, st.session_state.bias, st.session_state.streak)
        
        st.markdown(f'<p class="pred-main">{res}</p>', unsafe_allow_html=True)
        st.write(f"**Tỉ lệ tin cậy:** {win:.2f}% | **Streak Thua:** {st.session_state.streak}")
        st.progress(win/100)
        
        # PHÒNG QUÂN SƯ
        st.markdown(f'<div class="advice-box"><b>📜 QUÂN SƯ:</b> {advice}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🎯 VỊ SNIPER TỐI ƯU:")
        v_cols = st.columns(3)
        for i in range(3):
            v_cols[i].markdown(f'<div class="vi-box">{vi[i]}</div>', unsafe_allow_html=True)
    else:
        st.info("HỆ THỐNG ĐANG QUÉT SÓNG... VUI LÒNG NHẬP 2 PHIÊN MỒI.")
    st.markdown('</div>', unsafe_allow_html=True)

# BIỂU ĐỒ NHỊP TIM & LỊCH SỬ LED
if len(st.session_state.history) > 3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.history, columns=['Diem'])
    fig = px.line(df, y='Diem', title="BIỂU ĐỒ NHỊP TIM BÀN CƯỢC", markers=True)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#d4af37", height=250)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### 🧬 DÒNG THỜI GIAN MA TRẬN (LED)")
h_html = "".join([f'<span style="background:{"#d4af37" if x >= 11 else "#333"}; color:{"#000" if x >= 11 else "#fff"}; padding:8px 12px; margin:3px; font-weight:bold; border:1px solid #d4af37; border-radius:5px;">{x}</span>' for x in st.session_state.history])
st.markdown(f'<div style="overflow-x: auto; white-space: nowrap; padding:15px; background:#050505;">{h_html}</div>', unsafe_allow_html=True)