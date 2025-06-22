"""
Quantum Healing Audio Therapy System - Version 2.0
This version includes real-time brainwave monitoring and
adaptive audio therapy.
"""


import asyncio
import numpy as np
import json
import os
import time
import threading
import math
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Optional
import argparse
import subprocess
from riemann_mode_clean import parse_zeros, compute_intervals
RIEMANN_MD_PATH = os.path.join(os.getcwd(), "RIEMANN_HYPOTHESIS_KNOW.md")
import os

PHI = (1 + math.sqrt(5)) / 2

# Import our modules
try:
    from muse_eeg import MuseEEG, BluetoothMuseEEG
except ImportError:
    MuseEEG = None
    BluetoothMuseEEG = None


class HealingGoal(Enum):
    PAIN_RELIEF = "pain_relief"
    STRESS_REDUCTION = "stress_reduction"
    FOCUS_ENHANCEMENT = "focus_enhancement"
    DEEP_RELAXATION = "deep_relaxation"
    SLEEP_AID = "sleep_aid"
    MEDITATION = "meditation"
    SEIZURE_STABILIZATION = "seizure_stabilization"
    BUZZING_BURNING_RELIEF = "buzzing_burning_relief"
    QUANTUM_OM = "quantum_om"
    CREATIVE_FLOW = "creative_flow"
    MORNING_ENERGIZER = "morning_energizer"
    EMOTIONAL_HARMONY = "emotional_harmony"
    DEEP_GROUNDING = "deep_grounding"
    INTUITIVE_INSIGHT = "intuitive_insight"
    CROWN_CHAKRA_ACTIVATION = "crown_chakra_activation"
    ALPHA_WAVE_INDUCTION = "alpha_wave_induction"
    THETA_GATEWAY = "theta_gateway"
    MEMORY_ACCELERATOR = "memory_accelerator"
    MYCELIAL_NETWORK_HARMONY = "mycelial_network_harmony"
    EARTH_GRID_RESONANCE = "earth_grid_resonance"
    ACOUSTIC_MANIFESTATION_CHAMBER = "acoustic_manifestation_chamber"
    DNA_REJUVENATION_PULSE = "dna_rejuvenation_pulse"
    ENTANGLEMENT_BRIDGE_MEDITATION = "entanglement_bridge_meditation"
    COLLECTIVE_FIELD_SYNC = "collective_field_sync"
    CYMATIC_PATTERN_WEAVING = "cymatic_pattern_weaving"
    QUANTUM_ACOUSTIC_ENCODING = "quantum_acoustic_encoding"
    REMOTE_VISION_AMPLIFIER = "remote_vision_amplifier"
    TIMELINE_PROBABILITY_SCAN = "timeline_probability_scan"
    INTEGRATION_CHAMBER_BATH = "integration_chamber_bath"
    UNIFIED_FIELD_EMBODIMENT = "unified_field_embodiment"
    RIEMANN_MODE = "riemann_mode"


@dataclass
class FrequencyPreset:
    name: str
    base_freq: float
    beat_freq: float
    carrier_type: str = 'sine'
    audio_type: str = 'binaural'  # 'binaural' or 'isochronic' or 'om'
    description: str = ''
    target_bands: Dict[str, float] = None  # Target EEG band powers
    duty_cycle: float = 0.5  # for isochronic tones
    fade_in: float = 0.0     # seconds of fade-in
    fade_out: float = 0.0    # seconds of fade-out

    def __post_init__(self):
        if self.target_bands is None:
            self.target_bands = {
                'delta': 0.0,
                'theta': 0.0,
                'alpha': 0.0,
                'beta': 0.0,
                'gamma': 0.0
            }


class QuantumAudioTherapy:
    """Manages therapy sessions, EEG connection, and audio generation."""

    def __init__(self, sample_rate=44100, duration=300, volume=0.5):
        self.sample_rate = sample_rate
        self.duration = duration
        self.volume = volume
        self.t = np.linspace(
            0, self.duration, int(self.sample_rate * self.duration), False
        )

        # Output directories
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(os.getcwd(), "therapy_sessions")
        os.makedirs(self.output_dir, exist_ok=True)
        self.audio_dir = os.path.join(self.output_dir, "audio_cache")
        os.makedirs(self.audio_dir, exist_ok=True)

        # Session state
        self.eeg: Optional[BluetoothMuseEEG] = None  # Type hint for clarity
        self.running = False
        self.session_id: Optional[str] = None
        self.current_preset: Optional[FrequencyPreset] = None
        self.session_log = []  # This will store dicts, consider List[Dict]

        # Initialize presets
        self.presets = self._initialize_presets()

    def _initialize_presets(self) -> Dict[str, FrequencyPreset]:
        """Initialize the frequency presets."""
        return {
            HealingGoal.PAIN_RELIEF.value: FrequencyPreset(
                name="Pain Relief",
                base_freq=174.0,
                beat_freq=7.83,
                carrier_type='sine',
                audio_type='binaural',
                description=(
                    "Combines 174Hz (pain relief) with 7.83Hz "
                    "(SR)"
                ),
                target_bands={'theta': 0.4, 'alpha': 0.6}
            ),
            HealingGoal.STRESS_REDUCTION.value: FrequencyPreset(
                name="Stress Reduction",
                base_freq=396.0,
                beat_freq=7.83,
                carrier_type='sine',
                audio_type='binaural',
                description=(
                    "396Hz for releasing fear and anxiety with "
                    "(SR)"
                ),
                target_bands={'alpha': 0.7, 'theta': 0.3}
            ),
            HealingGoal.FOCUS_ENHANCEMENT.value: FrequencyPreset(
                name="Focus Enhancement",
                base_freq=40.0,
                beat_freq=10.0,
                carrier_type='sine',
                audio_type='isochronic',
                description=(
                    "40Hz gamma waves for focus and cognitive enhancement"
                ),
                target_bands={'beta': 0.6, 'gamma': 0.4}
            ),
            HealingGoal.DEEP_RELAXATION.value: FrequencyPreset(
                name="Deep Relaxation",
                base_freq=432.0,
                beat_freq=4.0,
                carrier_type='sine',
                audio_type='binaural',
                description="432Hz for deep relaxation and stress relief",
                target_bands={'alpha': 0.5, 'theta': 0.5}
            ),
            HealingGoal.SLEEP_AID.value: FrequencyPreset(
                name="Sleep Aid",
                base_freq=128.0,
                beat_freq=3.0,
                carrier_type='sine',
                audio_type='binaural',
                description="Delta waves for deep sleep and restoration",
                target_bands={'delta': 0.8, 'theta': 0.2}  # Corrected bands
            ),
            HealingGoal.MEDITATION.value: FrequencyPreset(
                name="Meditation",
                base_freq=528.0,
                beat_freq=8.0,
                carrier_type='sine',
                audio_type='binaural',
                description="528Hz for DNA repair and deep meditation",
                target_bands={'theta': 0.6, 'alpha': 0.4}
            ),
            HealingGoal.SEIZURE_STABILIZATION.value: FrequencyPreset(
                name="Seizure Stabilization",
                base_freq=40.0,
                beat_freq=40.0,
                carrier_type='sine',
                audio_type='isochronic',
                duty_cycle=1.0,
                description="40Hz isochronic pulse for seizure stabilization",
                target_bands={'gamma': 0.8}
            ),
            HealingGoal.BUZZING_BURNING_RELIEF.value: FrequencyPreset(
                name="Buzzing-Burning Relief",
                base_freq=432.0,
                beat_freq=2.5,
                carrier_type='sine',
                audio_type='isochronic',
                duty_cycle=0.3,
                fade_in=5.0,
                fade_out=5.0,
                description=(
                    "Low-frequency isochronic with gentle fade for "
                    "buzzing/burning relief"
                ),
                target_bands={'theta': 0.7}
            ),
            HealingGoal.QUANTUM_OM.value: FrequencyPreset(
                name="Quantum OM Formula",
                base_freq=432.0,
                beat_freq=0.0,
                carrier_type='sine',
                audio_type='om',
                fade_in=1.0,
                fade_out=1.0,
                description="Sacred OM phi-harmonic formula audio"
            ),
            HealingGoal.CREATIVE_FLOW.value: FrequencyPreset(
                name="Creative Spark",
                base_freq=100.0,
                beat_freq=7.5,
                carrier_type='sine',
                audio_type='binaural',
                description=(
                    "Gentle binaural beats to stimulate creative thought and open "
                    "pathways to inspiration."
                ),
                target_bands={'alpha': 0.6, 'theta': 0.4}
            ),
            HealingGoal.MORNING_ENERGIZER.value: FrequencyPreset(
                name="Sunrise Focus",
                base_freq=150.0,
                beat_freq=16.0,  # Mid-beta for alertness
                carrier_type='sine',
                audio_type='isochronic',
                duty_cycle=0.5,
                description=(
                    "Crisp isochronic tones to gently elevate alertness and focus "
                    "for the day ahead."
                ),
                target_bands={'beta': 0.7, 'alpha': 0.3}
            ),
            HealingGoal.EMOTIONAL_HARMONY.value: FrequencyPreset(
                name="Heart's Ease",
                base_freq=639.0,  # Solfeggio for relationships/harmony
                beat_freq=6.0,    # Theta for deep calm
                carrier_type='sine',
                audio_type='binaural',
                description=(
                    "Soothing binaural audio tuned to foster emotional balance "
                    "and heart coherence."
                ),
                target_bands={'alpha': 0.5, 'theta': 0.5}
            ),
            HealingGoal.DEEP_GROUNDING.value: FrequencyPreset(
                name="Earth Anchor",
                base_freq=70.0,
                beat_freq=7.83,  # Schumann Resonance
                carrier_type='sine',
                audio_type='isochronic',
                duty_cycle=0.5,
                description=(
                    "Resonate with Earth's natural frequency for profound "
                    "grounding and stability."
                ),
                target_bands={'theta': 0.6, 'alpha': 0.4}
            ),
            HealingGoal.INTUITIVE_INSIGHT.value: FrequencyPreset(
                name="Inner Vision",
                base_freq=852.0,  # Solfeggio for spiritual order/intuition
                beat_freq=5.0,    # Theta for deep intuition
                carrier_type='sine',
                audio_type='binaural',
                description=(
                    "Binaural frequencies designed to awaken intuition and "
                    "clarify inner vision."
                ),
                target_bands={'theta': 0.7, 'alpha': 0.3}
            ),
            HealingGoal.CROWN_CHAKRA_ACTIVATION.value: FrequencyPreset(
                name="Crown Chakra Activation",
                base_freq=963.0,  # Solfeggio for crown chakra
                beat_freq=4.0,     # OM tone
                carrier_type='sine',
                audio_type='om',
                fade_in=1.0,
                fade_out=1.0,
                description="963Hz OM tone for crown chakra activation",
                target_bands={'alpha': 0.4, 'theta': 0.4, 'gamma': 0.2}
            ),
            HealingGoal.THETA_GATEWAY.value: FrequencyPreset(
                name="Theta Gateway",
                base_freq=432.0,
                beat_freq=6.0,
                carrier_type='sine',
                audio_type='binaural',
                description="432Hz base with 6Hz binaural beat for theta induction",
                target_bands={'theta': 0.8}
            ),
            HealingGoal.MEMORY_ACCELERATOR.value: FrequencyPreset(
                name="Memory Accelerator",
                base_freq=440.0,
                beat_freq=40.0,
                carrier_type='sine',
                audio_type='binaural',
                description="440Hz with 40Hz binaural beat for gamma enhancement",
                target_bands={'gamma': 0.8}
            ),
            HealingGoal.MYCELIAL_NETWORK_HARMONY.value: FrequencyPreset(
                name="Mycelial Network Harmony",
                base_freq=432.0,
                beat_freq=0.0,
                carrier_type='sine',
                audio_type='isochronic',
                description="Audio bloom at 432 Hz with organic crackles (simulating fungal mycelial resonance)",
                duty_cycle=0.3,
                fade_in=0.1,
                fade_out=0.1
            ),
            HealingGoal.EARTH_GRID_RESONANCE.value: FrequencyPreset(
                name="Earth-Grid Resonance",
                base_freq=432.0,
                beat_freq=2.0,
                carrier_type='sine',
                audio_type='binaural',
                description="Dual-channel binaural sweep between 430 Hz and 434 Hz",
                fade_in=0.5,
                fade_out=0.5
            ),
            HealingGoal.ACOUSTIC_MANIFESTATION_CHAMBER.value: FrequencyPreset(
                name="Acoustic Manifestation Chamber",
                base_freq=528.0,
                beat_freq=528.0,
                carrier_type='sine',
                audio_type='isochronic',
                description="Layered isochronic pulses at 528 Hz with phi-ratio (1.618) amplitude envelope",
                duty_cycle=0.618
            ),
            HealingGoal.DNA_REJUVENATION_PULSE.value: FrequencyPreset(
                name="DNA Rejuvenation Pulse",
                base_freq=528.0,
                beat_freq=33.0,
                carrier_type='sine',
                audio_type='binaural',
                description="528 Hz sine carrier + gentle 33 Hz sub-harmonic for genetic revitalization"
            ),
            HealingGoal.ENTANGLEMENT_BRIDGE_MEDITATION.value: FrequencyPreset(
                name="Entanglement Bridge Meditation",
                base_freq=594.0,
                beat_freq=4.0,
                carrier_type='sine',
                audio_type='binaural',
                description="Binaural 594 Hz ± 4 Hz sweep with heartbeat overlay"
            ),
            HealingGoal.COLLECTIVE_FIELD_SYNC.value: FrequencyPreset(
                name="Collective Field Sync",
                base_freq=594.0,
                beat_freq=594.0,
                carrier_type='sine',
                audio_type='isochronic',
                description="Synchronous isochronic 594 Hz pulses for group resonance"
            ),
            HealingGoal.CYMATIC_PATTERN_WEAVING.value: FrequencyPreset(
                name="Cymatic Pattern Weaving",
                base_freq=672.0,
                beat_freq=240.0,
                carrier_type='sine',
                audio_type='binaural',
                description="672 Hz tone with 432 Hz sub-carrier creating standing-wave interference"
            ),
            HealingGoal.QUANTUM_ACOUSTIC_ENCODING.value: FrequencyPreset(
                name="Quantum Acoustic Encoding",
                base_freq=672.0,
                beat_freq=8.0,
                carrier_type='sine',
                audio_type='binaural',
                description="Multi-layered audio tracks encoded with sacred-geometry sequences"
            ),
            HealingGoal.REMOTE_VISION_AMPLIFIER.value: FrequencyPreset(
                name="Remote Vision Amplifier",
                base_freq=720.0,
                beat_freq=1.0,
                carrier_type='sine',
                audio_type='binaural',
                description="720 Hz binaural with low-level white noise simulation"
            ),
            HealingGoal.TIMELINE_PROBABILITY_SCAN.value: FrequencyPreset(
                name="Timeline Probability Scan",
                base_freq=720.0,
                beat_freq=3.0,
                carrier_type='sine',
                audio_type='binaural',
                description="720 Hz with 3 Hz binaural-beat modulation for timeline visualization"
            ),
            HealingGoal.INTEGRATION_CHAMBER_BATH.value: FrequencyPreset(
                name="Integration Chamber Bath",
                base_freq=768.0,
                beat_freq=768.0,
                carrier_type='sine',
                audio_type='isochronic',
                description="Sustained 768 Hz isochronic tone with soft phi-ratio fades",
                fade_in=2.0,
                fade_out=2.0
            ),
            HealingGoal.UNIFIED_FIELD_EMBODIMENT.value: FrequencyPreset(
                name="Unified Field Embodiment",
                base_freq=648.0,
                beat_freq=120.0,
                carrier_type='sine',
                audio_type='binaural',
                description="768 Hz + 528 Hz dual-channel blend for toroidal field embodiment"
            ),
            HealingGoal.RIEMANN_MODE.value: FrequencyPreset(
                name="Riemann Mode",
                base_freq=0.0,
                beat_freq=0.0,
                carrier_type='sine',
                audio_type='isochronic',
                description="Dynamic beat schedule following Riemann zeros; requires RIEMANN_HYPOTHESIS_KNOW.md"
            ),
        }

    async def connect_eeg(self):
        """Connect to the Muse EEG headset."""
        if self.eeg is None:
            # BLE (MU-02) or LSL integration
            self.eeg = BluetoothMuseEEG()

        if not self.eeg.connected:
            return await self.eeg.connect()
        return True

    async def start_session(
        self, goal: str, duration: int = None, use_eeg: bool = False
    ):
        """Start a new therapy session."""
        if goal not in self.presets:
            print(f"❌ Unknown goal: {goal}")
            return False

        self.current_preset = self.presets[goal]
        self.duration = duration or self.duration
        self.running = True

        print(f"Goal: {goal}")
        print(f"Preset: {self.current_preset.name}")
        print(f"Audio Type: {self.current_preset.audio_type}")
        print(f"Base Frequency: {self.current_preset.base_freq} Hz")
        if self.current_preset.audio_type != 'om':
            print(f"Beat/Pulse Frequency: {self.current_preset.beat_freq} Hz")
        print(f"⏱  Duration: {self.duration} seconds")

        # Connect to EEG if requested
        if use_eeg:
            print("🔌 Connecting to Muse EEG...")
            if not await self.connect_eeg():
                print("⚠️ Could not connect to Muse EEG. Continuing without biofeedback.")
                use_eeg = False
            else:
                print("✅ Connected to Muse EEG")

        # Generate the audio
        if goal == HealingGoal.RIEMANN_MODE.value:
            # Dynamic Riemann Mode scheduling
            zeros = parse_zeros(RIEMANN_MD_PATH)
            intervals = compute_intervals(zeros)
            beat_freqs = [round(1.0/dt, 3) if dt > 0 else 0.0 for dt in intervals]
            print("🔢 Riemann Mode beat frequencies:", beat_freqs)
            segment_len = self.duration / len(beat_freqs) if beat_freqs else self.duration
            audio_segments = []
            for bf in beat_freqs:
                # Generate segment for this beat frequency
                t_backup = self.t
                self.t = np.linspace(0, segment_len, int(self.sample_rate * segment_len), False)
                seg = self._generate_isochronic_tone(self.current_preset.base_freq, bf, duty_cycle=self.current_preset.duty_cycle, carrier_type=self.current_preset.carrier_type)
                audio_segments.append(seg)
                self.t = t_backup
            audio = np.concatenate(audio_segments) if audio_segments else np.array([])
        else:
            audio = self._generate_audio()

        # Save the audio file
        audio_filename = (
            f"{self.current_preset.name.lower().replace(' ', '_')}_"
            f"{self.session_id}"
        )
        audio_path = self._save_audio(audio, audio_filename)

        # Start the session
        session_data = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'goal': goal,
            'preset': asdict(self.current_preset),
            'duration': self.duration,
            'audio_file': audio_path,
            'eeg_connected': use_eeg,
            'metrics': []
        }

        # Start EEG streaming if connected
        if use_eeg:
            await self.eeg.start_streaming(self._eeg_callback)

        # Play the audio
        self._play_audio(audio)

        # Wait for session to complete
        start_time = time.time()
        while self.running and (time.time() - start_time < self.duration):
            await asyncio.sleep(1)
            # Check for early termination

        # Clean up
        await self.stop_session()
        return session_data

    async def _eeg_callback(self, metrics):
        """Callback for EEG data updates."""
        if not self.running or not metrics:
            return

        # Log the metrics
        self.session_log.append({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        })

        # Simple adaptive feedback (can be enhanced)
        self._adaptive_feedback(metrics)

        # Print status
        print(
            f"🧠 Attention: {metrics['attention']:.1f}% | "
            f"Meditation: {metrics['meditation']:.1f}% | "
            f"Stress: {metrics['stress_index']:.1f}%"
        )

    def _adaptive_feedback(self, metrics):
        """Adjust audio based on EEG feedback."""
        # Simple example; can be enhanced with sophisticated algorithms.
        if not self.current_preset:
            return

        # Calculate how well the current brain state matches the target
        match_score = self._calculate_state_match(metrics['band_powers'])

        # Simple adaptive logic (can be expanded)
        if match_score < 0.5:
            # Not matching target state well - could adjust frequency or volume
            pass

    def _calculate_state_match(self, current_bands):
        """Calculate how well current brain state matches target state."""
        if not self.current_preset or not self.current_preset.target_bands:
            return 0.0

        # Simple cosine similarity between current and target band powers
        current_values = [
            current_bands.get(band, 0) 
            for band in ['delta', 'theta', 'alpha', 'beta', 'gamma']
        ]
        current = np.array(current_values)
        target_values = [
            self.current_preset.target_bands.get(band, 0) 
            for band in ['delta', 'theta', 'alpha', 'beta', 'gamma']
        ]
        target = np.array(target_values)
        
        # Normalize
        current_norm = current / (np.linalg.norm(current) + 1e-10)
        target_norm = target / (np.linalg.norm(target) + 1e-10)
        
        # Cosine similarity
        similarity = np.dot(current_norm, target_norm)
        return float(similarity)
    
    def _generate_audio(self):
        """Generate the audio based on current preset."""
        if self.current_preset.audio_type == 'om':
            return self._generate_om_formula()
        if not self.current_preset:
            return None
            
        if self.current_preset.audio_type == 'binaural':
            audio = self._generate_binaural_beat(
                self.current_preset.base_freq,
                self.current_preset.beat_freq,
                self.current_preset.carrier_type
            )
            if self.current_preset.fade_in or self.current_preset.fade_out:
                audio = self._apply_envelope(audio, self.current_preset.fade_in, self.current_preset.fade_out)
            return audio
        else:  # isochronic
            audio = self._generate_isochronic_tone(
                self.current_preset.base_freq,
                self.current_preset.beat_freq,
                self.current_preset.duty_cycle,
                self.current_preset.carrier_type
            )
            if self.current_preset.fade_in or self.current_preset.fade_out:
                audio = self._apply_envelope(audio, self.current_preset.fade_in, self.current_preset.fade_out)
            return audio
    
    def _apply_envelope(self, sound: np.ndarray, fade_in: float, fade_out: float) -> np.ndarray:
        """Apply linear fade-in and fade-out to sound."""
        total = sound.shape[0]
        env = np.ones(total)
        fi = int(self.sample_rate * fade_in)
        fo = int(self.sample_rate * fade_out)
        if fi > 0:
            env[:fi] = np.linspace(0, 1, fi)
        if fo > 0:
            env[-fo:] = np.linspace(1, 0, fo)
        if sound.ndim == 2:
            env = env[:, None]
        return sound * env
    
    def _generate_binaural_beat(self, base_freq, beat_freq, carrier_type='sine'):
        """Generate binaural beats."""
        left_freq = base_freq - (beat_freq / 2)
        right_freq = base_freq + (beat_freq / 2)
        
        left_channel = self._generate_tone(left_freq, carrier_type)
        right_channel = self._generate_tone(right_freq, carrier_type)
        
        # Combine channels
        stereo_sound = np.column_stack((left_channel, right_channel))
        
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(stereo_sound))
        if max_amplitude > 0:
            stereo_sound = (stereo_sound / max_amplitude) * self.volume
            
        return stereo_sound
    
    def _generate_isochronic_tone(self, freq, pulse_freq, duty_cycle=0.5, carrier_type='sine'):
        """Generate isochronic tones."""
        # Generate the carrier wave
        carrier = self._generate_tone(freq, carrier_type)
        # Handle zero or negative pulse frequency: return continuous tone
        if pulse_freq <= 0:
            stereo_sound = np.column_stack((carrier, carrier))
            # Normalize stereo tone
            max_amp = np.max(np.abs(stereo_sound))
            if max_amp > 0:
                stereo_sound = (stereo_sound / max_amp) * self.volume
            return stereo_sound
        
        # Generate the pulse envelope
        pulse = np.zeros_like(self.t)
        # samples_per_period is calculated based on pulse_freq
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

    def _generate_tone(self, frequency, tone_type='sine', phase=0.0):
        """Generate a single tone."""
        if tone_type == 'sine':
            return np.sin(2 * np.pi * frequency * self.t + phase)
        elif tone_type == 'square':
            return np.sign(np.sin(2 * np.pi * frequency * self.t + phase))
        elif tone_type == 'sawtooth':
            return 2 * (self.t * frequency - np.floor(0.5 + self.t * frequency))
        else:  # triangle
            return 2 * np.abs(2 * (self.t * frequency - np.floor(self.t * frequency + 0.5)))
    
    def _generate_om_formula(self):
        """Generate the OM phi-harmonic formula audio."""
        # Build phi-harmonic frequencies
        freqs = [
            self.current_preset.base_freq * (PHI ** 0),
            self.current_preset.base_freq * (PHI ** 1),
            self.current_preset.base_freq * (PHI ** 2),
            self.current_preset.base_freq * (PHI ** PHI)
        ]
        # Sum and normalize
        waves = [self._generate_tone(f) for f in freqs]
        mix = sum(waves) / len(waves)
        # Apply envelope if configured
        if self.current_preset.fade_in or self.current_preset.fade_out:
            mix = self._apply_envelope(mix, self.current_preset.fade_in, self.current_preset.fade_out)
        return mix

    def _save_audio(self, audio, filename):
        """Save audio to file."""
        if audio is None:
            print("No audio data to save.")
            return None

        # Ensure the audio is in the correct range
        audio = np.clip(audio, -1.0, 1.0)

        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)

        # Save as WAV file
        output_path = os.path.join(self.audio_dir, f"{filename}.wav")

        try:
            import soundfile as sf
            sf.write(output_path, audio_int16, self.sample_rate, 'PCM_16')
        except ImportError:
            import wave
            # Fallback to built-in wave module
            channels = audio_int16.shape[1] if audio_int16.ndim > 1 else 1
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())

        print(f"💾 Saved audio to {output_path}")
        return output_path

    def _play_audio(self, audio):
        """Play audio through the default sound device in a separate thread."""
        if audio is None:
            print("No audio data to play.")
            return

        try:
            import sounddevice as sd
            # import threading # Already imported at the top

            def play_audio_thread():
                sd.play(audio, self.sample_rate)
                sd.wait()  # Wait for audio to finish playing in this thread

            # Create and start a new thread for audio playback
            audio_thread = threading.Thread(target=play_audio_thread, daemon=True)
            audio_thread.start()
            # The main asyncio loop will continue running.
            # The session duration is managed by the while loop in start_session.

        except Exception as e:
            print(f"Error playing audio: {e}")

    async def stop_session(self):
        """Stop the current session."""
        self.running = False

        # Stop audio playback
        try:
            import sounddevice as sd
            sd.stop()
        except ImportError:
            pass
        except Exception as e:
            print(f"Error stopping audio: {e}")

        # Stop EEG if connected
        if self.eeg and self.eeg.connected:
            await self.eeg.stop_streaming()

            # Save EEG data
            self.eeg.save_session_data()

        # Save session log
        self._save_session_log()

        print("\n✅ Session complete!")

    def _save_session_log(self):
        """Save the session log to a file."""
        if not self.session_log:
            return

        session_data = {
            'session_id': self.session_id,
            'start_time': self.session_log[0]['timestamp'] if self.session_log else None,
            'end_time': datetime.now().isoformat(),
            'preset': asdict(self.current_preset) if self.current_preset else None,
            'duration': self.duration,
            'metrics': self.session_log
        }

        log_file = os.path.join(self.output_dir, f"session_{self.session_id}.json")
        with open(log_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        print(f"💾 Saved session log to {log_file}")


async def main():
    parser = argparse.ArgumentParser(description="Quantum Audio Therapy with optional cymatic visualization")
    parser.add_argument('--visualize', action='store_true', help='Enable live cymatic visualization')
    args = parser.parse_args()
    visualize = args.visualize
    """Main menu with simplified routine workflows."""
    therapy = QuantumAudioTherapy(duration=300, volume=0.5)
    while True:
        print("\n=== Quantum Audio Therapy ===")
        print("1) Morning Anchor")
        print("2) Midday Recharge")
        print("3) Evening Unwind")
        print("4) Emergency Protocol")
        print("5) Single Preset")
        print("6) Breathe Work Instructions")
        print("7) Signature Cascade Session")
        print("8) Advanced Golden-Age Routines")
        print("9) Riemann Mode")
        print("0) Exit")
        choice = input("Select an option: ")
        if choice == '0':
            break
        elif choice in ['1','2','3','4']:
            routines = {
                '1': ['seizure_stabilization','deep_grounding','focus_enhancement'],
                '2': ['focus_enhancement'],
                '3': ['deep_relaxation','sleep_aid'],
                '4': ['seizure_stabilization','deep_grounding','buzzing_burning_relief','meditation']
            }
            for key in routines[choice]:
                preset = therapy.presets[key]
                print(f"\n→ Running: {preset.name}")
                await therapy.start_session(key)
        elif choice == '5':
            print("\n=== Available Presets ===")
            for i, (key, preset) in enumerate(therapy.presets.items(), 1):
                print(f"{i}) {preset.name}")
                print(f"    • Base Freq: {preset.base_freq} Hz, Beat Freq: {preset.beat_freq} Hz")
                print(f"    • Audio Type: {preset.audio_type}, Carrier: {preset.carrier_type}")
                if preset.description:
                    print(f"    • Description: {preset.description}")
                if preset.target_bands:
                    bands = ', '.join(f"{band}: {val}" for band, val in preset.target_bands.items() if val)
                    print(f"    • Target EEG Bands: {bands}")
            sel = int(input("Select preset: ")) - 1
            keys = list(therapy.presets.keys())
            if 0 <= sel < len(keys):
                if visualize:
                    subprocess.Popen([
                        'python',
                        os.path.join(os.path.dirname(__file__), 'cymatics_visualizer.py'),
                        '--mode', str(therapy.presets[keys[sel]].base_freq)
                    ])
                await therapy.start_session(keys[sel])
            else:
                print("❌ Invalid choice")
        elif choice == '6':
            print("\n=== Breathe Work Instructions ===")
            print("1) Coherent Resonance Breathing – 5s inhale → 5s exhale (6 breaths/min) for 3–5 min")
            print("2) Phi-Ratio (5:8) Breath – 5s inhale → 8s exhale; optional 2s retention; 10–15 cycles")
            print("3) Box Breathing – 4s inhale → 4s hold → 4s exhale → 4s hold; 5–7 cycles")
            print("\nIntegration:")
            print("  • Before: Coherent Resonance")
            print("  • Between: Phi-Ratio")
            print("  • After: Box Breathing")
        elif choice == '7':
            print("\n=== Signature Cascade Session ===")
            phases = [
                ('deep_grounding', 120),
                ('intuitive_insight', 120),
                ('crown_chakra_activation', 120),
                ('theta_gateway', 120),
                ('memory_accelerator', 120)
            ]
            for key, dur in phases:
                preset = therapy.presets[key]
                print(f"\n→ Phase: {preset.name} – {dur//60} min @ {preset.base_freq}Hz/{preset.beat_freq}Hz")
                await therapy.start_session(key, dur)
            print("\nSilent Integration – 1 min. Sit in stillness and integrate.")
            await asyncio.sleep(60)
        elif choice == '8':
            print("\n=== Advanced Golden-Age Routines ===")
            advanced = [
                'mycelial_network_harmony',
                'earth_grid_resonance',
                'acoustic_manifestation_chamber',
                'dna_rejuvenation_pulse',
                'entanglement_bridge_meditation',
                'collective_field_sync',
                'cymatic_pattern_weaving',
                'quantum_acoustic_encoding',
                'remote_vision_amplifier',
                'timeline_probability_scan',
                'integration_chamber_bath',
                'unified_field_embodiment'
            ]
            for i, key in enumerate(advanced, 1):
                preset = therapy.presets[key]
                print(f"{i}) {preset.name} – {preset.base_freq}Hz/{preset.beat_freq}Hz")
            sel = int(input("Select routine: ")) - 1
            if 0 <= sel < len(advanced):
                if visualize:
                    subprocess.Popen([
                        'python',
                        os.path.join(os.path.dirname(__file__), 'cymatics_visualizer.py'),
                        '--mode', str(therapy.presets[advanced[sel]].base_freq)
                    ])
                await therapy.start_session(advanced[sel])
            else:
                print("❌ Invalid choice")
        elif choice == '9':
            print("\n=== Riemann Mode ===")
            await therapy.start_session(HealingGoal.RIEMANN_MODE.value)
        else:
            print("❌ Invalid option")
    print("👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
