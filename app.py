"""
DSP Pro Lab — MIT 6.003 Style  |  Team: 8vaults
Problem Statement 18: Sampling & Aliasing Visual Demonstrator
v4 — Industry-grade UI/UX overhaul
"""

import io
import wave

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DSP Pro Lab — 8vaults",
    layout="wide",
    page_icon="🔬",
    initial_sidebar_state="expanded",
)

# ── Global CSS — Design System ─────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base & Typography ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Background ── */
.stApp {
    background: #080c12;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1e2631 !important;
    padding-top: 0 !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem !important;
}

/* ── Header ── */
.dsp-header {
    background: linear-gradient(135deg, #0d1117 0%, #111827 60%, #0d1117 100%);
    border: 1px solid #1e2631;
    border-left: 4px solid #a855f7;
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}

.dsp-header-left h1 {
    color: #f1f5f9;
    margin: 0 0 4px 0;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.02em;
    font-family: 'Inter', sans-serif !important;
}

.dsp-header-left p {
    color: #64748b;
    margin: 0;
    font-size: 12.5px;
    font-weight: 400;
    letter-spacing: 0.01em;
}

.dsp-header-badge {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 11px;
    color: #64748b;
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
}

.dsp-header-badge span {
    color: #a855f7;
    font-weight: 600;
}

/* ── Metric Cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    margin-bottom: 20px;
}

.mcard {
    background: #0d1117;
    border: 1px solid #1e2631;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
    transition: border-color 0.2s, transform 0.15s;
    position: relative;
    overflow: hidden;
}

.mcard::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #a855f7, #6366f1);
    opacity: 0;
    transition: opacity 0.2s;
}

.mcard:hover {
    border-color: #2d3748;
    transform: translateY(-1px);
}

.mcard:hover::before {
    opacity: 1;
}

.mcard .val {
    font-size: 16px;
    font-weight: 600;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
    margin-top: 6px;
    display: block;
}

.mcard .lbl {
    font-size: 10px;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}

/* ── Status badges ── */
.badge-ok {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(16, 185, 129, 0.12);
    color: #10b981;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid rgba(16, 185, 129, 0.25);
    letter-spacing: 0.02em;
}

.badge-warn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(239, 68, 68, 0.12);
    color: #ef4444;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid rgba(239, 68, 68, 0.25);
    letter-spacing: 0.02em;
}

/* ── Audio Banner ── */
.audio-banner {
    background: linear-gradient(135deg, #0d1f35 0%, #0d1117 100%);
    border: 1px solid #1e3a5f;
    border-left: 3px solid #3b82f6;
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 16px;
    font-size: 13px;
    color: #93c5fd;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    flex-wrap: wrap;
}

.audio-banner strong {
    color: #bfdbfe;
    font-weight: 600;
}

.audio-banner .warn-note {
    color: #fbbf24;
    font-size: 12px;
    opacity: 0.9;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 20px 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e2631;
}

.section-header h3 {
    color: #cbd5e1;
    font-size: 14px;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.01em;
}

.section-num {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    color: #a855f7;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Sidebar typography ── */
section[data-testid="stSidebar"] .sidebar-section-title {
    font-size: 11px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 12px 0 6px 0;
    border-bottom: 1px solid #1e2631;
    margin-bottom: 10px;
}

/* ── Plotly container polish ── */
.stPlotlyChart {
    border-radius: 10px;
    overflow: hidden;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1117;
    border-bottom: 1px solid #1e2631;
    gap: 0;
    padding: 0;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b !important;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 500;
    transition: color 0.15s, border-color 0.15s;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: rgba(255,255,255,0.03);
}

.stTabs [aria-selected="true"] {
    color: #a855f7 !important;
    border-bottom-color: #a855f7 !important;
    background: transparent;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0d1117 !important;
    border: 1px solid #1e2631 !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-size: 13px !important;
}

/* ── Alert overrides ── */
.stAlert {
    background: #0d1117 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #080c12; }
::-webkit-scrollbar-thumb { background: #1e2631; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2d3748; }

/* ── Info box custom ── */
.info-box {
    background: #0d1117;
    border: 1px solid #1e2631;
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
    color: #475569;
    font-size: 13px;
    margin: 20px 0;
}

.info-box .icon {
    font-size: 32px;
    margin-bottom: 10px;
    display: block;
}

.info-box strong {
    color: #94a3b8;
    display: block;
    font-size: 15px;
    margin-bottom: 6px;
}

/* ── Theory table ── */
.stMarkdown table {
    background: #0d1117 !important;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #1e2631 !important;
    font-size: 13px;
}

.stMarkdown th {
    background: #111827 !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    border-color: #1e2631 !important;
}

.stMarkdown td {
    color: #cbd5e1 !important;
    border-color: #1e2631 !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
}

/* ── Sidebar upload area ── */
.sidebar-upload-zone {
    background: #0d1117;
    border: 1.5px dashed #2d3748;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}

/* ── Caption text ── */
.stCaption {
    color: #475569 !important;
    font-size: 11.5px !important;
}

/* ── Dividers ── */
hr {
    border-color: #1e2631 !important;
    margin: 18px 0 !important;
}

/* ── Subheader overrides ── */
h2, h3 {
    color: #cbd5e1 !important;
    font-family: 'Inter', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def next_pow2(n: int) -> int:
    p = 1
    while p < n:
        p <<= 1
    return p


def gen_signal(time_arr, f, a, wtype, dur):
    if wtype == "Sine":
        return a * np.sin(2 * np.pi * f * time_arr)
    if wtype == "Square":
        return a * np.sign(np.sin(2 * np.pi * f * time_arr))
    if wtype == "Triangle":
        return a * (2.0 / np.pi) * np.arcsin(np.sin(2 * np.pi * f * time_arr))
    if wtype == "Sawtooth":
        return a * (2.0 * ((time_arr * f) % 1.0) - 1.0)
    if wtype == "Chirp":
        k = f / max(dur, 1e-9)
        return a * np.sin(2 * np.pi * (f * time_arr + 0.5 * k * time_arr ** 2))
    return np.zeros_like(time_arr)


def moving_avg(s, w):
    w = max(1, int(w))
    return np.convolve(s, np.ones(w) / w, mode="same")


def compute_fft(sig, sample_rate):
    n = next_pow2(max(len(sig), 4))
    win = np.hanning(len(sig))
    padded = np.zeros(n)
    padded[: len(sig)] = sig * win
    spectrum = np.fft.rfft(padded)
    freqs = np.fft.rfftfreq(n, d=1.0 / max(sample_rate, 1.0))
    mags = np.abs(spectrum) / (n / 2.0)
    max_mag = float(mags.max()) if mags.max() > 0 else 1e-12
    power_db = 20.0 * np.log10(np.maximum(mags / max_mag, 1e-12))
    return freqs, mags, power_db, n


def fft_bandwidth(freqs, mags, threshold=0.1):
    max_mag = float(mags.max())
    mask = mags > max_mag * threshold
    if int(np.count_nonzero(mask)) >= 2:
        idx = np.where(mask)[0]
        return round(float(freqs[idx[-1]]) - float(freqs[idx[0]]), 2)
    return 0.0


def load_wav(file_obj):
    buf  = io.BytesIO(file_obj.read())
    wf   = wave.open(buf, "rb")
    rate = wf.getframerate()
    nch  = wf.getnchannels()
    nsmp = wf.getnframes()
    sw   = wf.getsampwidth()
    raw  = wf.readframes(nsmp)
    wf.close()
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw, np.int16)
    audio = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if nch >= 2:
        audio = audio[::nch]
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio /= peak
    return audio, rate


# ── Plotly theme ────────────────────────────────────────────────────────────
COLORS = {
    "green":   "#10b981",
    "blue":    "#3b82f6",
    "purple":  "#a855f7",
    "orange":  "#f97316",
    "yellow":  "#f59e0b",
    "red":     "#ef4444",
    "cyan":    "#06b6d4",
    "pink":    "#ec4899",
    "indigo":  "#6366f1",
    "bg":      "#080c12",
    "surface": "#0d1117",
    "border":  "#1e2631",
    "text":    "#94a3b8",
    "muted":   "#475569",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0b0f18",
    font=dict(color=COLORS["text"], size=11.5, family="JetBrains Mono, monospace"),
    legend=dict(
        bgcolor="rgba(13,17,23,0.9)",
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(color="#94a3b8", size=11),
        itemsizing="constant",
    ),
    margin=dict(l=60, r=20, t=46, b=52),
)

AXIS_STYLE = dict(
    gridcolor="rgba(30,38,49,0.9)",
    gridwidth=1,
    zerolinecolor="rgba(148,163,184,0.15)",
    zerolinewidth=1,
    color=COLORS["text"],
    linecolor=COLORS["border"],
    linewidth=1,
    tickfont=dict(size=10.5, family="JetBrains Mono, monospace"),
    showgrid=True,
)


def apply_theme(fig, height=420, title="", xtitle="Time (s)", ytitle="Amplitude",
                accent=None):
    layout = {**CHART_LAYOUT, "height": height}
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(color="#64748b", size=12, family="Inter, sans-serif"),
            x=0,
            xanchor="left",
            pad=dict(l=4),
        )
    fig.update_layout(**layout)
    fig.update_xaxes(title_text=xtitle, title_font=dict(size=11), **AXIS_STYLE)
    fig.update_yaxes(title_text=ytitle, title_font=dict(size=11), **AXIS_STYLE)


def mcard(label, value, accent=None):
    accent_color = accent or COLORS["purple"]
    st.markdown(
        f'<div class="mcard">'
        f'<div class="lbl">{label}</div>'
        f'<span class="val" style="color:{accent_color}">{value}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_header(num, title):
    st.markdown(
        f'<div class="section-header">'
        f'<div class="section-num">{num}</div>'
        f'<h3>{title}</h3>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="dsp-header">
  <div class="dsp-header-left">
    <h1>🔬 DSP Pro Lab</h1>
    <p>Interactive Digital Signal Processing Playground &nbsp;·&nbsp;
       Problem Statement 18 — Sampling &amp; Aliasing Visual Demonstrator</p>
  </div>
  <div class="dsp-header-badge">
    Team <span>8vaults</span> &nbsp;·&nbsp; Nyquist–Shannon: Fs ≥ 2·f_max
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<p class="sidebar-section-title">📂 Audio Input</p>', unsafe_allow_html=True)
    st.caption("Upload a WAV — it becomes the signal source for all modules.")

    uploaded_file = st.file_uploader(
        "WAV file", type=["wav"], label_visibility="collapsed",
        help="Supports mono/stereo WAV files. Stereo is downmixed to mono."
    )

    if uploaded_file is not None:
        file_key = uploaded_file.name + str(uploaded_file.size)
        if st.session_state.get("audio_key") != file_key:
            try:
                audio_data, audio_rate = load_wav(uploaded_file)
                st.session_state["audio_data"] = audio_data
                st.session_state["audio_rate"] = audio_rate
                st.session_state["audio_name"] = uploaded_file.name
                st.session_state["audio_key"]  = file_key
            except Exception as e:
                st.error(f"Could not read WAV: {e}")
    else:
        for k in ("audio_data", "audio_rate", "audio_name", "audio_key"):
            st.session_state.pop(k, None)

    audio_loaded = "audio_data" in st.session_state
    if audio_loaded:
        a_dur_sb = len(st.session_state["audio_data"]) / st.session_state["audio_rate"]
        st.success(
            f"✅ **{st.session_state['audio_name']}**\n\n"
            f"{st.session_state['audio_rate']} Hz · {a_dur_sb:.1f} s · "
            f"All modules active."
        )

    st.markdown("---")

    st.markdown('<p class="sidebar-section-title">🎛️ Signal Generator</p>', unsafe_allow_html=True)

    if audio_loaded:
        st.info(
            "**Audio mode active** — waveform controls overridden by WAV. "
            "Remove the file to use the synthesiser.",
            icon="🎵",
        )
        signal_type = st.selectbox("Waveform *(inactive)*", ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"], disabled=True)
        freq        = st.slider("Frequency Hz *(inactive)*",   1, 50, 5, disabled=True)
        amp         = st.slider("Amplitude *(inactive)*",    0.1, 3.0, 1.0, 0.1, disabled=True)
        duration    = st.slider("Duration s *(inactive)*",     1,  5,  2, disabled=True)
        st.markdown("**Sampling Rate** — active (controls resampling):")
        fs_raw      = st.slider("Sampling Rate (Hz)", 2, 200, 40,
                                help="How many samples per second to take from the audio signal.")
    else:
        signal_type = st.selectbox(
            "Waveform", ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"],
            help="Choose the waveform type to synthesise."
        )
        freq   = st.slider("Frequency (Hz)", 1, 50, 5,
                           help="Fundamental frequency of the signal in Hz.")
        fs_raw = st.slider("Sampling Rate (Hz)", 2, 200, 40,
                           help="Set below 2× frequency to trigger aliasing (Nyquist criterion).")
        amp    = st.slider("Amplitude", 0.1, 3.0, 1.0, 0.1,
                           help="Peak amplitude of the generated signal.")
        duration = st.slider("Duration (s)", 1, 5, 2,
                             help="Length of the generated signal in seconds.")

    st.markdown("---")
    st.markdown('<p class="sidebar-section-title">🔊 Noise &amp; Filter</p>', unsafe_allow_html=True)

    noise_level = st.slider(
        "Noise Level", 0.0, 2.0, 0.0, 0.1,
        help="Standard deviation of additive Gaussian noise."
    )
    filter_win  = st.slider(
        "Filter Window (samples)", 2, 80, 10,
        help="Moving-average FIR filter length. Larger = more smoothing, more delay."
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:10.5px;color:#334155;padding:4px 0;'>"
        "DSP Pro Lab · 8vaults · PS-18</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CORE SIGNAL
# ══════════════════════════════════════════════════════════════════════════════
fs = max(int(fs_raw), 2)
N  = 4000

if "audio_data" in st.session_state:
    raw_audio    = st.session_state["audio_data"]
    audio_rate   = st.session_state["audio_rate"]
    indices      = np.linspace(0, len(raw_audio) - 1, N).astype(int)
    signal       = raw_audio[indices]
    duration_eff = float(len(raw_audio) / audio_rate)
    t            = np.linspace(0.0, duration_eff, N, endpoint=False)
    ts           = np.arange(0.0, duration_eff, 1.0 / fs)
    ts_idx       = np.clip((ts * audio_rate).astype(int), 0, len(raw_audio) - 1)
    sampled      = raw_audio[ts_idx]
    fq, mq, _, _ = compute_fft(signal[:min(N, 8192)], float(audio_rate))
    freq_eff     = max(1, int(round(float(fq[int(np.argmax(mq))]))))
    source_label = f"🎵 {st.session_state['audio_name']}"
else:
    t            = np.linspace(0.0, duration, N, endpoint=False)
    ts           = np.arange(0.0, duration, 1.0 / fs)
    signal       = gen_signal(t, freq, amp, signal_type, duration)
    sampled      = gen_signal(ts, freq, amp, signal_type, duration)
    duration_eff = float(duration)
    freq_eff     = freq
    source_label = f"🔧 {signal_type} {freq} Hz"

nyquist  = 2 * freq_eff
alias_f  = abs(freq_eff - round(freq_eff / fs) * fs)
is_alias = fs < nyquist

rng       = np.random.default_rng(42)
noise_vec = rng.normal(0.0, noise_level, N) if noise_level > 0 else np.zeros(N)
noisy     = signal + noise_vec
filtered  = moving_avg(noisy, filter_win)


# ══════════════════════════════════════════════════════════════════════════════
# AUDIO BANNER
# ══════════════════════════════════════════════════════════════════════════════
if "audio_data" in st.session_state:
    a_dur = len(st.session_state["audio_data"]) / st.session_state["audio_rate"]
    st.markdown(
        f'<div class="audio-banner">'
        f'<div>🎵</div>'
        f'<div>'
        f'<strong>Audio mode active</strong> — '
        f'{st.session_state["audio_name"]} '
        f'({st.session_state["audio_rate"]} Hz · {a_dur:.1f} s) &nbsp;·&nbsp; '
        f'Dominant freq: <strong>{freq_eff} Hz</strong> &nbsp;·&nbsp; '
        f'Nyquist min: <strong>{nyquist} Hz</strong><br>'
        f'<span class="warn-note">⚠ Waveform / Frequency / Amplitude / Duration sliders overridden. '
        f'Only Sampling Rate, Noise and Filter controls are active.</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# STATUS METRIC BAR
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    mcard("Source", source_label[:18], COLORS["blue"])
with c2:
    mcard("Signal Freq", f"{freq_eff} Hz", COLORS["cyan"])
with c3:
    mcard("Sampling Rate", f"{fs} Hz", COLORS["purple"])
with c4:
    mcard("Nyquist Min", f"{nyquist} Hz", COLORS["indigo"])
with c5:
    mcard("Alias Freq", f"{alias_f:.1f} Hz", COLORS["orange"])
with c6:
    if is_alias:
        badge = '<span class="badge-warn">⚠ Aliasing</span>'
    else:
        badge = '<span class="badge-ok">✓ Clean</span>'
    st.markdown(
        f'<div class="mcard">'
        f'<div class="lbl">Status</div>'
        f'<div style="margin-top:7px">{badge}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
(tab_scope, tab_fft, tab_phase,
 tab_filter, tab_water, tab_liss, tab_audio) = st.tabs([
    "  Oscilloscope  ",
    "  FFT Spectrum  ",
    "  Phase Space  ",
    "  Filter Lab  ",
    "  Waterfall  ",
    "  Lissajous  ",
    "  Audio Analyzer  ",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OSCILLOSCOPE
# ══════════════════════════════════════════════════════════════════════════════
with tab_scope:

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        section_header("01", "Continuous Signal")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t, y=signal, mode="lines", name="x(t) — Continuous",
            line=dict(color=COLORS["green"], width=1.8),
        ))
        if noise_level > 0:
            fig.add_trace(go.Scatter(
                x=t, y=noisy, mode="lines", name=f"x(t) + Noise (σ={noise_level:.1f})",
                line=dict(color=COLORS["red"], width=1.0),
                opacity=0.55,
            ))
        apply_theme(fig, height=400,
                    title=f"{source_label}  ·  A = {amp:.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("02", "Sampled Signal")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=t, y=signal, mode="lines", name="Continuous (ref)",
            line=dict(color=COLORS["green"], width=1.2, dash="dot"),
            opacity=0.3,
        ))
        stem_x, stem_y = [], []
        for xi, yi in zip(ts, sampled):
            stem_x += [float(xi), float(xi), None]
            stem_y += [0.0, float(yi), None]
        fig2.add_trace(go.Scatter(
            x=stem_x, y=stem_y, mode="lines", showlegend=False,
            line=dict(color=COLORS["orange"], width=1.0),
            opacity=0.4,
        ))
        fig2.add_trace(go.Scatter(
            x=ts, y=sampled, mode="markers", name=f"Samples · Fs = {fs} Hz",
            marker=dict(
                color=COLORS["orange"], size=7,
                line=dict(color="#fff", width=0.5),
            ),
        ))
        apply_theme(fig2, height=400,
                    title=f"Fs = {fs} Hz · {len(ts)} samples · T = {1/fs*1000:.1f} ms")
        st.plotly_chart(fig2, use_container_width=True)

    section_header("03", "Aliasing Visualisation — Time Domain")
    alias_sig = gen_signal(t, alias_f, amp, "Sine", duration_eff)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=t, y=signal, mode="lines", name=f"Original  {freq_eff} Hz",
        line=dict(color=COLORS["green"], width=2.0),
    ))
    fig3.add_trace(go.Scatter(
        x=ts, y=sampled, mode="markers", name=f"Samples · Fs = {fs} Hz",
        marker=dict(color=COLORS["yellow"], size=6),
    ))
    if is_alias:
        fig3.add_trace(go.Scatter(
            x=t, y=alias_sig, mode="lines", name=f"Alias  {alias_f:.2f} Hz",
            line=dict(color=COLORS["orange"], width=2.0, dash="dash"),
        ))
    note = f"⚠ ALIASING  Fs={fs} < {nyquist}" if is_alias else f"✓ Clean  Fs={fs} ≥ {nyquist}"
    apply_theme(
        fig3, height=420,
        title=f"alias = |{freq_eff} − round({freq_eff}/{fs})×{fs}| = {alias_f:.2f} Hz   [{note}]",
    )
    st.plotly_chart(fig3, use_container_width=True)

    if is_alias:
        st.error(
            f"**Aliasing detected!**  {freq_eff} Hz requires Fs ≥ {nyquist} Hz (Nyquist criterion). "
            f"At Fs = {fs} Hz, the signal appears as **{alias_f:.2f} Hz**.",
            icon="⚠️",
        )
    else:
        st.success(
            f"**No aliasing.**  Fs = {fs} Hz ≥ Nyquist = {nyquist} Hz ✓",
            icon="✅",
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FFT SPECTRUM
# ══════════════════════════════════════════════════════════════════════════════
with tab_fft:

    freqs_hz, mags, power_db, n_fft = compute_fft(noisy, float(fs))
    max_mag  = float(mags.max()) if mags.size > 0 else 1e-12
    dom_idx  = int(np.argmax(mags))
    dom_freq = round(float(freqs_hz[dom_idx]), 2)
    bw_hz    = fft_bandwidth(freqs_hz, mags)
    snr_db   = (round(20.0 * np.log10(float(amp) / max(float(noise_level), 1e-9)), 1)
                if noise_level > 0 else 99.0)
    harm_rms = float(np.sqrt(np.sum(mags[dom_idx + 1:] ** 2))) if dom_idx + 1 < len(mags) else 0.0
    thd_pct  = round(harm_rms / max(float(mags[dom_idx]), 1e-9) * 100.0, 1)

    m1, m2, m3, m4 = st.columns(4)
    with m1: mcard("Dominant Freq",      f"{dom_freq} Hz", COLORS["cyan"])
    with m2: mcard("Bandwidth (−10 dB)", f"{bw_hz} Hz",    COLORS["blue"])
    with m3: mcard("SNR",                f"{min(snr_db, 99.9):.1f} dB", COLORS["green"])
    with m4: mcard("THD",                f"{thd_pct} %",   COLORS["orange"])

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Build colour gradient for bars
    bar_colors = [
        f"hsl({int(200 + i / max(len(freqs_hz)-1, 1) * 100)},70%,55%)"
        for i in range(len(freqs_hz))
    ]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Magnitude Spectrum", "Power Spectrum (dB)"),
        vertical_spacing=0.13,
        row_heights=[0.5, 0.5],
    )
    fig.add_trace(
        go.Bar(x=freqs_hz, y=mags, name="Magnitude",
               marker=dict(color=bar_colors, line=dict(width=0)),
               showlegend=False),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=freqs_hz, y=power_db, mode="lines",
                   line=dict(color=COLORS["blue"], width=1.6),
                   fill="tozeroy",
                   fillcolor="rgba(59,130,246,0.08)",
                   showlegend=False),
        row=2, col=1,
    )

    for r in (1, 2):
        if 0 < dom_freq <= float(freqs_hz[-1]):
            fig.add_vline(
                x=dom_freq, line_dash="dash", line_color=COLORS["orange"],
                annotation_text=f"f = {dom_freq} Hz",
                annotation_font=dict(color=COLORS["orange"], size=11),
                annotation_position="top right",
                row=r, col=1,
            )
        if is_alias and alias_f > 0 and alias_f <= float(freqs_hz[-1]):
            fig.add_vline(
                x=alias_f, line_dash="dot", line_color=COLORS["yellow"],
                annotation_text=f"alias {alias_f:.1f} Hz",
                annotation_font=dict(color=COLORS["yellow"], size=11),
                annotation_position="top left",
                row=r, col=1,
            )

    layout = {**CHART_LAYOUT, "height": 700, "showlegend": False}
    fig.update_layout(**layout)
    fig.update_xaxes(**AXIS_STYLE, title_text="Frequency (Hz)")
    fig.update_yaxes(**AXIS_STYLE)
    fig.update_yaxes(title_text="Magnitude", row=1, col=1)
    fig.update_yaxes(title_text="dB",        row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📐 FFT Theory & Parameters"):
        freq_res = round(float(fs) / n_fft, 4)
        st.markdown(f"""
| Parameter | Value |
|---|---|
| FFT size | {n_fft} points (zero-padded to next power of 2) |
| Window function | Hanning (von Hann) |
| Frequency resolution | {freq_res} Hz / bin |
| Nyquist limit | {fs // 2} Hz |
| Dominant frequency | {dom_freq} Hz |
| Alias frequency | {alias_f:.2f} Hz {'⚠ active' if is_alias else '(no aliasing)'} |
        """)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PHASE SPACE
# ══════════════════════════════════════════════════════════════════════════════
with tab_phase:

    lag = st.slider("Lag k (samples)", 1, min(50, N // 4), 5, key="lag_slider")
    x_ph = noisy[:-lag]
    y_ph = noisy[lag:]

    max_lag  = min(400, len(signal) // 2)
    mean_s   = float(signal.mean())
    var_s    = float(np.var(signal))
    lags_arr = np.arange(max_lag)
    if var_s > 1e-12:
        auto = np.array([
            float(np.mean((signal[:N-ll]-mean_s)*(signal[ll:]-mean_s))) / var_s
            for ll in lags_arr
        ])
    else:
        auto = np.zeros(max_lag)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        section_header("01", "Phase Portrait")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_ph, y=y_ph, mode="lines",
            line=dict(color=COLORS["purple"], width=0.9),
            name=f"x[n] vs x[n−{lag}]",
        ))
        apply_theme(fig, height=500,
                    title=f"Phase portrait — lag = {lag} samples",
                    xtitle=f"x[n−{lag}]", ytitle="x[n]")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("02", "Autocorrelation R[k]")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=lags_arr, y=auto, mode="lines",
            line=dict(color=COLORS["pink"], width=1.6),
            fill="tozeroy",
            fillcolor="rgba(236,72,153,0.07)",
            name="R[k]",
        ))
        fig2.add_hline(y=0, line_dash="dot",
                       line_color="rgba(148,163,184,0.2)")
        apply_theme(fig2, height=500,
                    title="Normalised autocorrelation",
                    xtitle="Lag (samples)", ytitle="R[k]")
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FILTER LAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_filter:

    rms_orig = float(np.sqrt(np.mean(signal   ** 2)))
    rms_n    = float(np.sqrt(np.mean(noisy    ** 2)))
    rms_f    = float(np.sqrt(np.mean(filtered ** 2)))
    snr_g    = round(20.0 * np.log10(max(rms_f, 1e-12) / max(rms_n, 1e-12)), 2)
    cutoff   = round(float(fs) / (2.0 * max(filter_win, 1)), 2)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: mcard("RMS Original", f"{rms_orig:.4f}", COLORS["green"])
    with m2: mcard("RMS Noisy",    f"{rms_n:.4f}",    COLORS["red"])
    with m3: mcard("RMS Filtered", f"{rms_f:.4f}",    COLORS["blue"])
    with m4: mcard("SNR Gain",     f"{snr_g} dB",     COLORS["purple"])
    with m5: mcard("−3 dB Cutoff", f"{cutoff} Hz",    COLORS["orange"])

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    section_header("01", "Original Clean Signal")
    fig_orig = go.Figure()
    fig_orig.add_trace(go.Scatter(
        x=t, y=signal, mode="lines", name="Original",
        line=dict(color=COLORS["green"], width=2),
    ))
    apply_theme(fig_orig, height=320, title=f"Original — {source_label}")
    st.plotly_chart(fig_orig, use_container_width=True)

    col_n, col_f = st.columns(2, gap="medium")
    with col_n:
        section_header("02", "Noisy Signal")
        fig_noisy = go.Figure()
        fig_noisy.add_trace(go.Scatter(
            x=t, y=noisy, mode="lines",
            name=f"Noisy (σ = {noise_level:.1f})",
            line=dict(color=COLORS["red"], width=1.2),
        ))
        apply_theme(fig_noisy, height=340, title=f"Noise level {noise_level:.1f}")
        st.plotly_chart(fig_noisy, use_container_width=True)

    with col_f:
        section_header("03", "Filtered Signal")
        fig_filt = go.Figure()
        fig_filt.add_trace(go.Scatter(
            x=t, y=filtered, mode="lines",
            name=f"Filtered (M = {filter_win})",
            line=dict(color=COLORS["blue"], width=2),
        ))
        apply_theme(fig_filt, height=340,
                    title=f"FIR M = {filter_win} · cutoff ≈ {cutoff} Hz")
        st.plotly_chart(fig_filt, use_container_width=True)

    section_header("04", "Noisy vs Filtered Comparison")
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Scatter(
        x=t, y=noisy, mode="lines",
        name=f"Noisy (σ = {noise_level:.1f})",
        line=dict(color=COLORS["red"], width=1.0),
        opacity=0.6,
    ))
    fig_cmp.add_trace(go.Scatter(
        x=t, y=filtered, mode="lines",
        name=f"Filtered (M = {filter_win})",
        line=dict(color=COLORS["blue"], width=2.2),
    ))
    apply_theme(fig_cmp, height=380, title="Noisy vs Filtered")
    st.plotly_chart(fig_cmp, use_container_width=True)

    section_header("05", "Filter Frequency Response |H(f)|")
    omega = np.linspace(0.0, np.pi, 1024)
    eps   = 1e-9
    M_f   = float(filter_win)
    H     = np.clip(
        np.abs(np.sin(M_f*omega/2+eps) / (M_f*np.sin(omega/2+eps)+eps)),
        0, 1,
    )
    f_ax  = omega / np.pi * (fs / 2.0)
    fig_hr = go.Figure()
    fig_hr.add_trace(go.Scatter(
        x=f_ax, y=H, mode="lines", name="|H(f)|",
        line=dict(color=COLORS["orange"], width=2.2),
        fill="tozeroy",
        fillcolor="rgba(249,115,22,0.07)",
    ))
    fig_hr.add_hline(
        y=0.707, line_dash="dash",
        line_color="rgba(148,163,184,0.4)",
        annotation_text="−3 dB (0.707)",
        annotation_font=dict(color="#94a3b8", size=11),
        annotation_position="bottom right",
    )
    apply_theme(fig_hr, height=360, xtitle="Frequency (Hz)", ytitle="|H(f)|")
    st.plotly_chart(fig_hr, use_container_width=True)

    with st.expander("📐 Filter Theory"):
        st.markdown(f"""
| Parameter | Value |
|---|---|
| Filter type | FIR moving-average (box / rectangular window) |
| Window length M | {filter_win} samples |
| Approx −3 dB cutoff | {cutoff} Hz |
| Group delay | {filter_win // 2} samples |

**Response:** `|H(f)| = |sin(Mω/2)| / (M·|sin(ω/2)|)`

Larger M → more noise suppression, more time lag (group delay ≈ M/2 samples).
        """)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — WATERFALL
# ══════════════════════════════════════════════════════════════════════════════
with tab_water:

    section_header("01", "Short-Time FFT Waterfall Spectrogram")

    n_frames  = 64
    frame_len = max(64, N // n_frames)
    n_fft_w   = next_pow2(frame_len)
    hop       = max(1, (N - frame_len) // max(n_frames - 1, 1))
    win_h     = np.hanning(frame_len)

    wfall, t_labels = [], []
    for i in range(n_frames):
        start = i * hop
        end   = start + frame_len
        if end > N:
            break
        padded = np.zeros(n_fft_w)
        padded[:frame_len] = noisy[start:end] * win_h
        wfall.append(np.abs(np.fft.rfft(padded)) / (n_fft_w / 2.0))
        t_labels.append(round(start / N * duration_eff, 3))

    if not wfall:
        st.warning("Signal too short for waterfall. Increase Duration.")
    else:
        wfall_arr = np.array(wfall)
        f_ax_w    = np.fft.rfftfreq(n_fft_w, d=1.0 / fs)
        z_db      = np.clip(20.0 * np.log10(wfall_arr + 1e-12), -80.0, 0.0)

        fig = go.Figure(go.Heatmap(
            z=z_db.T, x=t_labels, y=f_ax_w,
            colorscale="Plasma",
            zmin=-80, zmax=0,
            colorbar=dict(
                title=dict(text="dB", font=dict(color="#94a3b8", size=12)),
                ticksuffix=" dB",
                tickfont=dict(color="#94a3b8", size=10, family="JetBrains Mono"),
                bgcolor="rgba(13,17,23,0.0)",
                bordercolor=COLORS["border"],
                borderwidth=1,
            ),
        ))
        fig.update_layout(
            **{**CHART_LAYOUT, "height": 580},
            xaxis=dict(**AXIS_STYLE, title_text="Time (s)"),
            yaxis=dict(**AXIS_STYLE, title_text="Frequency (Hz)"),
        )
        st.plotly_chart(fig, use_container_width=True)

        freq_res_w = round(float(fs) / n_fft_w, 3)
        st.caption(
            f"Hanning STFT · {len(wfall)} frames · FFT size {n_fft_w} · "
            f"{freq_res_w} Hz/bin · Hop {hop} samples  ·  "
            f"Tip: select Chirp waveform for a diagonal frequency sweep"
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — LISSAJOUS
# ══════════════════════════════════════════════════════════════════════════════
with tab_liss:

    col_ctrl, col_plot = st.columns([1, 3], gap="medium")

    with col_ctrl:
        section_header("▶", "Controls")
        liss_max     = max(50, freq_eff * 4)
        liss_default = min(3, liss_max)
        freq2 = st.slider("Y-axis Freq (Hz)", 1, liss_max, liss_default, key="liss_freq2")
        phase = st.slider("Phase Offset (°)", 0, 360, 0, 5, key="liss_phase")

        gcd_v = np.gcd(freq_eff, freq2)
        ratio = f"{freq_eff // gcd_v} : {freq2 // gcd_v}"

        st.markdown(
            f'<div class="mcard" style="text-align:left;margin-top:12px">'
            f'<div class="lbl">Frequency Ratio</div>'
            f'<span class="val" style="color:{COLORS["purple"]}">{ratio}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("""
**Reference Patterns**

| Ratio | Phase | Shape |
|---|---|---|
| 1:1 | 0° | Diagonal |
| 1:1 | 90° | Circle |
| 1:2 | 90° | Figure-8 |
| 2:3 | 90° | Pretzel |
| 3:4 | 90° | Butterfly |

Non-integer ratios → quasi-periodic open paths.
        """)

    with col_plot:
        section_header("01", "Lissajous Figure")
        lcm_f  = freq_eff * freq2 // max(np.gcd(freq_eff, freq2), 1)
        cycles = lcm_f * 6
        t_liss = np.linspace(0.0, cycles / max(float(min(freq_eff, freq2)), 1.0), 12000)
        x_l    = amp * np.sin(2 * np.pi * freq_eff * t_liss)
        y_l    = amp * np.sin(2 * np.pi * freq2    * t_liss + np.radians(phase))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_l, y=y_l, mode="lines",
            line=dict(
                color=COLORS["purple"], width=1.5,
                colorscale=None,
            ),
            name=f"{freq_eff} Hz × {freq2} Hz  φ = {phase}°",
        ))
        apply_theme(
            fig, height=560,
            title=f"Lissajous  {freq_eff} × {freq2} Hz  ·  ratio {ratio}  ·  φ = {phase}°",
            xtitle="X  (A · sin 2πf₁t)",
            ytitle="Y  (A · sin(2πf₂t + φ))",
        )
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — AUDIO ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab_audio:

    section_header("◎", "Audio File Analyzer")

    if "audio_data" not in st.session_state:
        st.markdown("""
        <div class="info-box">
            <span class="icon">📂</span>
            <strong>No audio file loaded</strong>
            Upload a WAV file using the sidebar panel to analyse it here
            and use it as the signal source in all other modules.
        </div>
        """, unsafe_allow_html=True)
    else:
        audio = st.session_state["audio_data"]
        rate  = st.session_state["audio_rate"]
        a_dur = len(audio) / rate

        m1, m2, m3, m4 = st.columns(4)
        with m1: mcard("Sample Rate", f"{rate} Hz",      COLORS["blue"])
        with m2: mcard("Channels",    "1 (mono)",        COLORS["cyan"])
        with m3: mcard("Duration",    f"{a_dur:.2f} s",  COLORS["purple"])
        with m4: mcard("Samples",     f"{len(audio):,}", COLORS["indigo"])

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        clip   = audio[: rate * 10]
        t_clip = np.linspace(0.0, len(clip) / rate, len(clip), endpoint=False)

        section_header("01", "Waveform")
        ds = max(1, len(clip) // 4000)
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=t_clip[::ds], y=clip[::ds], mode="lines",
            line=dict(color=COLORS["green"], width=0.9), name="Waveform",
        ))
        apply_theme(fig_w, height=320, xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig_w, use_container_width=True)

        section_header("02", "Frequency Spectrum")
        clip_fft = clip[: min(len(clip), rate * 2)]
        n_fft_a  = next_pow2(max(len(clip_fft), 4))
        padded_a = np.zeros(n_fft_a)
        padded_a[: len(clip_fft)] = clip_fft * np.hanning(len(clip_fft))
        spec = np.abs(np.fft.rfft(padded_a)) / (n_fft_a / 2.0)
        fa   = np.fft.rfftfreq(n_fft_a, d=1.0 / rate)

        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(
            x=fa, y=spec, mode="lines",
            line=dict(color=COLORS["blue"], width=1.1),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.07)",
            name="Magnitude",
        ))
        apply_theme(fig_s, height=320, xtitle="Frequency (Hz)", ytitle="Magnitude")
        st.plotly_chart(fig_s, use_container_width=True)

        section_header("03", "Spectrogram (STFT)")
        frame_sz = min(2048, max(64, len(clip) // 200))
        hop_sz   = max(1, frame_sz // 4)
        n_fr     = (len(clip) - frame_sz) // hop_sz

        if n_fr < 2:
            st.info("Audio too short for spectrogram (need > 0.5 s).", icon="ℹ️")
        else:
            n_fft_sg = next_pow2(frame_sz)
            win_sg   = np.hanning(frame_sz)
            sgram    = np.zeros((n_fr, n_fft_sg // 2 + 1))
            for i in range(n_fr):
                ch = clip[i * hop_sz: i * hop_sz + frame_sz] * win_sg
                sgram[i] = np.abs(np.fft.rfft(ch, n=n_fft_sg)) / (n_fft_sg / 2.0)

            fa2  = np.fft.rfftfreq(n_fft_sg, d=1.0 / rate)
            ta2  = np.arange(n_fr) * hop_sz / rate
            z_sg = np.clip(20.0 * np.log10(sgram.T + 1e-12), -80.0, 0.0)

            fig_sg = go.Figure(go.Heatmap(
                z=z_sg, x=ta2, y=fa2,
                colorscale="Plasma",
                zmin=-80, zmax=0,
                colorbar=dict(
                    title=dict(text="dB", font=dict(color="#94a3b8", size=12)),
                    tickfont=dict(color="#94a3b8", size=10, family="JetBrains Mono"),
                ),
            ))
            fig_sg.update_layout(
                **{**CHART_LAYOUT, "height": 480},
                xaxis=dict(**AXIS_STYLE, title_text="Time (s)"),
                yaxis=dict(**AXIS_STYLE, title_text="Frequency (Hz)"),
            )
            st.plotly_chart(fig_sg, use_container_width=True)
            st.caption(
                f"STFT · Frame {frame_sz} · Hop {hop_sz} · "
                f"FFT {n_fft_sg} · {n_fr} frames"
            )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='display:flex;align-items:center;justify-content:space-between;"
    "flex-wrap:wrap;gap:8px;padding:4px 0'>"
    "<span style='font-size:11px;color:#334155'>"
    "DSP Pro Lab &nbsp;·&nbsp; Team <strong style='color:#a855f7'>8vaults</strong>"
    " &nbsp;·&nbsp; Problem Statement 18 — Sampling &amp; Aliasing"
    " &nbsp;·&nbsp; Nyquist–Shannon Theorem"
    "</span>"
    "<span style='font-size:11px;color:#1e2631'>"
    "Streamlit · NumPy · Plotly"
    "</span>"
    "</div>",
    unsafe_allow_html=True,
)
