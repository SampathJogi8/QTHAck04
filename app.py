import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="DSP Pro Lab", layout="wide")

COLORS = {
    "signal": "#10b981",
    "noise": "#ef4444",
    "filtered": "#3b82f6",
    "alias": "#f59e0b",
}

# ─────────────────────────────────────────────
# DSP ENGINE (SINGLE SOURCE OF TRUTH)
# ─────────────────────────────────────────────
class DSPState:
    def __init__(self, signal, fs, noise_level, filter_win):
        self.signal = signal
        self.fs = fs
        self.noise_level = noise_level
        self.filter_win = filter_win

        self.N = len(signal)
        self.t = np.arange(self.N) / fs

        rng = np.random.default_rng(42)
        self.noise = rng.normal(0, noise_level, self.N)
        self.noisy = self.signal + self.noise

        self.filtered = self._filter()

        self.freqs, self.mags = self._fft(self.noisy)
        self.dom_freq = self.freqs[np.argmax(self.mags)]

        self.nyquist = fs / 2
        self.alias_freq = abs(self.dom_freq - fs * np.round(self.dom_freq / fs))
        self.is_alias = self.dom_freq > self.nyquist

        self.snr = self._snr()

    def _filter(self):
        kernel = np.ones(self.filter_win) / self.filter_win
        y = np.convolve(self.noisy, kernel, mode="same")
        return np.roll(y, -self.filter_win // 2)

    def _fft(self, sig):
        n = 2 ** int(np.ceil(np.log2(len(sig))))
        spec = np.fft.rfft(sig * np.hanning(len(sig)), n=n)
        freqs = np.fft.rfftfreq(n, d=1/self.fs)
        mags = np.abs(spec)
        return freqs, mags

    def _snr(self):
        signal_power = np.mean(self.signal**2)
        noise_power = np.mean(self.noise**2)
        if noise_power == 0:
            return 99.9
        return 10 * np.log10(signal_power / noise_power)

# ─────────────────────────────────────────────
# SIGNAL GENERATOR
# ─────────────────────────────────────────────
def gen_signal(t, f, a, wtype, dur):
    if wtype == "Sine":
        return a * np.sin(2 * np.pi * f * t)
    if wtype == "Square":
        return a * np.sign(np.sin(2 * np.pi * f * t))
    if wtype == "Triangle":
        return a * (2/np.pi) * np.arcsin(np.sin(2*np.pi*f*t))
    if wtype == "Sawtooth":
        return a * (2*((t*f)%1)-1)
    if wtype == "Chirp":
        k = f / dur
        return a * np.sin(2*np.pi*(0*t + 0.5*k*t**2))
    return np.zeros_like(t)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("Controls")

wave = st.sidebar.selectbox("Waveform", ["Sine","Square","Triangle","Sawtooth","Chirp"])
freq = st.sidebar.slider("Frequency (Hz)", 1, 50, 5)
fs = st.sidebar.slider("Sampling Rate (Hz)", 10, 500, 100)
amp = st.sidebar.slider("Amplitude", 0.1, 3.0, 1.0)
duration = st.sidebar.slider("Duration (s)", 1, 5, 2)

noise_level = st.sidebar.slider("Noise Level", 0.0, 2.0, 0.0)
filter_win = st.sidebar.slider("Filter Window", 1, 50, 5)

# ─────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────
N = int(fs * duration)
t = np.arange(N) / fs
signal = gen_signal(t, freq, amp, wave, duration)
state = DSPState(signal, fs, noise_level, filter_win)

# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
cols = st.columns(5)
cols[0].metric("Dominant Freq", f"{state.dom_freq:.2f} Hz")
cols[1].metric("Sampling Rate", f"{fs} Hz")
cols[2].metric("Nyquist", f"{state.nyquist:.2f} Hz")
cols[3].metric("Alias", f"{state.alias_freq:.2f} Hz")
cols[4].metric("SNR", f"{state.snr:.2f} dB")

if state.is_alias:
    st.error("Aliasing detected")
else:
    st.success("No aliasing")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Oscilloscope",
    "FFT",
    "Phase",
    "Filter",
    "Waterfall",
    "Lissajous"
])

# ─────────────────────────────────────────────
# OSCILLOSCOPE
# ─────────────────────────────────────────────
with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=state.t, y=state.signal, name="Original"))
    fig.add_trace(go.Scatter(x=state.t, y=state.noisy, name="Noisy"))
    fig.add_trace(go.Scatter(x=state.t, y=state.filtered, name="Filtered"))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# FFT
# ─────────────────────────────────────────────
with tab2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=state.freqs, y=state.mags))
    fig.add_vline(x=state.dom_freq)
    fig.add_vline(x=state.alias_freq, line_dash="dot")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# PHASE
# ─────────────────────────────────────────────
with tab3:
    lag = st.slider("Lag", 1, 50, 5)
    x = state.noisy[:-lag]
    y = state.noisy[lag:]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines"))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────
with tab4:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=state.t, y=state.noisy, name="Noisy"))
    fig.add_trace(go.Scatter(x=state.t, y=state.filtered, name="Filtered"))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# WATERFALL
# ─────────────────────────────────────────────
with tab5:
    frame = 256
    hop = 128
    spec = []
    for i in range(0, len(state.noisy)-frame, hop):
        chunk = state.noisy[i:i+frame] * np.hanning(frame)
        fft = np.abs(np.fft.rfft(chunk))
        spec.append(fft)
    spec = np.array(spec).T

    fig = go.Figure(go.Heatmap(
        z=20*np.log10(spec+1e-9),
        colorscale="Plasma"
    ))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# LISSAJOUS
# ─────────────────────────────────────────────
with tab6:
    f2 = st.slider("Y Frequency", 1, 50, 3)
    phase = st.slider("Phase", 0, 360, 0)

    t = np.linspace(0, 2, 5000)
    x = np.sin(2*np.pi*state.dom_freq*t)
    y = np.sin(2*np.pi*f2*t + np.radians(phase))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines"))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# AUDIO OUTPUT
# ─────────────────────────────────────────────
st.subheader("Audio Output")
st.audio(state.filtered, sample_rate=fs)
