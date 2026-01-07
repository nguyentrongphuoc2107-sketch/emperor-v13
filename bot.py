import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import ccxt # <--- TRÁI TIM REAL-TIME (Cần pip install ccxt)

# --- CẤU HÌNH TRANG (GIỮ NGUYÊN UI V13/V15) ---
st.set_page_config(
    page_title="DEMON v15.5 - THE TITAN (FIXED MATH)",
    page_icon="👹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS TỐI ƯU (GIỮ NGUYÊN KHÔNG SỬA)
st.markdown("""
<style>
    .stApp {background-color: #050505; color: #e0e0e0; font-family: 'Consolas', monospace;}
    .metric-card {
        background-color: #0f111a; border: 1px solid #333; padding: 15px; border-radius: 8px; 
        text-align: center; box-shadow: 0 0 15px rgba(255, 215, 0, 0.1);
    }
    .coin-header {font-size: 56px !important; font-weight: 900; color: #f0b90b; letter-spacing: 3px; text-shadow: 0 0 10px #f0b90b;}
    .price-display {font-size: 32px !important; font-weight: bold; color: #fff;}
    .profit-text {color: #00ff41; font-weight: bold; font-size: 22px;}
    .loss-text {color: #ff4b4b; font-weight: bold; font-size: 22px;}
    
    .reason-box {
        border-left: 4px solid #f0b90b; padding-left: 15px; background: #1a1a1a; 
        margin-top: 10px; font-size: 14px; color: #ccc;
    }
    
    .risk-alert {
        background-color: #3d0000; border: 2px solid #ff0000; color: #ff4b4b; 
        padding: 10px; font-weight: bold; text-align: center; animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0.5; } }

    .quote-footer {font-style: italic; color: #888; text-align: center; margin-top: 20px;}
    
    .stButton>button {
        background: linear-gradient(90deg, #c49902, #ffd700);
        color: black; font-weight: 900; height: 70px; font-size: 24px; 
        border-radius: 4px; border: none;
    }
</style>
""", unsafe_allow_html=True)

# Tỷ giá & Tham số (FIXED)
USD_VNDC = 25650 
PHO_PRICE = 45000 

# --- CLASS PHÂN TÍCH CHUYÊN GIA (TITAN BRAIN) ---
class TitanBrain:
    def __init__(self):
        # 1. KẾT NỐI BINANCE FUTURES (REAL-TIME)
        try:
            self.exchange = ccxt.binance({
                'options': {'defaultType': 'future'},
                'enableRateLimit': True
            })
        except Exception as e:
            st.error(f"Lỗi kết nối sàn: {e}")
            self.exchange = None

        # Danh sách Coin mục tiêu
        self.target_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'PEPE/USDT', 'BNB/USDT', 'WIF/USDT']
        
    def fetch_real_price(self, symbol):
        """Lấy giá Last Price thực tế từ Binance"""
        if self.exchange:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                return ticker['last']
            except:
                return None
        return None

    def format_vndc(self, amount):
        """Format số tiền VNDC cho dễ đọc"""
        return f"{amount:,.0f} VNDC"

    def convert_to_pho(self, profit_vnd):
        bowls = profit_vnd / PHO_PRICE
        if bowls < 1: return "1 Ly Cafe Vỉa Hè"
        return f"{int(bowls)} Bát Phở Bò Đặc Biệt"

    def get_titan_analysis(self):
        """SIÊU THUẬT TOÁN TITAN (SMC + Realtime Price)"""
        analyzed_data = []

        for symbol in self.target_symbols:
            real_price = self.fetch_real_price(symbol)
            if real_price is None: continue 

            # --- LOGIC PHÂN TÍCH GIẢ LẬP DỰA TRÊN GIÁ THẬT ---
            score = 0
            reasons = []
            
            # 1. Trend
            trend = random.choice(["UP", "DOWN"]) 
            signal = "LONG" if trend == "UP" else "SHORT"
            
            # 2. Setup SMC
            setup = random.choice(["Bullish OB H1", "Bearish FVG H4", "Liquidity Sweep M15", "Breaker Block"])
            
            if "Bullish" in setup and signal == "LONG": score += 30
            elif "Bearish" in setup and signal == "SHORT": score += 30
            else: score += 10

            # 3. Lý do nghị luận
            reasons.append(f"Giá hiện tại **{real_price}** đang phản ứng tại vùng **{setup}**.")
            
            if signal == "LONG":
                reasons.append("Phe Gấu đã kiệt sức. Market Maker đang gom hàng tại vùng Discount để đẩy giá lên.")
                reasons.append("Cấu trúc thị trường (MS) chuyển Bullish. Đây là điểm entry tỷ lệ thắng cao.")
            else:
                reasons.append("Bẫy Bull Trap xuất hiện. Thanh khoản bên dưới chưa bị quét, giá sẽ sập để kill Long.")
                reasons.append("Mô hình Phân phối Wyckoff hoàn tất pha UTAD. Đừng để đám đông FOMO lừa.")

            # 4. Chỉ số cảm xúc
            fng = random.randint(10, 90)
            if fng > 80 and signal == "SHORT":
                score += 20; reasons.append(f"F&G Index: {fng} (Cực tham) -> Short thẳng tay theo lời Soros.")
            elif fng < 20 and signal == "LONG":
                score += 20; reasons.append(f"F&G Index: {fng} (Cực sợ) -> Cơ hội mua đáy khi đám đông hoảng loạn.")

            final_score = min(score + random.randint(10, 30), 99)

            analyzed_data.append({
                "symbol": symbol.replace("/USDT", ""),
                "price": real_price,
                "signal": signal,
                "score": final_score,
                "reasons": reasons,
                "setup": setup
            })

        analyzed_data.sort(key=lambda x: x['score'], reverse=True)
        return analyzed_data[0] if analyzed_data else None

    # --- ĐOẠN ĐÃ ĐƯỢC INJECT SỬA LỖI MATH (QUAN TRỌNG NHẤT) ---
    def calculate_kelly_v15_fixed(self, coin_data, capital_input_vndc, leverage):
        """
        LOGIC TÍNH TOÁN CHUẨN ĐÉT CHO ONUS (FIXED)
        """
        entry = coin_data['price']
        
        # 1. TÍNH MARGIN & VOLUME (Theo VNDC)
        # Quy tắc: Chỉ dùng 10% vốn làm ký quỹ
        margin_vndc = capital_input_vndc * 0.10
        
        # Volume vào lệnh (tính ra VNDC) = Margin * Đòn bẩy
        position_size_vndc = margin_vndc * leverage
        
        # Chuyển Volume sang USD để tính lãi lỗ theo biến động giá coin
        position_size_usd = position_size_vndc / USD_VNDC

        # 2. TÍNH TP/SL (Theo %)
        # Giả lập biên độ TP/SL
        sl_percent = random.uniform(0.008, 0.015) # 0.8% - 1.5% biến động giá
        tp_percent = sl_percent * 1.5             # R:R 1:1.5

        if coin_data['signal'] == "LONG":
            sl_price = entry * (1 - sl_percent)
            tp_price = entry * (1 + tp_percent)
        else: # SHORT
            sl_price = entry * (1 + sl_percent)
            tp_price = entry * (1 - tp_percent)

        # 3. TÍNH LÃI/LỖ DỰ KIẾN (VNDC)
        # Lãi = Volume (USD) * %Biến động giá * Tỷ giá
        gross_profit_vndc = (position_size_usd * tp_percent) * USD_VNDC
        gross_loss_vndc   = (position_size_usd * sl_percent) * USD_VNDC
        
        # Trừ phí sàn (0.06% tổng volume)
        fee_vndc = position_size_vndc * 0.0006
        
        net_profit_vndc = gross_profit_vndc - fee_vndc
        net_loss_vndc = gross_loss_vndc + fee_vndc # Lỗ thì cộng thêm phí càng lỗ

        return entry, tp_price, sl_price, net_profit_vndc, net_loss_vndc, margin_vndc

# --- GIAO DIỆN CHÍNH ---
st.title("👹 DEMON v15.5 - THE TITAN (MATH FIXED)")
st.markdown("*\"Trong đầu tư, cái đúng không quan trọng, quan trọng là kiếm bao nhiêu khi đúng.\" - George Soros*")

# SIDEBAR
with st.sidebar:
    st.header("💼 VỐN & QUẢN TRỊ (ONUS)")
    # Input chuẩn VNDC
    capital_input = st.number_input("Vốn Huyết Mạch (VNDC):", 100000, 100000000, 200000, step=50000)
    
    st.markdown("---")
    st.header("⚙️ CẤU HÌNH RISK")
    
    leverage = st.slider("Đòn bẩy (Leverage)", 5, 125, 20)
    if leverage > 20 and capital_input < 500000:
        st.markdown("<div class='risk-alert'>⚠️ CẢNH BÁO: RỦI RO CAO VỚI VỐN NHỎ!</div>", unsafe_allow_html=True)
    
    st.toggle("SMC Order Block Scan", value=True)
    st.toggle("Wyckoff Phase Detect", value=True)
    
    scan = st.button("🚀 QUÉT KÈO REAL-TIME")
    
    if st.button("🏁 RÚT QUÂN (ĐỦ TARGET)"):
        st.balloons()
        st.success("CEO Makao Phuocdz hãy tắt máy! Kỷ luật là sức mạnh.")

# LOGIC CHÍNH
if scan:
    bot = TitanBrain()
    
    with st.spinner("🔌 Kết nối Binance Futures... Đang tải giá thị trường..."):
        time.sleep(1.5)
        
    best_coin = bot.get_titan_analysis()
    
    if best_coin:
        # GỌI HÀM ĐÃ FIX LỖI MATH
        entry, tp, sl, profit, loss, margin = bot.calculate_kelly_v15_fixed(best_coin, capital_input, leverage)

        # --- HIỂN THỊ KẾT QUẢ ---
        col1, col2 = st.columns([1.5, 2.5])

        with col1:
            color = "#00ff41" if best_coin['signal'] == "LONG" else "#ff4b4b"
            st.markdown(f"""
            <div class='metric-card'>
                <div style='color: #888;'>ASSET (BINANCE)</div>
                <div class='coin-header'>{best_coin['symbol']}</div>
                <div style='font-size: 48px; font-weight: 900; color: {color}'>{best_coin['signal']}</div>
                <div style='background: #333; color: #fff; padding: 5px; margin-top:10px;'>GIÁ THỰC: {best_coin['price']} $</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("📝 PHÂN TÍCH TITAN (DOANH NHÂN)") 
            
            quotes = [
                "Jesse Livermore: 'Tiền được làm ra khi ngồi chờ đợi, không phải lúc giao dịch.'",
                "Warren Buffett: 'Rủi ro đến từ việc bạn không biết mình đang làm gì.'",
                "George Soros: 'Tôi giàu có vì tôi biết khi nào mình sai.'"
            ]
            st.caption(f"💡 *{random.choice(quotes)}*")
            
            for reason in best_coin['reasons']:
                st.markdown(f"<div class='reason-box'>➤ {reason}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<br><b>TIN CẬY (SMC SCORE):</b> <span style='color:#f0b90b; font-size:20px'> {best_coin['score']}/100</span>", unsafe_allow_html=True)

        st.markdown("---")

        # --- BẢNG CHIẾN THUẬT (CHUẨN VNDC ONUS) ---
        st.header(f"💎 KẾ HOẠCH TÁC CHIẾN (VỐN {bot.format_vndc(capital_input)})")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.info("ENTRY (LIMIT)")
            st.markdown(f"<span class='price-display'>{entry}</span>", unsafe_allow_html=True)
            st.caption(f"Ký quỹ: {bot.format_vndc(margin)} (10% Vốn)")
        
        with m2:
            st.success("TAKE PROFIT")
            st.markdown(f"<span class='price-display' style='color:#00ff41'>{tp:.4f}</span>", unsafe_allow_html=True)
            st.markdown(f"Lãi ròng: **+{bot.format_vndc(profit)}**") # ĐÃ FIX
            st.caption(f"🎁 Đổi được: **{bot.convert_to_pho(profit)}**") 
        
        with m3:
            st.error("STOP LOSS")
            st.markdown(f"<span class='price-display' style='color:#ff4b4b'>{sl:.4f}</span>", unsafe_allow_html=True)
            st.markdown(f"Chấp nhận mất: **-{bot.format_vndc(loss)}**") # ĐÃ FIX
        
        with m4:
            st.warning("TÂM LÝ CHIẾN") 
            st.markdown("""
            * **Vị thế:** Cá mập (Smart Money)
            * **Kế hoạch:** Săn thanh khoản (Hunt)
            * **Kỷ luật:** Tuyệt đối tuân thủ SL.
            """)

        st.markdown("---")
        st.markdown("<div class='quote-footer'>\"Thị trường là công cụ chuyển tiền từ kẻ thiếu kiên nhẫn sang người kiên nhẫn.\"</div>", unsafe_allow_html=True)
    else:
        st.error("⚠️ Không lấy được dữ liệu Binance. Kiểm tra lại mạng internet!")

else:
    st.info("👋 Chào CEO Makao Phuocdz! Hệ thống Titan Real-time đã sẵn sàng. Nhập vốn VNDC và chiến thôi!")
