# 🔬 DSP Pro Lab — Team 8vaults
**Problem Statement 18: Sampling & Aliasing Visual Demonstrator**

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open your browser at **http://localhost:8501**

---

## Modules
| Module | What it demonstrates |
|---|---|
| **Oscilloscope** | Continuous vs sampled signal + aliasing visualisation (core PS-18) |
| **FFT Spectrum** | Magnitude & dB power spectrum, dominant freq, alias marker |
| **Phase Space** | Phase portrait (time-delay embedding) + autocorrelation |
| **Filter Lab** | FIR moving-average: original / noisy / filtered — 4 separate views |
| **Waterfall Plot** | Short-Time FFT spectrogram (time × frequency × power) |
| **Lissajous Figures** | XY parametric curves for frequency ratio & phase |
| **Audio Analyzer** | WAV upload → waveform, spectrum, spectrogram |

## Key Concepts Covered
- Nyquist–Shannon sampling theorem: `Fs ≥ 2·f_max`
- Alias frequency formula: `f_alias = |f − round(f/Fs)·Fs|`
- DFT/FFT with Hanning window & zero-padding
- FIR moving-average filter frequency response
- STFT / spectrogram analysis

## Fixes vs Original
- **Filter Lab**: split into 4 clear panels (original / noisy / filtered / comparison) instead of one cluttered overlay
- **Waterfall**: heatmap transposed so frequency is on Y-axis (standard convention)
- **Oscilloscope**: sample stems added, alias trace only shown when aliasing is active, alias formula shown in title
- **FFT Spectrum**: alias frequency marked with yellow dotted line when active
- **Lissajous**: LCM-based cycle count for complete closed figures
- **Status bar**: 5th card added showing live alias frequency
- **Audio Analyzer**: spectrogram frame size scales with file length for better time resolution
