
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import wave
import io

st.set_page_config(page_title="DSP Pro Lab", layout="wide")

st.title("DSP  Lab - Interactive Signal Processing Playground")

st.sidebar.header("Signal Controls")

signal_type = st.sidebar.selectbox("Signal Type", ["Sine","Square","Triangle"])
freq = st.sidebar.slider("Signal Frequency (Hz)",1,50,5)
fs = st.sidebar.slider("Sampling Frequency (Hz)",1,100,20)
duration = st.sidebar.slider("Duration (seconds)",1,5,2)

t = np.linspace(0,duration,2000)
ts = np.arange(0,duration,1/fs)

if signal_type=="Sine":
    signal=np.sin(2*np.pi*freq*t)
    sampled=np.sin(2*np.pi*freq*ts)

elif signal_type=="Square":
    signal=np.sign(np.sin(2*np.pi*freq*t))
    sampled=np.sign(np.sin(2*np.pi*freq*ts))

elif signal_type=="Triangle":
    signal=2*np.arcsin(np.sin(2*np.pi*freq*t))/np.pi
    sampled=2*np.arcsin(np.sin(2*np.pi*freq*ts))/np.pi

nyquist=2*freq

col1,col2=st.columns(2)

with col1:
    st.subheader("Continuous Signal")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=t,y=signal,mode="lines",name="Continuous"))
    st.plotly_chart(fig,use_container_width=True)

with col2:
    st.subheader("Sampled Signal")
    fig2=go.Figure()
    fig2.add_trace(go.Scatter(x=t,y=signal,mode="lines",name="Original"))
    fig2.add_trace(go.Scatter(x=ts,y=sampled,mode="markers",name="Samples"))
    st.plotly_chart(fig2,use_container_width=True)

st.divider()

st.subheader("Nyquist Analysis")

c1,c2,c3=st.columns(3)
c1.metric("Signal Frequency",f"{freq} Hz")
c2.metric("Sampling Frequency",f"{fs} Hz")
c3.metric("Nyquist Requirement",f"{nyquist} Hz")

if fs < nyquist:
    st.error("Aliasing detected: sampling rate below Nyquist.")
else:
    st.success("Sampling satisfies Nyquist theorem.")

st.divider()

st.subheader("Aliasing Visualization")

alias_freq=abs(fs-freq)

fig3=go.Figure()
fig3.add_trace(go.Scatter(x=t,y=np.sin(2*np.pi*freq*t),mode="lines",name="Original"))
fig3.add_trace(go.Scatter(x=t,y=np.sin(2*np.pi*alias_freq*t),mode="lines",name="Aliased"))
st.plotly_chart(fig3,use_container_width=True)

st.divider()

st.subheader("FFT Spectrum Analyzer")

fft=np.fft.fft(signal)
freqs=np.fft.fftfreq(len(signal),d=(duration/len(signal)))
mask=freqs>=0

fig4=go.Figure()
fig4.add_trace(go.Scatter(x=freqs[mask],y=np.abs(fft)[mask],mode="lines"))
st.plotly_chart(fig4,use_container_width=True)

st.divider()

st.subheader("Audio File Signal Analyzer")

uploaded=st.file_uploader("Upload WAV file")

if uploaded:
    audio_bytes=uploaded.read()
    wf=wave.open(io.BytesIO(audio_bytes),'rb')
    rate=wf.getframerate()
    frames=wf.readframes(wf.getnframes())
    audio=np.frombuffer(frames,dtype=np.int16)

    st.write("Sampling Rate:",rate,"Hz")

    audio=audio[:5000]

    fig_audio=go.Figure()
    fig_audio.add_trace(go.Scatter(y=audio,mode="lines"))
    st.plotly_chart(fig_audio,use_container_width=True)

st.divider()

st.subheader("Noise Reduction Demo")

noise=np.random.normal(0,0.5,len(signal))
noisy=signal+noise

window=20
smooth=np.convolve(noisy,np.ones(window)/window,mode="same")

fig_noise=go.Figure()
fig_noise.add_trace(go.Scatter(x=t,y=noisy,mode="lines",name="Noisy"))
fig_noise.add_trace(go.Scatter(x=t,y=smooth,mode="lines",name="Filtered"))
st.plotly_chart(fig_noise,use_container_width=True)

st.markdown("Nyquist Sampling Theorem: Fs >= 2 * Fmax")


