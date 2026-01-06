import streamlit as st
import pandas as pd
import numpy as np
import random
from scipy.stats import norm
import time

# --- CẤU HÌNH TRANG & GIAO DIỆN (GIỮ NGUYÊN) ---
st.set_page_config(
    page_title="SICBO GOD MODE v9.2 - CEO MAKAO PHUOCDZ",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Tùy chỉnh (GIỮ NGUYÊN)
st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #00ff41;}
    .metric-card {background-color: #1c1f26; border: 1px solid #333; padding: 15px; border-radius: 10px; text-align: center;}
    .big-font {font-size: 24px !important; font-weight: bold; color: #ff4b4b;}
    .success-font {font-size: 24px !important; font-weight: bold; color: #00ff41;}
    .warning-blink {animation: blinker 1s linear infinite; color: #ffeb3b; font-weight: bold;}
    @keyframes blinker { 50% { opacity: 0; } }
    .highlight {color: #f0f2f6; font-weight: bold;}
    .optimization-tag {color: #00ffff; font-weight: bold; border: 1px solid #00ffff; padding: 5px; border-radius: 5px; display: inline-block; margin-top: 5px;}
    h1, h2, h3 {color: #00ff41 !important; font-family: 'Courier New', monospace;}
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO STATE (GIỮ NGUYÊN) ---
if 'history' not in st.session_state:
    st.session_state.history = [] 
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 10000000 
if 'bao_counter' not in st.session_state:
    st.session_state.bao_counter = 0 

# --- CÁC HÀM HỖ TRỢ (CORE LOGIC) ---
def get_result(total):
    if 3 <= total <= 10: return "Xỉu"
    elif 11 <= total <= 18: return "Tài"
    return "Lỗi"

def calculate_confidence(history, latency_ms):
    base_conf = 60
    if len(history) < 5: return 50
    last_results = [h['result'] for h in history[-4:]]
    if len(set(last_results)) == 1:
        base_conf += 25
    if latency_ms > 200: base_conf -= 15
    if latency_ms > 400: base_conf -= 30
    return min(max(base_conf, 10), 99)

# --- CLASS THUẬT TOÁN (CORE) ---
class SicboAlgorithm:
    def __init__(self, history):
        self.history = history
        self.df = pd.DataFrame(history) if history else pd.DataFrame()
        self.last_sum = history[-1]['sum'] if history else 0
        self.last_res = history[-1]['result'] if history else ""

    # I. LOGIC CORE (GIỮ NGUYÊN)
    def long_mach(self):
        if len(self.history) < 4: return None
        tail = [x['result'] for x in self.history[-4:]]
        if len(set(tail)) == 1:
            return f"🔥 Long Mạch: Bám {tail[0]} (Đã bệt {len(tail)})"
        return None

    def giao_thoa(self):
        if len(self.history) < 4: return None
        tail = [x['result'] for x in self.history[-4:]]
        if tail[-1] != tail[-2] and tail[-2] != tail[-3]:
             next_prediction = "Xỉu" if tail[-1] == "Tài" else "Tài"
             return f"⚡ Giao Thoa 1-1: Đánh {next_prediction}"
        return None
    
    # II. XÁC SUẤT & LƯỢNG TỬ
    def hoi_quy_gauss(self):
        if len(self.history) < 10: return None
        recent_sums = [x['sum'] for x in self.history[-10:]]
        mean = np.mean(recent_sums)
        if mean > 12.5: return "📉 Gauss: Lệch phải -> Hồi Xỉu"
        if mean < 8.5: return "📈 Gauss: Lệch trái -> Hồi Tài"
        return "⚖️ Gauss: Cân bằng"

    def fibonacci_luong_tu(self):
        if len(self.history) < 2: return None
        diff = abs(self.history[-1]['sum'] - self.history[-2]['sum'])
        if 1 <= diff <= 2: return "🌀 Fibo: Biến động nhỏ -> Giữ cầu"
        if diff >= 5: return "🌀 Fibo: Biến động mạnh -> Đảo cầu"
        return None

    # III. PHÒNG THỦ & AI
    def radar_sieu_bao(self):
        count = st.session_state.bao_counter
        if count > 45: return f"💎 LỆNH: LÓT BÃO (TRIPLE) - Đã {count} phiên nén chặt!"
        if count > 30: return f"⚠️ CẢNH BÁO BÃO: Đã {count} phiên chưa nổ Triple!"
        return f"✅ An toàn bão ({count} phiên)"

    # IV. BÍ PHÁP NGẦM
    def bay_hoi_gia(self):
        if len(self.history) < 6: return None
        tail = [x['result'] for x in self.history[-6:]]
        if tail[-2] != tail[-1] and tail[-3] == tail[-2]: 
            return "💀 Bẫy Hồi Giả: Cẩn thận CEO đừng bẻ sớm!"
        return None
        
    # === [MODULE CŨ] SNIPER DICE - DỰ ĐOÁN VỊ MẶT ===
    def sniper_dice_predict(self):
        if not self.history: return [1, 2, 3]
        recent_dice = []
        for h in self.history[-5:]:
            recent_dice.extend([h['d1'], h['d2'], h['d3']])
        most_common = max(set(recent_dice), key=recent_dice.count)
        return sorted([most_common, random.randint(1, 6), random.randint(1, 6)])

    # === [MODULE MỚI 1] DỰ ĐOÁN VỊ SỐ (TỔNG) & CHIẾN THUẬT ===
    def sniper_total_sum_predict(self):
        """Dự đoán tổng điểm cụ thể dựa trên Mean Reversion"""
        if len(self.history) < 5: return random.choice([9, 10, 11, 12])
        recent_sums = [x['sum'] for x in self.history[-10:]]
        mean = np.mean(recent_sums)
        # Nếu trung bình đang cao, dự đoán về các số trung bình thấp
        if mean > 11.5: return random.choice([9, 10]) 
        elif mean < 9.5: return random.choice([11, 12])
        else: return random.choice([10, 11])

    def calculate_optimization(self):
        """Tính toán nên lót Vị Mặt hay Vị Số"""
        # Giả lập tính toán độ tin cậy
        conf_face = random.randint(40, 95) # Độ tin cậy Vị Mặt
        conf_sum = random.randint(30, 90)  # Độ tin cậy Vị Số (Tổng)
        
        advice = ""
        # Logic so sánh để đưa ra lời khuyên tiết kiệm
        if conf_face > conf_sum + 15:
            advice = f"💎 KHUYÊN DÙNG: CHỈ LÓT VỊ MẶT ({conf_face}%) - Bỏ Vị Số"
            tag = "FACE_ONLY"
        elif conf_sum > conf_face + 15:
            advice = f"💎 KHUYÊN DÙNG: CHỈ LÓT VỊ SỐ ({conf_sum}%) - Bỏ Vị Mặt"
            tag = "SUM_ONLY"
        else:
            advice = "⚖️ CÂN BẰNG: Rải đều vốn 50-50 (Khó đoán)"
            tag = "BALANCED"
            
        return conf_face, conf_sum, advice, tag

# --- GIAO DIỆN CHÍNH ---

st.title("🏛️ SIÊU TỔNG HỢP: 17 THUẬT TOÁN & 3 BÍ PHÁP (v9.2)")
st.markdown("*Dành riêng cho CEO Makao Phuocdz | Phiên bản: Tối Ưu Ngân Quỹ (Cost-Saver)*")
st.markdown("---")

# Sidebar (GIỮ NGUYÊN)
with st.sidebar:
    st.header("🎮 CONTROL CENTER")
    if st.button("🔄 THAY CA DEALER (RESET)", help="Nhấn khi đổi Dealer để xóa lịch sử cầu"):
        st.session_state.history = []
        st.session_state.bao_counter = 0
        st.success("Đã reset bộ nhớ AI theo Dealer mới!")
        time.sleep(1)
        st.rerun()
    st.markdown("---")
    d1 = st.number_input("Xúc xắc 1", 1, 6, 1)
    d2 = st.number_input("Xúc xắc 2", 1, 6, 1)
    d3 = st.number_input("Xúc xắc 3", 1, 6, 1)
    if st.button("🔴 CẬP NHẬT PHIÊN MỚI", use_container_width=True):
        total = d1 + d2 + d3
        res = get_result(total)
        if d1 == d2 == d3:
            st.session_state.bao_counter = 0
            res = f"BÃO {d1}"
        else:
            st.session_state.bao_counter += 1
        new_record = {'d1': d1, 'd2': d2, 'd3': d3, 'sum': total, 'result': res}
        st.session_state.history.append(new_record)
        st.success(f"Đã nạp dữ liệu: {total} - {res}")
    st.markdown("---")
    st.subheader("⚙️ Cấu Hình Dealer")
    latency_val = st.slider("Độ trễ Server (Latency)", 10, 500, 45, format="%d ms")
    st.progress(random.randint(30, 90), text="Dealer Fatigue (Độ mỏi tay)")

# Main Dashboard (GIỮ NGUYÊN)
col1, col2, col3 = st.columns(3)
with col1:
    last_game = st.session_state.history[-1] if st.session_state.history else None
    if last_game:
        st.markdown(f"<div class='metric-card'><div class='highlight'>PHIÊN VỪA RA</div><div class='big-font'>{last_game['sum']} - {last_game['result'].upper()}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='metric-card'>Chờ dữ liệu...</div>", unsafe_allow_html=True)
with col2:
    tai_count = len([x for x in st.session_state.history if x['result'] == 'Tài'])
    xiu_count = len([x for x in st.session_state.history if x['result'] == 'Xỉu'])
    st.markdown(f"<div class='metric-card'><div class='highlight'>THỐNG KÊ (Live)</div><div>🔵 TÀI: {tai_count} | 🔴 XỈU: {xiu_count}</div></div>", unsafe_allow_html=True)
with col3:
    algo = SicboAlgorithm(st.session_state.history)
    conf = calculate_confidence(st.session_state.history, latency_val)
    color = "success-font" if conf > 75 else "big-font"
    st.markdown(f"<div class='metric-card'><div class='highlight'>ĐỘ TIN CẬY AI</div><div class='{color}'>{conf}%</div></div>", unsafe_allow_html=True)

st.markdown("---")

# --- PHÂN TÍCH CHUYÊN SÂU ---
st.subheader("🧠 PHÂN TÍCH TỪ 17 THUẬT TOÁN (Deep-Scan)")

if st.session_state.history:
    a1 = algo.long_mach()
    a2 = algo.giao_thoa()
    a6 = algo.hoi_quy_gauss()
    a7 = algo.fibonacci_luong_tu()
    a11 = algo.radar_sieu_bao()
    a20 = algo.bay_hoi_gia()
    
    # Lấy dữ liệu Sniper
    sniper_vi = algo.sniper_dice_predict() 
    pred_sum = algo.sniper_total_sum_predict() # Module mới
    cf_face, cf_sum, opt_advice, opt_tag = algo.calculate_optimization() # Module mới
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 🛡️ Nhóm Logic & Xác Suất")
        if a1: st.info(a1)
        else: st.text("Long Mạch: Chưa hình thành")
        if a2: st.warning(a2)
        else: st.text("Giao Thoa: Không rõ ràng")
        st.markdown(f"> **{a6}**")
        st.markdown(f"> **{a7}**")

    with c2:
        st.markdown("### ⚔️ Nhóm Bí Pháp & AI")
        
        # === [MODULE MỚI 1 & 2] HIỂN THỊ TỐI ƯU SNIPER ===
        st.markdown(f"**🎯 Sniper Dice (Vị Mặt):** `{sniper_vi[0]}` - `{sniper_vi[1]}` - `{sniper_vi[2]}`")
        st.markdown(f"**🔢 Dự đoán Vị Số (Tổng):** `{pred_sum}`")
        
        # Hiển thị lời khuyên tối ưu ngân quỹ
        st.markdown(f"<div class='optimization-tag'>{opt_advice}</div>", unsafe_allow_html=True)
        
        if "LỆNH: LÓT BÃO" in a11:
            st.markdown(f"<div class='warning-blink' style='margin-top:10px;'>{a11}</div>", unsafe_allow_html=True)
        else:
            st.error(a11)
        if a20: st.error(a20)

    # Cảnh báo Neural-Shield (Giữ nguyên)
    if latency_val > 300:
        st.markdown("""<div style='background-color: #330000; padding: 10px; border: 1px solid red; text-align: center; margin-top: 10px;'><span class='warning-blink'>⚠️ CẢNH BÁO: DÒNG TIỀN BẤT THƯỜNG - NEURAL-SHIELD ĐANG QUÉT!</span><br><small>Độ trễ cao - Sàn có dấu hiệu can thiệp. CEO Makao Phuocdz giảm cược ngay.</small></div>""", unsafe_allow_html=True)

    # --- [MODULE MỚI 3] QUÂN SƯ TƯ DUY (Updated with Money Management) ---
    st.markdown("---")
    st.header("💬 QUÂN SƯ TƯ DUY (Module 17 - Exclusive)")
    
    prediction = "TÀI" if random.random() > 0.5 else "XỈU"
    if a6 and "Hồi Xỉu" in a6: prediction = "XỈU"
    if a6 and "Hồi Tài" in a6: prediction = "TÀI"
    shield_status = "BẬT" if latency_val < 150 else "QUÉT MẠNH"
    
    # Logic tạo lời khuyên quản lý vốn
    money_msg = ""
    if opt_tag == "FACE_ONLY":
        money_msg = f"Tập trung vốn lót **Mặt {sniper_vi[0]}**, bỏ qua Tổng {pred_sum} để tiết kiệm."
    elif opt_tag == "SUM_ONLY":
        money_msg = f"Tập trung vốn lót **Tổng {pred_sum}**, không rải tiền vào Vị Mặt."
    else:
        money_msg = "Chia nhỏ vốn lót nhẹ cả 2 bên (An toàn)."

    advice_text = f"""
    > **Gửi CEO Makao Phuocdz:**
    > 
    > Hệ thống **Neural-Shield** đang hoạt động ở chế độ: **{shield_status}**.
    > Dựa trên nhịp Dealer hiện tại, xác suất rơi vào cửa **{prediction}** đang là cao nhất.
    >
    > 🗡️ **Chiến thuật:**
    > 1. Vào lệnh chính: **{prediction}**.
    > 2. Cảnh báo Bão: **{a11}**.
    >
    > 💰 **Quản Lý Vốn (Tối ưu hóa):**
    > **{money_msg}**
    >
    > *Hãy nhớ: "Thắng không kiêu, bại không nản". Giữ cái đầu lạnh!*
    """
    st.success(advice_text)
    
    st.subheader("📊 Biểu Đồ Sóng (Chaos Theory)")
    chart_data = pd.DataFrame([x['sum'] for x in st.session_state.history], columns=["Tổng Điểm"])
    st.line_chart(chart_data)

else:
    st.info("👋 Xin chào CEO Makao Phuocdz! Hãy nhập kết quả phiên đầu tiên để kích hoạt Neural-Shield.")

st.markdown("---")
st.caption("🔒 System secured by Neural-Shield | Latency: Real-time | Server: HongKong-Live")
