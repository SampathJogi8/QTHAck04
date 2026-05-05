import io, wave
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG + THEME (clean, minimal, consistent)
# ─────────────────────────────────────────────
st.set_page_config(page_title="DSP Pro Lab", layout="wide", page_icon="🔬")

COL = {
    "bg": "#0b0f14",
    "panel": "#11161d",
    "border": "#1f2a36",
    "text": "#cbd5e1",
    "muted": "#64748b",
    "green": "#10b981",
    "blue": "#3b82f6",
    "cyan": "#06b6d4",
    "orange": "#f59e0b",
    "red": "#ef4444",
}

st.markdown(f"""
<style>
html, body, [class*="css"] {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto; }}
.stApp {{ background: {COL["bg"]}; }}
hr {{ border-color: {COL["border"]}; }}
.metric {{
  background:{COL["panel"]}; border:1px solid {COL["border"]};
  border-radius:12px; padding:12px 14px; text-align:center;
}}
.metric .lbl {{ color:{COL["muted"]}; font-size:11px; letter-spacing:.08em; text-transform:uppercase; }}
.metric .val {{ color:{COL["text"]}; font-weight:600; margin-top:6px; display:block; }}
.badge-ok {{
  background: rgba(16,185,129,.12); color:#10b981; border:1px solid rgba(16,185,129,.25);
  padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600;
}}
.badge-warn {{
  background: rgba(239,68,68,.12); color:#ef4444; border:1px solid rgba(239,68,68,.25);
  padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600;
}}
.section {{
  display:flex; align-items:center; gap:10px; margin:18px 0 10px 0;
  border-bottom:1px solid {COL["border"]}; padding-bottom:8px;
}}
.section h3 {{ margin:0; color:{COL["text"]}; font-size:14px; }}
.num {{
  width:24px;height:24px;border-radius:6px;display:flex;align-items:center;justify-content:center;
  background:{COL["panel"]}; border:1px solid {COL["border"]}; color:{COL["cyan"]}; font-size:11px; font-weight:700;
}}
</style>
""", unsafe_allow_html=True)

def section(n, title):
    st.markdown(f'<div class="section"><div class="num">{n}</div><h3>{title}</h3></div>', unsafe_allow_html=True)

def metric(lbl, val):
    st.markdown(f'<div class="metric"><div class="lbl">{lbl}</div><span class="val">{val}</span></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS (robust + precise)
# ─────────────────────────────────────────────
def next_pow2(n):
    p = 1
    while p < n:
        p <<= 1
    return p

def gen_signal(t, f, a, kind, dur):
    if kind == "Sine":
        return a * np.sin(2*np.pi*f*t)
    if kind == "Square":
        return a * np.sign(np.sin(2*np.pi*f*t))
    if kind == "Triangle":
        return a * (2/np.pi) * np.arcsin(np.sin(2*np.pi*f*t))
    if kind == "Sawtooth":
        return a * (2*((t*f)%1)-1)
    if kind == "Chirp":
        k = f / max(dur, 1e-9)
        return a * np.sin(2*np.pi*(0*t + 0.5*k*t**2))
    return np.zeros_like(t)

def moving_avg(x, M):
    M = max(1, int(M))
    y = np.convolve(x, np.ones(M)/M, mode="same")
    return np.roll(y, -M//2)  # compensate delay

def compute_fft(x, fs):
    n = next_pow2(max(len(x), 4))
    win = np.hanning(len(x))
    pad = np.zeros(n)
    pad[:len(x)] = x * win
    spec = np.fft.rfft(pad)
    freqs = np.fft.rfftfreq(n, d=1.0/fs)
    mags = np.abs(spec)
    # stable dB
    max_mag = np.max(mags) if np.max(mags) > 0 else 1e-12
    db = 20*np.log10(np.maximum(mags/max_mag, 1e-12))
    return freqs, mags, db, n

def alias_frequency(f, fs):
    return abs(f - fs * np.round(f / fs))

def load_wav(file):
    wf = wave.open(io.BytesIO(file.read()), "rb")
    rate = wf.getframerate()
    ch = wf.getnchannels()
    n = wf.getnframes()
    sw = wf.getsampwidth()
    raw = wf.readframes(n)
    wf.close()
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw, np.int16)
    audio = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if ch > 1:
        audio = audio.reshape(-1, ch).mean(axis=1)  # proper downmix
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio /= peak
    return audio, rate

def plot_theme(fig, title=None, h=380, xt="Time (s)", yt="Amplitude"):
    fig.update_layout(
        height=h,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0e141b",
        margin=dict(l=60, r=20, t=40, b=50),
        font=dict(color=COL["text"], size=11),
        legend=dict(bgcolor="rgba(17,22,29,.9)", bordercolor=COL["border"], borderwidth=1),
        title=dict(text=title or "", x=0, font=dict(size=12, color=COL["muted"]))
    )
    fig.update_xaxes(title_text=xt, gridcolor=COL["border"], zerolinecolor=COL["border"])
    fig.update_yaxes(title_text=yt, gridcolor=COL["border"], zerolinecolor=COL["border"])

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔊 Audio Input")
    uploaded = st.file_uploader("Upload WAV", type=["wav"])
    use_audio = uploaded is not None

    st.markdown("---")
    st.markdown("### 🎛️ Signal")

    if use_audio:
        st.info("Audio mode active — generator controls disabled")
        wave = st.selectbox("Waveform", ["Sine","Square","Triangle","Sawtooth","Chirp"], disabled=True)
        freq = st.slider("Frequency", 1, 50, 5, disabled=True)
        amp  = st.slider("Amplitude", 0.1, 3.0, 1.0, disabled=True)
        dur  = st.slider("Duration (s)", 1, 5, 2, disabled=True)
        fs   = st.slider("Sampling Rate (Hz)", 10, 1000, 200)
    else:
        wave = st.selectbox("Waveform", ["Sine","Square","Triangle","Sawtooth","Chirp"])
        freq = st.slider("Frequency (Hz)", 1, 50, 5)
        fs   = st.slider("Sampling Rate (Hz)", 10, 1000, 200)
        amp  = st.slider("Amplitude", 0.1, 3.0, 1.0)
        dur  = st.slider("Duration (s)", 1, 5, 2)

    st.markdown("---")
    st.markdown("### 🔊 Noise & Filter")
    noise_level = st.slider("Noise", 0.0, 2.0, 0.0, 0.1)
    filt_M = st.slider("Filter Window", 2, 80, 10)

# ─────────────────────────────────────────────
# PIPELINE (single source of truth)
# ─────────────────────────────────────────────
N = int(fs * (dur if not use_audio else 2))  # base length

if use_audio:
    audio, ar = load_wav(uploaded)
    # resample by indexing (deterministic)
    idx = np.linspace(0, len(audio)-1, N).astype(int)
    signal = audio[idx]
    t = np.arange(len(signal)) / fs
    # dominant frequency from original audio (short chunk)
    freqs_a, mags_a, _, _ = compute_fft(audio[:min(len(audio), ar*3)], ar)
    f_eff = float(freqs_a[np.argmax(mags_a)])
    src_label = f"🎵 audio ({ar} Hz)"
else:
    t = np.arange(N) / fs
    signal = gen_signal(t, freq, amp, wave, dur)
    f_eff = float(freq)
    src_label = f"🔧 {wave} {freq} Hz"

# noise + filter
rng = np.random.default_rng(42)
noise = rng.normal(0.0, noise_level, len(signal)) if noise_level > 0 else np.zeros_like(signal)
noisy = signal + noise
filtered = moving_avg(noisy, filt_M)

# FFT from SAME signal everywhere
freqs, mags, db, nfft = compute_fft(noisy, fs)
dom_idx = int(np.argmax(mags))
dom_freq = float(freqs[dom_idx])

# Nyquist + alias (correct)
nyq = fs / 2.0
alias_f = alias_frequency(dom_freq, fs)
is_alias = dom_freq > nyq

# SNR (true power)
sig_p = np.mean(signal**2)
noi_p = np.mean(noise**2) if noise_level > 0 else 1e-12
snr_db = 10*np.log10(sig_p / noi_p)

# ─────────────────────────────────────────────
# HEADER METRICS
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: metric("Source", src_label)
with c2: metric("Dominant f", f"{dom_freq:.2f} Hz")
with c3: metric("Fs", f"{fs} Hz")
with c4: metric("Nyquist", f"{nyq:.2f} Hz")
with c5: metric("Alias", f"{alias_f:.2f} Hz")
with c6:
    badge = '<span class="badge-warn">Aliasing</span>' if is_alias else '<span class="badge-ok">Clean</span>'
    st.markdown(f'<div class="metric"><div class="lbl">Status</div><div style="margin-top:7px">{badge}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# TABS (ALL MODULES KEPT)
# ─────────────────────────────────────────────
tab_scope, tab_fft, tab_phase, tab_filter, tab_water, tab_liss, tab_audio = st.tabs([
    "Oscilloscope", "FFT Spectrum", "Phase Space", "Filter Lab", "Waterfall", "Lissajous", "Audio Analyzer"
])

# ─────────────────────────────────────────────
# 1) OSCILLOSCOPE
# ─────────────────────────────────────────────
with tab_scope:
    section("01", "Signals")
    step = max(1, len(t)//2000)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t[::step], y=signal[::step], name="Original", line=dict(color=COL["green"], width=1.8)))
    if noise_level > 0:
        fig.add_trace(go.Scatter(x=t[::step], y=noisy[::step], name="Noisy", line=dict(color=COL["red"], width=1.0), opacity=0.6))
    fig.add_trace(go.Scatter(x=t[::step], y=filtered[::step], name="Filtered", line=dict(color=COL["blue"], width=2.0)))
    plot_theme(fig, title="Time domain")
    st.plotly_chart(fig, use_container_width=True)

    section("02", "Aliasing (time)")
    alias_sig = gen_signal(t, alias_f, 1.0, "Sine", t[-1] if len(t)>0 else 1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t[::step], y=signal[::step], name="Original", line=dict(color=COL["green"])))
    if is_alias:
        fig2.add_trace(go.Scatter(x=t[::step], y=alias_sig[::step], name=f"Alias {alias_f:.2f} Hz", line=dict(color=COL["orange"], dash="dash")))
    plot_theme(fig2, title=f"alias = |f − round(f/Fs)·Fs| = {alias_f:.2f} Hz")
    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 2) FFT
# ─────────────────────────────────────────────
with tab_fft:
    section("01", "Spectrum")
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.12)
    fig.add_trace(go.Bar(x=freqs, y=mags, marker=dict(color=COL["cyan"]), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=freqs, y=db, line=dict(color=COL["blue"]), fill="tozeroy", showlegend=False), row=2, col=1)
    for r in (1,2):
        fig.add_vline(x=dom_freq, line_dash="dash", line_color=COL["orange"], row=r, col=1)
        if is_alias:
            fig.add_vline(x=alias_f, line_dash="dot", line_color=COL["orange"], row=r, col=1)
    fig.update_layout(height=650, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e141b")
    fig.update_xaxes(title_text="Frequency (Hz)")
    fig.update_yaxes(title_text="Magnitude", row=1, col=1)
    fig.update_yaxes(title_text="dB", row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 3) PHASE SPACE
# ─────────────────────────────────────────────
with tab_phase:
    section("01", "Phase portrait")
    lag = st.slider("Lag (samples)", 1, min(80, len(noisy)//4 if len(noisy)>0 else 10), 5)
    x = noisy[:-lag] if len(noisy)>lag else noisy
    y = noisy[lag:] if len(noisy)>lag else noisy
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=COL["cyan"], width=1)))
    plot_theme(fig, xt="x[n−k]", yt="x[n]")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 4) FILTER LAB
# ─────────────────────────────────────────────
with tab_filter:
    section("01", "Noisy vs Filtered")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=signal, name="Original", line=dict(color=COL["green"], dash="dot"), opacity=0.5))
    if noise_level > 0:
        fig.add_trace(go.Scatter(x=t, y=noisy, name="Noisy", line=dict(color=COL["red"], width=1.0), opacity=0.6))
    fig.add_trace(go.Scatter(x=t, y=filtered, name="Filtered", line=dict(color=COL["blue"], width=2)))
    plot_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    section("02", "Filter response |H(f)|")
    w = np.linspace(0, np.pi, 1024)
    eps = 1e-9
    M = float(filt_M)
    H = np.abs(np.sin(M*w/2+eps)/(M*np.sin(w/2+eps)+eps))
    f_ax = w/np.pi * (fs/2)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=f_ax, y=H, fill="tozeroy", line=dict(color=COL["orange"], width=2)))
    plot_theme(fig2, xt="Frequency (Hz)", yt="|H(f)|")
    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 5) WATERFALL
# ─────────────────────────────────────────────
with tab_water:
    section("01", "STFT Waterfall")
    frame = 256
    hop = 128
    frames = []
    for i in range(0, max(len(noisy)-frame, 0), hop):
        chunk = noisy[i:i+frame] * np.hanning(frame)
        fft = np.abs(np.fft.rfft(chunk))
        frames.append(fft)
    if len(frames) == 0:
        st.warning("Signal too short. Increase duration.")
    else:
        Z = np.array(frames).T
        fig = go.Figure(go.Heatmap(z=20*np.log10(Z+1e-12), colorscale="Plasma"))
        fig.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e141b")
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 6) LISSAJOUS
# ─────────────────────────────────────────────
with tab_liss:
    section("01", "Lissajous")
    f2 = st.slider("Y frequency (Hz)", 1, 80, 3)
    ph = st.slider("Phase (°)", 0, 360, 0, 5)
    tt = np.linspace(0, 2, 8000)
    x = np.sin(2*np.pi*dom_freq*tt)
    y = np.sin(2*np.pi*f2*tt + np.radians(ph))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=COL["cyan"], width=1.4)))
    plot_theme(fig, xt="X", yt="Y")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 7) AUDIO ANALYZER
# ─────────────────────────────────────────────
with tab_audio:
    section("01", "Analyzer")
    if use_audio:
        st.audio(signal, sample_rate=fs)
        fig = go.Figure()
        step = max(1, len(t)//2000)
        fig.add_trace(go.Scatter(x=t[::step], y=signal[::step], line=dict(color=COL["green"], width=1)))
        plot_theme(fig, title="Waveform")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=freqs, y=mags, line=dict(color=COL["blue"], width=1.4)))
        plot_theme(fig2, xt="Frequency (Hz)", yt="Magnitude")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Upload a WAV file to enable audio analysis.")
