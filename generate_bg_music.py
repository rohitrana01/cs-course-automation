"""
generate_bg_music.py — Generates a smooth, royalty-free ambient synth tech groove
Designed to sit subtly (-20dB) behind voiceovers to maintain viewer attention and momentum.
"""
import os
import wave
import numpy as np

def generate_lofi_track(output_path="assets/audio/bg_music.wav", duration=40.0, sr=44100):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # 92 BPM chilled tech groove
    bpm = 92
    beat_sec = 60.0 / bpm
    bar_sec = beat_sec * 4
    
    # Chords: Dm9 -> G13 -> Cmaj9 -> Am9
    # Frequencies (Hz)
    chord_prog = [
        [146.83, 220.0, 261.63, 329.63, 440.0],   # Dm9
        [98.0, 196.0, 246.94, 329.63, 392.0],     # G13
        [130.81, 196.0, 246.94, 293.66, 392.0],   # Cmaj9
        [110.0, 164.81, 220.0, 261.63, 329.63]    # Am9
    ]
    
    synth_pad = np.zeros(num_samples, dtype=np.float32)
    
    # Synthesize smooth pad chords with gentle chorus
    for i, chord in enumerate(chord_prog):
        start_time = i * bar_sec
        # Repeat every 4 bars (16 beats)
        while start_time < duration:
            end_time = min(start_time + bar_sec, duration)
            mask = (t >= start_time) & (t < end_time)
            t_chord = t[mask] - start_time
            
            # Envelope (soft attack & release)
            env = np.ones_like(t_chord)
            attack = 0.4
            release = 0.4
            env[t_chord < attack] = t_chord[t_chord < attack] / attack
            t_rel = t_chord - (bar_sec - release)
            env[t_rel > 0] = np.maximum(0, 1.0 - t_rel[t_rel > 0] / release)
            
            for freq in chord:
                # Fundamental + gentle harmonics
                synth_pad[mask] += 0.035 * np.sin(2 * np.pi * freq * t_chord) * env
                synth_pad[mask] += 0.015 * np.sin(2 * np.pi * (freq * 1.002) * t_chord) * env
                synth_pad[mask] += 0.008 * np.sin(2 * np.pi * (freq * 2) * t_chord) * env
            
            start_time += bar_sec * len(chord_prog)

    # Sub-bass pulse on each measure
    bass_track = np.zeros(num_samples, dtype=np.float32)
    bass_notes = [73.42, 98.0, 65.41, 55.0] # D, G, C, A
    for i, b_freq in enumerate(bass_notes):
        st = i * bar_sec
        while st < duration:
            et = min(st + bar_sec, duration)
            mask = (t >= st) & (t < et)
            t_b = t[mask] - st
            env_b = np.exp(-1.5 * t_b)
            bass_track[mask] += 0.06 * np.sin(2 * np.pi * b_freq * t_b) * env_b
            st += bar_sec * len(bass_notes)

    # Soft hi-hat tick on 8th notes to keep pacing
    hat_track = np.zeros(num_samples, dtype=np.float32)
    eighth = beat_sec / 2.0
    for beat_idx in range(int(duration / eighth)):
        tick_time = beat_idx * eighth
        mask = (t >= tick_time) & (t < tick_time + 0.04)
        t_h = t[mask] - tick_time
        noise = (np.random.rand(len(t_h)) * 2 - 1) * np.exp(-90 * t_h)
        hat_track[mask] += 0.015 * noise

    # Mix together & normalize
    mix = synth_pad + bass_track + hat_track
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = (mix / max_val) * 0.45  # Normalize to -7dB peak
        
    int_samples = (mix * 32767).astype(np.int16)
    
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int_samples.tobytes())
        
    print(f"[+] Generated Lo-Fi Tech Beat: {output_path} ({duration}s)")
    return output_path

if __name__ == "__main__":
    generate_lofi_track()
