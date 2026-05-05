"""
DSP Pro Lab — MIT 6.003 Style  |  Team: 8vaults
Problem Statement 18: Sampling & Aliasing Visual Demonstrator
v3 — larger graphs, audio-as-global-input, top tab navigation
"""

import io
import wave

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="DSP Pro Lab — 8vaults", layout="wide", page_icon="🔬")

st.markdown("""
<style>
body { background: #0d1117; }

.mit-header {
    background: linear-gradient(135deg, #8b0000 0%, #c0392b 100%);
    color: white; padding: 18px 32px; border-radius: 12px;
    margin-bottom: 20px; box-shadow: 0 4px 22px rgba(139,0,0,0.4);
}
.mit-header h1 { color: white; margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 0.02em; }
.mit-header p  { color: rgba(255,255,255,0.82); margin: 6px 0 0; font-size: 13px; }

.mcard {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 14px 16px; text-align: center;
    margin-bottom: 8px; transition: border-color 0.2s;
}
.mcard:hover { border-color: #8b0000; }
.mcard .val { font-size: 20px; font-weight: 700; color: #4ade80; font-family: 'Courier New', monospace; }
.mcard .lbl { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }

.ok   { background:#1a4731; color:#4ade80; padding:3px 14px; border-radius:5px;
        font-size:14px; font-weight:700; border:1px solid #4ade80; }
.warn { background:#4a1515; color:#f87171; padding:3px 14px; border-radius:5px;
        font-size:14px; font-weight:700; border:1px solid #f87171; }

.audio-banner {
    background: #0d2137; border: 1px solid #1f5c99; border-radius: 8px;
    padding: 10px 18px; margin-bottom: 14px; font-size: 13px; color: #60a5fa;
}
.audio-banner b { color: #93c5fd; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="mit-header">
  <h1>🔬 DSP Pro Lab &nbsp;·&nbsp; 8vaults</h1>
  <p>Interactive Digital Signal Processing Playground &nbsp;|&nbsp;
     Problem Statement 18 — Sampling &amp; Aliasing Visual Demonstrator</p>
</div>
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


def oscope_base():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0a0f0a",
        font=dict(color="#4ade80", size=12, family="Courier New, monospace"),
        legend=dict(
            bgcolor="rgba(10,15,10,0.85)",
            bordercolor="rgba(74,222,128,0.35)",
            borderwidth=1,
            font=dict(color="#9ca3af", size=11),
        ),
        margin=dict(l=64, r=20, t=52, b=56),
    )


def apply_oscope(fig, height=420, title="", xtitle="Time (s)", ytitle="Amplitude"):
    base = oscope_base()
    base["height"] = height
    if title:
        base["title"] = dict(text=title, font=dict(color="#4ade80", size=13))
    fig.update_layout(**base)
    axis_style = dict(
        gridcolor="rgba(74,222,128,0.09)",
        zerolinecolor="rgba(74,222,128,0.28)",
        zerolinewidth=1,
        color="#4ade80",
        linecolor="rgba(74,222,128,0.3)",
        linewidth=1,
        tickfont=dict(size=11),
    )
    fig.update_xaxes(title_text=xtitle, **axis_style)
    fig.update_yaxes(title_text=ytitle, **axis_style)


def mcard(label, value):
    st.markdown(
        f'<div class="mcard"><div class="lbl">{label}</div>'
        f'<div class="val">{value}</div></div>',
        unsafe_allow_html=True,
    )


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


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Audio upload FIRST so we know whether to disable synth controls ────
    st.markdown("### 📂 Audio Input *(global)*")
    st.caption("Upload a WAV — it becomes the signal source for ALL modules.")
    uploaded_file = st.file_uploader("WAV file", type=["wav"], label_visibility="collapsed")

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
            f"{st.session_state['audio_rate']} Hz · {a_dur_sb:.1f} s\n\n"
            f"All modules using this audio."
        )

    st.markdown("---")

    # ── Signal Generator — disabled (greyed out) when audio is active ─────
    st.markdown("### 🎛️ Signal Generator")
    if audio_loaded:
        st.info(
            "⚠️ **Audio mode active.**\n\n"
            "Waveform, Frequency, Amplitude and Duration controls are **overridden** "
            "by the uploaded WAV file.\n\n"
            "Remove the WAV to use the synthesiser.",
            icon=None,
        )
        # Read-only defaults — values won't be used for signal generation
        signal_type = st.selectbox("Waveform *(inactive)*",  ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"], disabled=True)
        freq        = st.slider("Frequency (Hz) *(inactive)*",     1,  50,  5, disabled=True)
        amp         = st.slider("Amplitude *(inactive)*",        0.1, 3.0, 1.0, 0.1, disabled=True)
        duration    = st.slider("Duration (s) *(inactive)*",       1,   5,   2, disabled=True)
        # Sampling rate IS still active — user can still change how the audio is resampled
        st.markdown("**Sampling Rate** — still active (controls resampling of audio):")
        fs_raw = st.slider("Sampling Rate (Hz)", 2, 200, 40)
    else:
        signal_type = st.selectbox("Waveform", ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"])
        freq        = st.slider("Frequency (Hz)",     1,  50,  5)
        fs_raw      = st.slider("Sampling Rate (Hz)", 2, 200, 40)
        amp         = st.slider("Amplitude",        0.1, 3.0, 1.0, 0.1)
        duration    = st.slider("Duration (s)",       1,   5,   2)

    st.markdown("---")
    st.markdown("### 🔊 Noise & Filter")
    noise_level = st.slider("Noise Level",       0.0, 2.0, 0.0, 0.1)
    filter_win  = st.slider("Filter Window (n)",   2,  80,  10)

    st.markdown("---")
    st.caption("DSP Pro Lab · 8vaults · PS-18")


# ══════════════════════════════════════════════════════════════════════════════
# CORE SIGNAL — synthesised OR from uploaded audio
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
    # Detect dominant frequency for Nyquist display
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
        f'<div class="audio-banner">🎵 &nbsp;<b>Audio mode active</b> — '
        f'<b>{st.session_state["audio_name"]}</b> '
        f'({st.session_state["audio_rate"]} Hz · {a_dur:.1f} s). '
        f'Dominant freq: <b>{freq_eff} Hz</b> · Nyquist min: <b>{nyquist} Hz</b> · '
        f'<span style="color:#fbbf24">⚠ Waveform / Frequency / Amplitude / Duration sliders are overridden by this file. '
        f'Only <b>Sampling Rate</b>, <b>Noise</b> and <b>Filter</b> controls are active.</span></div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# STATUS BAR
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: mcard("Source",        source_label[:22])
with c2: mcard("Signal Freq",   f"{freq_eff} Hz")
with c3: mcard("Sampling Rate", f"{fs} Hz")
with c4: mcard("Nyquist Min",   f"{nyquist} Hz")
with c5: mcard("Alias Freq",    f"{alias_f:.1f} Hz")
with c6:
    badge = '<span class="warn">⚠ Aliasing</span>' if is_alias else '<span class="ok">✓ Clean</span>'
    st.markdown(
        f'<div class="mcard"><div class="lbl">Status</div>'
        f'<div class="val" style="font-size:13px;padding-top:6px">{badge}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# TOP-LEVEL TABS  (always visible — most accessible navigation)
# ══════════════════════════════════════════════════════════════════════════════
(tab_scope, tab_fft, tab_phase,
 tab_filter, tab_water, tab_liss, tab_audio) = st.tabs([
    "🔭  Oscilloscope",
    "📈  FFT Spectrum",
    "🌀  Phase Space",
    "🔧  Filter Lab",
    "🌊  Waterfall",
    "〰️  Lissajous",
    "🎵  Audio Analyzer",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OSCILLOSCOPE
# ══════════════════════════════════════════════════════════════════════════════
with tab_scope:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("① Continuous Signal")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t, y=signal, mode="lines", name="Continuous x(t)",
            line=dict(color="#4ade80", width=1.8),
        ))
        if noise_level > 0:
            fig.add_trace(go.Scatter(
                x=t, y=noisy, mode="lines", name=f"+ Noise ({noise_level:.1f})",
                line=dict(color="rgba(248,113,113,0.5)", width=1),
            ))
        apply_oscope(fig, height=420,
                     title=f"{source_label}  ·  A={amp:.1f}")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("② Sampled Signal")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=t, y=signal, mode="lines", name="Continuous (ref)",
            line=dict(color="#4ade80", width=1.2, dash="dot"), opacity=0.4,
        ))
        stem_x, stem_y = [], []
        for xi, yi in zip(ts, sampled):
            stem_x += [float(xi), float(xi), None]
            stem_y += [0.0, float(yi), None]
        fig2.add_trace(go.Scatter(
            x=stem_x, y=stem_y, mode="lines", showlegend=False,
            line=dict(color="rgba(249,115,22,0.45)", width=1),
        ))
        fig2.add_trace(go.Scatter(
            x=ts, y=sampled, mode="markers", name=f"Samples (Fs={fs} Hz)",
            marker=dict(color="#f97316", size=7, line=dict(color="#fff", width=0.5)),
        ))
        apply_oscope(fig2, height=420,
                     title=f"Fs={fs} Hz · {len(ts)} samples · T={1/fs*1000:.1f} ms")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("③ Aliasing Visualisation — Time Domain")
    alias_sig = gen_signal(t, alias_f, amp, "Sine", duration_eff)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=t, y=signal, mode="lines", name=f"Original  {freq_eff} Hz",
        line=dict(color="#4ade80", width=2),
    ))
    fig3.add_trace(go.Scatter(
        x=ts, y=sampled, mode="markers", name=f"Samples (Fs={fs} Hz)",
        marker=dict(color="#facc15", size=6),
    ))
    if is_alias:
        fig3.add_trace(go.Scatter(
            x=t, y=alias_sig, mode="lines", name=f"Alias  {alias_f:.2f} Hz",
            line=dict(color="#f97316", width=2, dash="dash"),
        ))
    note = f"⚠ ALIASING  Fs={fs} < {nyquist}" if is_alias else f"✓ Clean  Fs={fs} ≥ {nyquist}"
    apply_oscope(
        fig3, height=440,
        title=f"alias = |{freq_eff} − round({freq_eff}/{fs})×{fs}| = {alias_f:.2f} Hz   [{note}]",
    )
    st.plotly_chart(fig3, use_container_width=True)

    if is_alias:
        st.error(
            f"**Aliasing!**  {freq_eff} Hz needs Fs ≥ {nyquist} Hz (Nyquist). "
            f"At Fs={fs} Hz it appears as **{alias_f:.2f} Hz**."
        )
    else:
        st.success(f"**No aliasing.**  Fs={fs} Hz ≥ Nyquist={nyquist} Hz ✓")


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
    with m1: mcard("Dominant Freq",      f"{dom_freq} Hz")
    with m2: mcard("Bandwidth (−10 dB)", f"{bw_hz} Hz")
    with m3: mcard("SNR",                f"{min(snr_db, 99.9):.1f} dB")
    with m4: mcard("THD",                f"{thd_pct} %")

    bar_colors = [
        f"hsl({int(140 + i / max(len(freqs_hz)-1, 1) * 80)},80%,55%)"
        for i in range(len(freqs_hz))
    ]
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Magnitude Spectrum", "Power Spectrum (dB)"),
        vertical_spacing=0.12,
    )
    fig.add_trace(go.Bar(x=freqs_hz, y=mags, name="Magnitude",
                         marker=dict(color=bar_colors), showlegend=False),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=freqs_hz, y=power_db, mode="lines",
                             line=dict(color="#60a5fa", width=1.6), showlegend=False),
                  row=2, col=1)

    for r in (1, 2):
        if 0 < dom_freq <= float(freqs_hz[-1]):
            fig.add_vline(x=dom_freq, line_dash="dash", line_color="#f97316",
                          annotation_text=f"{dom_freq} Hz",
                          annotation_font_color="#f97316",
                          annotation_position="top right", row=r, col=1)
        if is_alias and alias_f > 0 and alias_f <= float(freqs_hz[-1]):
            fig.add_vline(x=alias_f, line_dash="dot", line_color="#facc15",
                          annotation_text=f"alias {alias_f:.1f} Hz",
                          annotation_font_color="#facc15",
                          annotation_position="top left", row=r, col=1)

    base = oscope_base()
    base.update(height=720, showlegend=False)
    fig.update_layout(**base)
    fig.update_xaxes(gridcolor="rgba(74,222,128,0.08)", color="#4ade80",
                     title_text="Frequency (Hz)")
    fig.update_yaxes(gridcolor="rgba(74,222,128,0.08)", color="#4ade80")
    fig.update_yaxes(title_text="Magnitude", row=1, col=1)
    fig.update_yaxes(title_text="dB",        row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📐 FFT Theory & Parameters"):
        freq_res = round(float(fs) / n_fft, 4)
        st.markdown(f"""
| Parameter | Value |
|---|---|
| FFT size | {n_fft} points (zero-padded to next power of 2) |
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

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Phase Portrait")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_ph, y=y_ph, mode="lines",
                                 line=dict(color="#c084fc", width=0.9),
                                 name=f"x[n] vs x[n−{lag}]"))
        apply_oscope(fig, height=520,
                     title=f"Phase portrait  (lag = {lag} samples)",
                     xtitle=f"x[n−{lag}]", ytitle="x[n]")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Autocorrelation  R[k]")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=lags_arr, y=auto, mode="lines",
                                  line=dict(color="#f0abfc", width=1.6),
                                  name="R[k]"))
        fig2.add_hline(y=0, line_dash="dot", line_color="rgba(74,222,128,0.3)")
        apply_oscope(fig2, height=520,
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
    with m1: mcard("RMS original", f"{rms_orig:.4f}")
    with m2: mcard("RMS noisy",    f"{rms_n:.4f}")
    with m3: mcard("RMS filtered", f"{rms_f:.4f}")
    with m4: mcard("SNR gain",     f"{snr_g} dB")
    with m5: mcard("−3 dB cutoff", f"{cutoff} Hz")

    st.subheader("① Original Clean Signal")
    fig_orig = go.Figure()
    fig_orig.add_trace(go.Scatter(x=t, y=signal, mode="lines",
                                  name="Original",
                                  line=dict(color="#4ade80", width=2)))
    apply_oscope(fig_orig, height=360,
                 title=f"Original — {source_label}")
    st.plotly_chart(fig_orig, use_container_width=True)

    col_n, col_f = st.columns(2)
    with col_n:
        st.subheader("② Noisy Signal")
        fig_noisy = go.Figure()
        fig_noisy.add_trace(go.Scatter(x=t, y=noisy, mode="lines",
                                       name=f"Noisy (σ={noise_level:.1f})",
                                       line=dict(color="#f87171", width=1.2)))
        apply_oscope(fig_noisy, height=380,
                     title=f"Noise level {noise_level:.1f}")
        st.plotly_chart(fig_noisy, use_container_width=True)

    with col_f:
        st.subheader("③ Filtered Signal")
        fig_filt = go.Figure()
        fig_filt.add_trace(go.Scatter(x=t, y=filtered, mode="lines",
                                      name=f"Filtered (M={filter_win})",
                                      line=dict(color="#38bdf8", width=2)))
        apply_oscope(fig_filt, height=380,
                     title=f"FIR M={filter_win} · cutoff ≈ {cutoff} Hz")
        st.plotly_chart(fig_filt, use_container_width=True)

    st.subheader("④ Comparison: Noisy  vs  Filtered")
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Scatter(x=t, y=noisy, mode="lines",
                                 name=f"Noisy (σ={noise_level:.1f})",
                                 line=dict(color="rgba(248,113,113,0.55)", width=1)))
    fig_cmp.add_trace(go.Scatter(x=t, y=filtered, mode="lines",
                                 name=f"Filtered (M={filter_win})",
                                 line=dict(color="#38bdf8", width=2.2)))
    apply_oscope(fig_cmp, height=400,
                 title="Noisy (red) vs Filtered (blue)")
    st.plotly_chart(fig_cmp, use_container_width=True)

    st.subheader("⑤ Filter Frequency Response  |H(f)|")
    omega = np.linspace(0.0, np.pi, 1024)
    eps   = 1e-9
    M_f   = float(filter_win)
    H     = np.clip(
        np.abs(np.sin(M_f*omega/2+eps) / (M_f*np.sin(omega/2+eps)+eps)),
        0, 1,
    )
    f_ax  = omega / np.pi * (fs / 2.0)
    fig_hr = go.Figure()
    fig_hr.add_trace(go.Scatter(x=f_ax, y=H, mode="lines", name="|H(f)|",
                                line=dict(color="#f97316", width=2.2)))
    fig_hr.add_hline(y=0.707, line_dash="dash", line_color="rgba(74,222,128,0.7)",
                     annotation_text="−3 dB (0.707)",
                     annotation_font_color="#4ade80",
                     annotation_position="bottom right")
    apply_oscope(fig_hr, height=380, xtitle="Frequency (Hz)", ytitle="|H(f)|")
    st.plotly_chart(fig_hr, use_container_width=True)

    with st.expander("📐 Filter Theory"):
        st.markdown(f"""
| Parameter | Value |
|---|---|
| Filter type | FIR moving-average (box / rectangular) |
| Window length M | {filter_win} samples |
| Approx −3 dB cutoff | {cutoff} Hz |
| Group delay | {filter_win // 2} samples |

**Response**: `|H(f)| = |sin(Mω/2)| / (M·|sin(ω/2)|)`
Larger M → more noise suppression, more time lag (group delay = M/2 samples).
        """)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — WATERFALL
# ══════════════════════════════════════════════════════════════════════════════
with tab_water:

    st.subheader("Short-Time FFT Waterfall Spectrogram")

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
        f_ax_w   = np.fft.rfftfreq(n_fft_w, d=1.0 / fs)
        z_db     = np.clip(20.0 * np.log10(wfall_arr + 1e-12), -80.0, 0.0)

        fig = go.Figure(go.Heatmap(
            z=z_db.T, x=t_labels, y=f_ax_w,
            colorscale="Viridis", zmin=-80, zmax=0,
            colorbar=dict(title="dB", ticksuffix=" dB"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0a0f0a",
            font=dict(color="#4ade80", size=12, family="Courier New, monospace"),
            height=600,
            xaxis=dict(title="Time (s)",        color="#4ade80",
                       gridcolor="rgba(74,222,128,0.07)"),
            yaxis=dict(title="Frequency (Hz)", color="#4ade80",
                       gridcolor="rgba(74,222,128,0.07)"),
            margin=dict(l=64, r=20, t=28, b=60),
        )
        st.plotly_chart(fig, use_container_width=True)
        freq_res_w = round(float(fs) / n_fft_w, 3)
        st.caption(
            f"Hanning STFT · {len(wfall)} frames · FFT {n_fft_w} · "
            f"{freq_res_w} Hz/bin · Hop {hop} samples  |  "
            f"Tip: select Chirp waveform for a diagonal frequency sweep"
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — LISSAJOUS
# ══════════════════════════════════════════════════════════════════════════════
with tab_liss:

    col_plot, col_ctrl = st.columns([3, 1])

    with col_ctrl:
        st.markdown("#### Controls")
        # Adapt Y-freq slider max to actual signal freq so ratios always make sense
        liss_max = max(50, freq_eff * 4)
        liss_default = min(3, liss_max)
        freq2 = st.slider("Y-axis Freq (Hz)", 1, liss_max, liss_default, key="liss_freq2")
        phase = st.slider("Phase Offset (°)", 0, 360, 0, 5, key="liss_phase")
        gcd_v = np.gcd(freq_eff, freq2)
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

Non-integer ratios → open quasi-periodic paths.
        """)

    with col_plot:
        st.subheader("Lissajous Figure")
        lcm_f  = freq_eff * freq2 // max(np.gcd(freq_eff, freq2), 1)
        cycles = lcm_f * 6
        t_liss = np.linspace(0.0, cycles / max(float(min(freq_eff, freq2)), 1.0), 12000)
        x_l    = amp * np.sin(2 * np.pi * freq_eff * t_liss)
        y_l    = amp * np.sin(2 * np.pi * freq2    * t_liss + np.radians(phase))
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_l, y=y_l, mode="lines",
            line=dict(color="#c084fc", width=1.5),
            name=f"{freq_eff} Hz × {freq2} Hz  φ={phase}°",
        ))
        apply_oscope(
            fig, height=580,
            title=f"Lissajous  {freq_eff}×{freq2} Hz  |  ratio {ratio}  |  φ={phase}°",
            xtitle="X  (A·sin 2πf₁t)",
            ytitle="Y  (A·sin(2πf₂t + φ))",
        )
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — AUDIO ANALYZER  (dedicated deep-dive view)
# ══════════════════════════════════════════════════════════════════════════════
with tab_audio:

    st.subheader("Audio File Analyzer")

    if "audio_data" not in st.session_state:
        st.info(
            "📂 **Upload a WAV file using the sidebar panel** to analyse it here "
            "and use it as the signal source in all other modules."
        )
    else:
        audio = st.session_state["audio_data"]
        rate  = st.session_state["audio_rate"]
        a_dur = len(audio) / rate

        m1, m2, m3, m4 = st.columns(4)
        with m1: mcard("Sample Rate", f"{rate} Hz")
        with m2: mcard("Channels",    "1 (L)")
        with m3: mcard("Duration",    f"{a_dur:.2f} s")
        with m4: mcard("Samples",     f"{len(audio):,}")

        clip   = audio[: rate * 10]
        t_clip = np.linspace(0.0, len(clip) / rate, len(clip), endpoint=False)

        # Waveform
        st.subheader("Waveform")
        ds = max(1, len(clip) // 4000)
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=t_clip[::ds], y=clip[::ds], mode="lines",
            line=dict(color="#4ade80", width=0.9), name="Waveform",
        ))
        apply_oscope(fig_w, height=360, xtitle="Time (s)", ytitle="Amplitude")
        st.plotly_chart(fig_w, use_container_width=True)

        # Spectrum
        st.subheader("Frequency Spectrum")
        clip_fft = clip[: min(len(clip), rate * 2)]
        n_fft_a  = next_pow2(max(len(clip_fft), 4))
        padded_a = np.zeros(n_fft_a)
        padded_a[: len(clip_fft)] = clip_fft * np.hanning(len(clip_fft))
        spec = np.abs(np.fft.rfft(padded_a)) / (n_fft_a / 2.0)
        fa   = np.fft.rfftfreq(n_fft_a, d=1.0 / rate)
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=fa, y=spec, mode="lines",
                                   line=dict(color="#60a5fa", width=1.1),
                                   name="Magnitude"))
        apply_oscope(fig_s, height=360, xtitle="Frequency (Hz)", ytitle="Magnitude")
        st.plotly_chart(fig_s, use_container_width=True)

        # Spectrogram
        st.subheader("Spectrogram  (STFT)")
        frame_sz = min(2048, max(64, len(clip) // 200))
        hop_sz   = max(1, frame_sz // 4)
        n_fr     = (len(clip) - frame_sz) // hop_sz

        if n_fr < 2:
            st.info("Audio too short for spectrogram (need > 0.5 s).")
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
                colorscale="Plasma", zmin=-80, zmax=0,
                colorbar=dict(title="dB"),
            ))
            fig_sg.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0a0f0a",
                font=dict(color="#4ade80", size=12, family="Courier New, monospace"),
                height=500,
                xaxis=dict(title="Time (s)",       color="#4ade80",
                           gridcolor="rgba(74,222,128,0.07)"),
                yaxis=dict(title="Frequency (Hz)", color="#4ade80",
                           gridcolor="rgba(74,222,128,0.07)"),
                margin=dict(l=68, r=20, t=14, b=60),
            )
            st.plotly_chart(fig_sg, use_container_width=True)
            st.caption(
                f"STFT · Frame {frame_sz} · Hop {hop_sz} · "
                f"FFT {n_fft_sg} · {n_fr} frames"
            )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#555'>"
    "DSP Pro Lab &nbsp;·&nbsp; Team <b style='color:#8b0000'>8vaults</b>"
    " &nbsp;·&nbsp; Problem Statement 18 — Sampling &amp; Aliasing"
    " &nbsp;·&nbsp; Nyquist–Shannon: Fs ≥ 2·f_max"
    " &nbsp;·&nbsp; Streamlit · NumPy · Plotly"
    "</small>",
    unsafe_allow_html=True,
)
