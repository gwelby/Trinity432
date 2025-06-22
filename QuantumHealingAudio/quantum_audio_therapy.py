"""
Quantum Audio Therapy Generator
Created by Cascade | 2025-05-18

This script generates binaural beats and isochronic tones for healing and relaxation.
"""

import numpy as np
import sounddevice as sd
import time
import os
from datetime import datetime
import json
import wave
import struct
from scipy.io import wavfile

class QuantumAudioGenerator:
    def __init__(self, sample_rate=44100, duration=300, volume=0.5):
        """
        Initialize the audio generator.
        
        Parameters:
        - sample_rate: Samples per second (Hz)
        - duration: Duration in seconds
        - volume: Amplitude of the generated sound (0.0 to 1.0)
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.volume = volume
        self.t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create output directory if it doesn't exist
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Session log
        self.session_log = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_tone(self, frequency, tone_type='sine', phase=0.0):
        """Generate a single tone."""
        if tone_type == 'sine':
            return np.sin(2 * np.pi * frequency * self.t + phase)
        elif tone_type == 'square':
            return np.sign(np.sin(2 * np.pi * frequency * self.t + phase))
        elif tone_type == 'sawtooth':
            return 2 * (self.t * frequency - np.floor(0.5 + self.t * frequency))
        else:  # triangle
            return 2 * np.abs(2 * (self.t * frequency - np.floor(self.t * frequency + 0.5)))
    
    def generate_binaural_beat(self, base_freq, beat_freq, carrier_type='sine'):
        """Generate binaural beats."""
        left_freq = base_freq - (beat_freq / 2)
        right_freq = base_freq + (beat_freq / 2)
        
        left_channel = self.generate_tone(left_freq, carrier_type)
        right_channel = self.generate_tone(right_freq, carrier_type)
        
        # Combine channels
        stereo_sound = np.column_stack((left_channel, right_channel))
        
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(stereo_sound))
        if max_amplitude > 0:
            stereo_sound = (stereo_sound / max_amplitude) * self.volume
            
        return stereo_sound
    
    def generate_isochronic_tone(self, freq, pulse_freq, duty_cycle=0.5, carrier_type='sine'):
        """Generate isochronic tones."""
        # Generate the carrier wave
        carrier = self.generate_tone(freq, carrier_type)
        
        # Generate the pulse envelope
        pulse = np.zeros_like(self.t)
        pulse_period = 1.0 / pulse_freq
        samples_per_period = int(self.sample_rate / pulse_freq)
        samples_high = int(samples_per_period * duty_cycle)
        
        for i in range(0, len(pulse), samples_per_period):
            end = min(i + samples_high, len(pulse))
            pulse[i:end] = 1.0
        
        # Apply the pulse to the carrier
        mono_sound = carrier * pulse
        
        # Convert to stereo
        stereo_sound = np.column_stack((mono_sound, mono_sound))
        
        # Normalize
        max_amplitude = np.max(np.abs(stereo_sound))
        if max_amplitude > 0:
            stereo_sound = (stereo_sound / max_amplitude) * self.volume
            
        return stereo_sound
    
    def mix_sounds(self, *sounds):
        """Mix multiple sounds together."""
        if not sounds:
            return None
            
        # Find the maximum length
        max_len = max(s.shape[0] for s in sounds if s is not None)
        
        # Initialize output with zeros
        mixed = np.zeros((max_len, 2))
        
        # Sum all sounds
        for s in sounds:
            if s is not None:
                # Ensure the sound is the correct shape
                if len(s.shape) == 1:
                    s = np.column_stack((s, s))  # Convert mono to stereo
                elif s.shape[1] == 1:
                    s = np.column_stack((s, s))  # Convert mono to stereo
                
                # Ensure the sound is the right length
                if s.shape[0] < max_len:
                    # Pad with zeros if needed
                    pad_len = max_len - s.shape[0]
                    s = np.pad(s, ((0, pad_len), (0, 0)), 'constant')
                elif s.shape[0] > max_len:
                    # Truncate if needed
                    s = s[:max_len, :]
                
                mixed += s
        
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(mixed))
        if max_amplitude > 0:
            mixed = (mixed / max_amplitude) * self.volume
            
        return mixed
    
    def save_audio(self, audio, filename, format='wav'):
        """Save audio to file."""
        if audio is None:
            print("No audio data to save.")
            return
            
        # Ensure the audio is in the correct range
        audio = np.clip(audio, -1.0, 1.0)
        
        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Save as WAV file
        output_path = os.path.join(self.output_dir, f"{filename}.wav")
        wavfile.write(output_path, self.sample_rate, audio_int16)
        
        print(f"Saved audio to {output_path}")
        return output_path
    
    def play_audio(self, audio):
        """Play audio through the default sound device."""
        if audio is None:
            print("No audio data to play.")
            return
            
        try:
            sd.play(audio, self.sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def log_session(self, settings, audio_path):
        """Log the session details."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'settings': settings,
            'audio_file': audio_path,
            'duration_seconds': self.duration,
            'sample_rate': self.sample_rate,
            'volume': self.volume
        }
        
        self.session_log.append(log_entry)
        
        # Save log to file
        log_file = os.path.join(self.output_dir, 'session_log.json')
        with open(log_file, 'w') as f:
            json.dump(self.session_log, f, indent=2)
        
        return log_entry

def main():
    # Initialize the generator (5 minutes duration by default)
    generator = QuantumAudioGenerator(duration=300, volume=0.5)
    
    # Example 1: Pain Relief Protocol
    print("\n=== Generating Pain Relief Protocol ===")
    pain_relief_settings = {
        'name': 'Pain Relief',
        'description': 'Combines 174Hz (pain relief) with 7.83Hz (Schumann Resonance)',
        'base_frequency': 174,
        'beat_frequency': 7.83,
        'carrier_type': 'sine',
        'audio_type': 'binaural'
    }
    
    # Generate the audio
    if pain_relief_settings['audio_type'] == 'binaural':
        audio = generator.generate_binaural_beat(
            pain_relief_settings['base_frequency'],
            pain_relief_settings['beat_frequency'],
            pain_relief_settings['carrier_type']
        )
    else:
        audio = generator.generate_isochronic_tone(
            pain_relief_settings['base_frequency'],
            pain_relief_settings['beat_frequency'],
            0.5,  # duty cycle
            pain_relief_settings['carrier_type']
        )
    
    # Save and play
    filename = f"{pain_relief_settings['name'].lower().replace(' ', '_')}_{generator.session_id}"
    audio_path = generator.save_audio(audio, filename)
    
    # Log the session
    log_entry = generator.log_session(pain_relief_settings, audio_path)
    
    print("\n=== Audio Generation Complete ===")
    print(f"Settings: {json.dumps(pain_relief_settings, indent=2)}")
    print(f"Audio saved to: {audio_path}")
    
    # Ask if user wants to play the audio
    play = input("\nWould you like to play the audio now? (y/n): ").lower()
    if play == 'y':
        print("Playing audio... (Press Ctrl+C to stop)")
        generator.play_audio(audio)
    
    print("\nSession complete. You can find your audio files in the 'output' directory.")

if __name__ == "__main__":
    main()
