import numpy as np
import streamlit as st
import plotly.graph_objects as go

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

        # Noise
        rng = np.random.default_rng(42)
        self.noise = rng.normal(0, noise_level, self.N)
        self.noisy = self.signal + self.noise

        # Filter
        self.filtered = self._filter()

        # FFT
        self.freqs, self.mags = self._fft(self.noisy)
        self.dom_freq = self.freqs[np.argmax(self.mags)]

        # Nyquist
        self.nyquist = fs / 2
        self.alias_freq = self._alias()
        self.is_alias = self.dom_freq > self.nyquist

        # SNR
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

    def _alias(self):
        return abs(self.dom_freq - self.fs * np.round(self.dom_freq / self.fs))

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
        f0 = 0
        k = f / dur
        return a * np.sin(2*np.pi*(f0*t + 0.5*k*t**2))

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
# SIGNAL PIPELINE
# ─────────────────────────────────────────────
N = int(fs * duration)
t = np.arange(N) / fs

signal = gen_signal(t, freq, amp, wave, duration)

state = DSPState(signal, fs, noise_level, filter_win)

# ─────────────────────────────────────────────
# HEADER METRICS
# ─────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Dominant Freq", f"{state.dom_freq:.2f} Hz")
col2.metric("Sampling Rate", f"{fs} Hz")
col3.metric("Nyquist Limit", f"{state.nyquist:.2f} Hz")
col4.metric("Alias Freq", f"{state.alias_freq:.2f} Hz")
col5.metric("SNR", f"{state.snr:.2f} dB")

if state.is_alias:
    st.error(f"Aliasing occurs → Observed {state.alias_freq:.2f} Hz")
else:
    st.success("Nyquist satisfied — No aliasing")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Oscilloscope","FFT","Filter"])

# ─────────────────────────────────────────────
# OSCILLOSCOPE
# ─────────────────────────────────────────────
with tab1:
    step = max(1, len(state.t)//2000)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=state.t[::step], y=state.signal[::step],
        name="Original", line=dict(color=COLORS["signal"])
    ))

    fig.add_trace(go.Scatter(
        x=state.t[::step], y=state.noisy[::step],
        name="Noisy", line=dict(color=COLORS["noise"], width=1)
    ))

    fig.add_trace(go.Scatter(
        x=state.t[::step], y=state.filtered[::step],
        name="Filtered", line=dict(color=COLORS["filtered"])
    ))

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# FFT
# ─────────────────────────────────────────────
with tab2:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=state.freqs, y=state.mags,
        line=dict(color=COLORS["filtered"])
    ))

    fig.add_vline(x=state.dom_freq, line_dash="dash")
    fig.add_vline(x=state.alias_freq, line_dash="dot", line_color="orange")

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────
with tab3:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=state.t, y=state.noisy,
        name="Noisy", line=dict(color=COLORS["noise"])
    ))

    fig.add_trace(go.Scatter(
        x=state.t, y=state.filtered,
        name="Filtered", line=dict(color=COLORS["filtered"], width=2)
    ))

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# AUDIO OUTPUT (BONUS)
# ─────────────────────────────────────────────
st.subheader("Audio Output")
st.audio(state.filtered, sample_rate=fs)
