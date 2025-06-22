# Research Plan for Quantum Audio\Video Therapy

## Purpose
Establish a structured research framework to validate and optimize multisensory biofeedback modalities (sacred-geometry visuals, fluid-cymatics, adaptive audio, ambient lighting, haptics) driven by real-time Muse EEG data.

---

## Research Goals
1. Identify visual mappings that enhance alpha/theta entrainment:
   - Test phi-harmonic mandala shapes vs toroidal fields.
   - Measure subjective relaxation & EEG coherence.
2. Develop low-latency fluid-simulation shaders:
   - Evaluate reaction–diffusion & GPU Poisson ripple models.
   - Benchmark CPU vs WebGL latency (<100 ms end-to-end).
3. Optimize audio biofeedback patterns:
   - Compare binaural vs isochronic beat efficacy.
   - Correlate band-power shifts with audio modulation parameters.
4. Haptic entrainment profiling:
   - Test vibro pulses vs continuous sine on torso.
   - Collect comfort & EEG/heart-rate synchronization.
5. Ambient lighting synergy:
   - Map Philips Hue color schemes to dominant band-power.
   - Evaluate affective response via mood surveys.

---

## Task Breakdown

### 1. Visual Entrainment
- Gather shader assets (Shadertoy examples).
- Create test page with Three.js mandala generator.
- Hook WebSocket EEG → visual parameters.
- Conduct user/EEG trials.

### 2. Fluid Cymatics
- Integrate p5.js or custom WebGL sim.
- Stream EEG→shader uniforms.
- Measure latency and visual coherence.

### 3. Audio Patterns
- Implement Tone.js binaural module.
- Expose band-power controls in UI.
- Record EEG responses to presets.

### 4. Haptic Feedback
- Prototype with Woojer or Arduino vibro motor.
- Define pulse/spatial patterns.
- Sync with band-power; log comfort data.

### 5. Lighting Control
- Use Node.js Hue API to change bulbs.
- Map color/hue/saturation to EEG metrics.
- Survey mood shifts.

### 6. Live Cymatic Visualization
- Research 2D nodal pattern generation (Chladni plate analog).
- Prototype Python visualizer using numpy & matplotlib for 2D cymatic patterns.
- Stream audio output buffer to visualizer for real-time rendering.
- Measure performance: frame rate, latency, pattern coherence.

---

## Tools & Environments
- **EEG**: Bleak + pylsl outlet → Python broker → WebSocket
- **Frontend**: React + Three.js + Tone.js + p5.js GLSL
- **Env Control**: Node.js for Hue API, Arduino for haptics
- **Data Logging**: JSON sessions, CSV export for analysis

---

## Timeline (Phase 1)
1. Week 1: Setup WebSocket broker & Three.js mandala prototype
2. Week 2: Integrate EEG mapping, run alpha/theta entrainment tests


*Document automatically generated – refine as needed.*
