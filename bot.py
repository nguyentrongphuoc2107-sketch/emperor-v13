import streamlit as st
import pandas as pd
import numpy as np
import time
import ccxt
import requests

# --- 1. CONFIG TELEGRAM & SECRETS (ĐÃ INJECT BẢO MẬT) ---
# Bot sẽ tự tìm Token trong st.secrets trước, nếu không có mới dùng code cứng (để test local)
def get_secret(key, default_value):
    if key in st.secrets:
        return st.secrets[key]
    return default_value

# [INJECTED] Tự động lấy từ Secrets của Streamlit Cloud
TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN", "8526079835:AAEmdcFeACgvqdWF8vfkWG46Qq7_uZ7ztmE") 
CHAT_ID = get_secret("CHAT_ID", "1654323145")

def send_telegram_alert(symbol, signal, score, entry, tp1, tp2, sl, reasons):
    """Gửi tín hiệu Thần Thánh về Telegram"""
    icon = "🟢" if signal == "LONG" else "🔴"
    msg = (
        f"👹 *DEMON V17 - GOD MODE ACTIVATED* {icon}\n\n"
        f"💎 *Asset:* #{symbol}\n"
        f"🚀 *Signal:* {signal}\n"
        f"💯 *Confidence:* {score}/100\n"
        f"-------------------\n"
        f"⚡ Entry: {entry:.4f}\n"
        f"🎯 TP1: {tp1:.4f}\n"
        f"🎯 TP2: {tp2:.4f}\n"
        f"🛑 SL: {sl:.4f}\n\n"
        f"🧠 *Phân tích Tinh hoa:*\n"
        f"{' • '.join(reasons)}\n"
        f"_Kiểm tra chart ngay!_"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# --- 2. CONFIG GIAO DIỆN SIÊU CẤP ---
st.set_page_config(page_title="DEMON GOD MODE V17", layout="wide")
st.markdown("""
<style>
    .stApp {background-color: #000000; color: #00FF00; font-family: 'Courier New', monospace;}
    .metric-card {
        background: linear-gradient(135deg, #111, #222); 
        border: 1px solid #00FF00; padding: 20px; border-radius: 12px; 
        text-align: center; box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
    }
    .coin-header {font-size: 60px !important; font-weight: 900; color: #FFD700; text-shadow: 0 0 10px #FFD700;}
    .price-display {font-size: 32px !important; font-weight: bold; color: #fff;}
    .reason-box {
        border-left: 3px solid #00FF00; padding-left: 10px; margin-bottom: 8px; 
        font-size: 14px; color: #ccc;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CLASS TITAN BRAIN (GIỮ NGUYÊN BẢN V17) ---
class TitanBrain:
    def __init__(self):
        try:
            self.exchange = ccxt.binance({'options': {'defaultType': 'future'}, 'enableRateLimit': True})
        except:
            self.exchange = None
        self.target_symbols = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 
            'DOGE/USDT', 'PEPE/USDT', 'WIF/USDT', 
            'NEAR/USDT', 'APT/USDT', 'SUI/USDT', 'LINK/USDT', 'AVAX/USDT', 'FET/USDT', 'RNDR/USDT'
        ]

    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        df['ma_20'] = df['close'].rolling(window=period).mean()
        df['std_dev'] = df['close'].rolling(window=period).std()
        df['upper_bb'] = df['ma_20'] + (df['std_dev'] * std_dev)
        df['lower_bb'] = df['ma_20'] - (df['std_dev'] * std_dev)
        return df

    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal_line'] = df['macd'].ewm(span=signal, adjust=False).mean()
        return df

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        return 100 - (100 / (1 + rs))

    def fetch_market_context(self, symbol):
        if not self.exchange: return None
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='15m', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            ohlcv_4h = self.exchange.fetch_ohlcv(symbol, timeframe='4h', limit=50)
            df_4h = pd.DataFrame(ohlcv_4h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            ticker = self.exchange.fetch_ticker(symbol)
            spread_pct = (ticker['ask'] - ticker['bid']) / ticker['ask'] * 100

            df['tr'] = np.maximum((df['high'] - df['low']), np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
            atr = df['tr'].rolling(14).mean().iloc[-1]
            df['rsi'] = self.calculate_rsi(df['close'])
            df = self.calculate_bollinger_bands(df)
            df = self.calculate_macd(df)

            ema_20_15m = df['close'].ewm(span=20).mean().iloc[-1]
            ema_50_15m = df['close'].ewm(span=50).mean().iloc[-1] 
            trend_15m = "UP" if df['close'].iloc[-1] > ema_20_15m else "DOWN"
            ema_20_4h = df_4h['close'].ewm(span=20).mean().iloc[-1]
            trend_4h = "UP" if df_4h['close'].iloc[-1] > ema_20_4h else "DOWN"

            recent = df.iloc[-10:-1]
            swing_low, swing_high = recent['low'].min(), recent['high'].max()

            avg_vol = df['volume'].rolling(20).mean().iloc[-1]
            cur_vol = df['volume'].iloc[-1]
            vol_spike = cur_vol > (avg_vol * 1.5)

            c1, c3 = df.iloc[-4], df.iloc[-2]
            fvg = "Bullish FVG" if c1['high'] < c3['low'] else ("Bearish FVG" if c1['low'] > c3['high'] else None)

            return {
                "symbol": symbol, "price": df['close'].iloc[-1], "atr": atr,
                "rsi": df['rsi'].iloc[-1], 
                "macd": df['macd'].iloc[-1], "macds": df['signal_line'].iloc[-1],
                "bb_upper": df['upper_bb'].iloc[-1], "bb_lower": df['lower_bb'].iloc[-1],
                "trend_15m": trend_15m, "trend_4h": trend_4h, "ema_50": ema_50_15m,
                "vol_spike": vol_spike, "spread": spread_pct, "fvg": fvg,
                "low": swing_low, "high": swing_high, "is_green": df['close'].iloc[-1] > df['open'].iloc[-1]
            }
        except: return None

    def get_god_mode_analysis(self):
        analyzed_data = []
        # [INJECTED] Thêm try-except để tránh crash khi auto-run
        try:
            progress_text = "🧠 Titan Brain đang quét thị trường (GOD MODE)..."
            my_bar = st.progress(0, text=progress_text)
            
            raw_contexts = []
            total_coins = len(self.target_symbols)
            for i, symbol in enumerate(self.target_symbols):
                ctx = self.fetch_market_context(symbol)
                if ctx: raw_contexts.append(ctx)
                time.sleep(0.1) # [INJECTED] Nghỉ nhẹ để tránh rate limit của Binance
                my_bar.progress((i + 1) / total_coins, text=f"Đang phân tích {symbol}...")
            
            my_bar.empty()

            for ctx in raw_contexts:
                if ctx['spread'] > 0.15: continue
                
                score = 50
                reasons = []
                signal = "NEUTRAL"
                
                bullish_structure = ctx['price'] > ctx['ema_50'] and ctx['trend_15m'] == "UP"
                if bullish_structure:
                    if ctx['rsi'] < 75 or (ctx['rsi'] < 85 and ctx['vol_spike']):
                        signal = "LONG"
                        score += 10; reasons.append("Cấu trúc giá Tăng (Trên EMA 50)")
                        if ctx['macd'] > ctx['macds']: score += 15; reasons.append("MACD cắt lên (Momentum Tăng)")
                        if ctx['price'] > ctx['bb_upper'] * 0.99: score += 10; reasons.append("Giá bám dải trên BB")
                        if ctx['trend_4h'] == "UP": score += 15; reasons.append("Đồng pha khung 4H")

                bearish_structure = ctx['price'] < ctx['ema_50'] and ctx['trend_15m'] == "DOWN"
                if bearish_structure:
                    if ctx['rsi'] > 25 or (ctx['rsi'] > 15 and ctx['vol_spike']):
                        signal = "SHORT"
                        score += 10; reasons.append("Cấu trúc giá Giảm (Dưới EMA 50)")
                        if ctx['macd'] < ctx['macds']: score += 15; reasons.append("MACD cắt xuống (Momentum Giảm)")
                        if ctx['price'] < ctx['bb_lower'] * 1.01: score += 10; reasons.append("Giá bám dải dưới BB")
                        if ctx['trend_4h'] == "DOWN": score += 15; reasons.append("Đồng pha khung 4H")

                if signal != "NEUTRAL":
                    if ctx['vol_spike']: score += 15; reasons.append("⚡ Volume Đột biến")
                    if ctx['fvg']: score += 10; reasons.append(f"Phản ứng tại {ctx['fvg']}")

                if score >= 65 and signal != "NEUTRAL":
                    analyzed_data.append({
                        "symbol": ctx['symbol'].replace("/USDT", ""),
                        "price": ctx['price'], "atr": ctx['atr'],
                        "signal": signal, "score": score, "reasons": reasons,
                        "rsi": ctx['rsi'], "low": ctx['low'], "high": ctx['high']
                    })

            if not analyzed_data: return None
            return sorted(analyzed_data, key=lambda x: x['score'], reverse=True)[0]
        except Exception as e:
            st.error(f"Lỗi khi quét: {e}")
            return None

    def calculate_steel_risk(self, coin, capital, lev, mode):
        entry = coin['price']
        atr = coin['atr']
        atr_mult = 2.0 if mode == 'Học Đường/Qua Đêm (Swing)' else 1.2
        
        if coin['signal'] == "LONG":
            sl = entry - (atr * atr_mult)
            if (entry - sl) / entry < 0.004: sl = entry * 0.996
            tp1 = entry + (entry - sl) * 1.5 
            tp2 = entry + (entry - sl) * 3.0 
        else:
            sl = entry + (atr * atr_mult)
            if (sl - entry) / entry < 0.004: sl = entry * 1.004
            tp1 = entry - (sl - entry) * 1.5
            tp2 = entry - (sl - entry) * 3.0

        risk_per_trade = capital * 0.05
        dist_pct = abs(entry - sl) / entry
        pos_size = risk_per_trade / dist_pct
        margin = min(pos_size / lev, capital)
        
        return {"entry": entry, "tp1": tp1, "tp2": tp2, "sl": sl, "margin": margin}

# --- 4. MAIN APP ---
bot = TitanBrain()
st.title("👹 DEMON V17 - GOD MODE TRADING")
st.caption("🔥 Tích hợp: Bollinger Bands, MACD, Volume Spike, Smart Scoring & Multi-Timeframe")

# [INJECTED] Sidebar Control cho Auto-Bot
with st.sidebar:
    st.header("⚙️ CẤU HÌNH")
    cap = st.number_input("Vốn (VNDC):", value=500000, step=100000)
    lev = st.slider("Đòn bẩy (Leverage):", 5, 125, 20)
    mode = st.radio("Style đánh:", ["Scalping (Nhanh)", "Học Đường/Qua Đêm (Swing)"])
    
    st.markdown("---")
    st.header("🤖 AUTO-PILOT")
    auto_run = st.checkbox("🔄 Kích hoạt Auto-Bot 24/7")
    refresh_rate = st.number_input("Chu kỳ quét (giây):", min_value=60, value=300, step=60)
    
    manual_scan = st.button("🚀 QUÉT NGAY (MANUAL)", type="primary")

# Logic Chạy
if auto_run or manual_scan:
    # Nếu là auto-run, hiển thị trạng thái
    if auto_run:
        with st.empty():
            for seconds in range(refresh_rate, 0, -1):
                st.write(f"⏳ Bot sẽ quét lại sau {seconds} giây...")
                time.sleep(1)
            st.write("⚡ Đang quét...")

    best_coin = bot.get_god_mode_analysis()
    
    if best_coin:
        plan = bot.calculate_steel_risk(best_coin, cap, lev, mode)
        
        # Gửi Telegram
        send_telegram_alert(
            best_coin['symbol'], best_coin['signal'], best_coin['score'], 
            plan['entry'], plan['tp1'], plan['tp2'], plan['sl'], best_coin['reasons']
        )
        if manual_scan: st.toast("Đã bắn tín hiệu lên Vũ Trụ Telegram!", icon="🛰️")

        # UI Hiển thị
        c1, c2 = st.columns([1.5, 2.5])
        with c1:
            color = "#00FF00" if best_coin['signal'] == "LONG" else "#FF0000"
            st.markdown(f"""
            <div class='metric-card'>
                <div style='color: #888;'>VICTORY TARGET</div>
                <div class='coin-header'>{best_coin['symbol']}</div>
                <div style='font-size: 48px; font-weight: 900; color: {color}'>{best_coin['signal']}</div>
                <div style='margin-top: 10px; background: #333; color: white;'>RSI: {best_coin['rsi']:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"### 🛡️ CONFIDENCE SCORE: {best_coin['score']}/100")
            st.write("Logic phân tích:")
            for r in best_coin['reasons']:
                st.markdown(f"<div class='reason-box'>➤ {r}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        k1, k2, k3 = st.columns(3)
        k1.metric("🔵 ENTRY ZONE", f"{plan['entry']:.4f}", f"Margin: {bot.format_vndc(plan['margin'])}")
        k2.metric("🟢 TAKE PROFIT (TP)", f"{plan['tp1']:.4f}", f"TP2: {plan['tp2']:.4f}")
        k3.metric("🔴 STOP LOSS (SL)", f"{plan['sl']:.4f}", "Tuân thủ tuyệt đối")
    
    elif manual_scan:
        st.error("⚠️ Thị trường đang quá nhiễu (Sideways).")

    # [INJECTED] Logic Rerun cho Auto
    if auto_run:
        st.rerun()
