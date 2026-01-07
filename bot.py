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
        color: #ddd; font-size: 0.95em;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
        text-align: justify;
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
                return [[float(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in data], "LIVE (BINANCE)"
        except Exception:
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
                    formatted = [[x[0], x[1], x[2], x[3], x[4], 1000000] for x in data[-60:]]
                    return formatted, "LIVE (GECKO)"
        except:
            pass
        
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
        
        if not ohlcv or source == "DISCONNECTED": 
            return None
        
        d = self.process_indicators(ohlcv)
        if d is None: return None

        score = 50
        
        # --- LOGIC CHẤM ĐIỂM ---
        if d['close'] > d['ema89']: score += 20
        else: score -= 20
        
        if d['macd'] > d['signal_line']: score += 15
        else: score -= 15
        
        if d['rsi'] < 30: score += 10
        elif d['rsi'] > 70: score -= 10

        # Quyết định tín hiệu
        signal = "NEUTRAL"
        if score >= 75: signal = "LONG"
        elif score <= 25: signal = "SHORT"
        
        # --- GENERATE DISSERTATION (VĂN NGHỊ LUẬN MODE) ---
        # Phần mở bài
        if signal == "LONG":
            intro = f"Thị trường đang phát đi những tín hiệu khởi sắc mạnh mẽ đối với mã <b>#{symbol}</b>. Phe bò (Buyers) đang thể hiện sự áp đảo tuyệt đối trên biểu đồ kỹ thuật, tạo tiền đề cho một đợt tăng trưởng bùng nổ."
            trend_text = f"Xét về cấu trúc xu hướng, giá hiện đang giao dịch vững chắc <b>trên đường EMA89</b> (đường chỉ báo sinh tử). Đây là bằng chứng thép cho thấy dòng tiền lớn đang bảo vệ vị thế mua, biến mọi nhịp điều chỉnh thành cơ hội tích lũy."
        elif signal == "SHORT":
            intro = f"Cảnh báo đỏ đối với nhà đầu tư đang nắm giữ <b>#{symbol}</b>. Áp lực bán tháo đang bao trùm toàn bộ thị trường, phe gấu (Sellers) đang kiểm soát hoàn toàn cuộc chơi và đẩy giá về các vùng hỗ trợ thấp hơn."
            trend_text = f"Về mặt xu hướng, việc giá sập gãy và nằm sâu <b>dưới đường EMA89</b> cho thấy cấu trúc tăng giá đã bị phá vỡ hoàn toàn. Mọi nỗ lực hồi phục yếu ớt đều đang bị dập tắt bởi áp lực bán chủ động."
        else:
            return {
                "symbol": symbol, "signal": signal, "score": score,
                "price": d['close'], "atr": 0, "thesis": "", "source": source
            } # Neutral bỏ qua luôn để lọc cho sạch

        # Phần thân bài (Momentum & RSI)
        macd_val = "Cắt lên (Bullish)" if d['macd'] > d['signal_line'] else "Cắt xuống (Bearish)"
        momentum_text = f"Phân tích động lượng cho thấy chỉ báo MACD đang ở trạng thái <b>{macd_val}</b>. Điều này xác nhận xung lực của xu hướng hiện tại là rất mạnh, không phải là tín hiệu nhiễu."
        
        rsi_text = ""
        if d['rsi'] < 30:
            rsi_text = f"Đặc biệt lưu ý, chỉ báo RSI đang rơi vào vùng <b>Quá bán (Oversold - {d['rsi']:.1f})</b>. Theo lý thuyết Dow, đây thường là vùng giá chiết khấu cực tốt để dòng tiền thông minh bắt đầu giải ngân."
        elif d['rsi'] > 70:
            rsi_text = f"Tuy nhiên, cần thận trọng khi RSI đã chạm vùng <b>Quá mua (Overbought - {d['rsi']:.1f})</b>. Dù xu hướng mạnh, nhưng các nhịp rung lắc để rũ bỏ tay yếu (weak hands) có thể xảy ra bất cứ lúc nào."
        else:
            rsi_text = f"Chỉ báo RSI đang ở vùng trung tính ({d['rsi']:.1f}), cho thấy dư địa để giá tiếp tục chạy theo xu hướng chính là vẫn còn rất lớn, chưa có dấu hiệu kiệt sức."

        # Phần kết bài
        conclusion = f"Tổng hợp lại, với điểm tin cậy đạt <b>{score}/100</b>, hệ thống Emperor V3000 khuyến nghị một lệnh <b>{signal}</b> ngay tại vùng giá hiện tại. Hãy tuân thủ tuyệt đối Stoploss để bảo toàn vốn trước sự khắc nghiệt của thị trường."

        # Ghép bài văn
        thesis = f"{intro}<br><br>📉 <b>PHÂN TÍCH KỸ THUẬT CHUYÊN SÂU:</b><br>- {trend_text}<br>- {momentum_text}<br>- {rsi_text}<br><br>🔮 <b>KẾT LUẬN ĐẦU TƯ:</b><br>{conclusion}"
        
        atr_val = d['atr'] if not np.isnan(d['atr']) else d['close'] * 0.01
        
        return {
            "symbol": symbol, "signal": signal, "score": score,
            "price": d['close'], "atr": atr_val,
            "thesis": thesis, "source": source
        }

    def plan(self, coin, cap, lev):
        entry = coin['price']
        atr = coin['atr']
        
        if coin['signal'] == "LONG":
            sl = entry - (atr * 1.5)
            tp1 = entry + (atr * 2)
            tp2 = entry + (atr * 4)
        else:
            sl = entry + (atr * 1.5)
            tp1 = entry - (atr * 2)
            tp2 = entry - (atr * 4)
        
        margin = (cap * 0.05) / lev 
        return {"entry": entry, "tp1": tp1, "tp2": tp2, "sl": sl, "margin": margin}

    def send_telegram(self, symbol, signal, score, p, thesis, token, chat_id):
        if not token or not chat_id: return
        icon = "🟢 MÚC NGAY" if signal == "LONG" else "🔴 BÁN KHỐNG"
        # Rút gọn thesis cho Tele đỡ dài dòng, chỉ lấy ý chính
        short_thesis = thesis.replace("<br>", "\n").replace("<b>", "").replace("</b>", "")
        
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
            f"📝 *PHÂN TÍCH:* Xem chi tiết trên Dashboard."
        )
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=3)
        except: pass

# --- 4. GIAO DIỆN ĐIỀU KHIỂN ---
bot = TitanBrain()

if 'last_signal' not in st.session_state:
    st.session_state.last_signal = None

st.title("🌌 EMPEROR V3000: ANALYST MODE")
st.caption("AI Trading Neural Network • Deep Analysis • Safe Mode ON")

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
    refresh = st.number_input("Scan Time (s):", value=60, min_value=15)
    auto = st.checkbox("🔮 AUTO-HUNT", value=True)
    if st.button("🚀 FORCE SCAN"): auto = True

# --- 5. MAIN LOOP ---
if auto:
    placeholder = st.empty()
    with placeholder.container():
        st.info("📡 Titan đang quét dữ liệu thị trường thực...")
        
        progress_bar = st.progress(0)
        results = []
        
        for i, sym in enumerate(bot.targets):
            data = bot.analyze(sym)
            if data and data['signal'] != "NEUTRAL": # Chỉ lấy con nào có signal
                results.append(data)
            progress_bar.progress((i + 1) / len(bot.targets))
            time.sleep(0.5)
            
        progress_bar.empty()

        if results:
            # Lọc lại lần nữa cho chắc
            valid_results = [r for r in results if r['score'] >= 75 or r['score'] <= 25]
            
            if valid_results:
                best = sorted(valid_results, key=lambda x: abs(x['score']-50), reverse=True)[0]
                
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

                # THESIS BOX - VĂN NGHỊ LUẬN
                st.markdown(f"<div class='thesis-box'>{best['thesis']}</div>", unsafe_allow_html=True)
                
                # LOGIC BẮN TELEGRAM
                signal_signature = f"{best['symbol']}-{best['signal']}"
                if enable_tele and st.session_state.last_signal != signal_signature:
                    with st.spinner("Đang truyền tin về Telegram..."):
                        bot.send_telegram(best['symbol'], best['signal'], best['score'], p, best['thesis'], tele_token, tele_chat_id)
                        st.session_state.last_signal = signal_signature
                        st.toast(f"Đã bắn tín hiệu {best['symbol']}!", icon="🚀")

            else:
                # KHÔNG CÓ KÈO - BÁO CỰC GẮT
                st.warning("⚠️ KHÔNG CÓ KÈO NÀO RA HỒN CẢ!")
                st.markdown("""
                    <div style='text-align:center; color:#888; padding:50px; border: 1px dashed #333;'>
                        <h2 style='color: #FF4141'>⛔ MARKET SIDEWAY - ĐI NGỦ ĐI!</h2>
                        <p>Thị trường đang chạy như rùa bò, không có tín hiệu nào đủ chuẩn (Score > 75).<br>
                        Cố đấm ăn xôi giờ này chỉ có cúng tiền cho sàn thôi.</p>
                        <br>
                        <i>"Thà chảy nước miếng còn hơn chảy nước mắt."</i>
                    </div>
                """, unsafe_allow_html=True)
        else:
            # KHÔNG CÓ KÈO - BÁO CỰC GẮT (Trường hợp list rỗng)
            st.warning("⚠️ KHÔNG CÓ KÈO NÀO RA HỒN CẢ!")
            st.markdown("""
                <div style='text-align:center; color:#888; padding:50px; border: 1px dashed #333;'>
                    <h2 style='color: #FF4141'>⛔ MARKET SIDEWAY - ĐI NGỦ ĐI!</h2>
                    <p>Thị trường đang chạy như rùa bò, không có tín hiệu nào đủ chuẩn.<br>
                    Tắt máy ra ngoài chạm cỏ đi CEO.</p>
                </div>
            """, unsafe_allow_html=True)

    time.sleep(1)
    if auto:
        with st.empty():
            for s in range(int(refresh), 0, -1):
                st.write(f"⏳ Next Scan: {s}s")
                time.sleep(1)
        st.rerun()
