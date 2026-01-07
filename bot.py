import streamlit as st
import pandas as pd
import numpy as np
import time
import ccxt
import requests
import json

# --- 1. CẤU HÌNH HỆ THỐNG & TELEGRAM ---
st.set_page_config(page_title="EMPEROR V23 TITAN", layout="wide")

def get_secret(key, default_value):
    try: return st.secrets.get(key, default_value)
    except: return default_value

TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN", "8526079835:AAEmdcFeACgvqdWF8vfkWG46Qq7_uZ7ztmE") 
CHAT_ID = get_secret("CHAT_ID", "1654323145")

# --- 2. HÀM HỖ TRỢ ---
def format_vnd(amount_usdt, rate):
    val = amount_usdt * rate
    if val >= 1e9: return f"{val/1e9:.2f} Tỷ"
    if val >= 1e6: return f"{val/1e6:.1f} Tr"
    return f"{val:,.0f} đ"

def send_telegram(symbol, signal, score, plan, thesis, rate):
    icon = "🟢 LONG" if signal == "LONG" else "🔴 SHORT"
    msg = (
        f"🌪️ *V23 - TITAN ĐẠI ĐẾ* 🌪️\n\n"
        f"💎 *Asset:* #{symbol.replace('/USDT','')}\n"
        f"🔥 *Signal:* {icon} (Score: {score}/100)\n"
        f"--------------------------\n"
        f"💵 Entry: {plan['entry']} (~{format_vnd(plan['raw_entry'], rate)})\n"
        f"🎯 TP1: {plan['tp1']}\n"
        f"🚀 TP2: {plan['tp2']}\n"
        f"🛑 SL: {plan['sl']}\n"
        f"--------------------------\n"
        f"📜 *LUẬN ĐIỂM ĐẦU TƯ:*\n{thesis}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=3)
    except: pass

# --- 3. GIAO DIỆN TITAN ---
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
    .metric-label {color: #aaa; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px;}
    .metric-val {color: #fff; font-size: 1.8em; font-weight: 800;}
</style>
""", unsafe_allow_html=True)

# --- 4. BỘ NÃO TITAN (4D ANALYSIS) ---
class TitanBrain:
    def __init__(self):
        self.exchange = ccxt.binance({'options': {'defaultType': 'future'}, 'timeout': 5000})
        self.targets = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
            'DOGE/USDT', 'SUI/USDT', 'APT/USDT', 'NEAR/USDT', 'PEPE/USDT'
        ]

    def get_data(self, symbol):
        # Anti-Block: Thử CCXT -> Thử API Public
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '15m', limit=100)
            return self.process(ohlcv)
        except:
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol.replace('/','')}&interval=15m&limit=100"
                d = requests.get(url, timeout=3).json()
                ohlcv = [[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in d]
                return self.process(ohlcv)
            except: return None

    def process(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        
        # 1. Trend (EMA)
        df['ema34'] = df['close'].ewm(span=34).mean()
        df['ema89'] = df['close'].ewm(span=89).mean()
        
        # 2. Momentum (RSI + MACD)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema12 - ema26
        df['signal_line'] = df['macd'].ewm(span=9).mean()
        
        # 3. Volatility (Bollinger Bands)
        df['ma20'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper'] = df['ma20'] + 2*df['std']
        df['lower'] = df['ma20'] - 2*df['std']
        
        # 4. Money Flow (Volume)
        df['vol_ma'] = df['vol'].rolling(20).mean()
        
        # ATR for Stoploss
        df['tr'] = np.maximum((df['high'] - df['low']), abs(df['high'] - df['close'].shift(1)))
        df['atr'] = df['tr'].rolling(14).mean()
        
        return df.iloc[-1]

    def generate_narrative(self, data, trend, macd_signal, vol_signal, symbol):
        # Đây là module "Nhà Văn" - Tạo ra luận điểm thuyết phục
        narrative = f"Tôi đang quan sát **{symbol}** rất kỹ. "
        
        # Phân tích xu hướng
        if trend == "UP":
            narrative += f"Đầu tiên, cấu trúc giá đang nằm trong **Xu hướng Tăng (Uptrend)** khi giá nằm trên dải EMA89 vàng ngọc. phe Bò đang kiểm soát cuộc chơi. "
        elif trend == "DOWN":
            narrative += f"Đầu tiên, thị trường đang bị phe Gấu thống trị, giá nằm dưới EMA89 xác nhận **Xu hướng Giảm (Downtrend)** rõ rệt. "
        else:
            narrative += "Thị trường đang đi ngang (Sideway), phe mua và bán đang giằng co quyết liệt. "

        # Phân tích động lượng & Chỉ báo
        if macd_signal == "BULLISH":
            narrative += "Đáng chú ý, chỉ báo MACD đã cắt lên đường tín hiệu, cho thấy xung lực tăng đang quay trở lại. "
        elif macd_signal == "BEARISH":
            narrative += "Nguy hiểm hơn, MACD đã cắt xuống, báo hiệu áp lực bán đang gia tăng mạnh mẽ. "
            
        narrative += f"RSI hiện tại là {data['rsi']:.1f}, "
        if data['rsi'] < 30: narrative += "đang ở vùng QUÁ BÁN. Theo lý thuyết, một nhịp hồi phục kỹ thuật là rất khả thi. "
        elif data['rsi'] > 70: narrative += "đang ở vùng QUÁ MUA. Cẩn trọng cú sập điều chỉnh bất ngờ. "
        else: narrative += "nằm ở vùng trung tính, dư địa để giá chạy vẫn còn rất lớn. "

        # Phân tích dòng tiền (Volume)
        if vol_signal:
            narrative += "Đặc biệt, **Volume giao dịch đột biến** (lớn hơn trung bình 20 phiên) cho thấy 'Cá Mập' đã tham gia. Dấu chân dòng tiền lớn là bảo chứng cho độ tin cậy của kèo này."
        else:
            narrative += "Tuy nhiên, Volume chưa thực sự nổ mạnh, cần quản lý vốn chặt chẽ vì có thể là bẫy thanh khoản."

        # Kết luận
        narrative += "\n\n👉 **KẾT LUẬN:** Dựa trên sự hội tụ của các yếu tố trên, hệ thống kích hoạt tín hiệu này."
        return narrative

    def analyze(self, symbol):
        d = self.get_data(symbol)
        if d is None: return None
        
        score = 50
        signal = "NEUTRAL"
        
        # 1. Trend Check
        if d['close'] > d['ema89']: 
            score += 20; trend = "UP"
        elif d['close'] < d['ema89']: 
            score -= 20; trend = "DOWN"
        else: trend = "SIDEWAY"

        # 2. Momentum Check
        macd_sig = "NEUTRAL"
        if d['macd'] > d['signal_line']: 
            score += 15; macd_sig = "BULLISH"
        elif d['macd'] < d['signal_line']: 
            score -= 15; macd_sig = "BEARISH"

        # 3. RSI Adjustment
        if trend == "UP" and 40 <= d['rsi'] <= 60: score += 10 # Buy dip
        if trend == "DOWN" and 40 <= d['rsi'] <= 60: score -= 10 # Sell rip
        if d['rsi'] < 30: score += 15 # Oversold -> Long reversal potential
        if d['rsi'] > 70: score -= 15 # Overbought -> Short reversal potential

        # 4. Volume Confirmation (Smart Money)
        vol_confirmed = False
        if d['vol'] > d['vol_ma']:
            vol_confirmed = True
            if trend == "UP": score += 10
            if trend == "DOWN": score -= 10

        # Quyết định cuối cùng
        if score >= 75: signal = "LONG"
        elif score <= 25: signal = "SHORT"
        
        # Viết văn
        thesis = self.generate_narrative(d, trend, macd_sig, vol_confirmed, symbol)

        return {
            "symbol": symbol, "signal": signal, "score": score,
            "price": d['close'], "atr": d['atr'], "thesis": thesis
        }

    def plan(self, coin, cap, lev):
        entry = coin['price']
        atr = coin['atr']
        # Dynamic Risk Management
        if coin['signal'] == "LONG":
            sl = entry - (atr * 2.5)
            tp1 = entry + (atr * 2)
            tp2 = entry + (atr * 6) # R:R 1:3
        else:
            sl = entry + (atr * 2.5)
            tp1 = entry - (atr * 2)
            tp2 = entry - (atr * 6)
            
        margin = (cap * 0.1) / lev # Tự tin đi lệnh 10% vốn nếu bot báo
        
        def f(x): return f"{x:.4f}" if x < 50 else f"{x:,.2f}"
        return {
            "entry": f(entry), "raw_entry": entry,
            "tp1": f(tp1), "raw_tp1": tp1,
            "tp2": f(tp2), "raw_tp2": tp2,
            "sl": f(sl), "raw_sl": sl,
            "margin": margin
        }

# --- 5. MAIN EXECUTION ---
bot = TitanBrain()

st.title("🌪️ V23 TITAN: ĐẠI ĐẾ THỨC TỈNH")
st.caption("Phiên bản AI tự viết luận điểm đầu tư & Phân tích dòng tiền")

with st.sidebar:
    st.header("⚡ CONTROL CENTER")
    rate = st.number_input("Tỷ giá USDT:", 25750, step=10)
    cap = st.number_input("Vốn (VND):", 10000000, step=1000000)
    lev = st.slider("Đòn bẩy:", 5, 125, 20)
    st.divider()
    # Fix lỗi cú pháp min_value
    refresh = st.number_input("Scan Time (s):", value=30, min_value=10)
    auto = st.checkbox("🔮 AUTO-SCAN", value=True)
    if st.button("🚀 QUÉT NGAY LẬP TỨC"): auto = True

if auto:
    res_container = st.empty()
    with res_container.container():
        st.info("📡 Titan đang quét toàn bộ dữ liệu thị trường...")
        results = []
        bar = st.progress(0)
        
        for i, sym in enumerate(bot.targets):
            data = bot.analyze(sym)
            if data: results.append(data)
            bar.progress((i+1)/len(bot.targets))
            time.sleep(0.1)
        bar.empty()
        
        if results:
            # Lọc kèo ngon nhất (Score lệch xa 50 nhất)
            best = sorted(results, key=lambda x: abs(x['score']-50), reverse=True)[0]
            
            if best['signal'] != "NEUTRAL":
                p = bot.plan(best, cap, lev)
                send_telegram(best['symbol'], best['signal'], best['score'], p, best['thesis'], rate)
                
                # Giao diện hiển thị đỉnh cao
                c_color = "#00FF41" if best['signal'] == "LONG" else "#FF0041"
                st.markdown(f"""
                <div class='titan-card' style='border-color: {c_color};'>
                    <h3 style='color:#fff'>{best['symbol']}</h3>
                    <h1 style='color:{c_color}; font-size: 3.5em; margin: 10px 0;'>{best['signal']}</h1>
                    <span style='background:#333; padding: 5px 15px; border-radius: 20px; color: #fff;'>CONFIDENCE: {best['score']}/100</span>
                    <hr style='border-color: #444; margin-top: 20px;'>
                    <div style='display:grid; grid-template-columns: 1fr 1fr; text-align: left; gap: 20px;'>
                        <div>
                            <div class='metric-label'>ENTRY PRICE</div>
                            <div class='metric-val'>{p['entry']}</div>
                        </div>
                        <div>
                            <div class='metric-label'>SIZE (VND)</div>
                            <div class='metric-val' style='color:#FFD700'>{format_vnd(p['margin'], 1)}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("🎯 TP1 (Safe)", p['tp1'], f"+{format_vnd(p['raw_tp1']-p['raw_entry'] if best['signal']=='LONG' else p['raw_entry']-p['raw_tp1'], rate)}")
                c2.metric("🚀 TP2 (Moon)", p['tp2'], f"+{format_vnd(p['raw_tp2']-p['raw_entry'] if best['signal']=='LONG' else p['raw_entry']-p['raw_tp2'], rate)}")
                c3.metric("🛡️ STOP LOSS", p['sl'], delta_color="inverse")

                # Phần luận điểm nghị luận
                st.markdown(f"""
                <div class='thesis-box'>
                    <h3>📜 PHÂN TÍCH CHUYÊN SÂU:</h3>
                    {best['thesis']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("😴 Thị trường Sideway buồn ngủ. Titan khuyến nghị: Ngồi chơi xơi nước, giữ tiền là kiếm tiền!")
        else:
            st.error("⚠️ Mất kết nối vệ tinh. Đang thử định tuyến lại...")

    time.sleep(1)
    if auto:
        with st.empty():
            for s in range(refresh, 0, -1):
                st.write(f"⏳ Titan đang sạc năng lượng... {s}s")
                time.sleep(1)
        st.rerun()
