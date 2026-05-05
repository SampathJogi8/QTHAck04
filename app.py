import io, wave
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="DSP Pro Lab", layout="wide", page_icon="🔬")

# COLORS
COL = {
    "green": "#10b981",
    "blue": "#3b82f6",
    "cyan": "#06b6d4",
    "orange": "#f59e0b",
    "red": "#ef4444",
    "text": "#cbd5e1",
}

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def next_pow2(n):
    p = 1
    while p < n:
        p <<= 1
    return p

def gen_signal(t, f, a, kind, dur):
    if kind == "Sine":
        return a * np.sin(2*np.pi*f*t)
    if kind == "Square":
        return a * np.sign(np.sin(2*np.pi*f*t))
    if kind == "Triangle":
        return a * (2/np.pi)*np.arcsin(np.sin(2*np.pi*f*t))
    if kind == "Sawtooth":
        return a*(2*((t*f)%1)-1)
    if kind == "Chirp":
        k = f/dur
        return a*np.sin(2*np.pi*(0*t + 0.5*k*t**2))
    return np.zeros_like(t)

def moving_avg(x, M):
    M = max(1, int(M))
    y = np.convolve(x, np.ones(M)/M, mode="same")
    return np.roll(y, -M//2)

def compute_fft(x, fs):
    n = next_pow2(len(x))
    spec = np.fft.rfft(x*np.hanning(len(x)), n=n)
    freqs = np.fft.rfftfreq(n, 1/fs)
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

    audio /= np.max(np.abs(audio))
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
# PIPELINE
# ─────────────────────────────────────────────
N = int(fs*(dur if not use_audio else 2))

if use_audio:
    try:
        audio, ar = load_wav(uploaded)
        idx = np.linspace(0,len(audio)-1,N).astype(int)
        signal = audio[idx]
        t = np.arange(len(signal))/fs
    except:
        st.error("Invalid audio")
        st.stop()
else:
    t = np.arange(N)/fs
    signal = gen_signal(t,freq,amp,wave_type,dur)

noise = np.random.normal(0,noise_level,len(signal))
noisy = signal + noise
filtered = moving_avg(noisy,filt_M)

freqs, mags = compute_fft(noisy,fs)
dom_freq = freqs[np.argmax(mags)]

nyq = fs/2
alias = alias_freq(dom_freq,fs)
is_alias = dom_freq > nyq

snr = 10*np.log10(np.mean(signal**2)/(np.mean(noise**2)+1e-9))

# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Dominant Freq",f"{dom_freq:.2f} Hz")
c2.metric("Sampling Rate",f"{fs}")
c3.metric("Nyquist",f"{nyq}")
c4.metric("Alias",f"{alias:.2f}")
c5.metric("SNR",f"{snr:.2f} dB")

st.info(f"{'⚠ Aliasing' if is_alias else '✅ No Aliasing'}")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "Oscilloscope","FFT","Phase","Filter","Waterfall","Lissajous","Audio"
])

# OSCILLOSCOPE
with tab1:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    fig.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))
    st.plotly_chart(fig,use_container_width=True)

# FFT
with tab2:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=freqs,y=mags))
    fig.add_vline(x=dom_freq)
    fig.add_vline(x=alias,line_dash="dot")
    st.plotly_chart(fig,use_container_width=True)

# PHASE
with tab3:
    lag=st.slider("Lag",1,50,5)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=noisy[:-lag],y=noisy[lag:],mode="lines"))
    st.plotly_chart(fig,use_container_width=True)

# FILTER
with tab4:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    fig.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))
    st.plotly_chart(fig,use_container_width=True)

# WATERFALL
with tab5:
    frame=256
    hop=128
    spec=[]
    for i in range(0,len(noisy)-frame,hop):
        chunk=noisy[i:i+frame]*np.hanning(frame)
        spec.append(np.abs(np.fft.rfft(chunk)))
    if len(spec)>0:
        fig=go.Figure(go.Heatmap(z=np.array(spec).T))
        st.plotly_chart(fig,use_container_width=True)

# LISSAJOUS
with tab6:
    f2=st.slider("Y freq",1,50,3)
    phase=st.slider("Phase",0,360,0)
    tt=np.linspace(0,2,5000)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=np.sin(2*np.pi*dom_freq*tt),
                             y=np.sin(2*np.pi*f2*tt+np.radians(phase)),
                             mode="lines"))
    st.plotly_chart(fig,use_container_width=True)

# AUDIO
with tab7:
    if use_audio:
        st.audio(signal,sample_rate=fs)
        st.write("Detected Frequency:",dom_freq)
    else:
        st.info("Upload audio")
