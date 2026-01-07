import streamlit as st
import pandas as pd
import numpy as np
import time
import ccxt
import requests

# --- 1. HỆ THỐNG BẢO MẬT HOÀNG GIA (ROYAL SECRETS) ---
def get_secret(key, default_value):
    if key in st.secrets:
        return st.secrets[key]
    return default_value

TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN", "8526079835:AAEmdcFeACgvqdWF8vfkWG46Qq7_uZ7ztmE") 
CHAT_ID = get_secret("CHAT_ID", "1654323145")

def send_telegram_alert(symbol, signal, score, entry, tp1, tp2, sl, reasons):
    icon = "🟢" if signal == "LONG" else "🔴"
    msg = (
        f"👑 *EMPEROR V18 - ROYAL SIGNAL* {icon}\n\n"
        f"🏆 *Asset:* #{symbol}\n"
        f"ex: *Signal:* {signal}\n"
        f"💎 *Win Rate Score:* {score}/100\n"
        f"-------------------\n"
        f"💰 Entry: {entry}\n"
        f"🥂 TP1 (Safe): {tp1}\n"
        f"🚀 TP2 (Moon): {tp2}\n"
        f"🛡️ SL (Protect): {sl}\n\n"
        f"📜 *Royal Analysis:*\n"
        f"{' • '.join(reasons)}\n"
        f"_The King is watching..._"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# --- 2. GIAO DIỆN LUXURY (DOANH NHÂN) ---
st.set_page_config(page_title="EMPEROR V18 ROYAL", layout="wide")
st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #d4af37; font-family: 'Helvetica Neue', sans-serif;}
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a, #332a00); 
        border: 2px solid #d4af37; padding: 25px; border-radius: 15px; 
        text-align: center; box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
    }
    .coin-header {font-size: 70px !important; font-weight: 900; color: #d4af37; text-shadow: 0 0 15px #d4af37;}
    .signal-text {font-size: 50px; font-weight: bold; text-transform: uppercase;}
    .reason-box {
        border-left: 4px solid #d4af37; padding-left: 15px; margin-bottom: 10px; 
        font-size: 16px; color: #e0e0e0; background: rgba(255, 255, 255, 0.05);
        padding-top: 5px; padding-bottom: 5px;
    }
    h1, h2, h3 {color: #d4af37 !important;}
    .stButton>button {
        background-color: #d4af37; color: black; font-weight: bold; border-radius: 10px;
        height: 50px; font-size: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BỘ NÃO HOÀNG ĐẾ (EMPEROR BRAIN) ---
class EmperorBrain:
    def __init__(self):
        try:
            self.exchange = ccxt.binance({'options': {'defaultType': 'future'}, 'enableRateLimit': True})
        except:
            self.exchange = None
        # List coin top, thanh khoản cao, tránh râu ria
        self.target_symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
            'DOGE/USDT', 'ADA/USDT', 'LINK/USDT', 'AVAX/USDT', 'DOT/USDT',
            'NEAR/USDT', 'PEPE/USDT', 'WIF/USDT', 'SUI/USDT', 'APT/USDT'
        ]

    def format_price(self, price):
        if price < 1: return f"{price:.6f}"
        if price < 100: return f"{price:.4f}"
        return f"{price:.2f}"

    def calculate_indicators(self, df):
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # EMA 50 & 200 (King of Trend)
        df['ema_50'] = df['close'].ewm(span=50).mean()
        df['ema_200'] = df['close'].ewm(span=200).mean()
        
        # Bollinger Bands
        df['ma_20'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper_bb'] = df['ma_20'] + (2 * df['std'])
        df['lower_bb'] = df['ma_20'] - (2 * df['std'])
        
        # ATR
        df['tr'] = np.maximum((df['high'] - df['low']), np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
        df['atr'] = df['tr'].rolling(14).mean()
        
        return df

    def fetch_analysis(self, symbol):
        if not self.exchange: return None
        try:
            # Lấy nến 15m (Entry) và 4h (Trend)
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='15m', limit=201)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df = self.calculate_indicators(df)
            
            # Lấy trend khung lớn 4H
            ticker = self.exchange.fetch_ticker(symbol)
            change_24h = ticker['percentage'] # % thay đổi 24h

            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # --- LOGIC HOÀNG GIA ---
            score = 50 # Điểm khởi đầu
            signal = "NEUTRAL"
            reasons = []

            # 1. Xác định Xu hướng (Trend is King)
            is_uptrend = current['close'] > current['ema_200']
            is_downtrend = current['close'] < current['ema_200']

            if is_uptrend:
                score += 10; reasons.append("Nằm trên EMA 200 (Long Term Up)")
            elif is_downtrend:
                score += 10; reasons.append("Nằm dưới EMA 200 (Long Term Down)")

            # 2. Logic Vào Lệnh (Aggressive but Smart)
            # LONG SCENARIO
            if is_uptrend:
                # Điều kiện: Giá hồi về EMA50 hoặc RSI oversold nhẹ trong uptrend
                if current['rsi'] < 60 and current['rsi'] > 40: # Vùng tích lũy đẹp để bay
                    signal = "LONG"
                    score += 20; reasons.append("RSI vùng vàng (40-60) sẵn sàng bơm")
                if current['close'] > current['ema_50'] and prev['close'] < prev['ema_50']: # Cắt lên EMA50
                    signal = "LONG"
                    score += 15; reasons.append("Giá cắt lên EMA 50 (Golden Cross)")
                if current['volume'] > df['volume'].rolling(20).mean().iloc[-1] * 1.5:
                    score += 10; reasons.append("Dòng tiền cá mập vào (Vol x1.5)")

            # SHORT SCENARIO
            elif is_downtrend:
                if current['rsi'] > 40 and current['rsi'] < 60:
                    signal = "SHORT"
                    score += 20; reasons.append("RSI vùng phân phối đẹp")
                if current['close'] < current['ema_50'] and prev['close'] > prev['ema_50']:
                    signal = "SHORT"
                    score += 15; reasons.append("Giá thủng EMA 50 (Death Cross)")
                if current['close'] < current['lower_bb']: # Thủng band
                    signal = "SHORT"
                    score += 5; reasons.append("Thủng Bollinger Band dưới")

            # 3. Bộ lọc nhiễu
            if abs(change_24h) < 1.0: # Biến động quá ít
                score -= 10; reasons.append("⚠️ Market quá chán (Sideway)")
            
            return {
                "symbol": symbol, "price": current['close'], "atr": current['atr'],
                "signal": signal, "score": score, "reasons": reasons,
                "rsi": current['rsi']
            }
        except: return None

    def scan_market(self):
        results = []
        progress_text = "💎 Hệ thống Hoàng Gia đang chọn lọc kim cương..."
        my_bar = st.progress(0, text=progress_text)
        
        for i, symbol in enumerate(self.target_symbols):
            data = self.fetch_analysis(symbol)
            if data and data['signal'] != "NEUTRAL":
                results.append(data)
            time.sleep(0.1)
            my_bar.progress((i + 1) / len(self.target_symbols))
        
        my_bar.empty()
        
        # Sắp xếp lấy con ngon nhất
        if not results: return None
        best_coin = sorted(results, key=lambda x: x['score'], reverse=True)[0]
        return best_coin

    def calculate_royal_plan(self, coin, capital, lev):
        entry = coin['price']
        atr = coin['atr']
        
        # Stoploss dựa trên ATR (Co dãn theo thị trường)
        sl_dist = atr * 2.5 # Rộng hơn chút để tránh quét râu
        
        if coin['signal'] == "LONG":
            sl = entry - sl_dist
            tp1 = entry + (sl_dist * 1.5)
            tp2 = entry + (sl_dist * 4.0) # Ăn dày
        else:
            sl = entry + sl_dist
            tp1 = entry - (sl_dist * 1.5)
            tp2 = entry - (sl_dist * 4.0)
            
        # Quản lý vốn: Chỉ risk 3% vốn cho lệnh này
        risk_amount = capital * 0.03
        price_dist_pct = abs(entry - sl) / entry
        if price_dist_pct == 0: price_dist_pct = 0.01
        
        position_size = risk_amount / price_dist_pct
        margin = min(position_size / lev, capital)
        
        return {"entry": self.format_price(entry), 
                "tp1": self.format_price(tp1), 
                "tp2": self.format_price(tp2), 
                "sl": self.format_price(sl), 
                "margin": margin}

# --- 4. MAIN APP ---
bot = EmperorBrain()

c1, c2 = st.columns([1, 4])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/6941/6941697.png", width=100)
with c2: 
    st.title("EMPEROR V18")
    st.caption("ROYAL TRADING SYSTEM - KING OF MARKET")

with st.sidebar:
    st.header("⚙️ ROYAL CONFIG")
    cap = st.number_input("Vốn Đầu Tư (VNDC):", value=1000000, step=500000)
    lev = st.slider("Đòn bẩy Vua (Leverage):", 10, 125, 20)
    st.markdown("---")
    auto = st.checkbox("🔄 AUTO-HUNT (Săn Tự Động)", value=True)
    refresh = st.number_input("Tốc độ săn (s):", value=60, min_value=30)
    scan_now = st.button("⚜️ SĂN NGAY LẬP TỨC")

if auto or scan_now:
    if auto:
        with st.empty():
            for i in range(refresh, 0, -1):
                st.write(f"⏳ Thị trường đang được theo dõi... ({i}s)")
                time.sleep(1)
    
    # Quét
    best = bot.scan_market()
    
    if best:
        # Hạ chuẩn xuống 55 điểm là báo kèo (Aggressive Mode)
        if best['score'] >= 55:
            plan = bot.calculate_royal_plan(best, cap, lev)
            
            # Gửi Tele
            send_telegram_alert(best['symbol'], best['signal'], best['score'], 
                                plan['entry'], plan['tp1'], plan['tp2'], plan['sl'], best['reasons'])
            
            if scan_now: st.toast("Đã tìm thấy Long Mạch!", icon="🐉")
            
            # Hiển thị
            col_main, col_info = st.columns([2, 3])
            
            with col_main:
                color = "#00FF00" if best['signal'] == "LONG" else "#FF4444"
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='color: #d4af37; font-size: 20px; letter-spacing: 3px;'>ASSET CLASS A</div>
                    <div class='coin-header'>{best['symbol'].replace('/USDT','')}</div>
                    <div class='signal-text' style='color: {color}'>{best['signal']}</div>
                    <div style='font-size: 24px; color: white; margin-top: 10px;'>
                        SCORE: {best['score']}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_info:
                st.subheader("📜 PHÂN TÍCH HOÀNG GIA")
                for r in best['reasons']:
                    st.markdown(f"<div class='reason-box'>✦ {r}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("ENTRY", plan['entry'], f"Margin: {plan['margin']:,.0f}")
                m2.metric("TAKE PROFIT", plan['tp1'], "TP2: Moon")
                m3.metric("STOP LOSS", plan['sl'], "Bảo toàn vốn")
        
        else:
            st.warning(f"👑 Đã quét xong: Tốt nhất là {best['symbol']} ({best['score']} điểm). Nhưng chưa đủ chuẩn Hoàng Gia (55). Đang chờ cơ hội đẹp hơn...")
    else:
        st.error("⚠️ Thị trường đang ngủ đông. Không có biến động để kiếm tiền.")

    if auto: st.rerun()
