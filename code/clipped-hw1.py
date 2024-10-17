import numpy as np
from scipy.io import wavfile
import sounddevice as sd

sample_rate = 48000
duration = 1.0
frequency = 440
amplitude = 8192 

t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = amplitude * np.sin(2 * np.pi * frequency * t)
audio = audio.astype(np.int16)

wavfile.write('sound-files/sine.wav', sample_rate, audio)


amplitude_half = 16384  
clip_threshold = 8192  

audio_clipped = amplitude_half * np.sin(2 * np.pi * frequency * t)
audio_clipped = np.clip(audio_clipped, -clip_threshold, clip_threshold)
audio_clipped = audio_clipped.astype(np.int16)
wavfile.write('sound-files/clipped.wav', sample_rate, audio_clipped)

sd.play(audio_clipped / 32768.0, sample_rate)
sd.wait()
