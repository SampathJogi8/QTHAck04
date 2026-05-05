import numpy as np
import streamlit as st
import plotly.graph_objects as go
from scipy import signal as sp_signal

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
# DSP ENGINE
# ─────────────────────────────────────────────
class DSPState:
    def __init__(self, signal_arr, fs, noise_level, filter_win):
        self.signal = signal_arr
        self.fs = fs
        self.noise_level = noise_level
        self.filter_win = max(1, filter_win)

        self.N = len(signal_arr)
        self.t = np.arange(self.N) / fs

        # Noise Generation
        rng = np.random.default_rng(42)
        self.noise = rng.normal(0, noise_level, self.N)
        self.noisy = self.signal + self.noise

        # Improved Filter (Zero-phase style to avoid lag without wrap-around glitches)
        self.filtered = self._filter()

        # FFT Analysis
        self.freqs, self.mags = self._fft(self.noisy)
        # Avoid index errors on empty signals
        if len(self.mags) > 0:
            self.dom_freq = self.freqs[np.argmax(self.mags)]
        else:
            self.dom_freq = 0

        # Nyquist & Aliasing
        self.nyquist = fs / 2
        self.alias_freq = self._alias()
        # Aliasing detection logic
        self.is_alias = self.dom_freq >= self.nyquist - 0.1 and noise_level < 0.5

        # SNR Calculation
        self.snr = self._snr()

    def _filter(self):
        if self.filter_win <= 1:
            return self.noisy
        kernel = np.ones(self.filter_win) / self.filter_win
        # Use 'same' and then manually adjust or use scipy for cleaner results
        return sp_signal.filtfilt(kernel, [1.0], self.noisy)

    def _fft(self, sig):
        n = 2 ** int(np.ceil(np.log2(len(sig))))
        window = np.hanning(len(sig))
        spec = np.fft.rfft(sig * window, n=n)
        freqs = np.fft.rfftfreq(n, d=1/self.fs)
        mags = np.abs(spec)
        return freqs, mags

    def _alias(self):
        # Calculates where the dominant frequency folds back to
        return abs(self.dom_freq - self.fs * np.round(self.dom_freq / self.fs))

    def _snr(self):
        sig_p = np.mean(self.signal**2)
        noi_p = np.mean(self.noise**2)
        if noi_p < 1e-10: return 99.9
        if sig_p < 1e-10: return -99.9
        return 10 * np.log10(sig_p / noi_p)

# ─────────────────────────────────────────────
# SIGNAL GENERATOR
# ─────────────────────────────────────────────
def gen_signal(t, f, a, wtype, dur):
    if wtype == "Sine":
        return a * np.sin(2 * np.pi * f * t)
    if wtype == "Square":
        return a * sp_signal.square(2 * np.pi * f * t)
    if wtype == "Triangle":
        return a * sp_signal.sawtooth(2 * np.pi * f * t, width=0.5)
    if wtype == "Sawtooth":
        return a * sp_signal.sawtooth(2 * np.pi * f * t)
    if wtype == "Chirp":
        return a * sp_signal.chirp(t, f0=0, f1=f, t1=dur, method='linear')
    return np.zeros_like(t)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("🎛️ Signal Controls")

wave = st.sidebar.selectbox("Waveform", ["Sine","Square","Triangle","Sawtooth","Chirp"])
freq = st.sidebar.slider("Signal Frequency (Hz)", 1, 100, 5)
fs = st.sidebar.slider("Sampling Rate (Hz)", 10, 1000, 200)
amp = st.sidebar.slider("Amplitude", 0.1, 3.0, 1.0)
duration = st.sidebar.slider("Duration (s)", 1, 5, 2)

st.sidebar.markdown("---")
st.sidebar.title("🛠️ Processing")
noise_level = st.sidebar.slider("Noise Level", 0.0, 2.0, 0.2)
filter_win = st.sidebar.slider("Smoothing Window", 1, 50, 11)

# ─────────────────────────────────────────────
# DATA PIPELINE
# ─────────────────────────────────────────────
N = int(fs * duration)
t_points = np.arange(N) / fs
raw_signal = gen_signal(t_points, freq, amp, wave, duration)

state = DSPState(raw_signal, fs, noise_level, filter_win)

# ─────────────────────────────────────────────
# DASHBOARD HEADER
# ─────────────────────────────────────────────
st.title("DSP Pro Lab")
m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Observed Freq", f"{state.dom_freq:.1f} Hz")
m2.metric("Sampling Rate", f"{fs} Hz")
m3.metric("Nyquist", f"{state.nyquist:.1f} Hz")
m4.metric("SNR", f"{state.snr:.1f} dB")
m5.metric("Samples", f"{len(state.t)}")

if state.is_alias:
    st.warning(f"⚠️ Aliasing Detected: The signal freq exceeds Nyquist ({state.nyquist}Hz). Folded freq: {state.alias_freq:.2f}Hz")
else:
    st.success("✅ Signal integrity maintained (Nyquist Criteria met).")

# ─────────────────────────────────────────────
# VISUALIZATION TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Time Domain", "📊 Frequency Domain", "🧪 Filter Analysis"])

with tab1:
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=state.t, y=state.signal, name="Clean", line=dict(color=COLORS["signal"])))
    fig_time.add_trace(go.Scatter(x=state.t, y=state.noisy, name="Noisy", line=dict(color=COLORS["noise"], width=0.5), opacity=0.5))
    fig_time.update_layout(title="Oscilloscope View", xaxis_title="Time (s)", yaxis_title="Amplitude")
    st.plotly_chart(fig_time, use_container_width=True)

with tab2:
    fig_freq = go.Figure()
    fig_freq.add_trace(go.Scatter(x=state.freqs, y=state.mags, name="Magnitude", fill='tozeroy', line=dict(color=COLORS["filtered"])))
    fig_freq.add_vline(x=state.nyquist, line_dash="dash", line_color="red", annotation_text="Nyquist")
    fig_freq.update_layout(title="FFT Spectrum", xaxis_title="Frequency (Hz)", yaxis_title="Magnitude")
    st.plotly_chart(fig_freq, use_container_width=True)

with tab3:
    fig_filt = go.Figure()
    fig_filt.add_trace(go.Scatter(x=state.t, y=state.noisy, name="Input", line=dict(color=COLORS["noise"]), opacity=0.4))
    fig_filt.add_trace(go.Scatter(x=state.t, y=state.filtered, name="Filtered Output", line=dict(color=COLORS["filtered"], width=2)))
    fig_filt.update_layout(title="Low-Pass Smoothing Results", xaxis_title="Time (s)")
    st.plotly_chart(fig_filt, use_container_width=True)

# ─────────────────────────────────────────────
# AUDIO ENGINE
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🔊 Audio Monitor")
if fs < 4000:
    st.info("Note: The current sampling rate is too low for standard audio hardware. Audio playback may sound distorted or fail.")

# Normalize audio to prevent clipping
audio_out = state.filtered / (np.max(np.abs(state.filtered)) + 1e-6)
st.audio(audio_out, sample_rate=fs)
