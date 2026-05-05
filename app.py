"""
DSP Pro Lab — 8vaults
Problem Statement 18: Sampling & Aliasing Visual Demonstrator
Professional Edition — Company-grade UI/UX
Fixed Version: all bugs resolved
"""

import io
import wave
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DSP Pro Lab · 8vaults",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — full CSS injection
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080c10 !important;
    color: #e2e8f0;
    font-family: 'DM Sans', sans-serif;
}

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="collapsedControl"] { color: #4ade80 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #1e3a2f; border-radius: 99px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0b0f15 !important;
    border-right: 1px solid #1a2332 !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── All Streamlit inputs ── */
.stSlider > div > div > div > div { background: #4ade80 !important; }
.stSlider [data-baseweb="slider"] > div:first-child { background: #1a2332 !important; }
.stSelectbox > div > div { background: #0d1420 !important; border: 1px solid #1e3350 !important; color: #e2e8f0 !important; border-radius: 8px !important; }
.stSelectbox [data-baseweb="select"] { background: #0d1420 !important; }
.stFileUploader > div { background: #0d1420 !important; border: 1px dashed #1e3350 !important; border-radius: 10px !important; }
.stFileUploader label { color: #94a3b8 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1a2332 !important;
    gap: 2px;
    padding: 0 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 18px !important;
    border-radius: 8px 8px 0 0 !important;
    border: none !important;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: #0f1e14 !important;
    color: #4ade80 !important;
    border-bottom: 2px solid #4ade80 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: #0d1117 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 24px 0 0 0 !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0d1420 !important;
    border: 1px solid #1e3350 !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.streamlit-expanderContent {
    background: #090e16 !important;
    border: 1px solid #1e3350 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* ── Alerts ── */
.stSuccess { background: #0a1f14 !important; border: 1px solid #166534 !important; border-radius: 8px !important; color: #4ade80 !important; }
.stError   { background: #1f0a0a !important; border: 1px solid #991b1b !important; border-radius: 8px !important; color: #f87171 !important; }
.stInfo    { background: #0a0f1f !important; border: 1px solid #1e3a8a !important; border-radius: 8px !important; color: #93c5fd !important; }
.stWarning { background: #1a1200 !important; border: 1px solid #854d0e !important; border-radius: 8px !important; color: #fbbf24 !important; }

/* ── Custom components ── */

/* Topbar */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 28px;
    background: #0b0f15;
    border-bottom: 1px solid #1a2332;
    margin: -1rem -1rem 0 -1rem;
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: blur(12px);
}
.topbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.topbar-logo {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #4ade80, #22c55e);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 800;
    color: #000;
    font-family: 'Syne', sans-serif;
    letter-spacing: -1px;
    box-shadow: 0 0 20px rgba(74,222,128,0.3);
}
.topbar-name {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #f0fdf4;
    letter-spacing: -0.5px;
}
.topbar-name span { color: #4ade80; }
.topbar-tag {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #374151;
    background: #111827;
    border: 1px solid #1f2937;
    padding: 3px 8px;
    border-radius: 4px;
    letter-spacing: 0.1em;
}
.topbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
}
.badge-ps {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #4ade80;
    background: #0a1f14;
    border: 1px solid #166534;
    padding: 4px 10px;
    border-radius: 99px;
    letter-spacing: 0.05em;
}
.badge-team {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
}

/* Sidebar inner */
.sb-section {
    padding: 20px 18px 12px;
    border-bottom: 1px solid #111827;
}
.sb-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #374151;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sb-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #111827;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.mcard {
    flex: 1;
    min-width: 100px;
    background: #0b1117;
    border: 1px solid #1a2332;
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.mcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #4ade8030, transparent);
}
.mcard:hover {
    border-color: #1e3a2f;
    box-shadow: 0 0 20px rgba(74,222,128,0.06);
}
.mcard .lbl {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #374151;
    margin-bottom: 8px;
}
.mcard .val {
    font-family: 'Space Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: #4ade80;
    line-height: 1.1;
}
.mcard .val.warn { color: #f87171; }
.mcard .val.small { font-size: 13px; }

/* Status badge */
.status-ok {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #0a1f14;
    border: 1px solid #166534;
    color: #4ade80;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 99px;
}
.status-ok::before { content: '●'; font-size: 7px; animation: pulse-g 2s infinite; }
@keyframes pulse-g {
    0%,100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.status-warn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #1f0a0a;
    border: 1px solid #991b1b;
    color: #f87171;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 99px;
    animation: pulse-r 1.4s infinite;
}
@keyframes pulse-r {
    0%,100% { box-shadow: 0 0 0 0 rgba(248,113,113,0.3); }
    50% { box-shadow: 0 0 0 4px rgba(248,113,113,0); }
}

/* Section headers */
.section-header {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1a2332;
}
.section-header h3 {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #f0fdf4;
    letter-spacing: -0.3px;
}
.section-num {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #4ade80;
    background: #0a1f14;
    border: 1px solid #166534;
    padding: 2px 7px;
    border-radius: 4px;
}

/* Info callout */
.callout {
    background: #0a0f1f;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 13px;
    color: #93c5fd;
    font-family: 'DM Sans', sans-serif;
}
.callout.warn {
    background: #1a0f00;
    border-color: #f59e0b;
    color: #fbbf24;
}
.callout.success {
    background: #021a0a;
    border-color: #22c55e;
    color: #4ade80;
}
.callout strong { opacity: 0.9; }

/* Audio banner */
.audio-active {
    background: linear-gradient(135deg, #061220 0%, #091a2e 100%);
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 12px 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 13px;
    color: #60a5fa;
    font-family: 'DM Sans', sans-serif;
}
.audio-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #3b82f6;
    animation: pulse-b 1.5s infinite;
    flex-shrink: 0;
}
@keyframes pulse-b {
    0%,100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.4); }
    50% { box-shadow: 0 0 0 5px rgba(59,130,246,0); }
}

/* Chart wrapper */
.chart-wrap {
    background: #070b0e;
    border: 1px solid #111827;
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 16px;
    overflow: hidden;
}
.chart-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #374151;
    padding: 10px 14px 0;
}

/* Data table */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    margin: 12px 0;
}
.data-table th {
    background: #0d1420;
    color: #4ade80;
    font-weight: 700;
    padding: 8px 14px;
    text-align: left;
    border-bottom: 1px solid #1e3350;
    letter-spacing: 0.05em;
    font-size: 10px;
    text-transform: uppercase;
}
.data-table td {
    padding: 8px 14px;
    border-bottom: 1px solid #111827;
    color: #94a3b8;
}
.data-table tr:hover td { background: #0a0f16; color: #e2e8f0; }
.data-table .mono { font-family: 'Space Mono', monospace; color: #4ade80; }
.data-table .warn-td { color: #f87171; }
.data-table .ok-td   { color: #4ade80; }

/* Sidebar upload zone */
.upload-zone {
    border: 1px dashed #1e3350;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    background: #070c14;
    margin-bottom: 8px;
}
.upload-zone p { font-size: 12px; color: #374151; margin: 0; }

/* Footer */
.app-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    border-top: 1px solid #111827;
    margin-top: 32px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #1f2937;
    letter-spacing: 0.1em;
}
.footer-links { display: flex; gap: 20px; }
.footer-links span { cursor: default; }
.footer-links span:hover { color: #374151; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def next_pow2(n):
    p = 1
    while p < n:
        p <<= 1
    return p

def gen_signal(time_arr, f, a, wtype, dur):
    """Generate a signal of the given waveform type."""
    if wtype == "Sine":
        return a * np.sin(2 * np.pi * f * time_arr)
    if wtype == "Square":
        return a * np.sign(np.sin(2 * np.pi * f * time_arr))
    if wtype == "Triangle":
        return a * (2.0 / np.pi) * np.arcsin(np.sin(2 * np.pi * f * time_arr))
    if wtype == "Sawtooth":
        return a * (2.0 * ((time_arr * f) % 1.0) - 1.0)
    if wtype == "Chirp":
        # BUG FIX: guard against zero duration
        k = f / max(float(dur), 1e-9)
        return a * np.sin(2 * np.pi * (f * time_arr + 0.5 * k * time_arr ** 2))
    return np.zeros_like(time_arr)

def moving_avg(s, w):
    w = max(1, int(w))
    return np.convolve(s, np.ones(w) / w, mode="same")

def compute_fft(sig, sample_rate):
    """Compute FFT of signal. Returns (freqs, mags, power_db, n_fft)."""
    # BUG FIX: guard against empty or all-zero signal
    if len(sig) < 4:
        return np.array([0.0]), np.array([0.0]), np.array([-120.0]), 4
    n = next_pow2(max(len(sig), 4))
    win = np.hanning(len(sig))
    padded = np.zeros(n)
    padded[:len(sig)] = sig * win
    spectrum = np.fft.rfft(padded)
    freqs = np.fft.rfftfreq(n, d=1.0 / max(float(sample_rate), 1.0))
    mags = np.abs(spectrum) / (n / 2.0)
    max_mag = float(mags.max()) if mags.max() > 0 else 1e-12
    power_db = 20.0 * np.log10(np.maximum(mags / max_mag, 1e-12))
    return freqs, mags, power_db, n

def fft_bandwidth(freqs, mags, threshold=0.1):
    """Return signal bandwidth above threshold * peak."""
    if len(mags) == 0:
        return 0.0
    max_mag = float(mags.max())
    if max_mag <= 0:
        return 0.0
    mask = mags > max_mag * threshold
    if int(np.count_nonzero(mask)) >= 2:
        idx = np.where(mask)[0]
        return round(float(freqs[idx[-1]]) - float(freqs[idx[0]]), 2)
    return 0.0

def load_wav(file_obj):
    """Load a WAV file and return (audio_array, sample_rate)."""
    buf = io.BytesIO(file_obj.read())
    wf = wave.open(buf, "rb")
    rate  = wf.getframerate()
    nch   = wf.getnchannels()
    nsmp  = wf.getnframes()
    sw    = wf.getsampwidth()
    raw   = wf.readframes(nsmp)
    wf.close()
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw, np.int16)
    audio = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    # BUG FIX: handle mono and stereo safely
    if nch >= 2:
        audio = audio[::nch]
    peak = float(np.max(np.abs(audio))) if len(audio) > 0 else 0.0
    if peak > 0:
        audio /= peak
    return audio, rate

# ── Plotly theme ──────────────────────────────────────────────────────────────
CHART_BG   = "#070b0e"
GRID_COLOR = "rgba(74,222,128,0.06)"
ZERO_COLOR = "rgba(74,222,128,0.2)"
TICK_COLOR = "#374151"
FONT_MONO  = "Space Mono, Courier New, monospace"

def chart_layout(height=440, title="", xtitle="", ytitle=""):
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CHART_BG,
        height=height,
        font=dict(family=FONT_MONO, size=11, color=TICK_COLOR),
        legend=dict(
            bgcolor="rgba(7,11,14,0.9)",
            bordercolor="#1a2332",
            borderwidth=1,
            font=dict(family="DM Sans, sans-serif", size=11, color="#94a3b8"),
        ),
        margin=dict(l=60, r=20, t=50 if title else 28, b=50),
    )
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(family="DM Sans, sans-serif", size=13, color="#94a3b8"),
            x=0.01, xanchor="left",
        )
    return layout

def axis_style(label=""):
    return dict(
        title_text=label,
        title_font=dict(family="DM Sans, sans-serif", size=11, color="#4b5563"),
        gridcolor=GRID_COLOR,
        zerolinecolor=ZERO_COLOR,
        zerolinewidth=1,
        color=TICK_COLOR,
        linecolor="#111827",
        linewidth=1,
        tickfont=dict(family=FONT_MONO, size=10, color=TICK_COLOR),
    )

def apply_chart(fig, height=440, title="", xtitle="", ytitle=""):
    fig.update_layout(**chart_layout(height, title))
    fig.update_xaxes(**axis_style(xtitle))
    fig.update_yaxes(**axis_style(ytitle))

def mcard(label, value, warn=False, small=False):
    """Return an HTML metric card string."""
    # BUG FIX: small flag takes precedence only if not warn
    if warn:
        val_class = "val warn"
    elif small:
        val_class = "val small"
    else:
        val_class = "val"
    return f'<div class="mcard"><div class="lbl">{label}</div><div class="{val_class}">{value}</div></div>'

def render_metric_row(cards):
    """Render a list of mcard HTML strings inside a metric-row div."""
    # BUG FIX: cards must be a list; join them before wrapping
    html = '<div class="metric-row">' + "".join(cards) + '</div>'
    st.markdown(html, unsafe_allow_html=True)

def section_header(num, title):
    st.markdown(
        f'<div class="section-header">'
        f'<span class="section-num">{num}</span>'
        f'<h3>{title}</h3>'
        f'</div>',
        unsafe_allow_html=True
    )

def callout_box(text, kind="info"):
    kind_map = {"info": "callout", "warn": "callout warn", "success": "callout success"}
    cls = kind_map.get(kind, "callout")
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TOPBAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
  <div class="topbar-brand">
    <div class="topbar-logo">⚡</div>
    <div>
      <div class="topbar-name">DSP Pro<span>Lab</span></div>
    </div>
    <div class="topbar-tag">v3.0 · PROFESSIONAL</div>
  </div>
  <div class="topbar-right">
    <span class="badge-ps">PS-18 · SAMPLING &amp; ALIASING</span>
    <span class="badge-team">8vaults</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand
    st.markdown("""
    <div style="padding:20px 18px 16px;border-bottom:1px solid #111827">
      <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#f0fdf4;letter-spacing:-0.3px">
        ⚡ DSP Pro<span style="color:#4ade80">Lab</span>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:9px;color:#374151;margin-top:4px;letter-spacing:0.12em">
        SIGNAL PROCESSING WORKSTATION
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Audio upload
    st.markdown('<div class="sb-section">', unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Audio Input</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "WAV file", type=["wav"], label_visibility="collapsed",
        help="Upload a WAV to use as signal source across all modules"
    )
    if uploaded_file is not None:
        fkey = uploaded_file.name + str(uploaded_file.size)
        if st.session_state.get("audio_key") != fkey:
            try:
                audio_data, audio_rate = load_wav(uploaded_file)
                st.session_state.update({
                    "audio_data": audio_data, "audio_rate": audio_rate,
                    "audio_name": uploaded_file.name, "audio_key": fkey,
                })
            except Exception as e:
                st.error(f"WAV error: {e}")
    else:
        for k in ("audio_data", "audio_rate", "audio_name", "audio_key"):
            st.session_state.pop(k, None)

    audio_loaded = "audio_data" in st.session_state
    if audio_loaded:
        a_dur_sb = len(st.session_state["audio_data"]) / st.session_state["audio_rate"]
        st.markdown(f"""
        <div style="background:#061220;border:1px solid #1e3a5f;border-radius:8px;
                    padding:10px 12px;margin-top:8px;font-size:12px;color:#60a5fa;
                    font-family:'DM Sans',sans-serif">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
            <div style="width:6px;height:6px;border-radius:50%;background:#3b82f6"></div>
            <strong style="color:#93c5fd">{st.session_state['audio_name']}</strong>
          </div>
          <div style="color:#374151;font-size:11px;font-family:'Space Mono',monospace">
            {st.session_state['audio_rate']} Hz · {a_dur_sb:.1f}s · Active
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Signal Generator
    st.markdown('<div class="sb-section">', unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Signal Generator</div>', unsafe_allow_html=True)
    disabled = audio_loaded

    signal_type = st.selectbox(
        "Waveform", ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"],
        disabled=disabled,
        help="Waveform type (inactive in audio mode)"
    )
    freq = st.slider(
        "Frequency", 1, 50, 5, disabled=disabled,
        format="%d Hz",
        help="Signal fundamental frequency"
    )
    amp = st.slider(
        "Amplitude", 0.1, 3.0, 1.0, 0.1, disabled=disabled,
        format="%.1f",
        help="Peak amplitude"
    )
    duration = st.slider(
        "Duration", 1, 5, 2, disabled=disabled,
        format="%d s",
        help="Signal duration in seconds"
    )
    if audio_loaded:
        st.markdown(
            '<div style="font-size:11px;color:#374151;font-family:DM Sans,sans-serif;'
            'margin-top:6px;font-style:italic">↑ Overridden by audio file</div>',
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Sampling
    st.markdown('<div class="sb-section">', unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Sampling & Noise</div>', unsafe_allow_html=True)
    fs_raw = st.slider("Sampling Rate", 2, 200, 40, format="%d Hz")
    noise_level = st.slider("Noise Level", 0.0, 2.0, 0.0, 0.1, format="%.1f σ")
    filter_win  = st.slider("Filter Window", 2, 80, 10, format="%d n")
    st.markdown("</div>", unsafe_allow_html=True)

    # About
    st.markdown("""
    <div style="padding:16px 18px;margin-top:auto">
      <div style="font-family:'Space Mono',monospace;font-size:9px;color:#1f2937;
                  letter-spacing:0.12em;margin-bottom:8px">ABOUT</div>
      <div style="font-size:11px;color:#374151;font-family:'DM Sans',sans-serif;line-height:1.6">
        Nyquist–Shannon theorem<br>
        <span style="color:#1f2937;font-family:'Space Mono',monospace;font-size:10px">
        Fs ≥ 2 × f_max
        </span>
      </div>
      <div style="margin-top:12px;font-family:'Space Mono',monospace;font-size:9px;color:#1f2937">
        8vaults · PS-18 · 2025
      </div>
    </div>
    """, unsafe_allow_html=True)


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
    # BUG FIX: limit FFT input to max 8192 samples; guard empty result
    fft_input    = signal[:min(N, 8192)]
    fq, mq, _, _ = compute_fft(fft_input, float(audio_rate))
    # BUG FIX: only argmax if mq is non-empty and has nonzero values
    if len(mq) > 0 and mq.max() > 0:
        dom_idx_eff = int(np.argmax(mq))
        freq_eff    = max(1, int(round(float(fq[dom_idx_eff]))))
    else:
        freq_eff    = 1
    source_label = f"🎵 {st.session_state['audio_name']}"
else:
    t            = np.linspace(0.0, duration, N, endpoint=False)
    ts           = np.arange(0.0, duration, 1.0 / fs)
    signal       = gen_signal(t, freq, amp, signal_type, duration)
    sampled      = gen_signal(ts, freq, amp, signal_type, duration)
    duration_eff = float(duration)
    freq_eff     = freq
    source_label = f"{signal_type} · {freq} Hz"

# BUG FIX: protect against divide-by-zero when fs=0 (already guarded, but be safe)
nyquist  = 2 * freq_eff
# BUG FIX: alias frequency formula — guard division by zero
alias_f  = abs(freq_eff - round(freq_eff / max(fs, 1)) * fs)
is_alias = fs < nyquist

rng       = np.random.default_rng(42)
noise_vec = rng.normal(0.0, noise_level, N) if noise_level > 0 else np.zeros(N)
noisy     = signal + noise_vec
filtered  = moving_avg(noisy, filter_win)


# ══════════════════════════════════════════════════════════════════════════════
# AUDIO BANNER
# ══════════════════════════════════════════════════════════════════════════════
if audio_loaded:
    a_dur = len(st.session_state["audio_data"]) / st.session_state["audio_rate"]
    st.markdown(
        f'<div class="audio-active">'
        f'<div class="audio-dot"></div>'
        f'<div><strong style="color:#93c5fd">{st.session_state["audio_name"]}</strong>'
        f' &nbsp;·&nbsp; {st.session_state["audio_rate"]} Hz &nbsp;·&nbsp; {a_dur:.1f}s'
        f' &nbsp;·&nbsp; Dominant: <strong style="color:#60a5fa">{freq_eff} Hz</strong>'
        f' &nbsp;·&nbsp; Nyquist min: <strong>{nyquist} Hz</strong>'
        f'</div></div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# STATUS BAR — 6 metric cards
# BUG FIX: build as a list and pass to render_metric_row (consistent API)
# ══════════════════════════════════════════════════════════════════════════════
status_badge = (
    '<span class="status-warn">⚠ ALIASING</span>'
    if is_alias else
    '<span class="status-ok">CLEAN</span>'
)
render_metric_row([
    mcard("Source",        source_label[:24], small=True),
    mcard("Signal Freq",   f"{freq_eff} Hz"),
    mcard("Sampling Rate", f"{fs} Hz"),
    mcard("Nyquist Min",   f"{nyquist} Hz"),
    mcard("Alias Freq",    f"{alias_f:.1f} Hz", warn=is_alias),
    mcard("Status",        status_badge, small=True),
])
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "⬤ Oscilloscope",
    "▲ FFT Spectrum",
    "◎ Phase Space",
    "⧖ Filter Lab",
    "≋ Waterfall",
    "∞ Lissajous",
    "♫ Audio Analyzer",
])
tab_scope, tab_fft, tab_phase, tab_filter, tab_water, tab_liss, tab_audio = tabs


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OSCILLOSCOPE
# ══════════════════════════════════════════════════════════════════════════════
with tab_scope:

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        section_header("01", "Continuous Signal")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t, y=signal, mode="lines", name="x(t)",
            line=dict(color="#4ade80", width=1.8),
        ))
        if noise_level > 0:
            fig.add_trace(go.Scatter(
                x=t, y=noisy, mode="lines", name="x(t) + noise",
                line=dict(color="rgba(248,113,113,0.45)", width=1),
            ))
        apply_chart(fig, height=380,
                    xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("02", "Sampled Signal")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=t, y=signal, mode="lines", name="Continuous",
            line=dict(color="#4ade80", width=1.2, dash="dot"), opacity=0.35,
        ))
        # Stems
        stem_x, stem_y = [], []
        for xi, yi in zip(ts, sampled):
            stem_x += [float(xi), float(xi), None]
            stem_y += [0.0, float(yi), None]
        fig2.add_trace(go.Scatter(
            x=stem_x, y=stem_y, mode="lines", showlegend=False,
            line=dict(color="rgba(249,115,22,0.3)", width=1),
        ))
        fig2.add_trace(go.Scatter(
            x=ts, y=sampled, mode="markers",
            name=f"Samples (Fs={fs} Hz)",
            marker=dict(color="#f97316", size=7,
                        line=dict(color="#fed7aa", width=1)),
        ))
        apply_chart(fig2, height=380,
                    title=f"Fs = {fs} Hz   ·   {len(ts)} samples   ·   T = {1/fs*1000:.1f} ms",
                    xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig2, use_container_width=True)

    # Aliasing chart — full width
    section_header("03", "Aliasing Visualization")

    # BUG FIX: alias_sig must use duration_eff as the dur argument to gen_signal
    alias_sig = gen_signal(t, alias_f if alias_f > 0 else 0.1, amp, "Sine", duration_eff)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=t, y=signal, mode="lines",
        name=f"Original  {freq_eff} Hz",
        line=dict(color="#4ade80", width=2),
    ))
    fig3.add_trace(go.Scatter(
        x=ts, y=sampled, mode="markers",
        name=f"Samples  Fs={fs} Hz",
        marker=dict(color="#facc15", size=6, symbol="diamond"),
    ))
    if is_alias:
        fig3.add_trace(go.Scatter(
            x=t, y=alias_sig, mode="lines",
            name=f"Alias  {alias_f:.2f} Hz",
            line=dict(color="#f97316", width=2, dash="dash"),
        ))
    apply_chart(
        fig3, height=380,
        title=f"falias = |{freq_eff} − round({freq_eff}/{fs})×{fs}| = {alias_f:.2f} Hz",
        xtitle="Time (s)", ytitle="Amplitude"
    )
    st.plotly_chart(fig3, use_container_width=True)

    if is_alias:
        callout_box(
            f"<strong>Aliasing detected.</strong> Signal at {freq_eff} Hz requires "
            f"Fs ≥ {nyquist} Hz (Nyquist criterion). "
            f"At Fs = {fs} Hz it appears as <strong>{alias_f:.2f} Hz</strong>. "
            f"Increase sampling rate to eliminate.",
            kind="warn"
        )
    else:
        callout_box(
            f"<strong>No aliasing.</strong> Fs = {fs} Hz ≥ Nyquist = {nyquist} Hz. "
            f"Signal is correctly sampled.",
            kind="success"
        )

    # Nyquist table
    with st.expander("Nyquist Reference Table"):
        rows = []
        for test_fs in [2, 4, 6, 8, 10, 15, 20, 40, 100, 200]:
            # BUG FIX: guard division by zero for test_fs
            a_f = abs(freq_eff - round(freq_eff / max(test_fs, 1)) * test_fs)
            ok  = test_fs >= nyquist
            rows.append(
                f'<tr><td class="mono">{test_fs} Hz</td>'
                f'<td class="{"ok-td" if ok else "warn-td"}">'
                f'{"✓ Clean" if ok else "⚠ Alias"}</td>'
                f'<td class="mono">{a_f:.2f} Hz</td>'
                f'<td>{round(test_fs / max(freq_eff, 1), 2)}×</td></tr>'
            )
        st.markdown(f"""
        <table class="data-table">
          <tr><th>Fs</th><th>Status</th><th>Alias freq</th><th>Oversampling</th></tr>
          {"".join(rows)}
        </table>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FFT SPECTRUM
# ══════════════════════════════════════════════════════════════════════════════
with tab_fft:

    freqs_hz, mags, power_db, n_fft = compute_fft(noisy, float(fs))

    # BUG FIX: guard all operations that depend on non-empty mags
    max_mag  = float(mags.max()) if len(mags) > 0 and mags.max() > 0 else 1e-12
    dom_idx  = int(np.argmax(mags)) if len(mags) > 0 else 0
    dom_freq = round(float(freqs_hz[dom_idx]), 2) if len(freqs_hz) > dom_idx else 0.0
    bw_hz    = fft_bandwidth(freqs_hz, mags)
    snr_db   = (round(20.0 * np.log10(float(amp) / max(float(noise_level), 1e-9)), 1)
                if noise_level > 0 else 99.0)
    # BUG FIX: harmonic RMS — check index bounds
    if dom_idx + 1 < len(mags):
        harm_rms = float(np.sqrt(np.sum(mags[dom_idx + 1:] ** 2)))
    else:
        harm_rms = 0.0
    thd_pct  = round(harm_rms / max(float(mags[dom_idx]) if len(mags) > 0 else 1e-9, 1e-9) * 100.0, 1)
    freq_res = round(float(fs) / n_fft, 4) if n_fft > 0 else 0.0

    render_metric_row([
        mcard("Dominant Freq",     f"{dom_freq} Hz"),
        mcard("Bandwidth −10 dB",  f"{bw_hz} Hz"),
        mcard("SNR",               f"{min(snr_db, 99.9):.1f} dB"),
        mcard("THD",               f"{thd_pct} %"),
        mcard("FFT Size",          f"{n_fft} pts"),
        mcard("Resolution",        f"{freq_res} Hz/bin"),
    ])

    # BUG FIX: guard against empty freqs_hz when building bar colors
    n_bins = max(len(freqs_hz), 1)
    bar_colors = [
        f"hsl({int(140 + i / (n_bins - 1) * 80)},75%,52%)"
        for i in range(n_bins)
    ]

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Magnitude Spectrum", "Power Spectrum (dB)"),
        vertical_spacing=0.1,
    )
    fig.add_trace(go.Bar(
        x=freqs_hz, y=mags, name="Magnitude",
        marker=dict(color=bar_colors), showlegend=False,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=freqs_hz, y=power_db, mode="lines",
        line=dict(color="#60a5fa", width=1.6), showlegend=False, fill="tozeroy",
        fillcolor="rgba(96,165,250,0.07)",
    ), row=2, col=1)

    # BUG FIX: only add vlines when freqs_hz is non-empty and within range
    freq_max = float(freqs_hz[-1]) if len(freqs_hz) > 0 else 0.0
    for r in (1, 2):
        if 0 < dom_freq <= freq_max:
            fig.add_vline(x=dom_freq, line_dash="dash", line_color="#f97316",
                          annotation_text=f"f={dom_freq} Hz",
                          annotation_font=dict(color="#f97316", size=11),
                          annotation_position="top right", row=r, col=1)
        if is_alias and 0 < alias_f <= freq_max:
            fig.add_vline(x=alias_f, line_dash="dot", line_color="#facc15",
                          annotation_text=f"alias={alias_f:.1f}Hz",
                          annotation_font=dict(color="#facc15", size=10),
                          annotation_position="top left", row=r, col=1)

    base = chart_layout(height=680)
    base["showlegend"] = False
    # BUG FIX: removed duplicate annotations dict that conflicted with subplot titles
    fig.update_layout(**base)
    fig.update_xaxes(**axis_style("Frequency (Hz)"))
    fig.update_yaxes(**axis_style())
    fig.update_yaxes(title_text="Magnitude", row=1, col=1)
    fig.update_yaxes(title_text="dB",        row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("FFT Parameters & Theory"):
        alias_note = "⚠ Active" if is_alias else "No aliasing"
        st.markdown(f"""
<table class="data-table">
  <tr><th>Parameter</th><th>Value</th><th>Note</th></tr>
  <tr><td>FFT size</td><td class="mono">{n_fft}</td><td>Zero-padded to next power of 2</td></tr>
  <tr><td>Window</td><td class="mono">Hanning</td><td>Reduces spectral leakage</td></tr>
  <tr><td>Frequency resolution</td><td class="mono">{freq_res} Hz/bin</td><td>Fs / N_fft</td></tr>
  <tr><td>Nyquist limit</td><td class="mono">{fs // 2} Hz</td><td>Maximum representable frequency</td></tr>
  <tr><td>Dominant frequency</td><td class="mono">{dom_freq} Hz</td><td>Peak magnitude bin</td></tr>
  <tr><td>Alias frequency</td><td class="mono">{alias_f:.2f} Hz</td><td>{alias_note}</td></tr>
</table>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PHASE SPACE
# ══════════════════════════════════════════════════════════════════════════════
with tab_phase:

    # BUG FIX: clamp lag upper bound to avoid empty slices
    max_lag_val = max(1, min(50, N // 4))
    lag = st.slider("Lag k (samples)", 1, max_lag_val, min(5, max_lag_val), key="lag_sl")

    # BUG FIX: guard against lag >= N
    if lag < N:
        x_ph, y_ph = noisy[:-lag], noisy[lag:]
    else:
        x_ph, y_ph = noisy[:1], noisy[:1]

    max_lag_ac = min(400, len(signal) // 2)
    mean_s     = float(signal.mean())
    var_s      = float(np.var(signal))
    lags_arr   = np.arange(max_lag_ac)
    if var_s > 1e-12 and max_lag_ac > 0:
        auto = np.array([
            float(np.mean((signal[:N - ll] - mean_s) * (signal[ll:] - mean_s))) / var_s
            for ll in lags_arr
        ])
    else:
        auto = np.zeros(max(max_lag_ac, 1))

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        section_header("01", "Phase Portrait")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_ph, y=y_ph, mode="lines",
            line=dict(color="#c084fc", width=0.9),
            name=f"x[n] vs x[n−{lag}]",
        ))
        apply_chart(fig, height=460,
                    title=f"Phase portrait  ·  lag = {lag} samples",
                    xtitle=f"x[n−{lag}]", ytitle="x[n]")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("02", "Autocorrelation R[k]")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=lags_arr, y=auto, mode="lines",
            line=dict(color="#f0abfc", width=1.5), name="R[k]",
            fill="tozeroy", fillcolor="rgba(240,171,252,0.06)",
        ))
        fig2.add_hline(y=0, line_dash="dot", line_color="rgba(74,222,128,0.25)")
        apply_chart(fig2, height=460,
                    title="Normalised autocorrelation",
                    xtitle="Lag (samples)", ytitle="R[k]")
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FILTER LAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_filter:

    rms_orig = float(np.sqrt(np.mean(signal ** 2)))
    rms_n    = float(np.sqrt(np.mean(noisy ** 2)))
    rms_f    = float(np.sqrt(np.mean(filtered ** 2)))
    # BUG FIX: guard log of zero
    snr_g    = round(20.0 * np.log10(max(rms_f, 1e-12) / max(rms_n, 1e-12)), 2)
    # BUG FIX: filter_win could be 1 — guard division
    cutoff   = round(float(fs) / (2.0 * max(filter_win, 1)), 2)

    render_metric_row([
        mcard("RMS Clean",    f"{rms_orig:.4f}"),
        mcard("RMS Noisy",    f"{rms_n:.4f}"),
        mcard("RMS Filtered", f"{rms_f:.4f}"),
        mcard("SNR Gain",     f"{snr_g} dB"),
        mcard("−3 dB Cutoff", f"{cutoff} Hz"),
        mcard("Group Delay",  f"{filter_win // 2} smp"),
    ])

    section_header("01", "Clean Signal")
    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(x=t, y=signal, mode="lines", name="Clean",
                               line=dict(color="#4ade80", width=1.8)))
    apply_chart(fig_c, height=300, xtitle="Time (s)", ytitle="Amplitude")
    st.plotly_chart(fig_c, use_container_width=True)

    col_n, col_f = st.columns(2, gap="medium")
    with col_n:
        section_header("02", "Noisy Signal")
        fig_n = go.Figure()
        fig_n.add_trace(go.Scatter(x=t, y=noisy, mode="lines",
                                   name=f"Noisy (σ={noise_level:.1f})",
                                   line=dict(color="#f87171", width=1.2)))
        apply_chart(fig_n, height=320, xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig_n, use_container_width=True)

    with col_f:
        section_header("03", "Filtered Signal")
        fig_f = go.Figure()
        fig_f.add_trace(go.Scatter(x=t, y=filtered, mode="lines",
                                   name=f"FIR M={filter_win}",
                                   line=dict(color="#38bdf8", width=2)))
        apply_chart(fig_f, height=320, xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig_f, use_container_width=True)

    section_header("04", "Overlay Comparison")
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Scatter(x=t, y=noisy, mode="lines",
                                 name=f"Noisy (σ={noise_level:.1f})",
                                 line=dict(color="rgba(248,113,113,0.5)", width=1)))
    fig_cmp.add_trace(go.Scatter(x=t, y=filtered, mode="lines",
                                 name=f"Filtered M={filter_win}",
                                 line=dict(color="#38bdf8", width=2.2)))
    apply_chart(fig_cmp, height=340, xtitle="Time (s)", ytitle="Amplitude")
    st.plotly_chart(fig_cmp, use_container_width=True)

    section_header("05", "Filter Frequency Response |H(f)|")
    omega = np.linspace(0.0, np.pi, 1024)
    eps   = 1e-9
    M_f   = float(max(filter_win, 1))
    # BUG FIX: stable moving-average frequency response formula
    H = np.abs(np.sinc(M_f * omega / (2 * np.pi))) if False else \
        np.clip(np.abs(np.sin(M_f * omega / 2 + eps) / (M_f * (np.sin(omega / 2 + eps) + eps))), 0, 1)
    f_ax = omega / np.pi * (fs / 2.0)
    fig_hr = go.Figure()
    fig_hr.add_trace(go.Scatter(x=f_ax, y=H, mode="lines", name="|H(f)|",
                                line=dict(color="#f97316", width=2.2),
                                fill="tozeroy", fillcolor="rgba(249,115,22,0.07)"))
    fig_hr.add_hline(y=0.707, line_dash="dash", line_color="rgba(74,222,128,0.6)",
                     annotation_text="−3 dB (0.707)",
                     annotation_font=dict(color="#4ade80", size=11),
                     annotation_position="bottom right")
    apply_chart(fig_hr, height=320, xtitle="Frequency (Hz)", ytitle="|H(f)|")
    st.plotly_chart(fig_hr, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — WATERFALL
# ══════════════════════════════════════════════════════════════════════════════
with tab_water:

    section_header("01", "Short-Time FFT Waterfall Spectrogram")

    n_frames  = 64
    frame_len = max(64, N // n_frames)
    n_fft_w   = next_pow2(frame_len)
    # BUG FIX: prevent zero hop size
    hop       = max(1, (N - frame_len) // max(n_frames - 1, 1))
    win_h     = np.hanning(frame_len)

    wfall, t_labels = [], []
    for i in range(n_frames):
        start = i * hop
        end   = start + frame_len
        if end > N:
            break
        pad = np.zeros(n_fft_w)
        pad[:frame_len] = noisy[start:end] * win_h
        wfall.append(np.abs(np.fft.rfft(pad)) / (n_fft_w / 2.0))
        t_labels.append(round(start / N * duration_eff, 3))

    if not wfall:
        st.warning("Signal too short for waterfall. Increase Duration slider.")
    else:
        wfall_arr = np.array(wfall)
        f_ax_w    = np.fft.rfftfreq(n_fft_w, d=1.0 / max(fs, 1))
        z_db      = np.clip(20.0 * np.log10(wfall_arr + 1e-12), -80.0, 0.0)

        fig = go.Figure(go.Heatmap(
            z=z_db.T, x=t_labels, y=f_ax_w,
            colorscale="Viridis", zmin=-80, zmax=0,
            colorbar=dict(
                title="dB",
                titlefont=dict(family="DM Sans, sans-serif", size=11, color="#4b5563"),
                tickfont=dict(family=FONT_MONO, size=10, color=TICK_COLOR),
                ticksuffix=" dB",
                thickness=14,
            ),
        ))
        fig.update_layout(**chart_layout(height=580))
        fig.update_xaxes(**axis_style("Time (s)"))
        fig.update_yaxes(**axis_style("Frequency (Hz)"))
        st.plotly_chart(fig, use_container_width=True)

        freq_res_w = round(float(fs) / n_fft_w, 3) if n_fft_w > 0 else 0.0
        st.markdown(
            f'<div style="font-family:Space Mono,monospace;font-size:10px;color:#374151;'
            f'padding:6px 0;letter-spacing:0.06em">'
            f'Hanning STFT  ·  {len(wfall)} frames  ·  FFT {n_fft_w}  ·  '
            f'{freq_res_w} Hz/bin  ·  Hop {hop} samples'
            f'</div>',
            unsafe_allow_html=True
        )
        callout_box(
            "Tip: Select <strong>Chirp</strong> waveform in the sidebar to see "
            "a diagonal frequency sweep across the spectrogram.",
            kind="info"
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — LISSAJOUS
# ══════════════════════════════════════════════════════════════════════════════
with tab_liss:

    col_plot, col_ctrl = st.columns([3, 1], gap="medium")

    with col_ctrl:
        section_header("⚙", "Controls")
        liss_max     = max(50, freq_eff * 4)
        liss_default = min(3, liss_max)
        freq2 = st.slider("Y Frequency", 1, liss_max, liss_default, format="%d Hz", key="lf2")
        phase = st.slider("Phase Offset", 0, 360, 0, 5, format="%d°", key="lph")

        # BUG FIX: np.gcd requires non-negative integers; protect against 0
        gcd_v = int(np.gcd(max(freq_eff, 1), max(freq2, 1)))
        ratio = f"{max(freq_eff, 1) // gcd_v} : {max(freq2, 1) // gcd_v}"

        st.markdown(
            f'<div style="margin:12px 0;padding:10px 12px;background:#0b1117;'
            f'border:1px solid #1a2332;border-radius:8px">'
            f'<div style="font-family:Space Mono,monospace;font-size:9px;'
            f'color:#374151;margin-bottom:4px;letter-spacing:0.1em">RATIO</div>'
            f'<div style="font-family:Syne,sans-serif;font-size:24px;'
            f'font-weight:800;color:#4ade80">{ratio}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(f"""
<table class="data-table">
  <tr><th>Ratio</th><th>Phase</th><th>Shape</th></tr>
  <tr><td>1:1</td><td>0°</td><td>Line</td></tr>
  <tr><td>1:1</td><td>90°</td><td>Circle</td></tr>
  <tr><td>1:2</td><td>90°</td><td>Figure-8</td></tr>
  <tr><td>2:3</td><td>90°</td><td>Pretzel</td></tr>
  <tr><td>3:4</td><td>90°</td><td>Butterfly</td></tr>
</table>
        """, unsafe_allow_html=True)

    with col_plot:
        section_header("01", "Lissajous Figure")
        # BUG FIX: guard against zero gcd, zero frequencies, and overflow in lcm
        f_a = max(freq_eff, 1)
        f_b = max(freq2, 1)
        lcm_f  = f_a * f_b // gcd_v  # safe: gcd >= 1
        # BUG FIX: cap cycles to prevent enormous arrays
        cycles = min(lcm_f * 6, 10000)
        t_liss = np.linspace(0.0, cycles / float(min(f_a, f_b)), 12000)
        x_l    = amp * np.sin(2 * np.pi * f_a * t_liss)
        y_l    = amp * np.sin(2 * np.pi * f_b * t_liss + np.radians(phase))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_l, y=y_l, mode="lines",
            line=dict(color="#c084fc", width=1.5),
            name=f"{f_a} Hz × {f_b} Hz  φ={phase}°",
        ))
        apply_chart(
            fig, height=520,
            title=f"Lissajous  {f_a} × {f_b} Hz  |  ratio {ratio}  |  φ = {phase}°",
            xtitle=f"X — A·sin(2π·{f_a}·t)",
            ytitle=f"Y — A·sin(2π·{f_b}·t + φ)",
        )
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — AUDIO ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab_audio:

    section_header("♫", "Audio File Analyzer")

    if "audio_data" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;border:1px dashed #1a2332;
                    border-radius:12px;margin:20px 0">
          <div style="font-size:40px;margin-bottom:16px">♫</div>
          <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;
                      color:#374151;margin-bottom:8px">No Audio Loaded</div>
          <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:#1f2937">
            Upload a WAV file using the sidebar panel to analyse it here<br>
            and use it as the signal source across all modules.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        audio = st.session_state["audio_data"]
        rate  = st.session_state["audio_rate"]
        a_dur = len(audio) / max(rate, 1)

        render_metric_row([
            mcard("Sample Rate", f"{rate} Hz"),
            mcard("Channels",    "1 (mono)"),
            mcard("Duration",    f"{a_dur:.2f} s"),
            mcard("Samples",     f"{len(audio):,}"),
        ])

        # BUG FIX: clip to at most 10 s, but guard against rate=0
        clip_end = min(len(audio), rate * 10) if rate > 0 else len(audio)
        clip     = audio[:clip_end]
        t_clip   = np.linspace(0.0, len(clip) / max(rate, 1), len(clip), endpoint=False)

        section_header("01", "Waveform")
        ds = max(1, len(clip) // 4000)
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=t_clip[::ds], y=clip[::ds], mode="lines",
            line=dict(color="#4ade80", width=0.9), name="Waveform",
        ))
        apply_chart(fig_w, height=320, xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig_w, use_container_width=True)

        section_header("02", "Frequency Spectrum")
        # BUG FIX: limit FFT input length to 2 s of audio
        fft_len  = min(len(clip), rate * 2) if rate > 0 else len(clip)
        clip_fft = clip[:fft_len]
        n_fft_a  = next_pow2(max(len(clip_fft), 4))
        padded_a = np.zeros(n_fft_a)
        padded_a[:len(clip_fft)] = clip_fft * np.hanning(len(clip_fft))
        spec = np.abs(np.fft.rfft(padded_a)) / (n_fft_a / 2.0)
        fa   = np.fft.rfftfreq(n_fft_a, d=1.0 / max(rate, 1))
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(
            x=fa, y=spec, mode="lines",
            line=dict(color="#60a5fa", width=1.1), name="Magnitude",
            fill="tozeroy", fillcolor="rgba(96,165,250,0.06)",
        ))
        apply_chart(fig_s, height=320, xtitle="Frequency (Hz)", ytitle="Magnitude")
        st.plotly_chart(fig_s, use_container_width=True)

        section_header("03", "Spectrogram (STFT)")
        frame_sz = min(2048, max(64, len(clip) // 200))
        hop_sz   = max(1, frame_sz // 4)
        n_fr     = max(0, (len(clip) - frame_sz) // hop_sz)

        if n_fr < 2:
            callout_box("Audio too short for spectrogram (needs > 0.5 s).", kind="warn")
        else:
            n_fft_sg = next_pow2(frame_sz)
            win_sg   = np.hanning(frame_sz)
            sgram    = np.zeros((n_fr, n_fft_sg // 2 + 1))
            for i in range(n_fr):
                ch          = clip[i * hop_sz: i * hop_sz + frame_sz] * win_sg
                sgram[i]    = np.abs(np.fft.rfft(ch, n=n_fft_sg)) / (n_fft_sg / 2.0)
            fa2  = np.fft.rfftfreq(n_fft_sg, d=1.0 / max(rate, 1))
            ta2  = np.arange(n_fr) * hop_sz / max(rate, 1)
            z_sg = np.clip(20.0 * np.log10(sgram.T + 1e-12), -80.0, 0.0)
            fig_sg = go.Figure(go.Heatmap(
                z=z_sg, x=ta2, y=fa2,
                colorscale="Plasma", zmin=-80, zmax=0,
                colorbar=dict(
                    title="dB",
                    titlefont=dict(family="DM Sans, sans-serif", size=11, color="#4b5563"),
                    tickfont=dict(family=FONT_MONO, size=10, color=TICK_COLOR),
                    thickness=14,
                ),
            ))
            fig_sg.update_layout(**chart_layout(height=460))
            fig_sg.update_xaxes(**axis_style("Time (s)"))
            fig_sg.update_yaxes(**axis_style("Frequency (Hz)"))
            st.plotly_chart(fig_sg, use_container_width=True)
            st.markdown(
                f'<div style="font-family:Space Mono,monospace;font-size:10px;'
                f'color:#374151;padding:4px 0;letter-spacing:0.06em">'
                f'STFT · Frame {frame_sz} · Hop {hop_sz} · '
                f'FFT {n_fft_sg} · {n_fr} frames</div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-footer">
  <div>DSP PRO LAB &nbsp;·&nbsp; 8VAULTS &nbsp;·&nbsp; PROBLEM STATEMENT 18</div>
  <div class="footer-links">
    <span>NYQUIST–SHANNON: Fs ≥ 2·f_max</span>
    <span>STREAMLIT · NUMPY · PLOTLY</span>
    <span>v3.0 PROFESSIONAL</span>
  </div>
</div>
""", unsafe_allow_html=True)
