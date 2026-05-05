# DSP PRO LAB — ULTIMATE VERSION 🔥

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide", page_title="DSP Ultimate Lab")

# =========================
# ⚡ PERFORMANCE CACHE
# =========================
@st.cache_data(show_spinner=False)
def gen_signal(t, f, a):
    return a * np.sin(2 * np.pi * f * t)

@st.cache_data(show_spinner=False)
def compute_fft(sig, fs):
    n = len(sig)
    fft = np.fft.rfft(sig * np.hanning(n))
    freqs = np.fft.rfftfreq(n, d=1/fs)
    mags = np.abs(fft)
    return freqs, mags

# =========================
# 🎛️ SIDEBAR
# =========================
st.sidebar.title("Controls")

freq = st.sidebar.slider("Signal Frequency (Hz)", 1, 50, 5)
fs = st.sidebar.slider("Sampling Rate (Hz)", 2, 200, 40)
amp = st.sidebar.slider("Amplitude", 0.1, 3.0, 1.0)
noise_level = st.sidebar.slider("Noise", 0.0, 1.0, 0.0)

teach_mode = st.sidebar.toggle("🎓 Teaching Mode", True)

# =========================
# 🧠 SIGNAL GENERATION
# =========================
N = 2000
duration = 2

t = np.linspace(0, duration, N)
ts = np.arange(0, duration, 1/fs)

signal = gen_signal(t, freq, amp)
sampled = gen_signal(ts, freq, amp)

noise = np.random.normal(0, noise_level, N)
noisy = signal + noise

# =========================
# 📉 ALIASING
# =========================
alias_f = abs((freq + fs/2) % fs - fs/2)
is_alias = fs < 2 * freq

# =========================
# 📊 FFT + DSP METRICS
# =========================
freqs, mags = compute_fft(noisy, N/duration)

dom_idx = np.argmax(mags)
dom_freq = freqs[dom_idx]

signal_power = np.mean(signal**2)
noise_power = np.mean((noisy - signal)**2)

snr_db = 10 * np.log10(signal_power / max(noise_power, 1e-12))

harmonics = mags.copy()
harmonics[dom_idx] = 0
harmonics[0] = 0

harm_rms = np.sqrt(np.sum(harmonics**2))
fundamental = max(mags[dom_idx], 1e-12)

thd_pct = (harm_rms / fundamental) * 100

# =========================
# 📈 OSCILLOSCOPE
# =========================
st.title("🔬 DSP Ultimate Lab")

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=signal, name="Continuous"))

    if teach_mode:
        fig.add_annotation(text="Continuous Signal",
                           x=0.1, y=1,
                           showarrow=False)

    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=ts, y=sampled,
                              mode="markers",
                              name="Samples"))

    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 🔥 TRUE SINC RECONSTRUCTION
# =========================
st.subheader("🔥 True Reconstruction (Sinc)")

t_dense = np.linspace(0, duration, 4000)

def sinc_interp(x, s, u):
    if len(s) < 2:
        return np.zeros_like(u)
    T = s[1] - s[0]
    sinc_matrix = np.sinc((u[:, None] - s[None, :]) / T)
    return np.dot(sinc_matrix, x)

recon = sinc_interp(sampled, ts, t_dense)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=t_dense, y=recon, name="Reconstructed"))
fig3.add_trace(go.Scatter(x=t, y=signal, name="Original"))
fig3.add_trace(go.Scatter(x=ts, y=sampled, mode="markers", name="Samples"))

st.plotly_chart(fig3, use_container_width=True)

# =========================
# 📊 FFT
# =========================
st.subheader("📊 FFT Spectrum")

fig4 = go.Figure()
fig4.add_trace(go.Bar(x=freqs, y=mags))

if teach_mode:
    fig4.add_annotation(
        x=dom_freq,
        y=max(mags),
        text="Fundamental",
        showarrow=True
    )

st.plotly_chart(fig4, use_container_width=True)

# =========================
# 📊 METRICS
# =========================
col1, col2, col3 = st.columns(3)
col1.metric("SNR", f"{snr_db:.2f} dB")
col2.metric("THD", f"{thd_pct:.2f}%")
col3.metric("Alias Freq", f"{alias_f:.2f} Hz")

if is_alias:
    st.error("⚠ Aliasing Occurs")
else:
    st.success("✅ No Aliasing")

# =========================
# 📄 PDF EXPORT
# =========================
def generate_pdf():
    doc = SimpleDocTemplate("/mnt/data/dsp_report.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("DSP Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Frequency: {freq} Hz", styles["Normal"]))
    content.append(Paragraph(f"Sampling Rate: {fs} Hz", styles["Normal"]))
    content.append(Paragraph(f"SNR: {snr_db:.2f} dB", styles["Normal"]))
    content.append(Paragraph(f"THD: {thd_pct:.2f}%", styles["Normal"]))

    doc.build(content)
    return "/mnt/data/dsp_report.pdf"

if st.button("📄 Export PDF"):
    path = generate_pdf()
    with open(path, "rb") as f:
        st.download_button("Download Report", f, file_name="DSP_Report.pdf")
