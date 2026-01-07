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

# --- 3. QUANTUM BRAIN CORE ---
class TitanBrain:
    def __init__(self):
        self.targets = [
            'BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 
            'SUI', 'APT', 'NEAR', 'PEPE', 'XRP',
            'LINK', 'ADA', 'AVAX', 'WIF', 'FET'
        ]
        # Anti-Detect Layer
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        ]

    def get_headers(self):
        return {'User-Agent': random.choice(self.user_agents)}

    # --- KẾT NỐI VỆ TINH ---
    def fetch_binance(self, symbol):
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=15m&limit=60"
            r = requests.get(url, headers=self.get_headers(), timeout=4)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 30:
                    return [[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in data], "LIVE (BINANCE)"
        except: pass
        return None, None

    def fetch_coingecko(self, symbol):
        try:
            ids = {
                'BTC':'bitcoin', 'ETH':'ethereum', 'SOL':'solana', 'BNB':'binancecoin', 'DOGE':'dogecoin',
                'SUI':'sui', 'APT':'aptos', 'NEAR':'near', 'PEPE':'pepe', 'XRP':'ripple',
                'LINK':'chainlink', 'ADA':'cardano', 'AVAX':'avalanche-2', 'WIF':'dogwifhat', 'FET':'fetch-ai'
            }
            cg_id = ids.get(symbol)
            if not cg_id: return None, None

            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days=1"
            r = requests.get(url, headers=self.get_headers(), timeout=4)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 30:
                    # Smart Mock Volume
                    formatted = [[x[0], x[1], x[2], x[3], x[4], x[4]*random.uniform(500, 5000)] for x in data[-60:]]
                    return formatted, "LIVE (GECKO)"
        except: pass
        return None, None

    def generate_simulation(self, symbol):
        # Fallback an toàn (Anti-Crash)
        base_map = {'BTC': 96000, 'ETH': 3600, 'SOL': 210, 'BNB': 620}
        base_price = base_map.get(symbol, 100)
        data = []
        price = base_price
        for i in range(60):
            change = random.uniform(-0.02, 0.02)
            open_p = price
            close_p = price * (1 + change)
            high_p = max(open_p, close_p) * 1.005
            low_p = min(open_p, close_p) * 0.995
            vol = random.uniform(1000, 10000)
            data.append([time.time()*1000, open_p, high_p, low_p, close_p, vol])
            price = close_p
        return data, "SIMULATION (DEMO)"

    def get_data(self, symbol):
        data, source = self.fetch_binance(symbol)
        if data: return data, source
        data, source = self.fetch_coingecko(symbol)
        if data: return data, source
        return self.generate_simulation(symbol)

    # --- XỬ LÝ TÍN HIỆU ---
    def process_indicators(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        if len(df) < 50: return None

        # EMA
        df['ema34'] = df['close'].ewm(span=34).mean()
        df['ema89'] = df['close'].ewm(span=89).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['signal_line'] = df['macd'].ewm(span=9).mean()
        
        # ATR
        df['tr'] = np.maximum((df['high'] - df['low']), abs(df['high'] - df['close'].shift(1)))
        df['atr'] = df['tr'].rolling(14).mean()
        
        return df.iloc[-1]

    def analyze(self, symbol):
        ohlcv, source = self.get_data(symbol)
        if not ohlcv: return None
        
        d = self.process_indicators(ohlcv)
        if d is None: return None

        score = 50
        reasons = []
        
        # Logic V3000
        if d['close'] > d['ema89']: score += 20; reasons.append("Uptrend (Trên EMA89)")
        else: score -= 20; reasons.append("Downtrend (Dưới EMA89)")
        
        if d['macd'] > d['signal_line']: score += 10; reasons.append("MACD Bullish")
        elif d['macd'] < d['signal_line']: score -= 10; reasons.append("MACD Bearish")
        
        if d['rsi'] < 30: score += 15; reasons.append("RSI Quá bán (Đáy)")
        if d['rsi'] > 70: score -= 15; reasons.append("RSI Quá mua (Đỉnh)")

        signal = "NEUTRAL"
        if score >= 70: signal = "LONG"
        elif score <= 30: signal = "SHORT"
        
        atr_val = d['atr'] if not np.isnan(d['atr']) else d['close'] * 0.02
        thesis = f"{source} Data. " + ", ".join(reasons) + "."
        
        return {
            "symbol": symbol, "signal": signal, "score": score,
            "price": d['close'], "atr": atr_val,
            "thesis": thesis, "source": source
        }

    def plan(self, coin, cap, lev):
        entry = coin['price']
        atr = coin['atr']
        
        if coin['signal'] == "LONG":
            sl = entry - (atr * 2)
            tp1 = entry + (atr * 2)
            tp2 = entry + (atr * 5)
        else:
            sl = entry + (atr * 2)
            tp1 = entry - (atr * 2)
            tp2 = entry - (atr * 5)
        
        margin = (cap * 0.1) / lev
        return {"entry": entry, "tp1": tp1, "tp2": tp2, "sl": sl, "margin": margin}

    # --- TELEGRAM MODULE (MỚI) ---
    def send_telegram(self, symbol, signal, score, p, thesis, token, chat_id):
        if not token or not chat_id: return
        
        icon = "🟢" if signal == "LONG" else "🔴"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        msg = (
            f"🌪️ *TITAN V3000 ALERT*\n"
            f"-------------------\n"
            f"{icon} *SIGNAL:* {signal} (#{symbol})\n"
            f"⚡ *Score:* {score}/100\n\n"
            f"💵 Entry: {p['entry']:,.4f}\n"
            f"🎯 TP1: {p['tp1']:,.4f}\n"
            f"🚀 TP2: {p['tp2']:,.4f}\n"
            f"🛡️ SL: {p['sl']:,.4f}\n\n"
            f"📝 {thesis}"
        )
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=3)
        except Exception as e:
            print(f"Tele Err: {e}")

# --- 4. GIAO DIỆN ĐIỀU KHIỂN ---
bot = TitanBrain()

# Session State để tránh spam tele
if 'last_signal' not in st.session_state:
    st.session_state.last_signal = None

st.title("🌌 EMPEROR V3000: QUANTUM CORE")
st.caption("AI Trading Neural Network • Telegram Integrated • Anti-Block Protocol")


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
    refresh = st.number_input("Scan Time (s):", value=30, min_value=10)
    auto = st.checkbox("🔮 AUTO-HUNT", value=True)
    if st.button("🚀 FORCE SCAN"): auto = True

# --- 5. MAIN LOOP ---
if auto:
    placeholder = st.empty()
    with placeholder.container():
        st.info("📡 Titan đang quét sóng vũ trụ...")
        
        # Progress Bar ảo diệu
        progress_bar = st.progress(0)
        results = []
        
        for i, sym in enumerate(bot.targets):
            data = bot.analyze(sym)
            if data: results.append(data)
            progress_bar.progress((i + 1) / len(bot.targets))
            time.sleep(random.uniform(0.05, 0.15)) # Tốc độ quét cực nhanh
            
        progress_bar.empty()

        if results:
            # Chọn con ngon nhất
            best = sorted(results, key=lambda x: abs(x['score']-50), reverse=True)[0]
            
            # Logic hiển thị
            if best['signal'] != "NEUTRAL":
                p = bot.plan(best, cap, lev)
                c_color = "#00FF41" if best['signal'] == "LONG" else "#FF0041"
                status_class = "live" if "LIVE" in best['source'] else "sim"
                
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
                        <div><span class='metric-label'>MARGIN SIZE</span><br><span class='metric-val' style='color:#FFD700'>{format_vnd(p['margin'], rate)}</span></div>
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
                
                # LOGIC BẮN TELEGRAM (CHỈ BẮN KHI TÍN HIỆU THAY ĐỔI HOẶC COIN MỚI)
                signal_signature = f"{best['symbol']}-{best['signal']}"
                if enable_tele and st.session_state.last_signal != signal_signature:
                    with st.spinner("Đang truyền tin về Trái Đất..."):
                        bot.send_telegram(best['symbol'], best['signal'], best['score'], p, best['thesis'], tele_token, tele_chat_id)
                        st.session_state.last_signal = signal_signature
                        st.toast(f"Đã bắn tín hiệu {best['symbol']} về Telegram!", icon="🚀")

            else:
                st.warning("⚠️ Thị trường Sideway. Bot đang ở chế độ chờ (Sleep Mode)...")
                st.markdown(f"""
                    <div style='text-align:center; color:#555; padding:20px;'>
                        Không tìm thấy cơ hội có điểm số > 70.<br>
                        Coin mạnh nhất hiện tại: <b>{best['symbol']}</b> ({best['score']}/100)
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("⚠️ MẤT KẾT NỐI VỆ TINH. ĐANG THỬ LẠI...")

    # Đếm ngược
    time.sleep(1)
    if auto:
        with st.empty():
            for s in range(refresh, 0, -1):
                st.write(f"⏳ Next Scan: {s}s")
                time.sleep(1)
        st.rerun()
