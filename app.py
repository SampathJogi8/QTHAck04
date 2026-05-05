"""
DSP Pro Lab — MIT 6.003 Style  |  Team: 8vaults
Problem Statement 18: Sampling & Aliasing Visual Demonstrator
v5 — Apple-grade UI/UX + all bugs fixed
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

# ── Global CSS — Apple-Grade Design System ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── Background — rich near-black with a subtle blue tint ── */
.stApp {
    background: #07090e;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0a0d14 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.25rem !important;
}
section[data-testid="stSidebar"] .stSlider { margin-bottom: 4px; }
section[data-testid="stSidebar"] label {
    font-size: 12px !important;
    color: #8a97aa !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
}

/* ── Header ── */
.dsp-header {
    background: linear-gradient(135deg, #0d1220 0%, #101825 50%, #0a0f1a 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 14px;
    position: relative;
    overflow: hidden;
}
.dsp-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,210,255,0.4), transparent);
}
.dsp-header-left h1 {
    color: #f0f4f8;
    margin: 0 0 5px 0;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.03em;
}
.dsp-header-left p {
    color: #5a6882;
    margin: 0;
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 0.01em;
    line-height: 1.5;
}
.dsp-header-badge {
    background: rgba(0,210,255,0.06);
    border: 1px solid rgba(0,210,255,0.18);
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 11px;
    color: #7ab8cc;
    font-family: 'DM Mono', monospace;
    white-space: nowrap;
}
.dsp-header-badge span { color: #00d2ff; font-weight: 600; }

/* ── Metric Cards ── */
.mcard {
    background: #0c1018;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
    transition: border-color 0.2s ease, transform 0.18s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
    cursor: default;
}
.mcard::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 12px;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,210,255,0.06), transparent 70%);
    opacity: 0;
    transition: opacity 0.25s;
}
.mcard:hover {
    border-color: rgba(0,210,255,0.2);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,210,255,0.08);
}
.mcard:hover::after { opacity: 1; }
.mcard .val {
    font-size: 15px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    letter-spacing: -0.02em;
    margin-top: 7px;
    display: block;
    color: #e2e8f0;
}
.mcard .lbl {
    font-size: 9.5px;
    color: #3d4d5e;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 600;
}

/* ── Status badges ── */
.badge-ok {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(52, 211, 153, 0.1);
    color: #34d399;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 600;
    border: 1px solid rgba(52, 211, 153, 0.22);
    letter-spacing: 0.03em;
}
.badge-warn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(251, 113, 60, 0.12);
    color: #fb713c;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 600;
    border: 1px solid rgba(251, 113, 60, 0.25);
    letter-spacing: 0.03em;
}

/* ── Audio Banner ── */
.audio-banner {
    background: linear-gradient(135deg, #0c1a2e 0%, #0a1017 100%);
    border: 1px solid rgba(59,130,246,0.2);
    border-left: 3px solid #3b82f6;
    border-radius: 12px;
    padding: 13px 18px;
    margin-bottom: 18px;
    font-size: 12.5px;
    color: #93c5fd;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    flex-wrap: wrap;
    line-height: 1.6;
}
.audio-banner strong { color: #bfdbfe; font-weight: 600; }
.audio-banner .warn-note { color: #fbbf24; font-size: 11.5px; opacity: 0.9; }

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 22px 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.section-header h3 {
    color: #c8d3e0;
    font-size: 13.5px;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.01em;
}
.section-num {
    background: rgba(0,210,255,0.08);
    border: 1px solid rgba(0,210,255,0.2);
    color: #00d2ff;
    width: 24px;
    height: 24px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10.5px;
    font-weight: 700;
    flex-shrink: 0;
    font-family: 'DM Mono', monospace;
}

/* ── Sidebar typography ── */
.sidebar-section-title {
    font-size: 10px;
    font-weight: 700;
    color: #3a4554;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    padding: 14px 0 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 12px;
    margin-top: 4px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0a0d14;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    gap: 0;
    padding: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #4a5568 !important;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    padding: 11px 20px;
    font-size: 12.5px;
    font-weight: 500;
    transition: color 0.15s, border-color 0.15s;
    letter-spacing: 0.01em;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #8a97aa !important;
    background: rgba(255,255,255,0.02);
}
.stTabs [aria-selected="true"] {
    color: #00d2ff !important;
    border-bottom-color: #00d2ff !important;
    background: transparent;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0c1018 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    color: #8a97aa !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
}

/* ── Alert overrides ── */
.stAlert {
    background: #0c1018 !important;
    border-radius: 10px !important;
    font-size: 12.5px !important;
}

/* ── Plotly container ── */
.stPlotlyChart { border-radius: 12px; overflow: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #07090e; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }

/* ── Info box ── */
.info-box {
    background: #0c1018;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 28px 28px;
    text-align: center;
    color: #3d4d5e;
    font-size: 13px;
    margin: 24px 0;
}
.info-box .icon { font-size: 36px; margin-bottom: 12px; display: block; }
.info-box strong { color: #8a97aa; display: block; font-size: 15px; margin-bottom: 7px; }

/* ── Theory table ── */
.stMarkdown table {
    background: #0c1018 !important;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07) !important;
    font-size: 12.5px;
}
.stMarkdown th {
    background: #111827 !important;
    color: #8a97aa !important;
    font-weight: 600 !important;
    border-color: rgba(255,255,255,0.06) !important;
}
.stMarkdown td {
    color: #c8d3e0 !important;
    border-color: rgba(255,255,255,0.05) !important;
    font-family: 'DM Mono', monospace;
    font-size: 11.5px;
}

/* ── Caption ── */
.stCaption { color: #3a4554 !important; font-size: 11px !important; }

/* ── Dividers ── */
hr { border-color: rgba(255,255,255,0.05) !important; margin: 18px 0 !important; }

/* ── Subheader ── */
h2, h3 { color: #c8d3e0 !important; }

/* ── Slider thumb ── */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] { color: #3a4554 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def next_pow2(n: int) -> int:
    """Return next power of two ≥ n (always ≥ 1)."""
    n = max(int(n), 1)
    p = 1
    while p < n:
        p <<= 1
    return p


def gen_signal(time_arr: np.ndarray, f: float, a: float, wtype: str, dur: float) -> np.ndarray:
    """Generate a synthetic waveform safely."""
    f = max(float(f), 1e-9)
    a = float(a)
    if wtype == "Sine":
        return a * np.sin(2 * np.pi * f * time_arr)
    if wtype == "Square":
        return a * np.sign(np.sin(2 * np.pi * f * time_arr))
    if wtype == "Triangle":
        return a * (2.0 / np.pi) * np.arcsin(np.clip(np.sin(2 * np.pi * f * time_arr), -1, 1))
    if wtype == "Sawtooth":
        return a * (2.0 * ((time_arr * f) % 1.0) - 1.0)
    if wtype == "Chirp":
        k = f / max(float(dur), 1e-9)
        return a * np.sin(2 * np.pi * (f * time_arr + 0.5 * k * time_arr ** 2))
    return np.zeros_like(time_arr)


def moving_avg(s: np.ndarray, w: int) -> np.ndarray:
    w = max(1, int(w))
    return np.convolve(s, np.ones(w) / w, mode="same")


def compute_fft(sig: np.ndarray, sample_rate: float):
    """Return (freqs, mags, power_db, n_fft) with safe guards."""
    sample_rate = max(float(sample_rate), 1.0)
    sig = np.asarray(sig, dtype=np.float64)
    n_sig = max(len(sig), 4)
    n = next_pow2(n_sig)
    win = np.hanning(len(sig))
    padded = np.zeros(n)
    padded[:len(sig)] = sig * win
    spectrum = np.fft.rfft(padded)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    mags = np.abs(spectrum) / max(n / 2.0, 1.0)
    max_mag = float(mags.max()) if mags.max() > 0 else 1e-12
    power_db = 20.0 * np.log10(np.maximum(mags / max_mag, 1e-12))
    return freqs, mags, power_db, n


def fft_bandwidth(freqs: np.ndarray, mags: np.ndarray, threshold: float = 0.1) -> float:
    max_mag = float(mags.max())
    if max_mag <= 0:
        return 0.0
    mask = mags > max_mag * threshold
    if int(np.count_nonzero(mask)) >= 2:
        idx = np.where(mask)[0]
        return round(float(freqs[idx[-1]]) - float(freqs[idx[0]]), 2)
    return 0.0


def load_wav(file_obj) -> tuple:
    """Load WAV file into normalised float64 mono array. Returns (audio, rate)."""
    buf = io.BytesIO(file_obj.read())
    wf = wave.open(buf, "rb")
    rate = wf.getframerate()
    nch = wf.getnchannels()
    nsmp = wf.getnframes()
    sw = wf.getsampwidth()
    raw = wf.readframes(nsmp)
    wf.close()
    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sw, np.int16)
    audio = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if nch >= 2:
        # Downmix all channels to mono
        audio = audio.reshape(-1, nch).mean(axis=1)
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio /= peak
    return audio, int(rate)


def truncate_label(s: str, n: int = 16) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


# ── Plotly theme ─────────────────────────────────────────────────────────────
COLORS = {
    "green":   "#34d399",
    "blue":    "#60a5fa",
    "purple":  "#a78bfa",   # FIX: was incorrectly set to cyan
    "orange":  "#fb923c",
    "yellow":  "#fbbf24",
    "red":     "#f87171",
    "cyan":    "#22d3ee",
    "pink":    "#f472b6",
    "indigo":  "#818cf8",
    "bg":      "#07090e",
    "surface": "#0c1018",
    "border":  "rgba(255,255,255,0.07)",
    "text":    "#8a97aa",
    "muted":   "#3d4d5e",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#090c13",
    font=dict(color=COLORS["text"], size=11, family="DM Mono, monospace"),
    legend=dict(
        bgcolor="rgba(10,13,20,0.92)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        font=dict(color="#8a97aa", size=11),
        itemsizing="constant",
    ),
    margin=dict(l=58, r=18, t=44, b=50),
)

AXIS_STYLE = dict(
    gridcolor="rgba(255,255,255,0.04)",
    gridwidth=1,
    zerolinecolor="rgba(255,255,255,0.08)",
    zerolinewidth=1,
    color=COLORS["text"],
    linecolor="rgba(255,255,255,0.06)",
    linewidth=1,
    tickfont=dict(size=10, family="DM Mono, monospace"),
    showgrid=True,
)


def apply_theme(fig, height: int = 420, title: str = "", xtitle: str = "Time (s)",
                ytitle: str = "Amplitude"):
    layout = {**CHART_LAYOUT, "height": height}
    if title:
        layout["title"] = dict(
            text=title,
            font=dict(color="#4a5568", size=11.5, family="DM Sans, sans-serif"),
            x=0, xanchor="left", pad=dict(l=2),
        )
    fig.update_layout(**layout)
    fig.update_xaxes(title_text=xtitle, title_font=dict(size=11), **AXIS_STYLE)
    fig.update_yaxes(title_text=ytitle, title_font=dict(size=11), **AXIS_STYLE)


def mcard(label: str, value: str, accent=None):
    accent_color = accent or COLORS["cyan"]
    st.markdown(
        f'<div class="mcard">'
        f'<div class="lbl">{label}</div>'
        f'<span class="val" style="color:{accent_color}">{value}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_header(num: str, title: str):
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
        help="Supports mono/stereo WAV. Stereo is downmixed to mono."
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
            except Exception as exc:
                st.error(f"Could not read WAV: {exc}")
    else:
        for k in ("audio_data", "audio_rate", "audio_name", "audio_key"):
            st.session_state.pop(k, None)

    audio_loaded = "audio_data" in st.session_state
    if audio_loaded:
        a_dur_sb = len(st.session_state["audio_data"]) / st.session_state["audio_rate"]
        st.success(
            f"✅ **{st.session_state['audio_name']}**\n\n"
            f"{st.session_state['audio_rate']} Hz · {a_dur_sb:.1f} s · All modules active."
        )

    st.markdown("---")
    st.markdown('<p class="sidebar-section-title">🎛️ Signal Generator</p>', unsafe_allow_html=True)

    if audio_loaded:
        st.info(
            "**Audio mode active** — waveform controls overridden by WAV. "
            "Remove the file to use the synthesiser.",
            icon="🎵",
        )
        signal_type = st.selectbox("Waveform *(inactive)*",
                                   ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"],
                                   disabled=True)
        freq     = st.slider("Frequency Hz *(inactive)*", 1, 50, 5, disabled=True)
        amp      = st.slider("Amplitude *(inactive)*",    0.1, 3.0, 1.0, 0.1, disabled=True)
        duration = st.slider("Duration s *(inactive)*",   1, 5, 2, disabled=True)
        st.markdown("**Sampling Rate** — active (controls resampling):")
        fs_raw   = st.slider("Sampling Rate (Hz)", 2, 200, 40,
                             help="How many samples per second to take from the audio signal.")
    else:
        signal_type = st.selectbox(
            "Waveform", ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"],
            help="Choose the waveform type to synthesise."
        )
        freq    = st.slider("Frequency (Hz)", 1, 50, 5,
                            help="Fundamental frequency of the signal in Hz.")
        fs_raw  = st.slider("Sampling Rate (Hz)", 2, 200, 40,
                            help="Set below 2× frequency to trigger aliasing (Nyquist criterion).")
        amp     = st.slider("Amplitude", 0.1, 3.0, 1.0, 0.1,
                            help="Peak amplitude of the generated signal.")
        duration = st.slider("Duration (s)", 1, 5, 2,
                             help="Length of the generated signal in seconds.")

    st.markdown("---")
    st.markdown('<p class="sidebar-section-title">🔊 Noise &amp; Filter</p>',
                unsafe_allow_html=True)

    noise_level = st.slider(
        "Noise Level", 0.0, 2.0, 0.0, 0.1,
        help="Standard deviation of additive Gaussian noise."
    )
    filter_win = st.slider(
        "Filter Window (samples)", 2, 80, 10,
        help="Moving-average FIR filter length. Larger = more smoothing, more delay."
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:10px;color:#1e2631;padding:4px 0;'>"
        "DSP Pro Lab · 8vaults · PS-18</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CORE SIGNAL COMPUTATION
# ══════════════════════════════════════════════════════════════════════════════
fs = max(int(fs_raw), 2)
N  = 4000

if "audio_data" in st.session_state:
    raw_audio    = st.session_state["audio_data"]
    audio_rate   = int(st.session_state["audio_rate"])
    # Resample audio to N points for the continuous display
    indices      = np.linspace(0, len(raw_audio) - 1, N).astype(int)
    signal       = raw_audio[indices]
    duration_eff = float(len(raw_audio)) / float(audio_rate)
    t            = np.linspace(0.0, duration_eff, N, endpoint=False)
    # Discrete samples at user-chosen Fs
    ts           = np.arange(0.0, duration_eff, 1.0 / fs)
    ts_idx       = np.clip((ts * audio_rate).astype(int), 0, len(raw_audio) - 1)
    sampled      = raw_audio[ts_idx]
    # Detect dominant frequency from a 5-second chunk
    chunk_len    = min(len(raw_audio), audio_rate * 5)
    fq, mq, _, _ = compute_fft(raw_audio[:chunk_len], float(audio_rate))
    dom_idx_audio = int(np.argmax(mq)) if len(mq) > 0 else 0
    freq_eff     = max(1, int(round(float(fq[dom_idx_audio]))))
    source_label = f"🎵 {st.session_state['audio_name']}"
else:
    t            = np.linspace(0.0, float(duration), N, endpoint=False)
    ts           = np.arange(0.0, float(duration), 1.0 / fs)
    signal       = gen_signal(t,  float(freq), float(amp), signal_type, float(duration))
    sampled      = gen_signal(ts, float(freq), float(amp), signal_type, float(duration))
    duration_eff = float(duration)
    freq_eff     = int(freq)
    source_label = f"🔧 {signal_type} {freq} Hz"

nyquist  = 2 * freq_eff
# FIX: use proper modulo-based alias calculation, clamped to [0, fs/2]
alias_f  = float(freq_eff % fs) if fs > 0 else 0.0
if alias_f > fs / 2.0:
    alias_f = fs - alias_f
is_alias = fs < nyquist

rng       = np.random.default_rng(42)
noise_vec = rng.normal(0.0, float(noise_level), N) if noise_level > 0 else np.zeros(N)
noisy     = signal + noise_vec
filtered  = moving_avg(noisy, filter_win)


# ══════════════════════════════════════════════════════════════════════════════
# AUDIO BANNER
# ══════════════════════════════════════════════════════════════════════════════
if "audio_data" in st.session_state:
    a_dur_b = len(st.session_state["audio_data"]) / st.session_state["audio_rate"]
    st.markdown(
        f'<div class="audio-banner">'
        f'<div>🎵</div>'
        f'<div>'
        f'<strong>Audio mode active</strong> — '
        f'{st.session_state["audio_name"]} '
        f'({st.session_state["audio_rate"]} Hz · {a_dur_b:.1f} s)'
        f' &nbsp;·&nbsp; Dominant freq: <strong>{freq_eff} Hz</strong>'
        f' &nbsp;·&nbsp; Nyquist min: <strong>{nyquist} Hz</strong><br>'
        f'<span class="warn-note">⚠ Waveform / Frequency / Amplitude / Duration sliders overridden. '
        f'Only Sampling Rate, Noise and Filter controls are active.</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# STATUS METRIC BAR
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:  mcard("Source",        truncate_label(source_label, 16), COLORS["blue"])
with c2:  mcard("Signal Freq",   f"{freq_eff} Hz",  COLORS["cyan"])
with c3:  mcard("Sampling Rate", f"{fs} Hz",         COLORS["purple"])
with c4:  mcard("Nyquist Min",   f"{nyquist} Hz",    COLORS["indigo"])
with c5:  mcard("Alias Freq",    f"{alias_f:.1f} Hz", COLORS["orange"])
with c6:
    badge = ('<span class="badge-warn">⚠ Aliasing</span>' if is_alias
             else '<span class="badge-ok">✓ Clean</span>')
    st.markdown(
        f'<div class="mcard"><div class="lbl">Status</div>'
        f'<div style="margin-top:8px">{badge}</div></div>',
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
                x=t, y=noisy, mode="lines",
                name=f"x(t) + Noise (σ={noise_level:.1f})",
                line=dict(color=COLORS["red"], width=1.0),
                opacity=0.55,
            ))
        apply_theme(fig, height=400, title=f"{source_label}  ·  A = {amp:.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("02", "Sampled Signal")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=t, y=signal, mode="lines", name="Continuous (ref)",
            line=dict(color=COLORS["green"], width=1.2, dash="dot"),
            opacity=0.3,
        ))
        # Build stem lines for sampled points
        stem_x, stem_y = [], []
        for xi, yi in zip(ts, sampled):
            stem_x += [float(xi), float(xi), None]
            stem_y += [0.0, float(yi), None]
        fig2.add_trace(go.Scatter(
            x=stem_x, y=stem_y, mode="lines", showlegend=False,
            line=dict(color=COLORS["orange"], width=1.0), opacity=0.4,
        ))
        fig2.add_trace(go.Scatter(
            x=ts, y=sampled, mode="markers",
            name=f"Samples · Fs = {fs} Hz",
            marker=dict(color=COLORS["orange"], size=7,
                        line=dict(color="#fff", width=0.5)),
        ))
        apply_theme(fig2, height=400,
                    title=f"Fs = {fs} Hz · {len(ts)} samples · T = {1/fs*1000:.1f} ms")
        st.plotly_chart(fig2, use_container_width=True)

    section_header("03", "Aliasing Visualisation — Time Domain")
    # FIX: use the currently selected signal_type (not always "Sine") for alias signal
    alias_sig = gen_signal(t, float(alias_f), float(amp), signal_type, duration_eff)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=t, y=signal, mode="lines", name=f"Original  {freq_eff} Hz",
        line=dict(color=COLORS["green"], width=2.0),
    ))
    fig3.add_trace(go.Scatter(
        x=ts, y=sampled, mode="markers", name=f"Samples · Fs = {fs} Hz",
        marker=dict(color=COLORS["yellow"], size=6),
    ))
    if is_alias and alias_f > 0:
        fig3.add_trace(go.Scatter(
            x=t, y=alias_sig, mode="lines", name=f"Alias  {alias_f:.2f} Hz",
            line=dict(color=COLORS["orange"], width=2.0, dash="dash"),
        ))
    note = (f"⚠ ALIASING  Fs={fs} < {nyquist}" if is_alias
            else f"✓ Clean  Fs={fs} ≥ {nyquist}")
    apply_theme(
        fig3, height=420,
        title=f"alias = {alias_f:.2f} Hz   [{note}]",
    )
    st.plotly_chart(fig3, use_container_width=True)

    if is_alias:
        st.error(
            f"**Aliasing detected!**  {freq_eff} Hz requires Fs ≥ {nyquist} Hz "
            f"(Nyquist criterion). At Fs = {fs} Hz, the signal appears as **{alias_f:.2f} Hz**.",
            icon="⚠️",
        )
    else:
        st.success(f"**No aliasing.**  Fs = {fs} Hz ≥ Nyquist = {nyquist} Hz ✓", icon="✅")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FFT SPECTRUM
# ══════════════════════════════════════════════════════════════════════════════
with tab_fft:

    freqs_hz, mags, power_db, n_fft = compute_fft(noisy, float(fs))
    max_mag   = float(mags.max()) if mags.size > 0 else 1e-12
    dom_idx   = int(np.argmax(mags)) if len(mags) > 0 else 0
    dom_freq  = round(float(freqs_hz[dom_idx]), 2) if len(freqs_hz) > 0 else 0.0
    bw_hz     = fft_bandwidth(freqs_hz, mags)
    # FIX: safe SNR with float cast and cap at 99.9 dB
    raw_snr   = (20.0 * np.log10(float(amp) / max(float(noise_level), 1e-9))
                 if noise_level > 0 else 99.0)
    snr_db    = float(np.clip(raw_snr, -99.9, 99.9))
    harm_rms  = (float(np.sqrt(np.sum(mags[dom_idx + 1:] ** 2)))
                 if dom_idx + 1 < len(mags) else 0.0)
    thd_pct   = round(harm_rms / max(float(mags[dom_idx]), 1e-9) * 100.0, 1)

    m1, m2, m3, m4 = st.columns(4)
    with m1: mcard("Dominant Freq",      f"{dom_freq} Hz",       COLORS["cyan"])
    with m2: mcard("Bandwidth (−10 dB)", f"{bw_hz} Hz",          COLORS["blue"])
    with m3: mcard("SNR",                f"{snr_db:.1f} dB",     COLORS["green"])
    with m4: mcard("THD",                f"{thd_pct} %",         COLORS["orange"])

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    bar_colors = [
        f"hsl({int(200 + i / max(len(freqs_hz) - 1, 1) * 100)},65%,52%)"
        for i in range(len(freqs_hz))
    ]

    # FIX: use separate figures for magnitude and power spectrum
    # (add_vline with row= is not reliably supported on subplots in all Plotly versions)
    fig_mag = go.Figure()
    fig_mag.add_trace(go.Bar(
        x=freqs_hz, y=mags, name="Magnitude",
        marker=dict(color=bar_colors, line=dict(width=0)),
        showlegend=False,
    ))
    if 0 < dom_freq <= float(freqs_hz[-1]) if len(freqs_hz) > 0 else False:
        fig_mag.add_vline(
            x=dom_freq, line_dash="dash", line_color=COLORS["orange"],
            annotation_text=f"f = {dom_freq} Hz",
            annotation_font=dict(color=COLORS["orange"], size=11),
            annotation_position="top right",
        )
    if is_alias and 0 < alias_f <= (float(freqs_hz[-1]) if len(freqs_hz) > 0 else 0):
        fig_mag.add_vline(
            x=alias_f, line_dash="dot", line_color=COLORS["yellow"],
            annotation_text=f"alias {alias_f:.1f} Hz",
            annotation_font=dict(color=COLORS["yellow"], size=11),
            annotation_position="top left",
        )
    apply_theme(fig_mag, height=340, title="Magnitude Spectrum",
                xtitle="Frequency (Hz)", ytitle="Magnitude")
    st.plotly_chart(fig_mag, use_container_width=True)

    fig_pwr = go.Figure()
    fig_pwr.add_trace(go.Scatter(
        x=freqs_hz, y=power_db, mode="lines",
        line=dict(color=COLORS["blue"], width=1.6),
        fill="tozeroy", fillcolor="rgba(96,165,250,0.07)",
        showlegend=False,
    ))
    if 0 < dom_freq <= float(freqs_hz[-1]) if len(freqs_hz) > 0 else False:
        fig_pwr.add_vline(
            x=dom_freq, line_dash="dash", line_color=COLORS["orange"],
            annotation_text=f"f = {dom_freq} Hz",
            annotation_font=dict(color=COLORS["orange"], size=11),
            annotation_position="top right",
        )
    apply_theme(fig_pwr, height=300, title="Power Spectrum (dB)",
                xtitle="Frequency (Hz)", ytitle="dB")
    st.plotly_chart(fig_pwr, use_container_width=True)

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
    # FIX: ensure lag doesn't exceed signal length
    lag = min(lag, len(noisy) - 1)
    x_ph = noisy[:-lag]
    y_ph = noisy[lag:]

    max_lag  = min(400, len(signal) // 2)
    mean_s   = float(signal.mean())
    var_s    = float(np.var(signal))
    lags_arr = np.arange(max(max_lag, 1))
    if var_s > 1e-12:
        auto = np.array([
            float(np.mean((signal[:N - ll] - mean_s) * (signal[ll:] - mean_s))) / var_s
            for ll in lags_arr
        ])
    else:
        auto = np.zeros(len(lags_arr))

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        section_header("01", "Phase Portrait")
        fig_pp = go.Figure()
        fig_pp.add_trace(go.Scatter(
            x=x_ph, y=y_ph, mode="lines",
            line=dict(color=COLORS["purple"], width=0.9),
            name=f"x[n] vs x[n−{lag}]",
        ))
        apply_theme(fig_pp, height=500,
                    title=f"Phase portrait — lag = {lag} samples",
                    xtitle=f"x[n−{lag}]", ytitle="x[n]")
        st.plotly_chart(fig_pp, use_container_width=True)

    with col2:
        section_header("02", "Autocorrelation R[k]")
        fig_ac = go.Figure()
        fig_ac.add_trace(go.Scatter(
            x=lags_arr, y=auto, mode="lines",
            line=dict(color=COLORS["pink"], width=1.6),
            fill="tozeroy", fillcolor="rgba(244,114,182,0.07)",
            name="R[k]",
        ))
        fig_ac.add_hline(y=0, line_dash="dot",
                         line_color="rgba(255,255,255,0.1)")
        apply_theme(fig_ac, height=500,
                    title="Normalised autocorrelation",
                    xtitle="Lag (samples)", ytitle="R[k]")
        st.plotly_chart(fig_ac, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FILTER LAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_filter:

    rms_orig = float(np.sqrt(np.mean(signal   ** 2)))
    rms_n    = float(np.sqrt(np.mean(noisy    ** 2)))
    rms_f    = float(np.sqrt(np.mean(filtered ** 2)))
    # FIX: guard against zero division in SNR gain
    snr_g    = round(20.0 * np.log10(max(rms_f, 1e-12) / max(rms_n, 1e-12)), 2)
    cutoff   = round(float(fs) / (2.0 * max(int(filter_win), 1)), 2)

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
        x=t, y=signal, mode="lines",
        name="Original (clean)",
        line=dict(color=COLORS["green"], width=1.4, dash="dot"),
        opacity=0.55,
    ))
    if noise_level > 0:
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
    cmp_title = (
        f"Original vs Filtered (M = {filter_win})  ·  No noise applied"
        if noise_level == 0
        else f"Original vs Noisy (σ={noise_level:.1f}) vs Filtered (M={filter_win})"
    )
    apply_theme(fig_cmp, height=380, title=cmp_title)
    if noise_level == 0:
        st.info(
            "**Noise level is 0** — set the Noise Level slider above 0 to see the "
            "Noisy vs Filtered comparison. Currently showing Original vs Filtered only.",
            icon="ℹ️",
        )
    st.plotly_chart(fig_cmp, use_container_width=True)

    section_header("05", "Filter Frequency Response |H(f)|")
    omega = np.linspace(0.0, np.pi, 1024)
    eps   = 1e-9
    M_f   = float(max(int(filter_win), 1))
    # FIX: safer computation — avoid division by exactly zero
    H = np.abs(np.sin(M_f * omega / 2 + eps) / (M_f * np.sin(omega / 2 + eps) + eps))
    H = np.clip(H, 0.0, 1.0)
    f_ax  = omega / np.pi * (fs / 2.0)
    fig_hr = go.Figure()
    fig_hr.add_trace(go.Scatter(
        x=f_ax, y=H, mode="lines", name="|H(f)|",
        line=dict(color=COLORS["orange"], width=2.2),
        fill="tozeroy", fillcolor="rgba(251,146,60,0.07)",
    ))
    fig_hr.add_hline(
        y=0.707, line_dash="dash",
        line_color="rgba(255,255,255,0.2)",
        annotation_text="−3 dB (0.707)",
        annotation_font=dict(color="#8a97aa", size=11),
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
    # FIX: hanning window must match frame_len exactly
    win_h     = np.hanning(frame_len)

    wfall, t_labels = [], []
    for i in range(n_frames):
        start = i * hop
        end   = start + frame_len
        if end > N:
            break
        padded = np.zeros(n_fft_w)
        chunk  = noisy[start:end]
        padded[:len(chunk)] = chunk * win_h[:len(chunk)]
        wfall.append(np.abs(np.fft.rfft(padded)) / max(n_fft_w / 2.0, 1.0))
        t_labels.append(round(start / N * duration_eff, 3))

    if not wfall:
        st.warning("Signal too short for waterfall. Increase Duration.")
    else:
        wfall_arr = np.array(wfall)
        f_ax_w    = np.fft.rfftfreq(n_fft_w, d=1.0 / float(fs))
        z_db      = np.clip(20.0 * np.log10(wfall_arr + 1e-12), -80.0, 0.0)

        fig_wf = go.Figure(go.Heatmap(
            z=z_db.T, x=t_labels, y=f_ax_w,
            colorscale="Plasma",
            zmin=-80, zmax=0,
            colorbar=dict(
                title=dict(text="dB", font=dict(color="#8a97aa", size=12)),
                ticksuffix=" dB",
                tickfont=dict(color="#8a97aa", size=10, family="DM Mono"),
            ),
        ))
        fig_wf.update_layout(
            **{**CHART_LAYOUT, "height": 580},
            xaxis=dict(**AXIS_STYLE, title_text="Time (s)"),
            yaxis=dict(**AXIS_STYLE, title_text="Frequency (Hz)"),
        )
        st.plotly_chart(fig_wf, use_container_width=True)

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

        # FIX: np.gcd requires integers; freq_eff is already int, ensure freq2 is int
        fe_int  = int(max(freq_eff, 1))
        f2_int  = int(max(freq2, 1))
        gcd_v   = int(np.gcd(fe_int, f2_int))
        ratio   = f"{fe_int // gcd_v} : {f2_int // gcd_v}"

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
        # FIX: safe LCM with integer types and capped cycles to prevent memory issues
        lcm_f  = (fe_int * f2_int) // max(gcd_v, 1)
        cycles = min(lcm_f * 6, 1000)   # cap to avoid enormous arrays
        t_liss = np.linspace(
            0.0,
            float(cycles) / max(float(min(fe_int, f2_int)), 1.0),
            12000,
        )
        x_l = float(amp) * np.sin(2 * np.pi * float(fe_int) * t_liss)
        y_l = float(amp) * np.sin(2 * np.pi * float(f2_int) * t_liss + np.radians(phase))

        fig_liss = go.Figure()
        fig_liss.add_trace(go.Scatter(
            x=x_l, y=y_l, mode="lines",
            line=dict(color=COLORS["cyan"], width=1.5),
            name=f"{fe_int} Hz × {f2_int} Hz  φ = {phase}°",
        ))
        apply_theme(
            fig_liss, height=560,
            title=f"Lissajous  {fe_int} × {f2_int} Hz  ·  ratio {ratio}  ·  φ = {phase}°",
            xtitle="X  (A · sin 2πf₁t)",
            ytitle="Y  (A · sin(2πf₂t + φ))",
        )
        st.plotly_chart(fig_liss, use_container_width=True)


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
        rate  = int(st.session_state["audio_rate"])
        a_dur = float(len(audio)) / float(rate)

        m1, m2, m3, m4 = st.columns(4)
        with m1: mcard("Sample Rate", f"{rate} Hz",      COLORS["blue"])
        with m2: mcard("Channels",    "1 (mono)",         COLORS["cyan"])
        with m3: mcard("Duration",    f"{a_dur:.2f} s",   COLORS["purple"])
        with m4: mcard("Samples",     f"{len(audio):,}",  COLORS["indigo"])

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Use up to 10 seconds of audio
        clip   = audio[:min(len(audio), rate * 10)]
        t_clip = np.linspace(0.0, float(len(clip)) / float(rate), len(clip), endpoint=False)

        section_header("01", "Waveform")
        ds = max(1, len(clip) // 4000)
        fig_wav = go.Figure()
        fig_wav.add_trace(go.Scatter(
            x=t_clip[::ds], y=clip[::ds], mode="lines",
            line=dict(color=COLORS["green"], width=0.9), name="Waveform",
        ))
        apply_theme(fig_wav, height=320, xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig_wav, use_container_width=True)

        section_header("02", "Frequency Spectrum")
        clip_fft = clip[:min(len(clip), rate * 2)]
        n_fft_a  = next_pow2(max(len(clip_fft), 4))
        # FIX: hanning window must match clip_fft length, not n_fft_a
        win_a    = np.hanning(len(clip_fft))
        padded_a = np.zeros(n_fft_a)
        padded_a[:len(clip_fft)] = clip_fft * win_a
        spec = np.abs(np.fft.rfft(padded_a)) / max(n_fft_a / 2.0, 1.0)
        fa   = np.fft.rfftfreq(n_fft_a, d=1.0 / float(rate))

        fig_spec = go.Figure()
        fig_spec.add_trace(go.Scatter(
            x=fa, y=spec, mode="lines",
            line=dict(color=COLORS["blue"], width=1.1),
            fill="tozeroy", fillcolor="rgba(96,165,250,0.07)",
            name="Magnitude",
        ))
        apply_theme(fig_spec, height=320, xtitle="Frequency (Hz)", ytitle="Magnitude")
        st.plotly_chart(fig_spec, use_container_width=True)

        section_header("03", "Spectrogram (STFT)")
        frame_sz = min(2048, max(64, len(clip) // 200))
        hop_sz   = max(1, frame_sz // 4)
        n_fr     = (len(clip) - frame_sz) // hop_sz

        if n_fr < 2:
            st.info("Audio too short for spectrogram (need > 0.5 s).", icon="ℹ️")
        else:
            n_fft_sg = next_pow2(frame_sz)
            # FIX: window must match frame_sz
            win_sg   = np.hanning(frame_sz)
            sgram    = np.zeros((n_fr, n_fft_sg // 2 + 1))
            for i in range(n_fr):
                ch = clip[i * hop_sz: i * hop_sz + frame_sz]
                # Guard: chunk might be shorter than frame_sz at the end
                if len(ch) < frame_sz:
                    break
                sgram[i] = (np.abs(np.fft.rfft(ch * win_sg, n=n_fft_sg))
                            / max(n_fft_sg / 2.0, 1.0))

            fa2  = np.fft.rfftfreq(n_fft_sg, d=1.0 / float(rate))
            ta2  = np.arange(n_fr) * hop_sz / float(rate)
            z_sg = np.clip(20.0 * np.log10(sgram.T + 1e-12), -80.0, 0.0)

            fig_sg = go.Figure(go.Heatmap(
                z=z_sg, x=ta2, y=fa2,
                colorscale="Plasma",
                zmin=-80, zmax=0,
                colorbar=dict(
                    title=dict(text="dB", font=dict(color="#8a97aa", size=12)),
                    tickfont=dict(color="#8a97aa", size=10, family="DM Mono"),
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
    "<span style='font-size:10.5px;color:#1e2631'>"
    "DSP Pro Lab &nbsp;·&nbsp; Team <strong style='color:#22d3ee'>8vaults</strong>"
    " &nbsp;·&nbsp; Problem Statement 18 — Sampling &amp; Aliasing"
    " &nbsp;·&nbsp; Nyquist–Shannon Theorem"
    "</span>"
    "<span style='font-size:10.5px;color:#1a2130'>"
    "Streamlit · NumPy · Plotly"
    "</span>"
    "</div>",
    unsafe_allow_html=True,
)
