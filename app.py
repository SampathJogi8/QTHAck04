import io, wave
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="DSP Pro Lab", layout="wide")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def next_pow2(n):
    return 1 if n <= 1 else 2**int(np.ceil(np.log2(n)))

def gen_signal(t, f, a, kind, dur):
    if kind == "Sine":
        return a*np.sin(2*np.pi*f*t)
    if kind == "Square":
        return a*np.sign(np.sin(2*np.pi*f*t))
    if kind == "Triangle":
        return a*(2/np.pi)*np.arcsin(np.sin(2*np.pi*f*t))
    if kind == "Sawtooth":
        return a*(2*((t*f)%1)-1)
    if kind == "Chirp":
        k = f/max(dur,1e-9)
        return a*np.sin(2*np.pi*(0*t + 0.5*k*t**2))
    return np.zeros_like(t)

def moving_avg(x, M):
    M = max(1,int(M))
    y = np.convolve(x, np.ones(M)/M, mode="same")
    return np.roll(y, -M//2)

def compute_fft(x, fs):
    n = next_pow2(len(x))
    win = np.hanning(len(x))
    spec = np.fft.rfft(x*win, n=n)
    freqs = np.fft.rfftfreq(n, d=1/fs)
    mags = np.abs(spec)
    return freqs, mags

def alias_freq(f, fs):
    return abs(f - fs*np.round(f/fs))

def load_wav(file):
    file.seek(0)
    with wave.open(io.BytesIO(file.read()), "rb") as wf:
        rate = wf.getframerate()
        ch = wf.getnchannels()
        frames = wf.getnframes()
        raw = wf.readframes(frames)

    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float64)

    if ch > 1:
        audio = audio.reshape(-1, ch).mean(axis=1)

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio /= peak

    return audio, rate

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")

    uploaded = st.file_uploader("Upload WAV", type=["wav"])
    use_audio = uploaded is not None

    if use_audio:
        st.info("Audio mode active")

    wave_type = st.selectbox("Waveform", ["Sine","Square","Triangle","Sawtooth","Chirp"], disabled=use_audio)
    freq = st.slider("Frequency",1,50,5,disabled=use_audio)
    fs = st.slider("Sampling Rate",10,1000,200)
    amp = st.slider("Amplitude",0.1,3.0,1.0,disabled=use_audio)
    dur = st.slider("Duration",1,5,2,disabled=use_audio)

    noise_level = st.slider("Noise",0.0,2.0,0.0)
    filt_M = st.slider("Filter Window",2,80,10)

# ─────────────────────────────────────────────
# PIPELINE (SINGLE SOURCE OF TRUTH)
# ─────────────────────────────────────────────
if use_audio:
    try:
        audio, ar = load_wav(uploaded)
        N = int(fs*2)
        idx = np.linspace(0, len(audio)-1, N).astype(int)
        signal = audio[idx]
    except:
        st.error("Invalid audio file")
        st.stop()
else:
    N = int(fs*dur)
    t = np.arange(N)/fs
    signal = gen_signal(t, freq, amp, wave_type, dur)

t = np.arange(len(signal))/fs

# noise + filter
rng = np.random.default_rng(42)
noise = rng.normal(0, noise_level, len(signal))
noisy = signal + noise
filtered = moving_avg(noisy, filt_M)

# FFT
freqs, mags = compute_fft(noisy, fs)
dom_freq = float(freqs[np.argmax(mags)])

# metrics
nyq = fs/2
alias = alias_freq(dom_freq, fs)
is_alias = dom_freq > nyq

signal_power = np.mean(signal**2)
noise_power = np.mean(noise**2) if noise_level>0 else 1e-12
snr = 10*np.log10(signal_power/noise_power)

# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Dominant Freq",f"{dom_freq:.2f} Hz")
c2.metric("Fs",f"{fs}")
c3.metric("Nyquist",f"{nyq:.2f}")
c4.metric("Alias",f"{alias:.2f}")
c5.metric("SNR",f"{snr:.2f} dB")

st.info("⚠ Aliasing" if is_alias else "✅ No Aliasing")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "Oscilloscope","FFT","Phase","Filter Lab",
    "Waterfall","Lissajous","Audio Analyzer"
])

# ───────────────── OSCILLOSCOPE ─────────────────
with tabs[0]:
    st.subheader("Time Domain")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    fig.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))

    st.plotly_chart(fig,use_container_width=True)

# ───────────────── FFT ─────────────────
with tabs[1]:
    st.subheader("Frequency Spectrum")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freqs,y=mags,name="Spectrum"))
    fig.add_vline(x=dom_freq,line_dash="dash")
    fig.add_vline(x=alias,line_dash="dot")

    st.plotly_chart(fig,use_container_width=True)

# ───────────────── PHASE ─────────────────
with tabs[2]:
    st.subheader("Phase Space")

    lag = st.slider("Lag",1,50,5)
    x = noisy[:-lag]
    y = noisy[lag:]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x,y=y,mode="lines"))

    st.plotly_chart(fig,use_container_width=True)

# ───────────────── FILTER LAB ─────────────────
with tabs[3]:
    st.subheader("Filtering Process")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    st.plotly_chart(fig1,use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    st.plotly_chart(fig2,use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))
    st.plotly_chart(fig3,use_container_width=True)

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig4.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    fig4.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))
    st.plotly_chart(fig4,use_container_width=True)

# ───────────────── WATERFALL ─────────────────
with tabs[4]:
    st.subheader("Spectrogram")

    frame = 256
    hop = 128
    spec = []

    for i in range(0, len(noisy)-frame, hop):
        chunk = noisy[i:i+frame]*np.hanning(frame)
        spec.append(np.abs(np.fft.rfft(chunk)))

    if len(spec) > 0:
        fig = go.Figure(go.Heatmap(z=np.array(spec).T))
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.warning("Signal too short")

# ───────────────── LISSAJOUS ─────────────────
with tabs[5]:
    st.subheader("Lissajous")

    f2 = st.slider("Y Frequency",1,50,3)
    phase = st.slider("Phase",0,360,0)

    tt = np.linspace(0,2,5000)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.sin(2*np.pi*dom_freq*tt),
        y=np.sin(2*np.pi*f2*tt+np.radians(phase)),
        mode="lines"
    ))

    st.plotly_chart(fig,use_container_width=True)

# ───────────────── AUDIO ─────────────────
with tabs[6]:
    st.subheader("Audio Analyzer")

    if use_audio:
        st.audio(signal, sample_rate=fs)
        st.metric("Detected Frequency", f"{dom_freq:.2f} Hz")
    else:
        st.info("Upload a WAV file")
