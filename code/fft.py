import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

def analyze_bands(audio_path):
    sample_rate, audio_data = wavfile.read(audio_path)
    
    fft_result = np.fft.fft(audio_data)
    frequencies = np.fft.fftfreq(len(audio_data), 1/sample_rate)
    
    magnitudes = np.abs(fft_result)
    
    # from canvas description
    low_band = (0, 300)
    mid_band = (300, 2000)
    high_band = (2000, sample_rate//2)  
    
    def get_band_energy(freqs, mags, band):
        mask = (freqs >= band[0]) & (freqs <= band[1])
        return np.sum(mags[mask]**2)
    
    low_energy = get_band_energy(frequencies, magnitudes, low_band)
    mid_energy = get_band_energy(frequencies, magnitudes, mid_band)
    high_energy = get_band_energy(frequencies, magnitudes, high_band)
    
    # plt.figure(figsize=(12, 6))
    
    # positive_freq_mask = frequencies >= 0
    # plt.semilogx(frequencies[positive_freq_mask], 
    #              20 * np.log10(magnitudes[positive_freq_mask]))
    
    # plt.axvline(x=300, color='r', linestyle='--', label='(300 Hz)')
    # plt.axvline(x=2000, color='g', linestyle='--', label='(2000 Hz)')
    
    # plt.grid(True)
    # plt.xlabel('freq')
    # plt.ylabel('mag')
    # plt.legend()
    
    # print(f"(0-300 Hz): {low_energy:.2e}")
    # print(f"(300-2000 Hz): {mid_energy:.2e}")
    # print(f"(2000+ Hz): {high_energy:.2e}")
    
    # plt.show(block=False) # to get it to go next 
    # plt.pause(1)  
    # plt.close()  
    return sample_rate, audio_data, fft_result, frequencies, low_energy, mid_energy, high_energy

def equalize_bands(sample_rate, audio_data, fft_result, frequencies, low_energy, mid_energy, high_energy):
    target_energy = np.mean([low_energy, mid_energy, high_energy])
    
    low_scale = np.sqrt(target_energy / low_energy) if low_energy > 0 else 1
    mid_scale = np.sqrt(target_energy / mid_energy) if mid_energy > 0 else 1
    high_scale = np.sqrt(target_energy / high_energy) if high_energy > 0 else 1
    # print(f"Scaling factors - Low: {low_scale:.2f}, Mid: {mid_scale:.2f}, High: {high_scale:.2f}")
    
    pos_low_mask = (frequencies >= 0) & (frequencies <= 300)
    pos_mid_mask = (frequencies > 300) & (frequencies <= 2000)
    pos_high_mask = (frequencies > 2000) & (frequencies <= sample_rate//2)
    
    neg_low_mask = (frequencies >= -300) & (frequencies < 0)
    neg_mid_mask = (frequencies >= -2000) & (frequencies < -300)
    neg_high_mask = (frequencies < -2000) & (frequencies >= -sample_rate//2)
    
    equalized_fft = fft_result.copy()
    
    equalized_fft[pos_low_mask] *= low_scale
    equalized_fft[pos_mid_mask] *= mid_scale
    equalized_fft[pos_high_mask] *= high_scale
    
    equalized_fft[neg_low_mask] *= low_scale
    equalized_fft[neg_mid_mask] *= mid_scale
    equalized_fft[neg_high_mask] *= high_scale
    
    equalized_audio = np.real(np.fft.ifft(equalized_fft))
    
    equalized_audio = equalized_audio / np.max(np.abs(equalized_audio))
    
    # equalized_magnitudes = np.abs(equalized_fft)
    # positive_freq_mask = frequencies >= 0
    
    # plt.figure(figsize=(12, 6))
    # plt.semilogx(frequencies[positive_freq_mask], 
    #              20 * np.log10(equalized_magnitudes[positive_freq_mask]))
    # plt.axvline(x=300, color='r', linestyle='--', label='(300 Hz)')
    # plt.axvline(x=2000, color='g', linestyle='--', label=' (2000 Hz)')
    # plt.grid(True)
    # plt.xlabel('freq')
    # plt.ylabel('mag')
    # plt.legend()
    # plt.show(block=False)  
    # plt.pause(1)  
    # plt.close()  
    
    wavfile.write("equalized_audio.wav", sample_rate, equalized_audio.astype(np.float32))
    return equalized_audio

def apply_compression(audio_data, threshold=0.5, ratio=3):
    # https://dsp.stackexchange.com/questions/10536/help-implementing-audio-dynamic-range-compression?noredirect=1&lq=1
    compressed = np.zeros_like(audio_data) # creating empty copy
    sign = np.sign(audio_data) # above below waveform
    abs_audio = np.abs(audio_data)
    
    epsilon = 1e-10
    abs_audio = abs_audio + epsilon
    
    log_audio = np.log(abs_audio)
    log_threshold = np.log(threshold + epsilon)

    # if absolute audio less than threshoold leave it alone, else reduce it  
    compressed_log = np.where(
        abs_audio <= threshold,
        log_audio,
        (1/ratio) * log_audio + (1 - 1/ratio) * log_threshold
    )
    
    compressed = np.exp(compressed_log)
    
    compressed *= sign
    
    compressed = (compressed - epsilon) / np.max(np.abs(compressed - epsilon))
    
    return compressed

audio_path = "sound-files/my_amazing_loop.wav"

results = analyze_bands(audio_path)

equalized_audio = equalize_bands(*results)

compressed_audio = apply_compression(equalized_audio)
wavfile.write("compressed.wav", results[0], compressed_audio.astype(np.float32))