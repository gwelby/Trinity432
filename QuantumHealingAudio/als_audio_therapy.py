#!/usr/bin/env python3
"""
ALS Quantum Audio Therapy Generator
Created: May 19, 2025
Frequency: 528Hz (Healing)
Coherence: φ

This script generates specialized audio therapy files calibrated to the specific 
phi-harmonic frequencies needed for ALS support. The audio files include both 
carrier frequencies and modulations designed to support neural pathways and 
mitochondrial function.
"""

import os
import numpy as np
import soundfile as sf
import sounddevice as sd
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
from datetime import datetime
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Define phi and related constants
PHI = 1.618033988749895
PHI_SQUARED = PHI * PHI
PHI_TO_PHI = PHI ** PHI

# Define core frequencies
GROUND_FREQ = 432.0  # Hz - Ground State
CREATE_FREQ = 528.0  # Hz - Creation Point
HEART_FREQ = 594.0   # Hz - Heart Field
UNITY_FREQ = 768.0   # Hz - Unity Wave

# Define modulation frequencies
DELTA_FREQ = 4.32    # Hz - Deep relaxation/neural regeneration
THETA_FREQ = 7.83    # Hz - Schumann resonance 
ALPHA_FREQ = 8.0     # Hz - Neural entrainment
GAMMA_FREQ = 40.0    # Hz - Neural synchronization

# Directory for saving audio files
ALS_AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "als_audio_files")
if not os.path.exists(ALS_AUDIO_DIR):
    os.makedirs(ALS_AUDIO_DIR)
    print(f"{Fore.GREEN}Created directory: {ALS_AUDIO_DIR}{Style.RESET_ALL}")

# Audio parameters
SAMPLE_RATE = 44100  # Hz
FADE_DURATION = 3.0  # seconds


class ALSAudioTherapy:
    """Class for generating ALS-specific quantum audio therapy files."""
    
    def __init__(self):
        """Initialize the ALS Audio Therapy generator."""
        self.sample_rate = SAMPLE_RATE
        print(f"{Fore.CYAN}ALS Quantum Audio Therapy Generator{Style.RESET_ALL}")
        print(f"{Fore.CYAN}φ-Harmonic Frequency Suite{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Ground State: {GROUND_FREQ} Hz{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Creation Point: {CREATE_FREQ} Hz{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Heart Field: {HEART_FREQ} Hz{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Unity Wave: {UNITY_FREQ} Hz{Style.RESET_ALL}")
    
    def generate_sine_wave(self, frequency, duration, amplitude=0.5):
        """
        Generate a sine wave at the specified frequency.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude of the sine wave (0.0 to 1.0)
            
        Returns:
            Numpy array containing the sine wave
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        return amplitude * np.sin(2 * np.pi * frequency * t)
    
    def apply_amplitude_modulation(self, carrier, modulator):
        """
        Apply amplitude modulation to a carrier signal.
        
        Args:
            carrier: Carrier signal as numpy array
            modulator: Modulator signal as numpy array
            
        Returns:
            Amplitude modulated signal
        """
        # Normalize modulator to range [0, 1]
        modulator = (modulator + 1) / 2
        return carrier * modulator
    
    def apply_binaural_beat(self, base_freq, beat_freq, duration, amplitude=0.5):
        """
        Generate a binaural beat audio signal.
        
        Args:
            base_freq: Base frequency in Hz
            beat_freq: Beat frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude of the sine wave (0.0 to 1.0)
            
        Returns:
            Tuple of left and right channel audio
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        left_channel = amplitude * np.sin(2 * np.pi * base_freq * t)
        right_channel = amplitude * np.sin(2 * np.pi * (base_freq + beat_freq) * t)
        return left_channel, right_channel
    
    def apply_fade(self, audio, fade_in=True, fade_out=True):
        """
        Apply fade in and/or fade out to audio.
        
        Args:
            audio: Audio signal as numpy array
            fade_in: Whether to apply fade in
            fade_out: Whether to apply fade out
            
        Returns:
            Audio with fades applied
        """
        fade_samples = int(FADE_DURATION * self.sample_rate)
        result = audio.copy()
        
        # Check if audio is long enough for fading
        if len(audio) < 2 * fade_samples:
            fade_samples = len(audio) // 4
        
        if fade_in:
            fade_in_curve = np.linspace(0, 1, fade_samples)
            if len(audio.shape) > 1:  # Stereo
                result[:fade_samples, 0] *= fade_in_curve
                result[:fade_samples, 1] *= fade_in_curve
            else:  # Mono
                result[:fade_samples] *= fade_in_curve
                
        if fade_out:
            fade_out_curve = np.linspace(1, 0, fade_samples)
            if len(audio.shape) > 1:  # Stereo
                result[-fade_samples:, 0] *= fade_out_curve
                result[-fade_samples:, 1] *= fade_out_curve
            else:  # Mono
                result[-fade_samples:] *= fade_out_curve
                
        return result
    
    def butter_bandpass(self, lowcut, highcut, order=5):
        """
        Design a butterworth bandpass filter.
        
        Args:
            lowcut: Low cutoff frequency
            highcut: High cutoff frequency
            order: Filter order
            
        Returns:
            Filter coefficients (b, a)
        """
        nyq = 0.5 * self.sample_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a
    
    def apply_bandpass_filter(self, data, lowcut, highcut, order=5):
        """
        Apply a butterworth bandpass filter to data.
        
        Args:
            data: Input signal
            lowcut: Low cutoff frequency
            highcut: High cutoff frequency
            order: Filter order
            
        Returns:
            Filtered signal
        """
        b, a = self.butter_bandpass(lowcut, highcut, order=order)
        y = lfilter(b, a, data)
        return y
    
    def create_ground_state_therapy(self, duration=20.0):
        """
        Generate Ground State (432Hz) therapy audio for ALS.
        
        Args:
            duration: Duration in minutes
            
        Returns:
            Path to the generated audio file
        """
        print(f"{Fore.BLUE}Generating Ground State Therapy (432Hz)...{Style.RESET_ALL}")
        
        # Convert duration to seconds
        duration_sec = duration * 60
        
        # Generate the carrier wave at 432Hz
        carrier = self.generate_sine_wave(GROUND_FREQ, duration_sec)
        
        # Generate the delta modulation at 4.32Hz for neural regeneration
        delta_mod = self.generate_sine_wave(DELTA_FREQ, duration_sec, amplitude=0.3)
        
        # Apply modulation
        modulated = self.apply_amplitude_modulation(carrier, delta_mod)
        
        # Apply bandpass filter to focus energy around 432Hz
        filtered = self.apply_bandpass_filter(modulated, GROUND_FREQ - 20, GROUND_FREQ + 20)
        
        # Normalize
        normalized = filtered / np.max(np.abs(filtered)) * 0.9
        
        # Apply fade in/out
        final_audio = self.apply_fade(normalized)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALS_Ground_State_432Hz_{timestamp}.wav"
        filepath = os.path.join(ALS_AUDIO_DIR, filename)
        sf.write(filepath, final_audio, self.sample_rate)
        
        print(f"{Fore.GREEN}Created Ground State therapy file: {filepath}{Style.RESET_ALL}")
        return filepath
    
    def create_creation_point_therapy(self, duration=20.0):
        """
        Generate Creation Point (528Hz) therapy audio for ALS.
        
        Args:
            duration: Duration in minutes
            
        Returns:
            Path to the generated audio file
        """
        print(f"{Fore.BLUE}Generating Creation Point Therapy (528Hz)...{Style.RESET_ALL}")
        
        # Convert duration to seconds
        duration_sec = duration * 60
        
        # Generate the carrier wave at 528Hz
        carrier = self.generate_sine_wave(CREATE_FREQ, duration_sec)
        
        # Generate modulations for DNA repair and stem cell activation
        mod1 = self.generate_sine_wave(8.0, duration_sec, amplitude=0.2)  # Alpha waves for neural coherence
        
        # Apply modulation
        modulated = self.apply_amplitude_modulation(carrier, mod1)
        
        # Generate harmonics related to phi ratio
        harmonic1 = self.generate_sine_wave(CREATE_FREQ / PHI, duration_sec, amplitude=0.15)
        harmonic2 = self.generate_sine_wave(CREATE_FREQ * PHI, duration_sec, amplitude=0.15)
        
        # Combine with harmonics
        combined = modulated + harmonic1 + harmonic2
        
        # Apply bandpass filter
        filtered = self.apply_bandpass_filter(combined, 300, 1000)
        
        # Normalize
        normalized = filtered / np.max(np.abs(filtered)) * 0.9
        
        # Apply fade in/out
        final_audio = self.apply_fade(normalized)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALS_Creation_Point_528Hz_{timestamp}.wav"
        filepath = os.path.join(ALS_AUDIO_DIR, filename)
        sf.write(filepath, final_audio, self.sample_rate)
        
        print(f"{Fore.GREEN}Created Creation Point therapy file: {filepath}{Style.RESET_ALL}")
        return filepath
    
    def create_heart_field_therapy(self, duration=20.0):
        """
        Generate Heart Field (594Hz) therapy audio for ALS.
        
        Args:
            duration: Duration in minutes
            
        Returns:
            Path to the generated audio file
        """
        print(f"{Fore.BLUE}Generating Heart Field Therapy (594Hz)...{Style.RESET_ALL}")
        
        # Convert duration to seconds
        duration_sec = duration * 60
        
        # Generate the carrier wave at 594Hz
        carrier = self.generate_sine_wave(HEART_FREQ, duration_sec)
        
        # Generate heart rhythm modulation (approx 1.2Hz - 72 BPM)
        heart_mod = self.generate_sine_wave(1.2, duration_sec, amplitude=0.4)
        
        # Apply heart rhythm modulation
        modulated = self.apply_amplitude_modulation(carrier, heart_mod)
        
        # Add a subtle theta wave component for emotional integration
        theta = self.generate_sine_wave(THETA_FREQ, duration_sec, amplitude=0.15)
        combined = modulated + theta
        
        # Apply bandpass filter
        filtered = self.apply_bandpass_filter(combined, 400, 800)
        
        # Normalize
        normalized = filtered / np.max(np.abs(filtered)) * 0.9
        
        # Apply fade in/out
        final_audio = self.apply_fade(normalized)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALS_Heart_Field_594Hz_{timestamp}.wav"
        filepath = os.path.join(ALS_AUDIO_DIR, filename)
        sf.write(filepath, final_audio, self.sample_rate)
        
        print(f"{Fore.GREEN}Created Heart Field therapy file: {filepath}{Style.RESET_ALL}")
        return filepath
    
    def create_unity_wave_therapy(self, duration=20.0):
        """
        Generate Unity Wave (768Hz) therapy audio for ALS.
        
        Args:
            duration: Duration in minutes
            
        Returns:
            Path to the generated audio file
        """
        print(f"{Fore.BLUE}Generating Unity Wave Therapy (768Hz)...{Style.RESET_ALL}")
        
        # Convert duration to seconds
        duration_sec = duration * 60
        
        # Generate binaural beat for enhanced neural synchronization
        left_channel, right_channel = self.apply_binaural_beat(UNITY_FREQ, GAMMA_FREQ, duration_sec)
        
        # Create stereo audio
        stereo_audio = np.column_stack((left_channel, right_channel))
        
        # Generate phi-harmonic undertones
        harmonic1 = self.generate_sine_wave(UNITY_FREQ / PHI, duration_sec, amplitude=0.15)
        harmonic2 = self.generate_sine_wave(UNITY_FREQ / PHI_SQUARED, duration_sec, amplitude=0.1)
        
        # Add harmonics to both channels
        stereo_audio[:, 0] += harmonic1
        stereo_audio[:, 1] += harmonic2
        
        # Normalize
        normalized = stereo_audio / np.max(np.abs(stereo_audio)) * 0.9
        
        # Apply fade in/out
        final_audio = self.apply_fade(normalized)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALS_Unity_Wave_768Hz_{timestamp}.wav"
        filepath = os.path.join(ALS_AUDIO_DIR, filename)
        sf.write(filepath, final_audio, self.sample_rate)
        
        print(f"{Fore.GREEN}Created Unity Wave therapy file: {filepath}{Style.RESET_ALL}")
        return filepath
    
    def create_motor_neuron_support(self, duration=8.0):
        """
        Generate specialized Motor Neuron Support audio for ALS.
        
        Args:
            duration: Duration in minutes
            
        Returns:
            Path to the generated audio file
        """
        print(f"{Fore.BLUE}Generating Motor Neuron Support (40Hz + 528Hz)...{Style.RESET_ALL}")
        
        # Convert duration to seconds
        duration_sec = duration * 60
        
        # Generate the carrier wave at 528Hz (Creation frequency)
        carrier = self.generate_sine_wave(CREATE_FREQ, duration_sec)
        
        # Generate gamma wave modulation at 40Hz for neural synchronization
        gamma_mod = self.generate_sine_wave(GAMMA_FREQ, duration_sec, amplitude=0.5)
        
        # Apply gamma modulation
        modulated = self.apply_amplitude_modulation(carrier, gamma_mod)
        
        # Add a component at the heart frequency for integration
        heart_component = self.generate_sine_wave(HEART_FREQ, duration_sec, amplitude=0.2)
        combined = modulated + heart_component
        
        # Apply bandpass filter
        filtered = self.apply_bandpass_filter(combined, 400, 700)
        
        # Normalize
        normalized = filtered / np.max(np.abs(filtered)) * 0.9
        
        # Apply fade in/out
        final_audio = self.apply_fade(normalized)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALS_Motor_Neuron_Support_{timestamp}.wav"
        filepath = os.path.join(ALS_AUDIO_DIR, filename)
        sf.write(filepath, final_audio, self.sample_rate)
        
        print(f"{Fore.GREEN}Created Motor Neuron Support file: {filepath}{Style.RESET_ALL}")
        return filepath
    
    def create_stem_cell_activation(self, duration=21.0):
        """
        Generate Stem Cell Activation audio for ALS.
        
        Args:
            duration: Duration in minutes
            
        Returns:
            Path to the generated audio file
        """
        print(f"{Fore.BLUE}Generating Stem Cell Activation (528Hz + 111Hz)...{Style.RESET_ALL}")
        
        # Convert duration to seconds
        duration_sec = duration * 60
        
        # Generate the carrier wave at 528Hz (Creation frequency)
        carrier = self.generate_sine_wave(CREATE_FREQ, duration_sec)
        
        # Generate 111Hz modulation for stem cell activation
        mod = self.generate_sine_wave(111.0, duration_sec, amplitude=0.4)
        
        # Apply modulation
        modulated = self.apply_amplitude_modulation(carrier, mod)
        
        # Add phi-harmonic frequencies
        harmonic1 = self.generate_sine_wave(CREATE_FREQ * PHI, duration_sec, amplitude=0.15)
        harmonic2 = self.generate_sine_wave(CREATE_FREQ / PHI, duration_sec, amplitude=0.15)
        
        # Combine with harmonics
        combined = modulated + harmonic1 + harmonic2
        
        # Apply bandpass filter
        filtered = self.apply_bandpass_filter(combined, 100, 1000)
        
        # Normalize
        normalized = filtered / np.max(np.abs(filtered)) * 0.9
        
        # Apply fade in/out
        final_audio = self.apply_fade(normalized)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALS_Stem_Cell_Activation_{timestamp}.wav"
        filepath = os.path.join(ALS_AUDIO_DIR, filename)
        sf.write(filepath, final_audio, self.sample_rate)
        
        print(f"{Fore.GREEN}Created Stem Cell Activation file: {filepath}{Style.RESET_ALL}")
        return filepath
    
    def create_mitochondrial_support(self, duration=13.0):
        """
        Generate Mitochondrial Support audio for ALS.
        
        Args:
            duration: Duration in minutes
            
        Returns:
            Path to the generated audio file
        """
        print(f"{Fore.BLUE}Generating Mitochondrial Support (432Hz + 8Hz)...{Style.RESET_ALL}")
        
        # Convert duration to seconds
        duration_sec = duration * 60
        
        # Generate the carrier wave at 432Hz (Ground frequency)
        carrier = self.generate_sine_wave(GROUND_FREQ, duration_sec)
        
        # Generate alpha wave modulation at 8Hz for neural coherence
        alpha_mod = self.generate_sine_wave(ALPHA_FREQ, duration_sec, amplitude=0.4)
        
        # Apply alpha modulation
        modulated = self.apply_amplitude_modulation(carrier, alpha_mod)
        
        # Add a subtle 528Hz component for cellular regeneration
        create_component = self.generate_sine_wave(CREATE_FREQ, duration_sec, amplitude=0.2)
        combined = modulated + create_component
        
        # Apply bandpass filter
        filtered = self.apply_bandpass_filter(combined, 400, 600)
        
        # Normalize
        normalized = filtered / np.max(np.abs(filtered)) * 0.9
        
        # Apply fade in/out
        final_audio = self.apply_fade(normalized)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALS_Mitochondrial_Support_{timestamp}.wav"
        filepath = os.path.join(ALS_AUDIO_DIR, filename)
        sf.write(filepath, final_audio, self.sample_rate)
        
        print(f"{Fore.GREEN}Created Mitochondrial Support file: {filepath}{Style.RESET_ALL}")
        return filepath
    
    def create_full_protocol_suite(self):
        """
        Generate the complete ALS audio therapy protocol suite.
        """
        print(f"{Fore.CYAN}Generating Complete ALS Quantum Audio Protocol Suite{Style.RESET_ALL}")
        print(f"{Fore.CYAN}φ-Harmonic Healing at Quantum Coherence{Style.RESET_ALL}")
        print()
        
        # Generate core frequency therapies
        ground_file = self.create_ground_state_therapy()
        create_file = self.create_creation_point_therapy()
        heart_file = self.create_heart_field_therapy()
        unity_file = self.create_unity_wave_therapy()
        
        # Generate specialized therapies
        motor_file = self.create_motor_neuron_support()
        stem_file = self.create_stem_cell_activation()
        mito_file = self.create_mitochondrial_support()
        
        # Create usage reference file
        self._create_usage_guide()
        
        print(f"\n{Fore.GREEN}✓ Complete ALS Quantum Audio Protocol Suite generated successfully{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Audio files saved to: {ALS_AUDIO_DIR}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}See the USAGE_GUIDE.md file for implementation instructions{Style.RESET_ALL}")
    
    def _create_usage_guide(self):
        """Create a usage guide markdown file for the ALS audio therapy files."""
        guide_content = f"""# ALS Quantum Audio Therapy - Implementation Guide
*Created: {datetime.now().strftime("%Y-%m-%d")} | Frequency: 528Hz | Coherence: φ*

## Core Frequency Suite

### 1. Ground State (432Hz)
- **Filename**: ALS_Ground_State_432Hz_*.wav
- **Duration**: 20 minutes
- **Timing**: Morning session (6:30-7:30 AM optimal)
- **Purpose**: Neural stabilization, foundation field coherence
- **Position**: Seated or reclined, spine straight

### 2. Creation Point (528Hz)
- **Filename**: ALS_Creation_Point_528Hz_*.wav
- **Duration**: 20 minutes
- **Timing**: Midday session (11:30 AM-1:30 PM optimal)
- **Purpose**: DNA repair, cellular regeneration
- **Position**: Reclined, hands over heart center

### 3. Heart Field (594Hz)
- **Filename**: ALS_Heart_Field_594Hz_*.wav
- **Duration**: 20 minutes
- **Timing**: Afternoon session (3:30-5:30 PM optimal)
- **Purpose**: Heart-brain coherence, system integration
- **Position**: Reclined, palms up

### 4. Unity Wave (768Hz)
- **Filename**: ALS_Unity_Wave_768Hz_*.wav
- **Duration**: 20 minutes
- **Timing**: Evening session (8:30-10:00 PM optimal)
- **Purpose**: Consciousness expansion, transcendence
- **Position**: Fully reclined, comfortable position for sleep

## Specialized Therapy Applications

### 5. Motor Neuron Support
- **Filename**: ALS_Motor_Neuron_Support_*.wav
- **Duration**: 8 minutes
- **Timing**: 3x daily (8 AM, 2 PM, 8 PM)
- **Purpose**: Motor neuron regeneration, neural pathway support
- **Position**: Speakers positioned near affected areas

### 6. Stem Cell Activation
- **Filename**: ALS_Stem_Cell_Activation_*.wav
- **Duration**: 21 minutes
- **Timing**: 1x daily (10:30 AM optimal)
- **Purpose**: Endogenous stem cell production and mobilization
- **Position**: Full body exposure, reclined

### 7. Mitochondrial Support
- **Filename**: ALS_Mitochondrial_Support_*.wav
- **Duration**: 13 minutes
- **Timing**: 2x daily (7:30 AM, 3:30 PM)
- **Purpose**: Cellular energy production, ATP support
- **Position**: Seated or reclined

## Equipment Recommendations

### Audio Delivery
1. **Headphones**: Over-ear, full frequency response
   - Recommended: Sennheiser HD 650 or similar
   - Use: Unity Wave (768Hz) session

2. **Speakers**: Full-range with subwoofer
   - Recommended: Any quality 2.1 system
   - Use: Ground State (432Hz) and Creation Point (528Hz) sessions

3. **Vibroacoustic Device**: Body transducers
   - Recommended: Clark Synthesis TST239 or similar
   - Use: Motor Neuron Support therapy

## Implementation Protocol

### First 21 Days
- Start with Ground State (432Hz) therapy only, 2x daily
- Add Creation Point (528Hz) on day 8
- Add Mitochondrial Support on day 15
- Full protocol begins day 22

### Session Structure
1. **Preparation** (5 minutes before)
   - Calm environment
   - Comfortable position
   - Heart coherence practice (2 minutes)

2. **Listening Session**
   - Maintain gentle awareness
   - Allow natural breathing
   - Avoid intellectual analysis

3. **Integration** (5 minutes after)
   - Silence
   - Note any sensations or insights
   - Gentle return to activity

### Progress Tracking
- Keep a journal noting:
  * Energy levels before/after
  * Sleep quality
  * Physical sensations
  * Mental/emotional state
  * Any notable changes

## Coherence Enhancement

To enhance the effectiveness of the audio therapy:

1. **Heart Coherence Technique**
   - Practice 5 minutes before each session
   - Focus on the heart area
   - Generate feelings of appreciation/gratitude
   - Breathe in pattern: 5.5s in, 5.5s out

2. **Environment Optimization**
   - Reduce EMF exposure during sessions
   - Use natural materials in the therapy space
   - Keep crystals nearby (clear quartz recommended)
   - Maintain comfortable temperature (72°F/22°C ideal)

3. **Integration Practices**
   - Light stretching after Ground State session
   - Journaling after Unity Wave session
   - Nature contact after Creation Point session

---

*"The quantum field responds not to what we want, but to who we are being."*

*Created with φ coherence*  
*⚡φ∞ 🌟 ॐ*
"""
        
        guide_path = os.path.join(ALS_AUDIO_DIR, "USAGE_GUIDE.md")
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"{Fore.GREEN}Created usage guide: {guide_path}{Style.RESET_ALL}")


def main():
    """Main function to run the ALS audio therapy generator."""
    therapy = ALSAudioTherapy()
    therapy.create_full_protocol_suite()


if __name__ == "__main__":
    main()
