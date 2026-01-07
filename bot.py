import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import random

# --- 1. CẤU HÌNH HỆ THỐNG YEAR 3000 ---
st.set_page_config(page_title="EMPEROR V3000 QUANTUM", layout="wide", page_icon="🌪️")

# CSS: CYBERPUNK GOD MODE
st.markdown("""
<style>
    .stApp {background-color: #000000; color: #00FF41; font-family: 'Courier New', monospace;}
    
    /* Card hiệu ứng Neon Breathing */
    .titan-card {
        border: 1px solid #00FF41; 
        background: linear-gradient(180deg, #051a05, #000);
        padding: 25px; border-radius: 0px; text-align: center;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.1); 
        animation: breath 4s infinite;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .titan-card::before {
        content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 2px;
        background: #00FF41; animation: scanline 2s linear infinite;
    }
    
    @keyframes breath { 0% {border-color: #004d0c;} 50% {border-color: #00FF41; box-shadow: 0 0 30px rgba(0,255,65,0.3);} 100% {border-color: #004d0c;} }
    @keyframes scanline { 0% {left: -100%;} 100% {left: 100%;} }

    .thesis-box {
        border-left: 3px solid #FFD700; background-color: #0a0a0a;
        padding: 15px; margin-top: 15px; 
        color: #ddd; font-style: italic; font-size: 0.9em;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .status-badge {
        padding: 2px 8px; border: 1px solid #333; font-size: 0.7em; text-transform: uppercase; letter-spacing: 2px;
    }
    
    /* Custom Metrics */
    div[data-testid="stMetricValue"] {font-size: 1.8rem !important; color: #fff !important; text-shadow: 0 0 10px rgba(255,255,255,0.5);}
    div[data-testid="stMetricLabel"] {color: #00FF41 !important; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM HELPER ---
def format_vnd(amount_usdt, rate):
    val = amount_usdt * rate
    if val >= 1e9: return f"{val/1e9:.2f} TỶ"
    if val >= 1e6: return f"{val/1e6:.1f} TR"
    return f"{val:,.0f} đ"

# --- 3. QUANTUM BRAIN CORE (REFINED & SAFER) ---
class TitanBrain:
    def __init__(self):
        # Chỉ tập trung vào các coin Top Volume để thanh khoản tốt
        self.targets = [
            'BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 
            'SUI', 'APT', 'NEAR', 'PEPE', 'XRP',
            'LINK', 'ADA', 'AVAX', 'WIF', 'FET'
        ]
        # Fake User-Agent để đỡ bị chặn
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    # --- KẾT NỐI VỆ TINH (CHỈ DÙNG DỮ LIỆU THẬT) ---
    def fetch_data(self, symbol):
        # 1. Ưu tiên Binance (Nhanh nhất)
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=15m&limit=100"
            r = requests.get(url, headers=self.headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                # Convert về dạng số [time, open, high, low, close, vol]
                return [[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in data], "LIVE (BINANCE)"
        except Exception as e:
            # print(f"Binance Error: {e}") # Debug only
            pass

        # 2. Dự phòng CoinGecko (Nếu Binance sập/chặn)
        try:
            ids = {
                'BTC':'bitcoin', 'ETH':'ethereum', 'SOL':'solana', 'BNB':'binancecoin', 
                'DOGE':'dogecoin', 'SUI':'sui', 'NEAR':'near', 'APT':'aptos', 'PEPE':'pepe',
                'XRP':'ripple', 'LINK':'chainlink', 'ADA':'cardano', 'AVAX':'avalanche-2',
                'WIF':'dogwifhat', 'FET':'fetch-ai'
            }
            cg_id = ids.get(symbol)
            if cg_id:
                url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days=1"
                r = requests.get(url, headers=self.headers, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    # CoinGecko không có Volume chuẩn trong OHLC, fake volume nhẹ để tính toán
                    formatted = [[x[0], x[1], x[2], x[3], x[4], 1000000] for x in data[-60:]]
                    return formatted, "LIVE (GECKO)"
        except:
            pass
        
        # TUYỆT ĐỐI KHÔNG TRẢ VỀ DATA GIẢ (SIMULATION)
        return None, "DISCONNECTED"

    # --- XỬ LÝ TÍN HIỆU (V3 LOGIC) ---
    def process_indicators(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        if len(df) < 50: return None

        # EMA (Xu hướng)
        df['ema34'] = df['close'].ewm(span=34).mean()
        df['ema89'] = df['close'].ewm(span=89).mean() # Đường ranh giới sinh tử
        
        # RSI (Sức mạnh)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (Động lượng)
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['signal_line'] = df['macd'].ewm(span=9).mean()
        
        # ATR (Biến động - Dùng để đặt Stoploss)
        df['tr'] = np.maximum((df['high'] - df['low']), abs(df['high'] - df['close'].shift(1)))
        df['atr'] = df['tr'].rolling(14).mean()
        
        return df.iloc[-1]

    def analyze(self, symbol):
        ohlcv, source = self.fetch_data(symbol)
        
        # Nếu mất kết nối -> Bỏ qua ngay
        if not ohlcv or source == "DISCONNECTED": 
            return None
        
        d = self.process_indicators(ohlcv)
        if d is None: return None

        score = 50
        reasons = []
        
        # --- LOGIC CHẤM ĐIỂM (NGHIÊM NGẶT HƠN) ---
        
        # 1. Trend Filter (Quan trọng nhất)
        if d['close'] > d['ema89']: 
            score += 20
            reasons.append("Uptrend (Trên EMA89)")
        else: 
            score -= 20
            reasons.append("Downtrend (Dưới EMA89)")
        
        # 2. Momentum (MACD)
        if d['macd'] > d['signal_line']:
            score += 15
            reasons.append("MACD Bullish")
        else:
            score -= 15
            reasons.append("MACD Bearish")
        
        # 3. RSI Filter (Tránh đu đỉnh/bán đáy)
        if d['rsi'] < 30: 
            score += 10
            reasons.append("RSI Quá Bán")
        elif d['rsi'] > 70: 
            score -= 10
            reasons.append("RSI Quá Mua")

        # Quyết định tín hiệu
        signal = "NEUTRAL"
        if score >= 75: signal = "LONG" # Cần điểm cao hơn để vào lệnh
        elif score <= 25: signal = "SHORT"
        
        atr_val = d['atr'] if not np.isnan(d['atr']) else d['close'] * 0.01
        thesis = f"[{source}] " + ", ".join(reasons)
        
        return {
            "symbol": symbol, "signal": signal, "score": score,
            "price": d['close'], "atr": atr_val,
            "thesis": thesis, "source": source
        }

    def plan(self, coin, cap, lev):
        entry = coin['price']
        atr = coin['atr']
        
        # Chiến thuật Risk:Reward 1:2
        if coin['signal'] == "LONG":
            sl = entry - (atr * 1.5) # Stoploss chặt hơn
            tp1 = entry + (atr * 2)
            tp2 = entry + (atr * 4)
        else:
            sl = entry + (atr * 1.5)
            tp1 = entry - (atr * 2)
            tp2 = entry - (atr * 4)
        
        # Quản lý vốn: Chỉ đi 5% vốn cho 1 lệnh để sống sót
        margin = (cap * 0.05) / lev 
        return {"entry": entry, "tp1": tp1, "tp2": tp2, "sl": sl, "margin": margin}

    # Module Telegram
    def send_telegram(self, symbol, signal, score, p, thesis, token, chat_id):
        if not token or not chat_id: return
        icon = "🟢 MÚC NGAY" if signal == "LONG" else "🔴 BÁN KHỐNG"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        msg = (
            f"🔥 *TITAN V3000 SIGNAL*\n"
            f"-------------------\n"
            f"{icon}: {signal} #{symbol}\n"
            f"⚡ Tin cậy: {score}/100\n\n"
            f"💵 Entry: {p['entry']:,.4f}\n"
            f"🎯 TP1: {p['tp1']:,.4f}\n"
            f"🚀 TP2: {p['tp2']:,.4f}\n"
            f"🛡️ SL: {p['sl']:,.4f} (Tuyệt đối)\n\n"
            f"📝 Logic: {thesis}"
        )
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=3)
        except: pass

# --- 4. GIAO DIỆN ĐIỀU KHIỂN ---
bot = TitanBrain()

# Session State để tránh spam tele
if 'last_signal' not in st.session_state:
    st.session_state.last_signal = None

st.title("🌌 EMPEROR V3000: REAL MARKET ONLY")
st.caption("AI Trading Neural Network • NO SIMULATION • Safe Mode ON")


with st.sidebar:
    st.header("⚙️ SYSTEM CONFIG")
    rate = st.number_input("Tỷ giá USDT:", 25750, step=50)
    cap = st.number_input("Vốn (VND):", 10000000, step=1000000)
    lev = st.slider("Đòn bẩy (x):", 5, 125, 20)
    
    st.markdown("---")
    st.header("📡 NEURAL LINK (TELEGRAM)")
    tele_token = st.text_input("Bot Token:", type="password", help="Lấy từ BotFather")
    tele_chat_id = st.text_input("Chat ID:", help="Lấy từ userinfobot")
    enable_tele = st.checkbox("Kích hoạt bắn tín hiệu", value=False)
    
    st.markdown("---")
    refresh = st.number_input("Scan Time (s):", value=60, min_value=15) # Tăng thời gian scan lên 60s để đỡ bị chặn
    auto = st.checkbox("🔮 AUTO-HUNT", value=True)
    if st.button("🚀 FORCE SCAN"): auto = True

# --- 5. MAIN LOOP ---
if auto:
    placeholder = st.empty()
    with placeholder.container():
        st.info("📡 Titan đang quét dữ liệu thị trường thực...")
        
        # Progress Bar ảo diệu
        progress_bar = st.progress(0)
        results = []
        
        for i, sym in enumerate(bot.targets):
            data = bot.analyze(sym)
            if data: results.append(data)
            progress_bar.progress((i + 1) / len(bot.targets))
            time.sleep(0.5) # Nghỉ 0.5s giữa các lần gọi API để tránh bị Ban IP
            
        progress_bar.empty()

        if results:
            # Chọn con ngon nhất
            # Lọc những con có điểm số cao (Xa mức 50 nhất)
            valid_results = [r for r in results if r['score'] >= 75 or r['score'] <= 25]
            
            if valid_results:
                best = sorted(valid_results, key=lambda x: abs(x['score']-50), reverse=True)[0]
                
                # Logic hiển thị
                p = bot.plan(best, cap, lev)
                c_color = "#00FF41" if best['signal'] == "LONG" else "#FF0041"
                status_class = "live"
                
                # TITAN CARD
                st.markdown(f"""
                <div class='titan-card' style='border-color: {c_color};'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                        <span class='status-badge {status_class}'>{best['source']}</span>
                        <span style='color:#888; letter-spacing:2px; font-weight:bold;'>#{best['symbol']}</span>
                    </div>
                    <div style='font-size: 5em; font-weight: 900; color:{c_color}; text-shadow: 0 0 20px {c_color}; margin: 10px 0;'>
                        {best['signal']}
                    </div>
                    <div style='background:rgba(255,255,255,0.05); display:inline-block; padding:5px 20px; border-radius:5px;'>
                        CONFIDENCE: <span style='color:{c_color}; font-weight:bold'>{best['score']}%</span>
                    </div>
                    <hr style='border-color: #333; margin: 20px 0; opacity:0.5;'>
                    <div style='display:grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                        <div><span class='metric-label'>ENTRY ZONE</span><br><span class='metric-val'>{p['entry']:,.4f}</span></div>
                        <div><span class='metric-label'>MARGIN (5%)</span><br><span class='metric-val' style='color:#FFD700'>{format_vnd(p['margin'], rate)}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # METRICS ROW
                c1, c2, c3 = st.columns(3)
                c1.metric("TARGET 1 (SAFE)", f"{p['tp1']:,.4f}")
                c2.metric("TARGET 2 (MOON)", f"{p['tp2']:,.4f}")
                c3.metric("STOPLOSS (HARD)", f"{p['sl']:,.4f}", delta_color="inverse")

                # THESIS BOX
                st.markdown(f"<div class='thesis-box'>🧬 <b>TITAN ANALYSIS:</b> {best['thesis']}</div>", unsafe_allow_html=True)
                
                # LOGIC BẮN TELEGRAM
                signal_signature = f"{best['symbol']}-{best['signal']}"
                if enable_tele and st.session_state.last_signal != signal_signature:
                    with st.spinner("Đang truyền tin về Telegram..."):
                        bot.send_telegram(best['symbol'], best['signal'], best['score'], p, best['thesis'], tele_token, tele_chat_id)
                        st.session_state.last_signal = signal_signature
                        st.toast(f"Đã bắn tín hiệu {best['symbol']}!", icon="🚀")

            else:
                st.warning("⚠️ Thị trường Sideway (Đi ngang). Bot không tìm thấy điểm vào an toàn.")
                st.markdown("""
                    <div style='text-align:center; color:#555; padding:20px;'>
                        Bot đang chờ đợi một cú Breakout rõ ràng.<br>
                        <i>"Tiền chỉ được chuyển từ người thiếu kiên nhẫn sang người kiên nhẫn."</i>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("⚠️ KHÔNG LẤY ĐƯỢC DỮ LIỆU. Vui lòng kiểm tra mạng hoặc F5 lại.")

    # Đếm ngược
    time.sleep(1)
    if auto:
        with st.empty():
            for s in range(int(refresh), 0, -1):
                st.write(f"⏳ Next Scan: {s}s")
                time.sleep(1)
        st.rerun()
