# 🧠✨ Quantum Audio Therapy with Muse EEG Integration

A revolutionary tool that combines binaural beats, isochronic tones, and real-time brainwave feedback using the Muse EEG headset. Experience personalized audio therapy that adapts to your brain's response in real-time.

## 🚀 Features

### 🎵 Audio Generation
- Generate binaural beats and isochronic tones
- Multiple wave types: sine, square, sawtooth, triangle
- Customize frequencies, duration, and volume
- High-quality 44.1kHz audio output

### 🧠 Muse EEG Integration
- Real-time brainwave monitoring
- Attention, meditation, and stress metrics
- Adaptive audio therapy based on your brain state
- Session logging with EEG data

### 📊 Data & Analysis
- Save audio sessions with metadata
- Export EEG data for analysis
- Track progress over time
- Generate reports and visualizations

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- Muse EEG headset (optional but recommended)
- Working sound system

### Quick Start

1. **Clone or download** this repository
2. **Run the setup script**:
   ```
   python setup.py
   ```
   This will install all required dependencies and set up the necessary directories.

3. **For Muse EEG users**:
   - Install the official Muse SDK from [Muse Developers](https://developer.choosemuse.com/sdk)
   - Follow the platform-specific setup instructions
   - Make sure your Muse headset is paired with your computer

## 🎵 Usage

### Basic Usage

1. **Start the application**:
   ```
   python quantum_audio_therapy_v2.py
   ```

2. **Select a therapy preset**:
   - Pain Relief
   - Stress Reduction
   - Focus Enhancement
   - Deep Relaxation
   - Sleep Aid
   - Meditation

3. **Choose whether to use Muse EEG** for biofeedback (recommended)

4. **Let the session run** or press Ctrl+C to stop early

### With Muse EEG

1. **Put on your Muse headset** and ensure it's connected
2. **Start a session** with EEG enabled
3. **View real-time metrics**:
   - Attention level
   - Meditation level
   - Stress index
   - Brainwave activity

4. **The audio will adapt** based on your brain's response

### Output Files
Audio sessions: `output/audio_sessions/`
EEG data: `output/eeg_data/`
Session logs: `output/session_*.json`

## 🖥️ Visual Mandala Front-End

To visualize real-time brainwave-driven mandala animation:

1. Install WebSocket server dependencies:
   ```bash
   pip install websockets
   ```
2. Start the Python WebSocket server:
   ```bash
   python ws_server.py
   ```
3. Serve the front-end files:
   ```bash
   cd frontend
   python -m http.server 8000
   ```
4. Open your browser to [http://localhost:8000](http://localhost:8000)

## 🌈 Therapy Presets

### 🩹 Pain Relief
- **174Hz + 7.83Hz Binaural Beat**
  - Targets: Theta (4-8Hz), Alpha (8-13Hz)
  - Benefits: Physical pain relief, tension release
  - Best with: Muse EEG for biofeedback

### 😌 Stress Reduction
- **396Hz + 7.83Hz Binaural Beat**
  - Targets: Alpha (8-13Hz), Theta (4-8Hz)
  - Benefits: Anxiety reduction, emotional release
  - Best for: Daily stress management

### 🎯 Focus Enhancement
- **40Hz + 10Hz Isochronic Tone**
  - Targets: Beta (13-30Hz), Gamma (30-100Hz)
  - Benefits: Improved concentration, mental clarity
  - Best for: Work or study sessions

### 😴 Deep Relaxation
- **432Hz + 4Hz Binaural Beat**
  - Targets: Alpha (8-13Hz), Theta (4-8Hz)
  - Benefits: Deep relaxation, stress relief
  - Best for: Evening wind-down

### 💤 Sleep Aid
- **128Hz + 3Hz Binaural Beat**
  - Targets: Delta (0.5-4Hz), Theta (4-8Hz)
  - Benefits: Deep sleep, restoration
  - Best for: Bedtime routine

### 🧘 Meditation
- **528Hz + 8Hz Binaural Beat**
  - Targets: Theta (4-8Hz), Alpha (8-13Hz)
  - Benefits: Deep meditation, spiritual connection
  - Best with: Muse EEG for state monitoring

## 🔬 Scientific Approach

1. **Baseline Session**: Start with the default pain relief protocol
2. **Document**: Note any physical or emotional sensations
3. **Adjust**: Tweak frequencies based on your experience
4. **Repeat**: Continue the process to find your optimal frequencies

## 📊 Data & Analysis

### Session Logs
All sessions are automatically logged with detailed metadata:
- Timestamp and duration
- Preset and settings used
- Audio file location
- EEG metrics (if available)
- User feedback (optional)

### EEG Data
When using Muse EEG, raw data is saved in the following formats:
- CSV files for easy analysis
- JSON metadata with session details
- Visualizations (coming soon)

### Export Options
- Export session data to CSV/JSON
- Generate PDF reports
- Share anonymized data for research (opt-in)

## ⚠️ Safety & Best Practices

### General Safety
- Start with shorter sessions (5-10 minutes)
- Keep volume at a comfortable level (below 60% of maximum)
- Take regular breaks between sessions
- Discontinue use if you experience discomfort

### Muse EEG Specific
- Ensure proper electrode contact
- Keep the headset clean and charged
- Be aware of potential interference from other devices
- Take breaks every 30 minutes when using EEG

### Medical Disclaimer
This software is for experimental and educational purposes only. It is not intended to diagnose, treat, cure, or prevent any disease. Always consult with a qualified healthcare professional before starting any new therapy.

## 📚 Resources & Learning

### Scientific Research
- [Binaural Beats Research](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4428073/)
- [EEG and Neurofeedback](https://www.frontiersin.org/articles/10.3389/fnhum.2019.00100/full)
- [Sound Therapy Studies](https://www.sciencedirect.com/science/article/pii/S0960982219310404)

### Muse Development
- [Muse Developers Portal](https://developer.choosemuse.com/)
- [Muse LSL Documentation](https://github.com/alexandrebarachant/muse-lsl)
- [EEG 101](https://learn.adafruit.com/adafruit-pill/overview)

## 🙏 Credits & Support

Created with ❤️ by Cascade

### Special Thanks
- InteraXon Inc. for the Muse headset
- The open-source neuroscience community
- All the researchers pushing the boundaries of brain-computer interfaces

### Support This Project
- Report issues on GitHub
- Contribute code or documentation
- Share your experiences and results

---
*This tool is for experimental and educational purposes only. Not intended as medical advice. Always consult with a qualified healthcare professional for medical concerns.*

## 📅 Version History

### v2.0 (2025-05-18)
- Added Muse EEG integration
- Real-time brainwave monitoring
- Adaptive audio therapy
- Enhanced session logging
- New presets and audio options

### v1.0 (2025-05-17)
- Initial release
- Basic binaural beats generator
- Simple frequency presets
- Basic audio export
