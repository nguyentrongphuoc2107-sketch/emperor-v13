import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="EMPEROR V24 STEALTH", layout="wide")

# CSS HACKER
st.markdown("""
<style>
    .stApp {background-color: #0E1117; color: #00FF41; font-family: 'Segoe UI', sans-serif;}
    .titan-card {
        border: 2px solid #00FF41; background: linear-gradient(145deg, #111, #002200);
        padding: 25px; border-radius: 15px; text-align: center;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.15); animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% {box-shadow: 0 0 0 0 rgba(0, 255, 65, 0.4);} 70% {box-shadow: 0 0 0 10px rgba(0, 255, 65, 0);} 100% {box-shadow: 0 0 0 0 rgba(0, 255, 65, 0);} }
    .thesis-box {
        border-left: 4px solid #FFD700; background-color: #1a1a1a;
        padding: 15px; margin-top: 20px; border-radius: 0 10px 10px 0;
        color: #ddd; font-style: italic; font-size: 1.1em;
    }
    .status-badge {
        padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 0.8em;
    }
    .live {background-color: #00FF41; color: #000;}
    .sim {background-color: #FFA500; color: #000;}
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỖ TRỢ ---
def format_vnd(amount_usdt, rate):
    val = amount_usdt * rate
    if val >= 1e9: return f"{val/1e9:.2f} Tỷ"
    if val >= 1e6: return f"{val/1e6:.1f} Tr"
    return f"{val:,.0f} đ"

# --- 3. BỘ NÃO TITAN (ĐA NGUỒN DỮ LIỆU) ---
class TitanBrain:
    def __init__(self):
        self.targets = [
            'BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 
            'SUI', 'APT', 'NEAR', 'PEPE', 'XRP'
        ]
        # Giả lập trình duyệt để tránh bị chặn IP
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_binance(self, symbol):
        try:
            # Dùng API Public của Binance với Headers
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=15m&limit=50"
            r = requests.get(url, headers=self.headers, timeout=2)
            if r.status_code == 200:
                data = r.json()
                return [[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in data], "LIVE (Binance)"
        except: pass
        return None, None

    def fetch_coingecko(self, symbol):
        try:
            # Fallback sang CoinGecko (Dữ liệu OHLC đơn giản)
            # CoinGecko ID mapping (đơn giản hóa)
            ids = {'BTC':'bitcoin', 'ETH':'ethereum', 'SOL':'solana', 'BNB':'binancecoin', 'DOGE':'dogecoin'}
            cg_id = ids.get(symbol, 'bitcoin')
            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days=1"
            r = requests.get(url, headers=self.headers, timeout=2)
            if r.status_code == 200:
                data = r.json()
                # Coingecko trả về [time, open, high, low, close]. Thiếu volume, ta fake volume
                formatted = [[x[0], x[1], x[2], x[3], x[4], random.uniform(1000, 5000)] for x in data[-50:]]
                return formatted, "LIVE (Coingecko)"
        except: pass
        return None, None

    def generate_simulation(self, symbol):
        # Chế độ giả lập để APP KHÔNG BAO GIỜ CHẾT (Dành cho Demo)
        base_price = 100000 if symbol == 'BTC' else 3000 if symbol == 'ETH' else 100
        data = []
        price = base_price
        for i in range(50):
            change = random.uniform(-0.02, 0.02)
            open_p = price
            close_p = price * (1 + change)
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.01))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.01))
            vol = random.uniform(100, 1000)
            data.append([time.time()*1000, open_p, high_p, low_p, close_p, vol])
            price = close_p
        return data, "SIMULATION (Demo)"

    def get_data(self, symbol):
        # 1. Thử Binance
        data, source = self.fetch_binance(symbol)
        if data: return data, source
        
        # 2. Thử CoinGecko (Nếu Binance chặn)
        data, source = self.fetch_coingecko(symbol)
        if data: return data, source

        # 3. Đường cùng: Giả lập (Để show UI)
        return self.generate_simulation(symbol)

    def process_indicators(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        
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
        
        # BB
        df['ma20'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper'] = df['ma20'] + 2*df['std']
        df['lower'] = df['ma20'] - 2*df['std']
        
        # ATR
        df['tr'] = np.maximum((df['high'] - df['low']), abs(df['high'] - df['close'].shift(1)))
        df['atr'] = df['tr'].rolling(14).mean()
        
        return df.iloc[-1]

    def analyze(self, symbol):
        ohlcv, source = self.get_data(symbol)
        if not ohlcv: return None
        
        d = self.process_indicators(ohlcv)
        
        score = 50
        reasons = []
        
        # Logic phân tích (Giữ nguyên độ "bú" của V23)
        if d['close'] > d['ema89']: score += 15; reasons.append("Trên EMA89")
        else: score -= 15; reasons.append("Dưới EMA89")
        
        if d['macd'] > d['signal_line']: score += 10; reasons.append("MACD cắt lên")
        elif d['macd'] < d['signal_line']: score -= 10; reasons.append("MACD cắt xuống")
        
        if d['rsi'] < 30: score += 15; reasons.append("RSI Quá bán (Bắt đáy)")
        if d['rsi'] > 70: score -= 15; reasons.append("RSI Quá mua (Short đỉnh)")

        signal = "NEUTRAL"
        if score >= 65: signal = "LONG"
        elif score <= 35: signal = "SHORT"
        
        # Viết văn
        thesis = f"Dữ liệu từ nguồn {source}. " + ", ".join(reasons) + "."
        
        return {
            "symbol": symbol, "signal": signal, "score": score,
            "price": d['close'], "atr": d['atr'] if not np.isnan(d['atr']) else d['close']*0.01,
            "thesis": thesis, "source": source
        }

    def plan(self, coin, cap, lev):
        entry = coin['price']
        atr = coin['atr']
        if coin['signal'] == "LONG":
            sl = entry - (atr * 2); tp1 = entry + (atr * 2); tp2 = entry + (atr * 5)
        else:
            sl = entry + (atr * 2); tp1 = entry - (atr * 2); tp2 = entry - (atr * 5)
        
        margin = (cap * 0.1) / lev
        return {"entry": entry, "tp1": tp1, "tp2": tp2, "sl": sl, "margin": margin}

# --- 4. GIAO DIỆN CHÍNH ---
bot = TitanBrain()

st.title("🌪️ V24 TITAN: STEALTH MODE")
st.caption("Phiên bản tàng hình - Vượt tường lửa Streamlit Cloud")

with st.sidebar:
    st.header("⚡ CONTROL CENTER")
    rate = st.number_input("Tỷ giá USDT:", 25750, step=10)
    cap = st.number_input("Vốn (VND):", 10000000, step=1000000)
    lev = st.slider("Đòn bẩy:", 5, 125, 20)
    refresh = st.number_input("Scan Time (s):", value=30, min_value=10)
    auto = st.checkbox("🔮 AUTO-SCAN", value=True)
    if st.button("🚀 QUÉT NGAY"): auto = True

if auto:
    res_container = st.empty()
    with res_container.container():
        st.info("📡 Titan đang kết nối đa vệ tinh (Binance/Coingecko)...")
        results = []
        bar = st.progress(0)
        
        for i, sym in enumerate(bot.targets):
            data = bot.analyze(sym)
            if data: results.append(data)
            bar.progress((i+1)/len(bot.targets))
            time.sleep(0.1)
        bar.empty()
        
        if results:
            best = sorted(results, key=lambda x: abs(x['score']-50), reverse=True)[0]
            
            p = bot.plan(best, cap, lev)
            c_color = "#00FF41" if best['signal'] == "LONG" else "#FF0041" if best['signal'] == "SHORT" else "#FFFF00"
            
            # Badge trạng thái nguồn dữ liệu
            status_class = "live" if "LIVE" in best['source'] else "sim"
            
            st.markdown(f"""
            <div class='titan-card' style='border-color: {c_color};'>
                <span class='status-badge {status_class}'>{best['source']}</span>
                <h3 style='color:#fff; margin-top:10px;'>{best['symbol']} / USDT</h3>
                <h1 style='color:{c_color}; font-size: 3.5em; margin: 5px 0;'>{best['signal']}</h1>
                <p>CONFIDENCE: {best['score']}/100</p>
                <hr style='border-color: #444;'>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap: 20px;'>
                    <div><span class='metric-label'>ENTRY</span><br><span class='metric-val'>{p['entry']:,.4f}</span></div>
                    <div><span class='metric-label'>SIZE (VND)</span><br><span class='metric-val' style='color:#FFD700'>{format_vnd(p['margin'], rate)}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("TP1", f"{p['tp1']:,.4f}")
            c2.metric("TP2", f"{p['tp2']:,.4f}")
            c3.metric("SL", f"{p['sl']:,.4f}")
            
            st.markdown(f"<div class='thesis-box'>{best['thesis']}</div>", unsafe_allow_html=True)
            
        else:
            st.error("⚠️ Toàn bộ vệ tinh bị chặn. Vui lòng F5 lại trang!")

    time.sleep(1)
    if auto:
        with st.empty():
            for s in range(refresh, 0, -1):
                st.write(f"⏳ Titan đang ẩn mình... {s}s")
                time.sleep(1)
        st.rerun()
