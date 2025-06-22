import asyncio
import json
import pylsl
import websockets
import time
import numpy as np

# EEG Processing Constants
SAMPLE_RATE = 256  # Hz, typical for Muse
FFT_WINDOW_SECONDS = 1
SAMPLES_PER_WINDOW = int(SAMPLE_RATE * FFT_WINDOW_SECONDS)
N_CHANNELS = 4  # Assuming 4 channels from Muse (e.g., TP9, AF7, AF8, TP10)
BANDS = {
    'delta': (1, 4),
    'theta': (4, 8),
    'alpha': (8, 13),  # Adjusted alpha upper bound slightly
    'beta': (13, 30),
    'gamma': (30, 100)  # Can be adjusted based on desired focus
}

eeg_buffer = np.zeros((N_CHANNELS, 0))  # Buffer for EEG data: channels x samples
timestamps_buffer = []



def calculate_band_powers(data_window, fs):
    """Calculates band powers for a window of EEG data."""
    _n_channels, n_samples = data_window.shape

    if n_samples == 0:
        return {band: 0.0 for band in BANDS}

    hanning_window = np.hanning(n_samples)
    data_windowed = data_window * hanning_window  # Apply window per channel

    fft_values = np.fft.rfft(data_windowed, axis=1)
    fft_freqs = np.fft.rfftfreq(n_samples, 1.0 / fs)

    psd = np.abs(fft_values)**2

    avg_band_powers = {}
    for band, (low_freq, high_freq) in BANDS.items():
        freq_indices = np.where((fft_freqs >= low_freq) &
                                (fft_freqs < high_freq))[0]
        if len(freq_indices) > 0:
            band_power_per_channel = np.mean(psd[:, freq_indices], axis=1)
            avg_band_powers[band] = float(np.mean(band_power_per_channel))
        else:
            avg_band_powers[band] = 0.0

    return avg_band_powers


async def eeg_sender(websocket):
    """WebSocket handler: reads from LSL, calculates band powers, and sends them."""
    global eeg_buffer, timestamps_buffer
    print("🔌 Attempting to connect to LSL EEG outlet ('Muse EEG')...")
    inlet = None

    async def connect_lsl_stream():
        nonlocal inlet
        global eeg_buffer, timestamps_buffer  # Ensure global buffer is reset
        print("🔄 Trying to resolve LSL stream 'Muse EEG'...")
        for _ in range(15):  # Retry for a bit
            streams = pylsl.resolve_byprop('name', 'Muse EEG', 1, 0.5)
            if streams:
                try:
                    inlet = pylsl.StreamInlet(streams[0])
                    eeg_buffer = np.zeros((N_CHANNELS, 0))
                    timestamps_buffer = []
                    print("✅ LSL EEG outlet connected.")
                    return True
                except Exception as e_connect:
                    print(f"⚠️ Error initializing StreamInlet: {e_connect}")
                    inlet = None
            await asyncio.sleep(1)
        print("❌ Failed to connect to LSL stream after retries.")
        return False

    if not await connect_lsl_stream():
        await websocket.close(code=1011, reason="LSL stream not found")
        return

    print("📡 Streaming processed EEG band powers to client...")
    last_sample_reception_time = time.time()

    try:
        while True:
            if inlet is None:
                print("🔴 LSL connection lost. Attempting to reconnect...")
                if not await connect_lsl_stream():
                    print("❌ Failed to reconnect. Closing WebSocket.")
                    reason = "LSL stream lost and reconnect failed"
                    await websocket.close(code=1011, reason=reason)
                    break
                last_sample_reception_time = time.time()  # Reset after reconnect

            try:
                # Short timeout for responsiveness
                sample, timestamp = inlet.pull_sample(timeout=0.1)

                if sample:
                    last_sample_reception_time = time.time()
                    current_sample_np = np.array(sample).reshape(N_CHANNELS, 1)
                    eeg_buffer = np.concatenate((eeg_buffer, current_sample_np), axis=1)
                    timestamps_buffer.append(timestamp)

                    # Keep buffer from growing too large, maintain a bit more
                    # than needed for one window
                    # 1 window + 0.25s margin
                    max_buf_s = SAMPLES_PER_WINDOW + (SAMPLE_RATE // 4)
                    if eeg_buffer.shape[1] > max_buf_s:
                        # Keep exactly one window for next processing
                        excess = eeg_buffer.shape[1] - SAMPLES_PER_WINDOW
                        eeg_buffer = eeg_buffer[:, excess:]
                        timestamps_buffer = timestamps_buffer[excess:]

                    if eeg_buffer.shape[1] >= SAMPLES_PER_WINDOW:
                        # Process the most recent full window
                        data_to_process = eeg_buffer[:, -SAMPLES_PER_WINDOW:]

                        band_powers = calculate_band_powers(data_to_process,
                                                            SAMPLE_RATE)

                        payload = {
                            'timestamp': timestamps_buffer[-1],
                            'band_powers': band_powers
                        }
                        await websocket.send(json.dumps(payload))
                        # print(f"➡️ Sent: {band_powers}")  # Verbose

                        # Sliding buffer handled by trimming logic above.

                elif (time.time() - last_sample_reception_time) > 5.0:
                    print("🕒 No data from LSL for >5s. Assuming stream issue.")
                    if inlet:
                        inlet.close_stream()
                    inlet = None  # Trigger reconnection

            except pylsl.LostError:
                print("📉 LSL LostError. Stream connection lost abruptly.")
                if inlet:
                    inlet.close_stream()
                inlet = None  # Trigger reconnection
            except Exception as e_pull:
                error_msg = f"{type(e_pull).__name__}: {e_pull}"
                print(f"🔥 Error during LSL pull or processing: {error_msg}")
                if inlet:
                    inlet.close_stream()
                inlet = None  # Trigger reconnection
                await asyncio.sleep(0.5)  # Brief pause before retry

            # Adjust sleep for desired processing rate, e.g. 4Hz update
            sleep_duration = 1.0 / (SAMPLE_RATE / (SAMPLES_PER_WINDOW / 4))
            await asyncio.sleep(sleep_duration)

    except websockets.exceptions.ConnectionClosed:
        print("💔 Client WebSocket connection closed.")
    except Exception as e_outer:
        error_msg = f"{type(e_outer).__name__}: {e_outer}"
        print(f"💥 Unhandled exception in eeg_sender: {error_msg}")
    finally:
        if inlet:
            inlet.close_stream()
        print("🛑 EEG sender task for this client finished.")


async def main():
    async with websockets.serve(eeg_sender, 'localhost', 8765) as _:
        print("🌐 WebSocket server running at ws://localhost:8765")
        print("   Listening for LSL stream 'Muse EEG'...")
        print("   Will send processed EEG band powers to connected clients.")
        await asyncio.Future()  # Run forever until interrupted



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🌀 Server shutting down...")
