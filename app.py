import io
import wave
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="DSP Pro Lab — 8vaults", layout="wide", page_icon="🔬")

# ---------------- HELPERS ----------------
def next_pow2(n: int) -> int:
    return 1 if n == 0 else 2 ** int(np.ceil(np.log2(n)))


def gen_signal(t, f, a, wtype, dur):
    if wtype == "Sine":
        return a * np.sin(2 * np.pi * f * t)
    if wtype == "Square":
        return a * np.sign(np.sin(2 * np.pi * f * t))
    if wtype == "Triangle":
        return a * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * f * t))
    if wtype == "Sawtooth":
        return a * (2 * ((t * f) % 1) - 1)
    if wtype == "Chirp":
        k = f / max(dur, 1e-9)
        return a * np.sin(2 * np.pi * (f * t + 0.5 * k * t**2))
    return np.zeros_like(t)


def compute_fft(sig, fs):
    n = next_pow2(len(sig))
    win = np.hanning(len(sig))

    scale = np.sum(win) / len(win)
    sig_win = (sig * win) / scale

    padded = np.zeros(n)
    padded[:len(sig)] = sig_win

    spectrum = np.fft.rfft(padded)
    freqs = np.fft.rfftfreq(n, 1 / fs)

    mags = np.abs(spectrum) / (n / 2)
    phase = np.angle(spectrum)

    max_mag = np.max(mags) if np.max(mags) > 0 else 1e-12
    power_db = 20 * np.log10(np.maximum(mags / max_mag, 1e-12))

    return freqs, mags, power_db, phase


def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size // 2:]


def load_wav(file):
    buf = io.BytesIO(file.read())
    wf = wave.open(buf, "rb")

    rate = wf.getframerate()
    nch = wf.getnchannels()
    frames = wf.getnframes()
    sw = wf.getsampwidth()

    raw = wf.readframes(frames)
    wf.close()

    if sw == 3:
        raise ValueError("24-bit WAV not supported")

    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw)
    audio = np.frombuffer(raw, dtype=dtype).astype(np.float64)

    if nch > 1:
        audio = audio[::nch]

    audio /= np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else 1

    return audio, rate


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Controls")

    signal_type = st.selectbox("Waveform", ["Sine", "Square", "Triangle", "Sawtooth", "Chirp"])
    freq = st.slider("Frequency (Hz)", 1, 50, 5)
    user_fs = st.slider("Sampling Rate (Hz)", 2, 200, 40)
    amp = st.slider("Amplitude", 0.1, 3.0, 1.0)
    duration = st.slider("Duration (s)", 1, 5, 2)

    uploaded_file = st.file_uploader("Upload WAV", type=["wav"])

# ---------------- SIGNAL ----------------
N = 4000

if uploaded_file:
    try:
        raw_audio, audio_rate = load_wav(uploaded_file)

        duration_audio = len(raw_audio) / audio_rate

        indices = np.linspace(0, len(raw_audio) - 1, N)
        signal = np.interp(indices, np.arange(len(raw_audio)), raw_audio)

        t = np.linspace(0, duration_audio, N)
        freq_eff = 5

    except Exception as e:
        st.error(f"Audio error: {e}")
        st.stop()
else:
    t = np.linspace(0, duration, N)
    signal = gen_signal(t, freq, amp, signal_type, duration)
    freq_eff = freq

# consistent fs
duration_safe = max((t[-1] - t[0]), 1e-9)
actual_fs = N / duration_safe

# ---------------- SAMPLING ----------------
ts = np.arange(0, t[-1], 1 / user_fs)
sampled = np.interp(ts, t, signal)

# ---------------- ALIASING ----------------
required_fs = 2 * freq_eff
is_alias = user_fs < required_fs

alias_f = abs(freq_eff - round(freq_eff / user_fs) * user_fs)

# ---------------- FFT ----------------
freqs, mags, power_db, phase = compute_fft(signal, actual_fs)

# ---------------- LAYOUT ----------------
st.title("🔬 DSP Pro Lab — Ultimate Version")

col1, col2 = st.columns(2)

# ---------------- TIME DOMAIN ----------------
with col1:
    st.subheader("Continuous Signal")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=signal))
    fig.update_layout(xaxis_title="Time", yaxis_title="Amplitude")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Sampled Signal")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=ts, y=sampled, mode='markers+lines'))
    fig2.update_layout(xaxis_title="Time", yaxis_title="Samples")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- FFT ----------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Magnitude Spectrum")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=freqs, y=mags))
    fig3.add_vline(x=user_fs/2, line_dash="dash")
    fig3.update_layout(xaxis_title="Frequency", yaxis_title="Magnitude")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Power Spectrum (dB)")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=freqs, y=power_db))
    fig4.update_layout(xaxis_title="Frequency", yaxis_title="dB")
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- PHASE ----------------
st.subheader("Phase Spectrum")
fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=freqs, y=phase))
st.plotly_chart(fig5, use_container_width=True)

# ---------------- PHASE PORTRAIT ----------------
st.subheader("Phase Portrait")
fig6 = go.Figure()
fig6.add_trace(go.Scatter(x=signal[:-1], y=signal[1:], mode='lines'))
st.plotly_chart(fig6, use_container_width=True)

# ---------------- AUTOCORRELATION ----------------
st.subheader("Autocorrelation R[k]")
r = autocorr(signal)
fig7 = go.Figure()
fig7.add_trace(go.Scatter(y=r))
st.plotly_chart(fig7, use_container_width=True)

# ---------------- ALIASING VISUAL ----------------
st.subheader("Aliasing Visualization")
alias_wave = np.sin(2 * np.pi * alias_f * t)

fig8 = go.Figure()
fig8.add_trace(go.Scatter(x=t, y=signal, name="Original"))
fig8.add_trace(go.Scatter(x=t, y=alias_wave, name="Aliased"))
st.plotly_chart(fig8, use_container_width=True)

# ---------------- STATUS ----------------
st.markdown("### 📊 Analysis")
st.write(f"Nyquist Rate: {required_fs:.2f} Hz")
st.write(f"Sampling Rate: {user_fs} Hz")
st.write(f"Aliasing: {'🔴 YES' if is_alias else '🟢 NO'}")
st.write(f"Aliased Frequency: {alias_f:.2f} Hz")
