from quantum_audio_therapy_v2 import QuantumAudioTherapy

if __name__ == '__main__':
    # 10-second Quantum OM Formula demo
    therapy = QuantumAudioTherapy(duration=10, volume=0.5)
    # Select the Quantum OM preset
    therapy.current_preset = therapy.presets['quantum_om']
    # Generate and save demo audio
    audio = therapy._generate_audio()
    therapy._save_audio(audio, 'quantum_om_demo')
    print("Demo completed: quantum_om_demo.wav saved in output/audio_sessions")
