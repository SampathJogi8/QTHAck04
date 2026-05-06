"""
DSP Pro Lab — MIT 6.003 Style  |  Team: 8vaults
Problem Statement 18: Sampling & Aliasing Visual Demonstrator
v7 — FIXED: proper light/dark mode for ALL plots and UI elements
"""

import io
import wave

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="DSP Pro Lab — 8vaults",
    layout="wide",
    page_icon="🔬",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# THEME — sidebar toggle (Streamlit cannot read OS theme in Python)
# ══════════════════════════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# We read the toggle AFTER the sidebar block below, but we initialise it here
# so the rest of the script can reference it immediately.
# The actual widget is rendered inside the sidebar section.


def _theme():
    """Return a dict of all colour tokens based on current dark_mode state."""
    dark = st.session_state["dark_mode"]
    if dark:
        return dict(
            dark=True,
            # Plot backgrounds
            PBG="#111827",
            PPBG="#0d1220",
            # Text / tick
            PTXT="#e2e8f0",
            PTICK="#94a3b8",
            # Grid / zero / lines / legend
            PGRID="rgba(148,163,184,0.10)",
            PZERO="rgba(99,179,237,0.30)",
            PLINE="rgba(148,163,184,0.18)",
            PLEG="rgba(17,24,39,0.92)",
            # Colourscales
            HEAT="Plasma",
            SURF="Plasma",
            # Fill alphas (stronger in dark)
            FA=0.12,
        )
    else:
        return dict(
            dark=False,
            PBG="#ffffff",
            PPBG="#f8fafc",
            PTXT="#1e3a5f",
            PTICK="#64748b",
            PGRID="rgba(100,116,139,0.12)",
            PZERO="rgba(37,99,235,0.20)",
            PLINE="rgba(100,116,139,0.22)",
            PLEG="rgba(255,255,255,0.94)",
            HEAT="Blues",
            SURF="Viridis",
            FA=0.07,
        )


# Signal palette — same in both modes (vibrant, accessible)
_C = {
    "cont":  "#3b82f6",
    "samp":  "#f97316",
    "alias": "#ef4444",
    "noisy": "#f87171",
    "filt":  "#06b6d4",
    "phase": "#818cf8",
    "auto":  "#a78bfa",
    "power": "#0ea5e9",
}

# ══════════════════════════════════════════════════════════════════════════════
# CSS — adaptive light / dark via CSS custom properties
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=DM+Sans:wght@300;400;600;800&display=swap');

/* ── Tokens ─────────────────────────────────────────────── */
:root {
  --bg-page:    #f2f4f8;
  --bg-card:    #ffffff;
  --bg-sidebar: #f8faff;
  --bg-input:   #f0f3fa;
  --txt-p:      #0f172a;
  --txt-s:      #475569;
  --txt-m:      #94a3b8;
  --accent:     #2563eb;
  --accent-sub: rgba(37,99,235,0.08);
  --bdr:        rgba(148,163,184,0.25);
  --bdr-s:      rgba(148,163,184,0.45);
  --sh-sm:      0 1px 4px rgba(0,0,0,0.06),0 0 0 1px rgba(0,0,0,0.04);
  --sh-md:      0 4px 24px rgba(37,99,235,0.10),0 1px 4px rgba(0,0,0,0.06);
  --sh-lg:      0 16px 48px rgba(37,99,235,0.14),0 4px 12px rgba(0,0,0,0.08);
  --ok-bg:#dcfce7; --ok-txt:#166534; --ok-bdr:#86efac;
  --wn-bg:#fef2f2; --wn-txt:#991b1b; --wn-bdr:#fca5a5;
  --ease:cubic-bezier(0.25,0.46,0.45,0.94);
  --spring:cubic-bezier(0.34,1.56,0.64,1);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg-page:    #0a0e1a;
    --bg-card:    #111827;
    --bg-sidebar: #0d1220;
    --bg-input:   #1e2d45;
    --txt-p:      #f1f5f9;
    --txt-s:      #94a3b8;
    --txt-m:      #64748b;
    --accent-sub: rgba(37,99,235,0.14);
    --bdr:        rgba(148,163,184,0.12);
    --bdr-s:      rgba(148,163,184,0.22);
    --sh-sm:      0 1px 4px rgba(0,0,0,0.4);
    --sh-md:      0 4px 24px rgba(37,99,235,0.20);
    --sh-lg:      0 16px 48px rgba(37,99,235,0.24),0 4px 12px rgba(0,0,0,0.4);
    --ok-bg:rgba(16,185,129,0.12); --ok-txt:#34d399; --ok-bdr:rgba(16,185,129,0.3);
    --wn-bg:rgba(239,68,68,0.10);  --wn-txt:#f87171; --wn-bdr:rgba(239,68,68,0.25);
  }
}

/* ── Global reset ───────────────────────────────────────── */
html,body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] * {
  font-family:'DM Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  -webkit-font-smoothing:antialiased;
  color:var(--txt-p);
  box-sizing:border-box;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"]   { background:var(--bg-page) !important; }

/* ── Sidebar ────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebar"]>div     { background:var(--bg-sidebar) !important; border-right:1px solid var(--bdr) !important; }
[data-testid="stSidebar"] *       { color:var(--txt-p) !important; }

/* ── Text ───────────────────────────────────────────────── */
.stMarkdown,.stMarkdown p,.stMarkdown li,.stMarkdown td,
.stMarkdown th,p,span,li,td,th,
.element-container p              { color:var(--txt-p) !important; }
h1,h2,h3,h4,h5,h6,
[data-testid="stHeading"]         { color:var(--txt-p) !important; }

/* ── Widget labels ──────────────────────────────────────── */
label,.stSlider label,.stSelectbox label,
.stFileUploader label,
[data-testid="stSidebar"] label   { color:var(--txt-p) !important; }
[data-testid="stSlider"] *,[data-testid="stSlider"] span { color:var(--txt-p) !important; }
[data-testid="stSelectbox"] *,div[data-baseweb="select"] * { color:var(--txt-p) !important; }

/* ── Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab"]      { color:var(--txt-s) !important; font-size:12px; font-weight:600; letter-spacing:.03em; padding:8px 14px; transition:color 150ms var(--ease); }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color:#2563eb !important; }
.stTabs [data-baseweb="tab-list"] { background:var(--bg-card) !important; border-radius:10px; padding:4px; border:1px solid var(--bdr); }

/* ── Expander ───────────────────────────────────────────── */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * { color:var(--txt-p) !important; }
[data-testid="stExpander"]>div    { background:var(--bg-card) !important; }

/* ── Alerts ─────────────────────────────────────────────── */
[data-testid="stAlert"],[data-testid="stAlert"] *,
.stInfo,.stSuccess,.stError,.stWarning { color:var(--txt-p) !important; }

/* ── Captions ───────────────────────────────────────────── */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
small,.stCaption                  { color:var(--txt-m) !important; }

/* ── File uploader ──────────────────────────────────────── */
[data-testid="stFileUploader"] *,
[data-testid="stFileUploaderDropzone"] * { color:var(--txt-p) !important; }

/* ── Tables / Code ──────────────────────────────────────── */
table,thead,tbody,tr,td,th        { color:var(--txt-p) !important; }
code,pre,.stCode                  { color:var(--txt-p) !important; background:var(--bg-input) !important; font-family:'IBM Plex Mono',monospace; }

/* ── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar               { width:6px; height:6px; }
::-webkit-scrollbar-track         { background:transparent; }
::-webkit-scrollbar-thumb         { background:var(--bdr-s); border-radius:999px; }
hr                                { border-color:var(--bdr) !important; }

/* ════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ════════════════════════════════════════════════════════ */

/* ── Hero header ────────────────────────────────────────── */
.dsp-header {
  position:relative; overflow:hidden;
  background:linear-gradient(135deg,#0f2557 0%,#1d4ed8 55%,#312e81 100%);
  padding:28px 36px; border-radius:16px; margin-bottom:24px;
  box-shadow:var(--sh-lg);
  animation:heroIn .7s var(--ease) both;
}
@keyframes heroIn { from{opacity:0;transform:translateY(-14px) scale(.98)} to{opacity:1;transform:translateY(0) scale(1)} }
.dsp-header::before {
  content:''; position:absolute; inset:0; pointer-events:none;
  background:radial-gradient(ellipse 60% 80% at 10% 50%,rgba(99,179,237,.18) 0%,transparent 60%),
             radial-gradient(ellipse 40% 60% at 80% 20%,rgba(167,139,250,.18) 0%,transparent 60%);
}
.dsp-header::after {
  content:''; position:absolute; inset:0; pointer-events:none;
  background-image:radial-gradient(rgba(255,255,255,.06) 1px,transparent 1px);
  background-size:28px 28px;
}
.dsp-header-inner { position:relative; z-index:1; }
.dsp-header h1    { margin:0 0 5px; font-size:27px; font-weight:800; letter-spacing:-.02em; color:#fff !important; }
.dsp-header p     { margin:0; opacity:.80; font-size:13px; color:#fff !important; }
.dsp-header .pill {
  display:inline-block; margin-top:12px;
  background:rgba(255,255,255,.12); backdrop-filter:blur(8px);
  border:1px solid rgba(255,255,255,.20); border-radius:999px;
  padding:3px 14px; font-size:11px; font-weight:600; color:#dbeafe !important; letter-spacing:.06em;
}

/* ── Metric card ────────────────────────────────────────── */
.mcard {
  background:var(--bg-card); border:1px solid var(--bdr); border-radius:12px;
  padding:14px 16px; text-align:center; margin-bottom:10px;
  box-shadow:var(--sh-sm);
  animation:cardIn .5s var(--ease) both;
  transition:border-color 280ms var(--ease),box-shadow 280ms var(--ease),transform 280ms var(--spring);
  cursor:default;
}
.mcard:hover { border-color:#2563eb; box-shadow:0 0 0 3px var(--accent-sub),var(--sh-md); transform:translateY(-2px); }
@keyframes cardIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.mcard .val  { font-size:15px; font-weight:700; color:var(--txt-p) !important; font-family:'IBM Plex Mono',monospace; letter-spacing:-.01em; }
.mcard .lbl  { font-size:9px; color:var(--txt-m) !important; text-transform:uppercase; letter-spacing:.10em; margin-bottom:5px; font-weight:600; }

/* ── Status badges ──────────────────────────────────────── */
.badge-ok   { background:var(--ok-bg); color:var(--ok-txt) !important; padding:3px 14px; border-radius:6px; font-size:12px; font-weight:700; border:1px solid var(--ok-bdr); animation:pulseOk 3s ease infinite; }
.badge-warn { background:var(--wn-bg); color:var(--wn-txt) !important; padding:3px 14px; border-radius:6px; font-size:12px; font-weight:700; border:1px solid var(--wn-bdr); animation:pulseWarn 1.4s ease infinite; }
@keyframes pulseOk   { 0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,0)} 50%{box-shadow:0 0 0 4px rgba(16,185,129,.12)} }
@keyframes pulseWarn { 0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}  50%{box-shadow:0 0 0 5px rgba(239,68,68,.14)} }

/* ── Audio banner ───────────────────────────────────────── */
.audio-banner {
  background:linear-gradient(90deg,var(--accent-sub),transparent);
  border:1px solid rgba(37,99,235,.22); border-left:3px solid #2563eb;
  border-radius:10px; padding:11px 18px; margin-bottom:16px; font-size:13px;
  color:var(--txt-p) !important;
  animation:slideIn .4s var(--ease) both;
}
@keyframes slideIn { from{opacity:0;transform:translateX(-10px)} to{opacity:1;transform:translateX(0)} }
.audio-banner b { color:#2563eb !important; }

/* ── Sidebar section headers ────────────────────────────── */
[data-testid="stSidebar"] h3 {
  font-size:11px !important; font-weight:700 !important;
  letter-spacing:.10em !important; text-transform:uppercase !important;
  color:var(--txt-m) !important; margin-top:20px !important;
}

/* ── Dark mode toggle row ───────────────────────────────── */
.theme-row {
  display:flex; align-items:center; gap:10px;
  padding:8px 0; font-size:12px; font-weight:600;
  color:var(--txt-s) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dsp-header">
  <div class="dsp-header-inner">
    <h1>🔬 DSP Pro Lab · 8vaults</h1>
    <p>Interactive Digital Signal Processing Playground</p>
    <p>Problem Statement 18 — Sampling &amp; Aliasing Visual Demonstrator</p>
    <span class="pill">MIT 6.003 · Nyquist–Shannon · Streamlit + Plotly</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
N_POINTS = 4_000
FFT_NORM_FLOOR = 1e-12
DB_FLOOR = -80.0

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Theme toggle (FIRST so it affects everything below) ──────────────────
    st.markdown("### 🎨 Display")
    st.session_state["dark_mode"] = st.toggle(
        "Dark mode plots",
        value=st.session_state["dark_mode"],
        help="Toggles Plotly chart backgrounds between light and dark. "
             "Match this to your system theme for best readability.",
    )

    st.markdown("---")
    st.markdown("### 🎛️ Signal Generator")
    signal_type = st.selectbox(
        "Waveform", ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"])
    freq = st.slider("Frequency (Hz)",      1,  50,  5)
    fs_raw = st.slider("Sampling Rate (Hz)",  2, 200, 40)
    amp = st.slider("Amplitude",         0.1, 3.0, 1.0, 0.1)
    duration = st.slider("Duration (s)",        1,   5,   2)

    st.markdown("---")
    st.markdown("### 🔊 Noise & Filter")
    noise_level = st.slider("Noise Level",       0.0, 2.0, 0.0, 0.1)
    filter_win = st.slider("Filter Window (n)", 2,    80,  10)

    st.markdown("---")
    st.markdown("### 📂 Audio Input")
    st.caption("Upload a WAV — replaces synthesised signal in all modules.")
    uploaded_file = st.file_uploader(
        "WAV file", type=["wav"], label_visibility="collapsed")

    if uploaded_file is not None:
        fkey = uploaded_file.name + str(uploaded_file.size)
        if st.session_state.get("_akey") != fkey:
            try:
                def _load_wav(file_obj):
                    buf = io.BytesIO(file_obj.read())
                    with wave.open(buf, "rb") as wf:
                        rate = wf.getframerate()
                        nch = wf.getnchannels()
                        nsmp = wf.getnframes()
                        sw = wf.getsampwidth()
                        raw = wf.readframes(nsmp)
                    dtype = {1: np.int8, 2: np.int16,
                             4: np.int32}.get(sw, np.int16)
                    audio = np.frombuffer(raw, dtype=dtype).astype(np.float64)
                    if nch >= 2:
                        audio = audio[::nch]
                    peak = float(np.max(np.abs(audio)))
                    if peak > 0:
                        audio /= peak
                    return audio, rate
                _ad, _ar = _load_wav(uploaded_file)
                st.session_state.update({"_adata": _ad, "_arate": _ar,
                                         "_aname": uploaded_file.name, "_akey": fkey})
            except Exception as e:
                st.error(f"Could not read WAV: {e}")
    else:
        for k in ("_adata", "_arate", "_aname", "_akey"):
            st.session_state.pop(k, None)

    if "_adata" in st.session_state:
        _ad, _ar = st.session_state["_adata"], st.session_state["_arate"]
        st.success(f"✅ **{st.session_state['_aname']}**\n\n"
                   f"{_ar} Hz · {len(_ad)/_ar:.1f} s · All modules active.")

    st.markdown("---")
    st.caption("DSP Pro Lab · 8vaults · PS-18")

# ══════════════════════════════════════════════════════════════════════════════
# RESOLVE THEME  (after sidebar renders — toggle value is now committed)
# ══════════════════════════════════════════════════════════════════════════════
T = _theme()   # dict with all colour tokens for current mode

# ══════════════════════════════════════════════════════════════════════════════
# PURE HELPERS
# ══════════════════════════════════════════════════════════════════════════════


def next_pow2(n: int) -> int:
    p = 1
    while p < n:
        p <<= 1
    return p


def gen_signal(t: np.ndarray, f: float, a: float, wtype: str, dur: float) -> np.ndarray:
    if f <= 0:
        return np.zeros_like(t)
    w = 2.0 * np.pi * f * t
    if wtype == "Sine":
        return a * np.sin(w)
    if wtype == "Square":
        return a * np.sign(np.sin(w))
    if wtype == "Triangle":
        return a * (2.0 / np.pi) * np.arcsin(np.clip(np.sin(w), -1, 1))
    if wtype == "Sawtooth":
        return a * (2.0 * ((t * f) % 1.0) - 1.0)
    if wtype == "Chirp":
        k = f / max(dur, 1e-9)
        return a * np.sin(2.0 * np.pi * (f * t + 0.5 * k * t ** 2))
    return np.zeros_like(t)


def moving_avg(s: np.ndarray, w: int) -> np.ndarray:
    w = max(1, int(w))
    return np.convolve(s, np.ones(w) / w, mode="same")


def compute_fft(sig: np.ndarray, sample_rate: float):
    n = next_pow2(max(len(sig), 4))
    win = np.hanning(len(sig))
    pad = np.zeros(n)
    pad[:len(sig)] = sig * win
    spec = np.fft.rfft(pad)
    freqs = np.fft.rfftfreq(n, d=1.0 / max(sample_rate, 1.0))
    mags = np.abs(spec) / (n / 2.0)
    mx = float(mags.max()) if mags.max() > 0 else FFT_NORM_FLOOR
    pdb = 20.0 * np.log10(np.maximum(mags / mx, FFT_NORM_FLOOR))
    return freqs, mags, pdb, n


def fft_bandwidth(freqs: np.ndarray, mags: np.ndarray, thr: float = 0.1) -> float:
    mx = float(mags.max())
    mask = mags > mx * thr
    if int(np.count_nonzero(mask)) >= 2:
        idx = np.where(mask)[0]
        return round(float(freqs[idx[-1]]) - float(freqs[idx[0]]), 2)
    return 0.0


def fill_color(hex_color: str, alpha: float) -> str:
    """Convert hex colour + alpha → rgba string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ══════════════════════════════════════════════════════════════════════════════
# PLOT HELPERS — all use T (theme dict) evaluated at render time
# ══════════════════════════════════════════════════════════════════════════════
def _ax():
    return dict(
        gridcolor=T["PGRID"],
        zerolinecolor=T["PZERO"],
        zerolinewidth=1,
        color=T["PTXT"],
        linecolor=T["PLINE"],
        linewidth=1,
        tickfont=dict(size=11, color=T["PTICK"],
                      family="'IBM Plex Mono',monospace"),
        title_font=dict(color=T["PTXT"], size=12),
    )


def _base_layout(height=420, title=""):
    d = dict(
        paper_bgcolor=T["PBG"],
        plot_bgcolor=T["PPBG"],
        font=dict(color=T["PTXT"], size=12,
                  family="'IBM Plex Mono',monospace"),
        legend=dict(
            bgcolor=T["PLEG"],
            bordercolor=T["PLINE"],
            borderwidth=1,
            font=dict(color=T["PTXT"], size=11),
        ),
        margin=dict(l=64, r=24, t=52, b=56),
        height=height,
        transition=dict(duration=350, easing="cubic-in-out"),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=T["PBG"],
            bordercolor=T["PLINE"],
            font=dict(color=T["PTXT"],
                      family="'IBM Plex Mono',monospace", size=11),
        ),
    )
    if title:
        d["title"] = dict(text=title, font=dict(color=T["PTXT"], size=12,
                                                family="'DM Sans',sans-serif"))
    return d


def theme_fig(fig, height=420, title="", xt="Time (s)", yt="Amplitude"):
    fig.update_layout(**_base_layout(height, title))
    a = _ax()
    fig.update_xaxes(title_text=xt, **a)
    fig.update_yaxes(title_text=yt, **a)


def mcard(label: str, value: str):
    st.markdown(
        f'<div class="mcard"><div class="lbl">{label}</div>'
        f'<div class="val">{value}</div></div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CORE SIGNAL
# ══════════════════════════════════════════════════════════════════════════════
fs = max(int(fs_raw), 2)

if "_adata" in st.session_state:
    raw_audio = st.session_state["_adata"]
    audio_rate = st.session_state["_arate"]
    idx = np.linspace(0, len(raw_audio) - 1, N_POINTS).astype(int)
    signal = raw_audio[idx]
    dur_eff = float(len(raw_audio) / audio_rate)
    t = np.linspace(0.0, dur_eff, N_POINTS, endpoint=False)
    ts = np.arange(0.0, dur_eff, 1.0 / fs)
    ts_idx = np.clip((ts * audio_rate).astype(int), 0, len(raw_audio) - 1)
    sampled = raw_audio[ts_idx]
    fq, mq, _, _ = compute_fft(signal[:min(N_POINTS, 8192)], float(audio_rate))
    freq_eff = max(1, int(round(float(fq[int(np.argmax(mq))]))))
    src_lbl = f"🎵 {st.session_state['_aname']}"
else:
    t = np.linspace(0.0, duration, N_POINTS, endpoint=False)
    ts = np.arange(0.0, duration, 1.0 / fs)
    signal = gen_signal(t, freq, amp, signal_type, float(duration))
    sampled = gen_signal(ts, freq, amp, signal_type, float(duration))
    dur_eff = float(duration)
    freq_eff = freq
    src_lbl = f"🔧 {signal_type} {freq} Hz"

nyquist = 2 * freq_eff
alias_f = abs(freq_eff - round(freq_eff / fs) * fs)
is_alias = fs < nyquist

rng = np.random.default_rng(42)
noise_vec = rng.normal(
    0.0, noise_level, N_POINTS) if noise_level > 0 else np.zeros(N_POINTS)
noisy = signal + noise_vec
filtered = moving_avg(noisy, filter_win)

# ── Audio banner ──────────────────────────────────────────────────────────────
if "_adata" in st.session_state:
    _ad, _ar = st.session_state["_adata"], st.session_state["_arate"]
    st.markdown(
        f'<div class="audio-banner">🎵 &nbsp;<b>Audio mode</b> — '
        f'<b>{st.session_state["_aname"]}</b> '
        f'({_ar} Hz · {len(_ad)/_ar:.1f} s) · '
        f'Dominant: <b>{freq_eff} Hz</b> · Nyquist min: <b>{nyquist} Hz</b></div>',
        unsafe_allow_html=True,
    )

# ── Status bar ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    mcard("Source",        src_lbl[:22])
with c2:
    mcard("Signal Freq",   f"{freq_eff} Hz")
with c3:
    mcard("Sampling Rate", f"{fs} Hz")
with c4:
    mcard("Nyquist Min",   f"{nyquist} Hz")
with c5:
    mcard("Alias Freq",    f"{alias_f:.1f} Hz")
with c6:
    badge = ('<span class="badge-warn">⚠ Aliasing</span>' if is_alias
             else '<span class="badge-ok">✓ Clean</span>')
    st.markdown(f'<div class="mcard"><div class="lbl">Status</div>'
                f'<div class="val" style="font-size:13px;padding-top:6px">{badge}</div></div>',
                unsafe_allow_html=True)
st.markdown("---")

# ── Plot fill alpha — stronger in dark for contrast ───────────────────────────
FA = T["FA"]

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
(tab_scope, tab_fft, tab_phase,
 tab_filter, tab_water, tab_liss,
 tab_3d, tab_audio) = st.tabs([
     "🔭  Oscilloscope",
     "📈  FFT Spectrum",
     "🌀  Phase Space",
     "🔧  Filter Lab",
     "🌊  Waterfall",
     "〰️  Lissajous",
     "🌐  3D Models",
     "🎵  Audio Analyzer",
 ])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OSCILLOSCOPE
# ══════════════════════════════════════════════════════════════════════════════
with tab_scope:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("① Continuous Signal")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=signal, mode="lines", name="x(t)",
                                 line=dict(color=_C["cont"], width=2)))
        if noise_level > 0:
            fig.add_trace(go.Scatter(x=t, y=noisy, mode="lines",
                                     name=f"+ Noise ({noise_level:.1f})",
                                     line=dict(
                                         color=_C["noisy"], width=1, dash="dot"),
                                     opacity=0.7))
        theme_fig(fig, 420, f"{src_lbl}  ·  A={amp:.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("② Sampled Signal")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=t, y=signal, mode="lines", name="Continuous (ref)",
                                  line=dict(color=_C["cont"],
                                            width=1.4, dash="dot"),
                                  opacity=0.28))
        # Stem lines
        sx, sy = [], []
        for xi, yi in zip(ts, sampled):
            sx += [float(xi), float(xi), None]
            sy += [0.0, float(yi), None]
        stem_col = "rgba(249,115,22,0.50)" if T["dark"] else "rgba(249,115,22,0.35)"
        fig2.add_trace(go.Scatter(x=sx, y=sy, mode="lines", showlegend=False,
                                  line=dict(color=stem_col, width=1)))
        fig2.add_trace(go.Scatter(x=ts, y=sampled, mode="markers",
                                  name=f"Samples (Fs={fs} Hz)",
                                  marker=dict(color=_C["samp"], size=7,
                                              line=dict(color=T["PBG"], width=1.2))))
        theme_fig(
            fig2, 420, f"Fs={fs} Hz · {len(ts)} samples · T={1/fs*1000:.1f} ms")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("③ Aliasing Visualisation")
    alias_sig = gen_signal(t, alias_f, amp, "Sine", dur_eff)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=t, y=signal, mode="lines",
                              name=f"Original {freq_eff} Hz",
                              line=dict(color=_C["cont"], width=2.2)))
    fig3.add_trace(go.Scatter(x=ts, y=sampled, mode="markers",
                              name=f"Samples Fs={fs}Hz",
                              marker=dict(color=_C["samp"], size=6,
                                          line=dict(color=T["PBG"], width=1))))
    if is_alias:
        fig3.add_trace(go.Scatter(x=t, y=alias_sig, mode="lines",
                                  name=f"Alias {alias_f:.2f} Hz",
                                  line=dict(color=_C["alias"], width=2, dash="dash")))
    note = f"⚠ Fs={fs} < {nyquist}" if is_alias else f"✓ Fs={fs} ≥ {nyquist}"
    theme_fig(fig3, 440,
              f"alias = |{freq_eff} − round({freq_eff}/{fs})×{fs}| = {alias_f:.2f} Hz  [{note}]")
    st.plotly_chart(fig3, use_container_width=True)

    if is_alias:
        st.error(f"**Aliasing!** {freq_eff} Hz needs Fs ≥ {nyquist} Hz. "
                 f"At Fs={fs} Hz it appears as **{alias_f:.2f} Hz**.")
    else:
        st.success(f"**No aliasing.** Fs={fs} Hz ≥ Nyquist={nyquist} Hz ✓")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FFT SPECTRUM
# ══════════════════════════════════════════════════════════════════════════════
with tab_fft:
    freqs_hz, mags, power_db, n_fft = compute_fft(noisy, float(fs))
    dom_idx = int(np.argmax(mags))
    dom_freq = round(float(freqs_hz[dom_idx]), 2)
    bw_hz = fft_bandwidth(freqs_hz, mags)
    snr_db = (round(20.0 * np.log10(float(amp) / max(float(noise_level), 1e-9)), 1)
              if noise_level > 0 else 99.0)
    harm_rms = float(
        np.sqrt(np.sum(mags[dom_idx+1:] ** 2))) if dom_idx + 1 < len(mags) else 0.0
    thd_pct = round(
        harm_rms / max(float(mags[dom_idx]), FFT_NORM_FLOOR) * 100.0, 1)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        mcard("Dominant Freq",      f"{dom_freq} Hz")
    with m2:
        mcard("Bandwidth (−10 dB)", f"{bw_hz} Hz")
    with m3:
        mcard("SNR",                f"{min(snr_db, 99.9):.1f} dB")
    with m4:
        mcard("THD",                f"{thd_pct} %")

    nb = len(freqs_hz)
    # Bar colours — brighter in dark mode
    sat = "75%" if T["dark"] else "65%"
    lgt = "62%" if T["dark"] else "52%"
    bar_colors = [
        f"hsl({int(210 + i/max(nb-1, 1)*60)},{sat},{lgt})" for i in range(nb)]

    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=("Magnitude Spectrum",
                                        "Power Spectrum (dB)"),
                        vertical_spacing=0.14)
    fig.add_trace(go.Bar(x=freqs_hz, y=mags, showlegend=False,
                         marker=dict(color=bar_colors, line=dict(width=0))), row=1, col=1)
    fig.add_trace(go.Scatter(x=freqs_hz, y=power_db, mode="lines", showlegend=False,
                             line=dict(color=_C["power"], width=1.8),
                             fill="tozeroy",
                             fillcolor=fill_color(_C["power"], FA * 1.2)), row=2, col=1)

    for r in (1, 2):
        if 0 < dom_freq <= float(freqs_hz[-1]):
            fig.add_vline(x=dom_freq, line_dash="dash", line_color=_C["samp"],
                          annotation_text=f"{dom_freq} Hz",
                          annotation_font_color=_C["samp"],
                          annotation_position="top right", row=r, col=1)
        if is_alias and 0 < alias_f <= float(freqs_hz[-1]):
            fig.add_vline(x=alias_f, line_dash="dot", line_color=_C["alias"],
                          annotation_text=f"alias {alias_f:.1f} Hz",
                          annotation_font_color=_C["alias"],
                          annotation_position="top left", row=r, col=1)

    a = _ax()
    fig.update_layout(**_base_layout(740))
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="Frequency (Hz)", **a)
    fig.update_yaxes(**a)
    fig.update_yaxes(title_text="Magnitude", row=1, col=1)
    fig.update_yaxes(title_text="dB",        row=2, col=1)
    # Fix subplot title colours
    for ann in fig.layout.annotations:
        ann.font.color = T["PTXT"]
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📐 FFT Theory & Parameters"):
        freq_res = round(float(fs) / n_fft, 4)
        st.markdown(f"""
| Parameter | Value |
|---|---|
| FFT size | {n_fft} pts (zero-padded → next power of 2) |
| Window | Hanning (von Hann) |
| Frequency resolution | {freq_res} Hz / bin |
| Nyquist limit | {fs // 2} Hz |
| Dominant frequency | {dom_freq} Hz |
| Alias frequency | {alias_f:.2f} Hz {'⚠ active' if is_alias else '(no aliasing)'} |
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PHASE SPACE
# ══════════════════════════════════════════════════════════════════════════════
with tab_phase:
    lag = st.slider("Lag k (samples)", 1, min(
        50, N_POINTS // 4), 5, key="lag_sl")
    x_ph = noisy[:-lag]
    y_ph = noisy[lag:]

    max_lag = min(400, len(signal) // 2)
    mean_s = float(signal.mean())
    var_s = float(np.var(signal))
    lags_arr = np.arange(max_lag)
    if var_s > 1e-12:
        auto = np.array([
            float(np.mean((signal[:N_POINTS-ll] - mean_s)
                          * (signal[ll:] - mean_s))) / var_s
            for ll in lags_arr
        ])
    else:
        auto = np.zeros(max_lag)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Phase Portrait")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_ph, y=y_ph, mode="lines",
                                 line=dict(color=_C["phase"], width=1.0),
                                 name=f"x[n] vs x[n−{lag}]"))
        theme_fig(
            fig, 520, f"Phase portrait (lag={lag})", xt=f"x[n−{lag}]", yt="x[n]")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Autocorrelation  R[k]")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=lags_arr, y=auto, mode="lines",
                                  line=dict(color=_C["auto"], width=1.8),
                                  fill="tozeroy",
                                  fillcolor=fill_color(_C["auto"], FA * 1.3),
                                  name="R[k]"))
        fig2.add_hline(y=0, line_dash="dot", line_color=T["PZERO"])
        theme_fig(fig2, 520, "Normalised autocorrelation",
                  xt="Lag (samples)", yt="R[k]")
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FILTER LAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_filter:
    rms_orig = float(np.sqrt(np.mean(signal ** 2)))
    rms_n = float(np.sqrt(np.mean(noisy ** 2)))
    rms_f = float(np.sqrt(np.mean(filtered ** 2)))
    snr_g = round(20.0 * np.log10(max(rms_f, FFT_NORM_FLOOR) /
                                  max(rms_n, FFT_NORM_FLOOR)), 2)
    cutoff = round(float(fs) / (2.0 * max(filter_win, 1)), 2)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        mcard("RMS Original", f"{rms_orig:.4f}")
    with m2:
        mcard("RMS Noisy",    f"{rms_n:.4f}")
    with m3:
        mcard("RMS Filtered", f"{rms_f:.4f}")
    with m4:
        mcard("SNR Gain",     f"{snr_g} dB")
    with m5:
        mcard("−3 dB Cutoff", f"{cutoff} Hz")

    st.subheader("① Original Signal")
    fo = go.Figure()
    fo.add_trace(go.Scatter(x=t, y=signal, mode="lines", name="Original",
                            line=dict(color=_C["cont"], width=2),
                            fill="tozeroy", fillcolor=fill_color(_C["cont"], FA)))
    theme_fig(fo, 330, f"Original — {src_lbl}")
    st.plotly_chart(fo, use_container_width=True)

    cn, cf = st.columns(2)
    with cn:
        st.subheader("② Noisy")
        fn = go.Figure()
        fn.add_trace(go.Scatter(x=t, y=noisy, mode="lines",
                                name=f"Noisy (σ={noise_level:.1f})",
                                line=dict(color=_C["noisy"], width=1.2)))
        theme_fig(fn, 340, f"Noise level {noise_level:.1f}")
        st.plotly_chart(fn, use_container_width=True)

    with cf:
        st.subheader("③ Filtered")
        ff = go.Figure()
        ff.add_trace(go.Scatter(x=t, y=filtered, mode="lines",
                                name=f"Filtered (M={filter_win})",
                                line=dict(color=_C["filt"], width=2.2),
                                fill="tozeroy", fillcolor=fill_color(_C["filt"], FA * 1.2)))
        theme_fig(ff, 340, f"FIR M={filter_win} · cutoff ≈ {cutoff} Hz")
        st.plotly_chart(ff, use_container_width=True)

    st.subheader("④ Noisy vs Filtered Overlay")
    fc = go.Figure()
    noisy_line = "rgba(239,68,68,0.60)" if T["dark"] else "rgba(239,68,68,0.45)"
    fc.add_trace(go.Scatter(x=t, y=noisy, mode="lines",
                            name=f"Noisy (σ={noise_level:.1f})",
                            line=dict(color=noisy_line, width=1)))
    fc.add_trace(go.Scatter(x=t, y=filtered, mode="lines",
                            name=f"Filtered (M={filter_win})",
                            line=dict(color=_C["filt"], width=2.5)))
    theme_fig(fc, 360, "Noisy (red) vs Filtered (cyan)")
    st.plotly_chart(fc, use_container_width=True)

    st.subheader("⑤ Filter Frequency Response  |H(f)|")
    omega = np.linspace(0.0, np.pi, 1024)
    eps = 1e-9
    M_f = float(filter_win)
    H = np.clip(np.abs(np.sin(M_f * omega / 2 + eps) /
                       (M_f * np.sin(omega / 2 + eps) + eps)), 0, 1)
    f_ax = omega / np.pi * (fs / 2.0)
    fh = go.Figure()
    fh.add_trace(go.Scatter(x=f_ax, y=H, mode="lines", name="|H(f)|",
                            line=dict(color=_C["samp"], width=2.4),
                            fill="tozeroy", fillcolor=fill_color(_C["samp"], FA)))
    fh.add_hline(y=0.707, line_dash="dash", line_color=_C["cont"],
                 annotation_text="−3 dB (0.707)",
                 annotation_font_color=_C["cont"],
                 annotation_position="bottom right")
    theme_fig(fh, 340, xt="Frequency (Hz)", yt="|H(f)|")
    st.plotly_chart(fh, use_container_width=True)

    with st.expander("📐 Filter Theory"):
        st.markdown(f"""
| Parameter | Value |
|---|---|
| Filter type | FIR moving-average (rectangular window) |
| Window length M | {filter_win} samples |
| Approx −3 dB cutoff | {cutoff} Hz |
| Group delay | {filter_win // 2} samples |

**Response**: `|H(f)| = |sin(Mω/2)| / (M · |sin(ω/2)|)`  
Larger M → more smoothing, more group delay (M/2 samples).
""")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — WATERFALL
# ══════════════════════════════════════════════════════════════════════════════
with tab_water:
    st.subheader("Short-Time FFT Waterfall Spectrogram")
    n_fr2 = 64
    flen = max(64, N_POINTS // n_fr2)
    nfft_w = next_pow2(flen)
    hop = max(1, (N_POINTS - flen) // max(n_fr2 - 1, 1))
    win_h = np.hanning(flen)

    wfall, tlab = [], []
    for i in range(n_fr2):
        s = i * hop
        e = s + flen
        if e > N_POINTS:
            break
        p = np.zeros(nfft_w)
        p[:flen] = noisy[s:e] * win_h
        wfall.append(np.abs(np.fft.rfft(p)) / (nfft_w / 2.0))
        tlab.append(round(s / N_POINTS * dur_eff, 3))

    if len(wfall) < 2:
        st.warning("Signal too short. Increase Duration.")
    else:
        wa = np.array(wfall)
        faxw = np.fft.rfftfreq(nfft_w, d=1.0 / fs)
        zdb = np.clip(20.0 * np.log10(wa + 1e-12), DB_FLOOR, 0.0)
        fw = go.Figure(go.Heatmap(
            z=zdb.T, x=tlab, y=faxw,
            colorscale=T["HEAT"],
            zmin=DB_FLOOR, zmax=0,
            colorbar=dict(
                title=dict(text="dB", font=dict(color=T["PTXT"])),
                tickfont=dict(color=T["PTXT"]),
            ),
        ))
        a = _ax()
        fw.update_layout(**_base_layout(560))
        fw.update_xaxes(title_text="Time (s)", **a)
        fw.update_yaxes(title_text="Frequency (Hz)", **a)
        st.plotly_chart(fw, use_container_width=True)
        st.caption(f"Hanning STFT · {len(wfall)} frames · FFT {nfft_w} · "
                   f"{round(fs/nfft_w, 3)} Hz/bin · Hop {hop} samp  |  "
                   f"Tip: select Chirp for a diagonal frequency sweep")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — LISSAJOUS
# ══════════════════════════════════════════════════════════════════════════════
with tab_liss:
    cp, cc = st.columns([3, 1])
    with cc:
        st.markdown("#### Controls")
        freq2 = st.slider("Y Freq (Hz)", 1, 50, 3, key="lf2")
        phase = st.slider("Phase (°)",   0, 360, 0, 5, key="lph")
        gcd_v = int(np.gcd(freq_eff, freq2))
        ratio = f"{freq_eff // gcd_v} : {freq2 // gcd_v}"
        st.markdown(f"**Ratio:** `{ratio}`")
        st.markdown("""
---
| Ratio | Phase | Shape |
|---|---|---|
| 1:1 | 0° | Diagonal |
| 1:1 | 90° | Circle |
| 1:2 | 90° | Figure-8 |
| 2:3 | 90° | Pretzel |
| 3:4 | 90° | Butterfly |
""")
    with cp:
        st.subheader("Lissajous Figure")
        lcm_f = freq_eff * freq2 // max(gcd_v, 1)
        cycles = lcm_f * 6
        t_l = np.linspace(
            0.0, cycles / max(float(min(freq_eff, freq2)), 1.0), 12_000)
        x_l = amp * np.sin(2.0 * np.pi * freq_eff * t_l)
        y_l = amp * np.sin(2.0 * np.pi * freq2 * t_l + np.radians(phase))
        fl = go.Figure()
        fl.add_trace(go.Scatter(x=x_l, y=y_l, mode="lines",
                                line=dict(color=_C["phase"], width=1.6),
                                name=f"{freq_eff}×{freq2} Hz φ={phase}°"))
        theme_fig(fl, 540, f"Lissajous {freq_eff}×{freq2} Hz · {ratio} · φ={phase}°",
                  xt="X = A·sin(2πf₁t)", yt="Y = A·sin(2πf₂t + φ)")
        st.plotly_chart(fl, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — 3D MODELS
# ══════════════════════════════════════════════════════════════════════════════
with tab_3d:
    st.subheader("3D Signal Visualisations")
    st.caption("Rotate · zoom · pan with mouse or trackpad.")

    d3c = st.radio("Select 3D model",
                   ["① 3D Waveform Ribbon",
                    "② Freq–Time–Amplitude Surface",
                    "③ 3D Lissajous Helix",
                    "④ Sampling Constellation"],
                   horizontal=True)

    def _3dl(title="", height=660):
        sbg = T["PPBG"]
        gc = T["PGRID"]
        axd = dict(
            gridcolor=gc,
            zerolinecolor=T["PZERO"],
            color=T["PTXT"],
            tickfont=dict(size=10, color=T["PTICK"]),
            title_font=dict(color=T["PTXT"], size=12),
        )
        return dict(
            paper_bgcolor=T["PBG"],
            font=dict(color=T["PTXT"], size=11,
                      family="'IBM Plex Mono',monospace"),
            height=height,
            margin=dict(l=0, r=0, t=54, b=0),
            title=dict(text=title, font=dict(color=T["PTXT"], size=13,
                                             family="'DM Sans',sans-serif")),
            transition=dict(duration=350, easing="cubic-in-out"),
            hoverlabel=dict(bgcolor=T["PBG"], bordercolor=T["PLINE"],
                            font=dict(color=T["PTXT"],
                                      family="'IBM Plex Mono',monospace", size=11)),
            legend=dict(bgcolor=T["PLEG"], bordercolor=T["PLINE"], borderwidth=1,
                        font=dict(color=T["PTXT"], size=11)),
            scene=dict(
                bgcolor=sbg,
                xaxis=dict(**axd),
                yaxis=dict(**axd),
                zaxis=dict(**axd),
                camera=dict(eye=dict(x=1.5, y=1.5, z=0.8),
                            up=dict(x=0, y=0, z=1)),
            ),
        )

    # ── MODEL 1: 3D Waveform Ribbon ───────────────────────────────────────────
    if d3c.startswith("①"):
        n_strips = 8
        t3 = np.linspace(0.0, dur_eff, N_POINTS // 4, endpoint=False)
        f3d = go.Figure()
        for i in range(n_strips):
            s3 = gen_signal(t3, freq_eff, amp * max(0.2, 1 - i * 0.06),
                            signal_type, dur_eff)
            hue = int(210 + i / max(n_strips - 1, 1) * 80)
            lgt = "62%" if T["dark"] else "50%"
            col = f"hsl({hue},80%,{lgt})"
            f3d.add_trace(go.Scatter3d(
                x=t3, y=np.full_like(t3, i * 0.35), z=s3, mode="lines",
                line=dict(color=col, width=3),
                name="Strip 1" if i == 0 else f"Strip {i+1}",
                showlegend=(i == 0),
            ))
        ts3 = np.arange(0.0, dur_eff, 1.0 / fs)
        samp3 = gen_signal(ts3, freq_eff, amp, signal_type, dur_eff)
        f3d.add_trace(go.Scatter3d(
            x=ts3, y=np.zeros_like(ts3), z=samp3, mode="markers",
            marker=dict(size=4, color=_C["samp"],
                        line=dict(color=T["PBG"], width=0.5)),
            name=f"Samples Fs={fs}Hz",
        ))
        lay = _3dl(f"3D Waveform Ribbon — {signal_type} {freq_eff} Hz")
        lay["scene"]["xaxis"]["title"] = "Time (s)"
        lay["scene"]["yaxis"]["title"] = "Strip offset"
        lay["scene"]["zaxis"]["title"] = "Amplitude"
        f3d.update_layout(**lay)
        st.plotly_chart(f3d, use_container_width=True)
        st.info("Orange dots = sample points on the front strip. "
                "Rotate to see the ribbon depth perspective.")

    # ── MODEL 2: Freq–Time–Amplitude Surface ──────────────────────────────────
    elif d3c.startswith("②"):
        nfr3 = 48
        fl3 = max(64, N_POINTS // nfr3)
        nf3 = next_pow2(fl3)
        hp3 = max(1, (N_POINTS - fl3) // max(nfr3 - 1, 1))
        wh3 = np.hanning(fl3)
        wf3, tl3 = [], []
        for i in range(nfr3):
            s3 = i * hp3
            e3 = s3 + fl3
            if e3 > N_POINTS:
                break
            p3 = np.zeros(nf3)
            p3[:fl3] = noisy[s3:e3] * wh3
            wf3.append(np.abs(np.fft.rfft(p3)) / (nf3 / 2.0))
            tl3.append(round(s3 / N_POINTS * dur_eff, 3))

        if len(wf3) < 2:
            st.warning("Signal too short. Increase Duration.")
        else:
            wa3 = np.array(wf3)
            fa3 = np.fft.rfftfreq(nf3, d=1.0 / fs)
            fmi = min(len(fa3), max(2, len(fa3) // 2))
            Z3 = np.clip(20.0 * np.log10(wa3[:, :fmi] + 1e-12), DB_FLOOR, 0)
            f3d = go.Figure(go.Surface(
                x=np.array(tl3), y=fa3[:fmi], z=Z3.T,
                colorscale=T["SURF"], cmin=DB_FLOOR, cmax=0,
                colorbar=dict(
                    title=dict(text="dB", font=dict(color=T["PTXT"])),
                    tickfont=dict(color=T["PTXT"]),
                ),
                contours=dict(z=dict(show=True, usecolormap=True,
                                     highlightcolor="white", project_z=True)),
                lighting=dict(ambient=0.5, diffuse=0.8, roughness=0.5,
                              specular=0.3, fresnel=0.2),
                lightposition=dict(x=100, y=200, z=0),
            ))
            lay3 = _3dl("Frequency–Time–Amplitude Surface (dB)")
            lay3["scene"]["camera"]["eye"] = dict(x=1.8, y=-1.6, z=1.2)
            lay3["scene"]["xaxis"]["title"] = "Time (s)"
            lay3["scene"]["yaxis"]["title"] = "Frequency (Hz)"
            lay3["scene"]["zaxis"]["title"] = "Power (dB)"
            f3d.update_layout(**lay3)
            st.plotly_chart(f3d, use_container_width=True)
            st.info("Drag to orbit. Bright peaks = dominant frequencies. "
                    "Try Chirp waveform for a rising ridge.")

    # ── MODEL 3: 3D Lissajous Helix ──────────────────────────────────────────
    elif d3c.startswith("③"):
        t_h = np.linspace(0, 8 * np.pi, 6_000)
        x_h = np.sin(t_h)
        y_h = np.sin(2 * t_h + np.pi / 4)
        z_h = t_h / (8 * np.pi)

        proj_col = "rgba(148,163,184,0.30)" if T["dark"] else "rgba(100,116,139,0.20)"
        f3d = go.Figure()
        f3d.add_trace(go.Scatter3d(
            x=x_h, y=y_h, z=z_h, mode="lines",
            line=dict(color=z_h, colorscale="Rainbow", width=4),
            name="Lissajous helix",
        ))
        f3d.add_trace(go.Scatter3d(
            x=x_h, y=y_h, z=np.zeros_like(z_h), mode="lines",
            line=dict(color=proj_col, width=1), name="XY projection",
        ))
        f3d.add_trace(go.Scatter3d(
            x=x_h, y=np.full_like(y_h, 1.1), z=z_h, mode="lines",
            line=dict(color=proj_col, width=1), name="XZ projection",
        ))
        lh = _3dl("3D Lissajous Helix (1:2, φ=45°) — time as Z-depth")
        lh["scene"]["camera"]["eye"] = dict(x=1.6, y=1.6, z=1.0)
        lh["scene"]["xaxis"]["title"] = "X = sin(t)"
        lh["scene"]["yaxis"]["title"] = "Y = sin(2t + π/4)"
        lh["scene"]["zaxis"]["title"] = "Time (normalised)"
        f3d.update_layout(**lh)
        st.plotly_chart(f3d, use_container_width=True)
        st.info("Colour encodes time. Shadow projections show 2D Lissajous "
                "on each coordinate plane.")

    # ── MODEL 4: Sampling Constellation ──────────────────────────────────────
    else:
        t4 = np.linspace(0.0, dur_eff, N_POINTS // 2, endpoint=False)
        nt4 = len(t4) // 2
        sig4 = gen_signal(t4[:nt4], freq_eff, amp, signal_type, dur_eff)
        ts4 = np.arange(0.0, dur_eff, 1.0 / fs)
        samp4 = gen_signal(ts4, freq_eff, amp, signal_type, dur_eff)

        f3d = go.Figure()
        f3d.add_trace(go.Scatter3d(
            x=t4[:nt4], y=np.zeros(nt4), z=sig4, mode="lines",
            line=dict(color=_C["cont"], width=3),
            name=f"Signal {freq_eff} Hz",
        ))
        f3d.add_trace(go.Scatter3d(
            x=ts4, y=np.zeros_like(ts4), z=samp4, mode="markers",
            marker=dict(size=5, color=_C["samp"],
                        line=dict(color=T["PBG"], width=0.8)),
            name=f"Samples Fs={fs}Hz",
        ))
        if is_alias:
            alias4 = gen_signal(t4[:nt4], alias_f, amp, "Sine", dur_eff)
            f3d.add_trace(go.Scatter3d(
                x=t4[:nt4], y=np.full(nt4, 0.3), z=alias4, mode="lines",
                line=dict(color=_C["alias"], width=2),
                opacity=0.7,
                name=f"Alias {alias_f:.1f}Hz",
            ))
        l4 = _3dl(
            f"Sampling Constellation — {signal_type} {freq_eff}Hz · Fs={fs}Hz")
        l4["scene"]["camera"]["eye"] = dict(x=2.0, y=-1.0, z=1.0)
        l4["scene"]["xaxis"]["title"] = "Time (s)"
        l4["scene"]["yaxis"]["title"] = "Channel"
        l4["scene"]["zaxis"]["title"] = "Amplitude"
        f3d.update_layout(**l4)
        st.plotly_chart(f3d, use_container_width=True)
        if is_alias:
            st.error(f"Alias ribbon at {alias_f:.2f} Hz (semi-transparent) — "
                     f"increase Fs ≥ {nyquist} Hz to remove it.")
        else:
            st.success("No aliasing. Fs meets Nyquist criterion ✓")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — AUDIO ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab_audio:
    st.subheader("Audio File Analyzer")
    if "_adata" not in st.session_state:
        st.info("📂 Upload a WAV file via the **sidebar** to analyse it here "
                "and use it as the signal source for all modules.")
    else:
        audio = st.session_state["_adata"]
        rate = st.session_state["_arate"]
        a_dur = len(audio) / rate

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            mcard("Sample Rate", f"{rate} Hz")
        with m2:
            mcard("Channels",    "1 (L)")
        with m3:
            mcard("Duration",    f"{a_dur:.2f} s")
        with m4:
            mcard("Samples",     f"{len(audio):,}")

        clip = audio[:rate * 10]
        t_clip = np.linspace(0.0, len(clip) / rate, len(clip), endpoint=False)

        st.subheader("Waveform")
        ds = max(1, len(clip) // 4000)
        fw2 = go.Figure()
        fw2.add_trace(go.Scatter(x=t_clip[::ds], y=clip[::ds], mode="lines",
                                 line=dict(color=_C["cont"], width=0.9),
                                 fill="tozeroy",
                                 fillcolor=fill_color(_C["cont"], FA),
                                 name="Waveform"))
        theme_fig(fw2, 330, xt="Time (s)", yt="Amplitude")
        st.plotly_chart(fw2, use_container_width=True)

        st.subheader("Frequency Spectrum")
        clip_fft = clip[:min(len(clip), rate * 2)]
        nfa = next_pow2(max(len(clip_fft), 4))
        pada = np.zeros(nfa)
        pada[:len(clip_fft)] = clip_fft * np.hanning(len(clip_fft))
        spec = np.abs(np.fft.rfft(pada)) / (nfa / 2.0)
        fa = np.fft.rfftfreq(nfa, d=1.0 / rate)
        nfa2 = len(fa)
        sat2 = "75%" if T["dark"] else "65%"
        lgt2 = "62%" if T["dark"] else "52%"
        sc = [
            f"hsl({int(210 + i/max(nfa2-1, 1)*60)},{sat2},{lgt2})" for i in range(nfa2)]
        fs2 = go.Figure()
        fs2.add_trace(go.Bar(x=fa, y=spec, showlegend=False,
                             marker=dict(color=sc, line=dict(width=0))))
        theme_fig(fs2, 320, xt="Frequency (Hz)", yt="Magnitude")
        st.plotly_chart(fs2, use_container_width=True)

        st.subheader("Spectrogram (STFT)")
        frame_sz = min(2048, max(64, len(clip) // 200))
        hop_sz = max(1, frame_sz // 4)
        n_fr3 = (len(clip) - frame_sz) // hop_sz

        if n_fr3 < 2:
            st.info("Audio too short for spectrogram (need > 0.5 s).")
        else:
            nsg = next_pow2(frame_sz)
            wsg = np.hanning(frame_sz)
            sgram = np.zeros((n_fr3, nsg // 2 + 1))
            for i in range(n_fr3):
                ch = clip[i * hop_sz: i * hop_sz + frame_sz] * wsg
                sgram[i] = np.abs(np.fft.rfft(ch, n=nsg)) / (nsg / 2.0)
            fa2 = np.fft.rfftfreq(nsg, d=1.0 / rate)
            ta2 = np.arange(n_fr3) * hop_sz / rate
            zsg = np.clip(20.0 * np.log10(sgram.T + 1e-12), DB_FLOOR, 0.0)
            fsg = go.Figure(go.Heatmap(
                z=zsg, x=ta2, y=fa2,
                colorscale=T["HEAT"],
                zmin=DB_FLOOR, zmax=0,
                colorbar=dict(
                    title=dict(text="dB", font=dict(color=T["PTXT"])),
                    tickfont=dict(color=T["PTXT"]),
                ),
            ))
            a = _ax()
            fsg.update_layout(**_base_layout(460))
            fsg.update_xaxes(title_text="Time (s)", **a)
            fsg.update_yaxes(title_text="Frequency (Hz)", **a)
            st.plotly_chart(fsg, use_container_width=True)
            st.caption(f"STFT · Frame {frame_sz} · Hop {hop_sz} · "
                       f"FFT {nsg} · {n_fr3} frames")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#64748b'>"
    "DSP Pro Lab &nbsp;·&nbsp; Team <b>8vaults</b>"
    " &nbsp;·&nbsp; Problem Statement 18 — Sampling &amp; Aliasing"
    " &nbsp;·&nbsp; Nyquist–Shannon: Fs ≥ 2·f_max"
    " &nbsp;·&nbsp; Streamlit · NumPy · Plotly"
    "</small>",
    unsafe_allow_html=True,
)
