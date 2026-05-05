import io, wave
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="DSP Pro Lab", layout="wide")

# ─────────────────────────────
# FUNCTIONS
# ─────────────────────────────
def gen_signal(t,f,a,typ,dur):
    if typ=="Sine": return a*np.sin(2*np.pi*f*t)
    if typ=="Square": return a*np.sign(np.sin(2*np.pi*f*t))
    if typ=="Triangle": return a*(2/np.pi)*np.arcsin(np.sin(2*np.pi*f*t))
    if typ=="Sawtooth": return a*(2*((t*f)%1)-1)
    if typ=="Chirp":
        k=f/dur
        return a*np.sin(2*np.pi*(0*t+0.5*k*t**2))
    return np.zeros_like(t)

def moving_avg(x,M):
    y=np.convolve(x,np.ones(M)/M,mode="same")
    return np.roll(y,-M//2)

def compute_fft(x,fs):
    n=2**int(np.ceil(np.log2(len(x))))
    spec=np.fft.rfft(x*np.hanning(len(x)),n=n)
    freqs=np.fft.rfftfreq(n,1/fs)
    mags=np.abs(spec)
    power=mags**2
    return freqs,mags,power

def alias_freq(f,fs):
    return abs(f-fs*np.round(f/fs))

def load_wav(file):
    file.seek(0)
    with wave.open(io.BytesIO(file.read()),"rb") as wf:
        rate=wf.getframerate()
        ch=wf.getnchannels()
        raw=wf.readframes(wf.getnframes())

    audio=np.frombuffer(raw,dtype=np.int16).astype(float)
    if ch>1:
        audio=audio.reshape(-1,ch).mean(axis=1)

    audio/=np.max(np.abs(audio))+1e-9
    return audio,rate

# ─────────────────────────────
# SIDEBAR (FIXED)
# ─────────────────────────────
uploaded = st.sidebar.file_uploader("Upload Audio", type=["wav"])
use_audio = uploaded is not None   # ✅ FIX

teach = st.sidebar.toggle("🎓 Teaching Mode", True)

wave_type = st.sidebar.selectbox(
    "Wave", ["Sine","Square","Triangle","Sawtooth","Chirp"],
    disabled=use_audio
)

freq = st.sidebar.slider("Frequency",1,50,5,disabled=use_audio)
fs = st.sidebar.slider("Sampling Rate",50,1000,200)
amp = st.sidebar.slider("Amplitude",0.1,3.0,1.0,disabled=use_audio)
dur = st.sidebar.slider("Duration",1,5,2,disabled=use_audio)

noise_lvl = st.sidebar.slider("Noise",0.0,2.0,0.0)
filt = st.sidebar.slider("Filter Window",2,80,10)

# ─────────────────────────────
# SIGNAL PIPELINE
# ─────────────────────────────
if use_audio:
    audio,ar = load_wav(uploaded)
    N = int(fs*2)
    idx = np.linspace(0,len(audio)-1,N).astype(int)
    signal = audio[idx]
else:
    N = int(fs*dur)
    t = np.arange(N)/fs
    signal = gen_signal(t,freq,amp,wave_type,dur)

t = np.arange(len(signal))/fs

noise = np.random.normal(0,noise_lvl,len(signal))
noisy = signal + noise
filtered = moving_avg(noisy,filt)

freqs,mags,power = compute_fft(noisy,fs)
dom = float(freqs[np.argmax(mags)])

# ─────────────────────────────
# TABS
# ─────────────────────────────
tabs = st.tabs([
    "Oscilloscope","FFT","Phase","Filter",
    "Waterfall","Lissajous","Audio"
])

# ───────── OSCILLOSCOPE ─────────
with tabs[0]:
    st.markdown("### 01 Continuous Signal")
    st.plotly_chart(go.Figure(go.Scatter(x=t,y=signal)), key="osc1", width="stretch")

    st.markdown("### 02 Sampled Signal")
    st.plotly_chart(go.Figure(go.Scatter(x=t,y=signal,mode="markers")), key="osc2", width="stretch")

    st.markdown("### 03 Aliasing")
    alias = alias_freq(dom,fs)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig.add_trace(go.Scatter(x=t,y=np.sin(2*np.pi*alias*t),name="Alias"))
    st.plotly_chart(fig, key="osc3", width="stretch")

# ───────── FFT ─────────
with tabs[1]:
    st.markdown("### Magnitude Spectrum")
    st.plotly_chart(go.Figure(go.Scatter(x=freqs,y=mags)), key="fft1", width="stretch")

    st.markdown("### Power Spectrum")
    st.plotly_chart(go.Figure(go.Scatter(x=freqs,y=power)), key="fft2", width="stretch")

# ───────── PHASE ─────────
with tabs[2]:
    lag = 5
    st.markdown("### 01 Phase Portrait")
    st.plotly_chart(go.Figure(go.Scatter(x=noisy[:-lag],y=noisy[lag:],mode="lines")),
                    key="ph1", width="stretch")

    st.markdown("### 02 Autocorrelation")
    ac = np.correlate(noisy,noisy,mode="full")
    st.plotly_chart(go.Figure(go.Scatter(y=ac)), key="ph2", width="stretch")

# ───────── FILTER ─────────
with tabs[3]:
    st.markdown("### 01 Original")
    st.plotly_chart(go.Figure(go.Scatter(x=t,y=signal)), key="f1", width="stretch")

    st.markdown("### 02 Noisy")
    st.plotly_chart(go.Figure(go.Scatter(x=t,y=noisy)), key="f2", width="stretch")

    st.markdown("### 03 Filtered")
    st.plotly_chart(go.Figure(go.Scatter(x=t,y=filtered)), key="f3", width="stretch")

    st.markdown("### 04 Comparison")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,name="Original"))
    fig.add_trace(go.Scatter(x=t,y=noisy,name="Noisy"))
    fig.add_trace(go.Scatter(x=t,y=filtered,name="Filtered"))
    st.plotly_chart(fig, key="f4", width="stretch")

# ───────── WATERFALL ─────────
with tabs[4]:
    st.markdown("### STFT Spectrogram")
    frame,hop = 256,128
    spec = [np.abs(np.fft.rfft(noisy[i:i+frame]))
            for i in range(0,len(noisy)-frame,hop)]
    if len(spec)>0:
        st.plotly_chart(go.Figure(go.Heatmap(z=np.array(spec).T)),
                        key="wf", width="stretch")

# ───────── LISSAJOUS ─────────
with tabs[5]:
    f2 = st.slider("Y-axis Freq",1,50,3)
    phase = st.slider("Phase Offset",0,360,0)

    st.markdown("### 01 Lissajous Figure")
    tt = np.linspace(0,2,5000)
    st.plotly_chart(go.Figure(go.Scatter(
        x=np.sin(2*np.pi*dom*tt),
        y=np.sin(2*np.pi*f2*tt+np.radians(phase)),
        mode="lines")), key="liss", width="stretch")

# ───────── AUDIO ─────────
with tabs[6]:
    if use_audio:
        st.audio(signal, sample_rate=fs)
        st.metric("Detected Frequency", f"{dom:.2f} Hz")
    else:
        st.info("Upload WAV file")
