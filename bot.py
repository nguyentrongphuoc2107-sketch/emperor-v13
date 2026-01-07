import streamlit as st
import pandas as pd
import numpy as np
import time
import ccxt
import requests

# --- 1. HỆ THỐNG BẢO MẬT & TELEGRAM (GIỮ NGUYÊN) ---
def get_secret(key, default_value):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return default_value

TELEGRAM_TOKEN = get_secret("TELEGRAM_TOKEN", "8526079835:AAEmdcFeACgvqdWF8vfkWG46Qq7_uZ7ztmE") 
CHAT_ID = get_secret("CHAT_ID", "1654323145")

# --- 2. HÀM CHUYỂN ĐỔI TIỀN TỆ (NEW INJECTION) ---
def format_vnd(amount_usdt, rate=25750):
    amount_vnd = amount_usdt * rate
    if amount_vnd >= 1000000000:
        return f"{amount_vnd/1000000000:.2f} Tỷ đ"
    if amount_vnd >= 1000000:
        return f"{amount_vnd/1000000:.1f} Triệu đ"
    return f"{amount_vnd:,.0f} đ"

def send_telegram_alert(symbol, signal, score, plan, thesis, rate):
    icon = "🟢" if signal == "LONG" else "🔴"
    # Convert sang VND để báo tin nhắn
    e_vnd = format_vnd(float(plan['raw_entry']), rate)
    tp1_vnd = format_vnd(float(plan['raw_tp1']), rate)
    tp2_vnd = format_vnd(float(plan['raw_tp2']), rate)
    sl_vnd = format_vnd(float(plan['raw_sl']), rate)
    
    msg = (
        f"🇻🇳 *EMPEROR V20 - VIETNAM DRAGON* {icon}\n\n"
        f"🏆 *Asset:* #{symbol}\n"
        f"🚀 *Action:* {signal}\n"
        f"💯 *Power Score:* {score}/100\n"
        f"-------------------\n"
        f"💰 Entry: {plan['entry']} (~{e_vnd})\n"
        f"🎯 TP1: {plan['tp1']} (~{tp1_vnd})\n"
        f"🌕 TP2: {plan['tp2']} (~{tp2_vnd})\n"
        f"🛡️ SL: {plan['sl']} (~{sl_vnd})\n\n"
        f"🧠 *Luận điểm Đầu tư:*\n"
        f"{thesis}\n"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
    try:
        requests.get(url, timeout=5)
    except:
        pass

# --- 3. GIAO DIỆN SIÊU CẤP ---
st.set_page_config(page_title="EMPEROR V20 VND", layout="wide")
st.markdown("""
<style>
    .stApp {background-color: #050505; color: #e5c100; font-family: 'Times New Roman', serif;}
    .metric-card {
        background: linear-gradient(180deg, #1f1f1f, #000); 
        border: 1px solid #e5c100; padding: 20px; border-radius: 10px; 
        text-align: center; box-shadow: 0 0 15px rgba(229, 193, 0, 0.2);
    }
    .thesis-box {
        border-left: 5px solid #e5c100; background-color: #111; padding: 15px;
        font-size: 16px; line-height: 1.6; font-style: italic; color: #fff;
        border-radius: 0 10px 10px 0;
    }
    .label-stat {font-size: 14px; color: #888; text-transform: uppercase;}
    .price-sub {font-size: 14px; color: #00ff00; font-weight: bold;}
    .stButton>button {background-color: #e5c100; color: #000; border: none; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- 4. BỘ NÃO HOÀNG ĐẾ (LOGIC XỬ LÝ) ---
class EmperorBrain:
    def __init__(self):
        try:
            self.exchange = ccxt.binance({
                'options': {'defaultType': 'future'}, 
                'enableRateLimit': True,
                'timeout': 15000 
            })
        except:
            self.exchange = None
        
        self.target_symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
            'DOGE/USDT', 'ADA/USDT', 'LINK/USDT', 'AVAX/USDT', 'NEAR/USDT', 
            'APT/USDT', 'SUI/USDT', 'WIF/USDT', 'PEPE/USDT'
        ]

    def format_price(self, price):
        if price < 1: return f"{price:.6f}"
        if price < 100: return f"{price:.4f}"
        return f"{price:,.2f}"

    def calculate_indicators(self, df):
        # RSI & MACD
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # EMA
        df['ema_34'] = df['close'].ewm(span=34).mean()
        df['ema_89'] = df['close'].ewm(span=89).mean() # Sonic R System
        df['ema_200'] = df['close'].ewm(span=200).mean()
        
        # Bollinger & ATR
        df['ma_20'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper_bb'] = df['ma_20'] + (2 * df['std'])
        df['lower_bb'] = df['ma_20'] - (2 * df['std'])
        df['tr'] = np.maximum((df['high'] - df['low']), np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
        df['atr'] = df['tr'].rolling(14).mean()
        df['vol_ma'] = df['volume'].rolling(20).mean()
        
        return df

    def generate_persuasive_thesis(self, symbol, signal, reasons, context):
        if signal == "NEUTRAL":
            return f"Thị trường {symbol} đang ngủ đông. Tiền lớn chưa vào. Vào lệnh lúc này dễ bị chôn vốn. Kiến nghị: Ngồi chơi xơi nước chờ thời."
        
        direction = "TĂNG (LONG)" if signal == "LONG" else "GIẢM (SHORT)"
        intro = f"Hệ thống phát hiện {symbol} đang vào pha {direction} cực đẹp."
        body = ""
        if "EMA" in str(reasons): body += " Cấu trúc giá đã phá vỡ các cản cứng, phe đối lập đã đầu hàng. "
        if "RSI" in str(reasons): body += " RSI đang ở vùng vàng, dư địa chạy lãi còn rất dài. "
        if "Volume" in str(reasons): body += " Cá mập đã vào hàng (Volume đột biến), đây không phải là bẫy. "
        return f"{intro}{body} Múc ngay kẻo lỡ tàu!"

    def fetch_analysis(self, symbol):
        if not self.exchange: return None
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='15m', limit=201)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df = self.calculate_indicators(df)
            
            curr = df.iloc[-1]
            score = 50
            signal = "NEUTRAL"
            tech_reasons = []

            # --- LOGIC HOÀNG GIA ---
            trend_up = curr['close'] > curr['ema_89'] and curr['ema_34'] > curr['ema_89']
            trend_down = curr['close'] < curr['ema_89'] and curr['ema_34'] < curr['ema_89']

            if trend_up:
                score += 15; tech_reasons.append("EMA34 > EMA89 (Uptrend)")
            elif trend_down:
                score += 15; tech_reasons.append("EMA34 < EMA89 (Downtrend)")

            if trend_up:
                if 45 <= curr['rsi'] <= 65: signal = "LONG"; score += 20; tech_reasons.append("RSI tích lũy đẹp")
                if curr['close'] > curr['upper_bb'] and curr['volume'] > curr['vol_ma']: signal = "LONG"; score += 15; tech_reasons.append("Phá Band trên + Vol to")
            elif trend_down:
                if 35 <= curr['rsi'] <= 55: signal = "SHORT"; score += 20; tech_reasons.append("RSI phân phối đẹp")
                if curr['close'] < curr['lower_bb'] and curr['volume'] > curr['vol_ma']: signal = "SHORT"; score += 15; tech_reasons.append("Thủng Band dưới + Vol to")

            if curr['volume'] > curr['vol_ma'] * 1.5: score += 10; tech_reasons.append("Volume nổ cực mạnh")

            thesis = self.generate_persuasive_thesis(symbol, signal, tech_reasons, curr)

            return {
                "symbol": symbol, "price": curr['close'], "atr": curr['atr'],
                "signal": signal, "score": score, "reasons": tech_reasons, "thesis": thesis
            }
        except: return None

    def scan_market(self):
        results = []
        progress_bar = st.progress(0, text="🔍 Đang soi kèo...")
        for i, symbol in enumerate(self.target_symbols):
            data = self.fetch_analysis(symbol)
            if data: results.append(data)
            time.sleep(0.05)
            progress_bar.progress((i + 1) / len(self.target_symbols))
        progress_bar.empty()
        return sorted(results, key=lambda x: x['score'], reverse=True)[0] if results else None

    def calculate_royal_plan(self, coin, capital, lev, rate):
        entry = coin['price']
        atr_val = coin['atr']
        
        if coin['signal'] == "LONG":
            sl = entry - (atr_val * 2.0)
            tp1 = entry + (atr_val * 2.0)
            tp2 = entry + (atr_val * 5.0)
        elif coin['signal'] == "SHORT":
            sl = entry + (atr_val * 2.0)
            tp1 = entry - (atr_val * 2.0)
            tp2 = entry - (atr_val * 5.0)
        else:
            sl = entry * 0.99; tp1 = entry * 1.01; tp2 = entry * 1.02

        risk_per_trade = capital * 0.05
        dist_pct = abs(entry - sl) / entry if entry else 1
        position_size = risk_per_trade / (dist_pct + 0.0001)
        margin = min(position_size / lev, capital)
        
        # Trả về cả giá trị gốc (raw) để tính toán và giá trị format để hiển thị
        return {
            "entry": self.format_price(entry), "raw_entry": entry,
            "tp1": self.format_price(tp1), "raw_tp1": tp1,
            "tp2": self.format_price(tp2), "raw_tp2": tp2,
            "sl": self.format_price(sl), "raw_sl": sl,
            "margin": margin
        }

# --- 5. MAIN APP ---
bot = EmperorBrain()

col_logo, col_title = st.columns([1, 5])
with col_title:
    st.title("🇻🇳 EMPEROR V20: RỒNG VIỆT")
    st.caption("Siêu Bot Phân Tích - Quy Đổi VND Tự Động")

with st.sidebar:
    st.header("⚙️ CONTROL PANEL")
    usdt_rate = st.number_input("Tỷ giá USDT/VND:", value=25750, step=10) # Tùy chỉnh tỷ giá
    cap = st.number_input("Vốn (VNDC):", value=1000000, step=100000)
    lev = st.slider("Đòn Bẩy:", 5, 125, 20)
    st.markdown("---")
    auto_mode = st.checkbox("🔮 AUTO-HUNT (Tự động săn)", value=True)
    refresh_rate = st.number_input("Chu kỳ (s):", value=60, min_value=10)
    manual_btn = st.button("SĂN KÈO NGAY")

if auto_mode or manual_btn:
    best_coin = bot.scan_market()
    
    if best_coin:
        plan = bot.calculate_royal_plan(best_coin, cap, lev, usdt_rate)
        
        # Gửi Telegram (chỉ khi điểm > 55)
        if best_coin['score'] >= 55:
            send_telegram_alert(best_coin['symbol'], best_coin['signal'], best_coin['score'], 
                                plan, best_coin['thesis'], usdt_rate)
            st.toast(f"Đã bắn tín hiệu {best_coin['symbol']} về Tele!", icon="💸")

        # --- HIỂN THỊ SONG NGỮ (USDT + VND) ---
        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        
        with c1:
            color = "#00FF00" if best_coin['signal'] == "LONG" else ("#FF0000" if best_coin['signal'] == "SHORT" else "#FFFF00")
            st.markdown(f"""
            <div class='metric-card'>
                <div class='label-stat'>COIN TIỀM NĂNG</div>
                <div style='font-size: 40px; font-weight: 900; color: #fff;'>{best_coin['symbol'].replace('/USDT','')}</div>
                <div style='font-size: 30px; font-weight: bold; color: {color}; margin: 10px 0;'>{best_coin['signal']}</div>
                <div class='label-stat'>SCORE: {best_coin['score']}/100</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 💎 KẾ HOẠCH (VND)")
            
            # Hàm hiển thị label metrics
            def show_metric(label, usdt_val, raw_val, color="normal"):
                vnd_val = format_vnd(float(raw_val), usdt_rate)
                st.metric(label, f"{usdt_val} $", f"≈ {vnd_val}", delta_color=color)

            m1, m2 = st.columns(2)
            with m1: show_metric("ENTRY", plan['entry'], plan['raw_entry'], "off")
            with m2: st.metric("VỐN LỆNH", f"{plan['margin']:,.0f} VND")
            
            m3, m4 = st.columns(2)
            with m3: show_metric("TP1 (An toàn)", plan['tp1'], plan['raw_tp1'], "normal")
            with m4: show_metric("TP2 (Siêu Lời)", plan['tp2'], plan['raw_tp2'], "normal")
            
            show_metric("STOP LOSS (Cắt lỗ)", plan['sl'], plan['raw_sl'], "inverse")

        with c2:
            st.markdown("### 📜 LUẬN ĐIỂM ĐẦU TƯ")
            st.markdown(f"<div class='thesis-box'>{best_coin['thesis']}</div>", unsafe_allow_html=True)
            st.markdown("#### 🧬 LÝ DO KỸ THUẬT:")
            for reason in best_coin['reasons']:
                st.markdown(f"- ✅ {reason}")

    else:
        st.error("Mất kết nối với sàn hoặc dữ liệu trống.")

    if auto_mode:
        st.markdown("---")
        t_ph = st.empty()
        for i in range(refresh_rate, 0, -1):
            t_ph.info(f"⏳ Nghỉ ngơi giữ sức... Quét lại sau **{i}s**")
            time.sleep(1)
        st.rerun()
