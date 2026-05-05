import io, wave
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="DSP Pro Lab", layout="wide")

# ─────────────────────────────
# FUNCTIONS
# ─────────────────────────────
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
        k = f/dur
        return a*np.sin(2*np.pi*(0*t + 0.5*k*t**2))
    return np.zeros_like(t)

def moving_avg(x, M):
    M = max(1,int(M))
    y = np.convolve(x, np.ones(M)/M, mode="same")
    return np.roll(y, -M//2)

def compute_fft(x, fs):
    n = 2**int(np.ceil(np.log2(len(x))))
    spec = np.fft.rfft(x*np.hanning(len(x)), n=n)
    freqs = np.fft.rfftfreq(n, 1/fs)
    mags = np.abs(spec)
    return freqs, mags

def alias_freq(f, fs):
    return abs(f - fs*np.round(f/fs))

# ✅ FIXED AUDIO LOADER
def load_wav(uploaded_file):
    try:
        uploaded_file.seek(0)
        data = uploaded_file.read()

        with wave.open(io.BytesIO(data), "rb") as wf:
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

    except Exception:
        return None, None

# ─────────────────────────────
# SIDEBAR
# ─────────────────────────────
with st.sidebar:
    st.header("Controls")

    uploaded = st.file_uploader("Upload WAV", type=["wav"])
    use_audio = uploaded is not None

    wave_type = st.selectbox("Waveform", ["Sine","Square","Triangle","Sawtooth","Chirp"], disabled=use_audio)
    freq = st.slider("Frequency",1,50,5,disabled=use_audio)
    fs = st.slider("Sampling Rate",10,1000,200)
    amp = st.slider("Amplitude",0.1,3.0,1.0,disabled=use_audio)
    dur = st.slider("Duration",1,5,2,disabled=use_audio)

    noise_level = st.slider("Noise",0.0,2.0,0.0)
    filt_M = st.slider("Filter Window",2,80,10)

# ─────────────────────────────
# PIPELINE
# ─────────────────────────────
if use_audio:
    audio, ar = load_wav(uploaded)

    if audio is None:
        st.error("Invalid WAV file")
        st.stop()

    N = int(fs*2)
    idx = np.linspace(0,len(audio)-1,N).astype(int)
    signal = audio[idx]

else:
    N = int(fs*dur)
    t = np.arange(N)/fs
    signal = gen_signal(t,freq,amp,wave_type,dur)

t = np.arange(len(signal))/fs

rng = np.random.default_rng(42)
noise = rng.normal(0,noise_level,len(signal))
noisy = signal + noise
filtered = moving_avg(noisy,filt_M)

freqs, mags = compute_fft(noisy,fs)
dom_freq = float(freqs[np.argmax(mags)])

nyq = fs/2
alias = alias_freq(dom_freq,fs)
is_alias = dom_freq > nyq

signal_power = np.mean(signal**2)
noise_power = np.mean(noise**2)+1e-9
snr = 10*np.log10(signal_power/noise_power)

# ─────────────────────────────
# METRICS
# ─────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Dominant Freq",f"{dom_freq:.2f}")
c2.metric("Fs",f"{fs}")
c3.metric("Nyquist",f"{nyq:.2f}")
c4.metric("Alias",f"{alias:.2f}")
c5.metric("SNR",f"{snr:.2f} dB")

st.info("⚠ Aliasing" if is_alias else "✅ No Aliasing")

# ─────────────────────────────
# TABS
# ─────────────────────────────
tabs = st.tabs([
    "Oscilloscope","FFT","Phase","Filter",
    "Waterfall","Lissajous","Audio"
])

# OSCILLOSCOPE
with tabs[0]:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    fig.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))
    st.plotly_chart(fig, key="scope", width='stretch')

# FFT
with tabs[1]:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=freqs,y=mags))
    fig.add_vline(x=dom_freq)
    fig.add_vline(x=alias,line_dash="dot")
    st.plotly_chart(fig, key="fft", width='stretch')

# PHASE
with tabs[2]:
    lag=st.slider("Lag",1,50,5)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=noisy[:-lag],y=noisy[lag:],mode="lines"))
    st.plotly_chart(fig, key="phase", width='stretch')

# FILTER
with tabs[3]:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    fig.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))
    st.plotly_chart(fig, key="filter", width='stretch')

# WATERFALL
with tabs[4]:
    frame=256
    hop=128
    spec=[]
    for i in range(0,len(noisy)-frame,hop):
        chunk=noisy[i:i+frame]*np.hanning(frame)
        spec.append(np.abs(np.fft.rfft(chunk)))

    if len(spec)>0:
        fig=go.Figure(go.Heatmap(z=np.array(spec).T))
        st.plotly_chart(fig, key="waterfall", width='stretch')

# LISSAJOUS
with tabs[5]:
    f2=st.slider("Y freq",1,50,3)
    phase=st.slider("Phase",0,360,0)
    tt=np.linspace(0,2,5000)

    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=np.sin(2*np.pi*dom_freq*tt),
        y=np.sin(2*np.pi*f2*tt+np.radians(phase)),
        mode="lines"
    ))
    st.plotly_chart(fig, key="liss", width='stretch')

# AUDIO
with tabs[6]:
    if use_audio:
        st.audio(signal,sample_rate=fs)
        st.metric("Detected Frequency", f"{dom_freq:.2f}")
    else:
        st.info("Upload WAV file")
