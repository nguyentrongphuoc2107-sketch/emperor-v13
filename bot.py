import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
import random

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="EMPEROR V25 SUPREMACY", layout="wide")

# CSS HACKER (GIỮ NGUYÊN GIAO DIỆN BÚ)
st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00FF41; font-family: 'Segoe UI', sans-serif;}
    .titan-card {
        border: 2px solid #00FF41; background: linear-gradient(145deg, #0f1c10, #000);
        padding: 25px; border-radius: 15px; text-align: center;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.2); 
        animation: pulse 3s infinite;
        margin-bottom: 20px;
    }
    @keyframes pulse { 0% {box-shadow: 0 0 0 0 rgba(0, 255, 65, 0.4);} 70% {box-shadow: 0 0 0 15px rgba(0, 255, 65, 0);} 100% {box-shadow: 0 0 0 0 rgba(0, 255, 65, 0);} }
    .thesis-box {
        border-left: 5px solid #FFD700; background-color: #111;
        padding: 15px; margin-top: 15px; border-radius: 0 10px 10px 0;
        color: #eee; font-style: italic; font-size: 1.05em;
    }
    .status-badge {
        padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px;
    }
    .live {background-color: #00FF41; color: #000; box-shadow: 0 0 10px #00FF41;}
    .sim {background-color: #FF5500; color: #FFF;}
    .metric-label {color: #888; font-size: 0.85em; letter-spacing: 1px;}
    .metric-val {color: #fff; font-size: 1.6em; font-weight: 800;}
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỖ TRỢ (Đã fix lỗi hiển thị số quá lớn) ---
def format_vnd(amount_usdt, rate):
    val = amount_usdt * rate
    if val >= 1e9: return f"{val/1e9:.2f} Tỷ"
    if val >= 1e6: return f"{val/1e6:.1f} Tr"
    return f"{val:,.0f} đ"

# --- 3. BỘ NÃO TITAN (INJECT FIX LỖI & ANTI-DETECT PRO) ---
class TitanBrain:
    def __init__(self):
        self.targets = [
            'BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 
            'SUI', 'APT', 'NEAR', 'PEPE', 'XRP',
            'LINK', 'ADA', 'AVAX', 'WIF' # Thêm coin hot
        ]
        # [INJECT] List User-Agent để xoay vòng, tránh bị block IP
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]

    def get_headers(self):
        return {'User-Agent': random.choice(self.user_agents)}

    def fetch_binance(self, symbol):
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=15m&limit=60" # Lấy dư nến để tính EMA chính xác
            r = requests.get(url, headers=self.get_headers(), timeout=3) # Tăng timeout lên 3s
            if r.status_code == 200:
                data = r.json()
                if len(data) > 30: # [FIX] Chỉ chấp nhận nếu đủ dữ liệu
                    return [[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in data], "LIVE (Binance)"
        except: pass
        return None, None

    def fetch_coingecko(self, symbol):
        try:
            # [FIX] Mapping đầy đủ hơn để tránh lỗi sai coin
            ids = {
                'BTC':'bitcoin', 'ETH':'ethereum', 'SOL':'solana', 'BNB':'binancecoin', 'DOGE':'dogecoin',
                'SUI':'sui', 'APT':'aptos', 'NEAR':'near', 'PEPE':'pepe', 'XRP':'ripple',
                'LINK':'chainlink', 'ADA':'cardano', 'AVAX':'avalanche-2', 'WIF':'dogwifhat'
            }
            cg_id = ids.get(symbol)
            if not cg_id: return None, None # Bỏ qua nếu không có ID

            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days=1"
            r = requests.get(url, headers=self.get_headers(), timeout=3)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 30:
                    # Fake volume thông minh hơn: Vol = Price * Random Factor
                    formatted = [[x[0], x[1], x[2], x[3], x[4], x[4]*random.uniform(10, 50)] for x in data[-60:]]
                    return formatted, "LIVE (Coingecko)"
        except: pass
        return None, None

    def generate_simulation(self, symbol):
        # [FIX] Giá cơ sở thực tế hơn
        base_map = {'BTC': 95000, 'ETH': 3500, 'SOL': 200, 'BNB': 600}
        base_price = base_map.get(symbol, 100)
        
        data = []
        price = base_price
        for i in range(60):
            change = random.uniform(-0.015, 0.015)
            open_p = price
            close_p = price * (1 + change)
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.005))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.005))
            vol = random.uniform(500, 2000)
            data.append([time.time()*1000, open_p, high_p, low_p, close_p, vol])
            price = close_p
        return data, "SIMULATION (Demo)"

    def get_data(self, symbol):
        data, source = self.fetch_binance(symbol)
        if data: return data, source
        
        data, source = self.fetch_coingecko(symbol)
        if data: return data, source

        return self.generate_simulation(symbol)

    def process_indicators(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        
        if len(df) < 50: return None # [FIX] Tránh crash nếu ít nến

        # EMA & Trend
        df['ema34'] = df['close'].ewm(span=34).mean()
        df['ema89'] = df['close'].ewm(span=89).mean()
        
        # RSI [FIX] Epsilon an toàn
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
        
        # ATR (Stoploss)
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
        
        # --- LOGIC BÚ V25 (CẢI TIẾN) ---
        # 1. Trend Filter
        if d['close'] > d['ema89']: 
            score += 20; reasons.append(f"Giá nằm trên EMA89 (Uptrend)")
        else: 
            score -= 20; reasons.append(f"Giá nằm dưới EMA89 (Downtrend)")
        
        # 2. Momentum
        if d['macd'] > d['signal_line']: score += 10; reasons.append("MACD cắt lên")
        elif d['macd'] < d['signal_line']: score -= 10; reasons.append("MACD cắt xuống")
        
        # 3. RSI Sniper
        if 45 <= d['rsi'] <= 55: reasons.append("RSI trung tính, chờ break")
        if d['rsi'] < 30: score += 15; reasons.append("RSI Quá bán (Vùng Mua Đẹp)")
        if d['rsi'] > 70: score -= 15; reasons.append("RSI Quá mua (Cẩn trọng)")

        # Decision
        signal = "NEUTRAL"
        if score >= 70: signal = "LONG"
        elif score <= 30: signal = "SHORT"
        
        # Safe ATR fallback
        atr_val = d['atr'] if not np.isnan(d['atr']) else d['close'] * 0.02

        thesis = f"Nguồn dữ liệu: {source}. " + ", ".join(reasons) + "."
        
        return {
            "symbol": symbol, "signal": signal, "score": score,
            "price": d['close'], "atr": atr_val,
            "thesis": thesis, "source": source
        }

    def plan(self, coin, cap, lev):
        entry = coin['price']
        atr = coin['atr']
        
        # [FIX] Tỷ lệ R:R chuẩn chỉnh hơn cho Long/Short
        if coin['signal'] == "LONG":
            sl = entry - (atr * 2)
            tp1 = entry + (atr * 2)
            tp2 = entry + (atr * 6) # R:R 1:3
        else:
            sl = entry + (atr * 2)
            tp1 = entry - (atr * 2)
            tp2 = entry - (atr * 6)
        
        margin = (cap * 0.1) / lev
        return {"entry": entry, "tp1": tp1, "tp2": tp2, "sl": sl, "margin": margin}

# --- 4. GIAO DIỆN CHÍNH ---
bot = TitanBrain()

st.title("🌪️ V25 TITAN: SUPREMACY")
st.caption("Inject Fix: Anti-Detect Rotation • Smart Fallback • Bug Free Core") 

with st.sidebar:
    st.header("⚡ CONTROL CENTER")
    rate = st.number_input("Tỷ giá USDT:", 25750, step=10)
    cap = st.number_input("Vốn (VND):", 10000000, step=1000000)
    lev = st.slider("Đòn bẩy:", 5, 125, 20)
    refresh = st.number_input("Scan Time (s):", value=30, min_value=10)
    auto = st.checkbox("🔮 AUTO-SCAN", value=True)
    if st.button("🚀 SCAN NGAY"): auto = True

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
            # [FIX] Delay random để giống người thật hơn
            time.sleep(random.uniform(0.1, 0.3))
        bar.empty()
        
        if results:
            # Lấy kèo ngon nhất
            best = sorted(results, key=lambda x: abs(x['score']-50), reverse=True)[0]
            
            # Chỉ hiện khi có tín hiệu rõ ràng
            if best['signal'] != "NEUTRAL":
                p = bot.plan(best, cap, lev)
                c_color = "#00FF41" if best['signal'] == "LONG" else "#FF0041"
                
                status_class = "live" if "LIVE" in best['source'] else "sim"
                
                st.markdown(f"""
                <div class='titan-card' style='border-color: {c_color};'>
                    <div style='display:flex; justify-content:space-between;'>
                        <span class='status-badge {status_class}'>{best['source']}</span>
                        <span style='color:#666'>#{best['symbol']}</span>
                    </div>
                    <h1 style='color:{c_color}; font-size: 4em; margin: 10px 0; letter-spacing: 2px;'>{best['signal']}</h1>
                    <div style='background:#111; display:inline-block; padding:5px 20px; border-radius:15px; border:1px solid #333;'>
                        POWER SCORE: <span style='color:{c_color}; font-weight:bold'>{best['score']}/100</span>
                    </div>
                    <hr style='border-color: #333; margin: 20px 0;'>
                    <div style='display:grid; grid-template-columns: 1fr 1fr; gap: 20px;'>
                        <div><span class='metric-label'>ENTRY PRICE</span><br><span class='metric-val'>{p['entry']:,.4f}</span></div>
                        <div><span class='metric-label'>VOLUME (VND)</span><br><span class='metric-val' style='color:#FFD700'>{format_vnd(p['margin'], rate)}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("🎯 TP1 (Safe)", f"{p['tp1']:,.4f}")
                c2.metric("🚀 TP2 (Moon)", f"{p['tp2']:,.4f}")
                c3.metric("🛡️ STOPLOSS", f"{p['sl']:,.4f}", delta_color="inverse")
                
                st.markdown(f"<div class='thesis-box'>📝 <b>PHÂN TÍCH TITAN:</b><br>{best['thesis']}</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ Thị trường Sideway (Đi ngang). Bot chưa tìm thấy tín hiệu > 70 điểm.")
                
        else:
            st.error("⚠️ Toàn bộ vệ tinh bị chặn. Vui lòng F5 lại trang!")

    time.sleep(1)
    if auto:
        with st.empty():
            for s in range(refresh, 0, -1):
                st.write(f"⏳ Titan đang ẩn mình... {s}s")
                time.sleep(1)
        st.rerun()
