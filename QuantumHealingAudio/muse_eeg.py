"""
Muse EEG Integration Module for Quantum Audio Therapy
Provides real-time brainwave monitoring and feedback.
"""

import asyncio
import numpy as np
from pylsl import StreamInlet, resolve_byprop, StreamInfo, StreamOutlet
from collections import deque
import time
import json
import os
from datetime import datetime
from bleak import BleakScanner, BleakClient
import struct
import bitstring # Added for decoding packed 12-bit EEG samples

# Control Characteristic
CONTROL_CHAR_UUID = "273e0001-4c4d-454d-96be-f03bac821358"  # MUSE_GATT_ATTR_STREAM_TOGGLE

# EEG Data Characteristics (as per muse-lsl constants.py)
EEG_TP9_UUID      = "273e0003-4c4d-454d-96be-f03bac821358"  # TP9 - Left Ear
EEG_AF7_UUID      = "273e0004-4c4d-454d-96be-f03bac821358"  # AF7 - Left Forehead (FP1)
EEG_AF8_UUID      = "273e0005-4c4d-454d-96be-f03bac821358"  # AF8 - Right Forehead (FP2)
EEG_TP10_UUID     = "273e0006-4c4d-454d-96be-f03bac821358"  # TP10 - Right Ear
EEG_RIGHTAUX_UUID = "273e0007-4c4d-454d-96be-f03bac821358"  # Right Aux

ALL_EEG_CHAR_UUIDS = [
    EEG_TP9_UUID,
    EEG_AF7_UUID,
    EEG_AF8_UUID,
    EEG_TP10_UUID,
    EEG_RIGHTAUX_UUID,
]

# Placeholder for the actual EEG characteristic we will subscribe to, will be replaced by iterating ALL_EEG_CHAR_UUIDS
# Constants for decoding EEG data from individual characteristics
MUSE_LSB = 0.48828125  # uV per LSB, for 12-bit ADC with 2Vpp range (2000000 uV / 2^12)

EEG_CHARACTERISTIC_TO_INDEX = {
    EEG_TP9_UUID: 0,
    EEG_AF7_UUID: 1,
    EEG_AF8_UUID: 2,
    EEG_TP10_UUID: 3,
    EEG_RIGHTAUX_UUID: 4,
}

EEG_CHANNEL_NAMES = ["TP9", "AF7", "AF8", "TP10", "RIGHTAUX"]

# Placeholder for the actual EEG characteristic we will subscribe to, will be replaced by iterating ALL_EEG_CHAR_UUIDS
EEG_CHAR_UUID = EEG_TP9_UUID # Retain for now, but will be superseded by the list

class MuseEEG:
    def __init__(self, buffer_duration=5.0, sample_rate=256):
        """
        Initialize the Muse EEG interface.
        
        Args:
            buffer_duration: Duration of the EEG data buffer in seconds
            sample_rate: Expected sample rate of the Muse headset (usually 220-256 Hz)
        """
        self.buffer_duration = buffer_duration
        self.sample_rate = sample_rate
        self.buffer_size = int(buffer_duration * sample_rate)
        self.eeg_data = {
            'timestamps': deque(maxlen=self.buffer_size),
            'channels': {
                'TP9': deque(maxlen=self.buffer_size),
                'AF7': deque(maxlen=self.buffer_size),
                'AF8': deque(maxlen=self.buffer_size),
                'TP10': deque(maxlen=self.buffer_size),
                'RIGHTAUX': deque(maxlen=self.buffer_size)  # Added RIGHTAUX for 5-channel support
            }
        }
        self.fft_data = {}
        self.band_powers = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }
        self.running = False
        self.connected = False
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eeg_data')
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def connect(self, timeout=10.0):
        """Connect to a Muse headset via LSL."""
        print("🔍 Searching for Muse EEG stream...")
        try:
            # Discover EEG streams via LSL by property
            streams = resolve_byprop('type', 'EEG', 1, timeout)
            if streams:
                info = streams[0]
                self.inlet = StreamInlet(info)
                print(f"✅ Connected to {info.name()}")
                self.connected = True
                return True
        except Exception as e:
            print(f"⚠️ LSL connection failed: {e}")

        print("❌ Could not find Muse EEG stream")
        return False
    
    async def start_streaming(self, callback=None):
        """Start streaming EEG data."""
        if not self.connected:
            if not await self.connect():
                return False
        
        self.running = True
        print("🎧 Starting EEG data stream...")
        
        # Start the data collection loop in a separate task
        self.stream_task = asyncio.create_task(self._stream_loop(callback))
        return True
    
    async def _stream_loop(self, callback):
        """Main loop for streaming and processing EEG data."""
        try:
            while self.running:
                # Get a new sample
                sample, timestamp = self.inlet.pull_sample(timeout=1.0)
                
                if sample:
                    # Add to buffer
                    self.eeg_data['timestamps'].append(timestamp)
                    for i, ch in enumerate(self.eeg_data['channels'].keys()):
                        self.eeg_data['channels'][ch].append(sample[i])
                    
                    # Process the data
                    self._process_eeg()
                    
                    # Call the callback with the latest data
                    if callback:
                        await callback(self.get_latest_metrics())
                
                # Small sleep to prevent CPU overload
                await asyncio.sleep(0.001)
                
        except Exception as e:
            print(f"❌ Error in stream loop: {e}")
            self.running = False
    
    def _process_eeg(self):
        """Process the EEG data to extract frequency bands and metrics."""
        # Ensure we have enough data
        if len(self.eeg_data['timestamps']) < self.sample_rate:  # At least 1 second of data
            return
        
        # Convert to numpy arrays for processing
        data = {ch: np.array(self.eeg_data['channels'][ch]) for ch in self.eeg_data['channels']}
        
        # Process each channel
        self.fft_data = {}
        self.band_power = {}
        
        for ch in data:
            # Apply FFT
            fft_vals = np.fft.fft(data[ch])
            fft_freq = np.fft.fftfreq(len(fft_vals), 1.0/self.sample_rate)
            
            # Store FFT data
            self.fft_data[ch] = {
                'freq': fft_freq,
                'power': np.abs(fft_vals) ** 2
            }
            
            # Calculate band powers
            self.band_power[ch] = {}
            for band, (low, high) in self.band_powers.items():
                idx = np.where((fft_freq >= low) & (fft_freq <= high))[0]
                if len(idx) > 0:
                    self.band_power[ch][band] = np.mean(self.fft_data[ch]['power'][idx])
                else:
                    self.band_power[ch][band] = 0.0
    
    def get_latest_metrics(self):
        """Get the latest EEG metrics."""
        if not self.band_power:
            return None
        
        # Calculate average across channels for each band
        avg_bands = {}
        for band in self.band_powers.keys():
            band_powers = [self.band_power[ch].get(band, 0) for ch in self.eeg_data['channels']]
            avg_bands[band] = np.mean(band_powers)
        
        return {
            'timestamp': time.time(),
            'band_powers': avg_bands,
            'attention': self._calculate_attention(),
            'meditation': self._calculate_meditation(),
            'stress_index': self._calculate_stress_index()
        }
    
    def _calculate_attention(self):
        """Calculate attention metric from beta/(alpha+theta)."""
        if not self.band_power:
            return 0.0
        
        total_beta = 0
        total_alpha_theta = 0
        
        for ch in self.band_power:
            total_beta += self.band_power[ch].get('beta', 0)
            total_alpha_theta += self.band_power[ch].get('alpha', 0.1) + self.band_power[ch].get('theta', 0.1)
        
        attention = (total_beta / total_alpha_theta) * 100
        return np.clip(attention, 0, 100)
    
    def _calculate_meditation(self):
        """Calculate meditation metric from theta/alpha."""
        if not self.band_power:
            return 0.0
        
        total_theta = 0
        total_alpha = 0
        
        for ch in self.band_power:
            total_theta += self.band_power[ch].get('theta', 0.1)
            total_alpha += self.band_power[ch].get('alpha', 0.1)
        
        meditation = (total_theta / total_alpha) * 100
        return np.clip(meditation, 0, 100)
    
    def _calculate_stress_index(self):
        """Calculate a stress index from beta/theta."""
        if not self.band_power:
            return 0.0
        
        total_beta = 0
        total_theta = 0
        
        for ch in self.band_power:
            total_beta += self.band_power[ch].get('beta', 0.1)
            total_theta += self.band_power[ch].get('theta', 0.1)
        
        stress = (total_beta / total_theta) * 100
        return np.clip(stress, 0, 100)
    
    async def stop_streaming(self):
        """Stop the EEG data stream."""
        self.running = False
        if hasattr(self, 'stream_task'):
            await self.stream_task
        print("⏹️ EEG streaming stopped")
    
    def save_session_data(self):
        """Save the current session data to a file."""
        if not self.eeg_data['timestamps']:
            print("No EEG data to save")
            return
        
        # Prepare data for saving
        data = {
            'session_id': self.session_id,
            'start_time': datetime.fromtimestamp(self.eeg_data['timestamps'][0]).isoformat(),
            'end_time': datetime.fromtimestamp(self.eeg_data['timestamps'][-1]).isoformat(),
            'sample_rate': self.sample_rate,
            'channels': {ch: list(self.eeg_data['channels'][ch]) for ch in self.eeg_data['channels']},
            'timestamps': list(self.eeg_data['timestamps']),
            'band_powers': self.band_power
        }
        
        # Save to file
        filename = os.path.join(self.output_dir, f"eeg_session_{self.session_id}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved EEG session data to {filename}")
        return filename

class BluetoothMuseEEG:
    async def _write_control_command(self, command_bytes: bytearray):
        """Writes raw bytes to the control characteristic."""
        if self.client and self.client.is_connected:
            try:
                print(f"MuseEEG DEBUG: Writing to control char {CONTROL_CHAR_UUID}: {command_bytes.hex()}")
                await self.client.write_gatt_char(CONTROL_CHAR_UUID, command_bytes, response=True) # Assuming response=True is desired for control commands
                print(f"MuseEEG DEBUG: Successfully wrote to control char.")
            except Exception as e:
                print(f"MuseEEG ERROR: Failed to write to control char {CONTROL_CHAR_UUID}: {e}")
        else:
            print("MuseEEG ERROR: Client not connected, cannot write control command.")

    async def _write_control_command_str(self, command_str: str):
        """Encodes a string command and writes it to the control characteristic.
        Follows the format: [len_byte, char1, char2, ..., charN, newline_char]
        Example: 'd' -> [0x02, 0x64, 0x0a]
        """
        if not isinstance(command_str, str) or not command_str:
            print(f"MuseEEG ERROR: Invalid command string: {command_str}")
            return
        
        payload_bytes = command_str.encode('utf-8')
        # The length byte includes the payload + the newline character
        command_len = len(payload_bytes) + 1 
        
        if command_len > 255:
            print(f"MuseEEG ERROR: Command string too long for single byte length: {command_str}")
            return

        final_command = bytearray([command_len]) + payload_bytes + bytearray([ord('\n')])
        await self._write_control_command(final_command)

    """BLE integration for Muse MU-02 headset."""
    def __init__(self, device_name="Muse", buffer_duration=5.0, sample_rate=256):
        from muse_eeg import MuseEEG
        self.device_name = device_name
        self.muse = MuseEEG(buffer_duration, sample_rate)
        self.client = None
        self.outlet = None
        self.callback = None
        # Track BLE connection state on wrapper
        self.connected = False
        self.running = False
        # For assembling 5-channel samples from individual characteristic notifications
        self.current_sample_buffer = [0.0] * 5  # Order: TP9, AF7, AF8, TP10, RIGHTAUX
        self.channel_updated_flags = [False] * 5
        self.last_timestamp = 0 # To help reconstruct timestamps for LSL samples

    async def connect(self, timeout=10.0):
        """Scan and connect to Muse MU-02 via BLE using discover()"""
        print(f"🔍 Scanning for BLE device {self.device_name}...")
        # Discover nearby BLE devices
        try:
            devices = await BleakScanner.discover(timeout=timeout)
        except Exception as e:
            print(f"⚠️ Discovery error: {repr(e)}")
            devices = []
        if not devices:
            print("❌ No BLE devices discovered")
            return False
        print(f"📡 Discovered {len(devices)} devices:")
        for d in devices:
            print(f"- {d.name or 'Unknown'} ({d.address})")
        # Find target by name or address
        target = None
        for d in devices:
            if (d.name and self.device_name in d.name) \
               or (d.address.lower() == self.device_name.lower()):
                target = d
                break
        if not target:
            print(f"❌ Could not find BLE device {self.device_name}")
            # Prompt user to select from discovered devices
            for idx, d in enumerate(devices, start=1):
                print(f"{idx}. {d.name or 'Unknown'} ({d.address})")
            selection = input("Select device by number (or press Enter to cancel): ")
            if selection.strip().isdigit():
                idx = int(selection.strip()) - 1
                if 0 <= idx < len(devices):
                    target = devices[idx]
                else:
                    print("Invalid selection. Aborting BLE connection.")
                    return False
            else:
                print("No selection made. Aborting BLE connection.")
                return False
        print(f"🔎 Using BLE device {target.name or 'Unknown'} ({target.address})")
        print(f"MuseEEG DEBUG: Attempting BleakClient.connect() with timeout: {timeout}s") # Log timeout
        self.client = BleakClient(target, timeout=timeout)
        try:
            await self.client.connect()
            print(f"✅ Connected to {target.name} ({target.address})")
            print("MuseEEG INFO: Pausing for 1s after connection to allow stabilization...")
            await asyncio.sleep(1.0) # Allow time for connection to stabilize
            self.connected = True
            return True
        except Exception as e:
            print(f"⚠️ BLE connect failed: {repr(e)}")
            return False

    def _decode_eeg_channel_data(self, data: bytearray) -> list[float]:
        """
        Decodes a 20-byte EEG data packet for a single channel using bitstring.
        Muse 2016 (MU-02) packets:
        - Byte 0-1: Sequence number (uint16_be)
        - Byte 2-19: 12 samples, each 12 bits packed into 1.5 bytes (18 bytes total)
        Returns a list of float samples in uV.
        """
        # Sequence number (uint16_be), bytes 0-1. Not used for now.
        # seq_num = bitstring.BitArray(bytes=data[0:2]).read('uintbe:16')

        # EEG samples are in bytes 2-19 (18 bytes).
        # Each sample is 12 bits, unsigned, big-endian. There are 12 such samples.
        payload = data[2:]
        try:
            # Each 12 samples are 12 bits unsigned big-endian
            samples_raw = bitstring.BitArray(bytes=payload).unpack('uintbe:12'*12)
        except bitstring.ReadError as e:
            print(f"MuseEEG ERROR: Could not decode EEG channel data: {e}. Data: {payload.hex()}")
            return []
        
        # Convert to uV: (raw_value - 2048) * MUSE_LSB
        # The raw values are 0-4095 (12-bit). Subtracting 2048 centers them around 0.
        samples_uv = [(s - 2048) * MUSE_LSB for s in samples_raw]
        return samples_uv

    async def _notify_handler(self, sender: str, data: bytearray):
        """Handle BLE EEG notification from one of the 5 EEG characteristics."""
        # print(f"MuseEEG DEBUG: _notify_handler from {sender}, data len: {len(data)}")

        channel_index = EEG_CHARACTERISTIC_TO_INDEX.get(sender)
        if channel_index is None:
            # print(f"MuseEEG WARNING: Notification from unknown sender: {sender}")
            return

        decoded_samples_uv = self._decode_eeg_channel_data(data)
        if not decoded_samples_uv:
            # print(f"MuseEEG WARNING: No samples decoded from {sender}")
            return

        # Use the last sample from the packet for this channel
        # This matches muse-lsl behavior and ensures we use the most recent reading for this channel
        self.current_sample_buffer[channel_index] = decoded_samples_uv[-1]
        self.channel_updated_flags[channel_index] = True

        # Check if all 5 channels have reported new data
        if all(self.channel_updated_flags):
            current_timestamp = time.time()
            # If last_timestamp is 0, it's the first sample, so use current_timestamp
            # Otherwise, estimate timestamp based on sample rate (approximate)
            # This is a simplification; LSL usually gets timestamps from pull_sample or inlet
            if self.last_timestamp == 0:
                lsl_timestamp = current_timestamp
            else:
                # Approximate based on 12 samples per packet and ~256Hz (actually 220 or 256 for Muse)
                # This is a rough estimate. For precise timing, LSL server-side timestamps are better.
                lsl_timestamp = self.last_timestamp + (12 / self.muse.sample_rate) 
            
            self.last_timestamp = lsl_timestamp

            # print(f"MuseEEG DEBUG: Assembled 5-ch sample: {self.current_sample_buffer} @ {lsl_timestamp}")
            if self.outlet:
                try:
                    self.outlet.push_sample(self.current_sample_buffer, timestamp=lsl_timestamp)
                    # print(f"MuseEEG DEBUG: Pushed 5-ch sample to LSL.")
                except Exception as e:
                    print(f"MuseEEG ERROR: Failed to push 5-ch sample to LSL: {e}")
            else:
                print("MuseEEG WARNING: self.outlet is None, cannot push 5-ch sample.")

            # Reset flags for the next full sample assembly
            self.channel_updated_flags = [False] * 5

            # --- Integration with MuseEEG's internal buffer and processing ---
            # This part needs to be adapted if metrics from MuseEEG are still desired directly
            # For now, we focus on getting the 5-channel stream to LSL.
            # The original MuseEEG class expects samples to be fed differently.
            # A possible approach: self.muse could have a method like `push_sample_from_ble(sample_5ch, timestamp)`

            # Simplified: Add to the underlying MuseEEG buffer (if it's 5-channel aware)
            # self.muse.eeg_data['timestamps'].append(lsl_timestamp)
            # for i, ch_name in enumerate(EEG_CHANNEL_NAMES):
            #     if ch_name in self.muse.eeg_data['channels']:
            #          self.muse.eeg_data['channels'][ch_name].append(self.current_sample_buffer[i])

            # self.muse._process_eeg() # This would need adaptation for 5 channels if used
            # if self.callback:
            #     await self.callback(self.muse.get_latest_metrics()) # This also needs adaptation

    async def start_streaming(self, callback=None):
        """Start BLE EEG notifications and publish to LSL."""
        if not self.client or not self.client.is_connected:
            if not await self.connect():
                return False
        # store callback and create LSL outlet for 5 channels
        self.callback = callback
        if not self.outlet:
            # StreamInfo: name, type, channel_count, nominal_srate, channel_format, source_id
            info = StreamInfo('MuseEEG-BLE', 'EEG', 5, self.muse.sample_rate, 'float32', f"{self.device_name}-BLE")
            # Add channel names to the StreamInfo
            chns = info.desc().append_child("channels")
            for ch_name in EEG_CHANNEL_NAMES:
                chns.append_child("channel")\
                    .append_child_value("label", ch_name)\
                    .append_child_value("unit", "microvolts")\
                    .append_child_value("type", "EEG")
            self.outlet = StreamOutlet(info)
            print(f"MuseEEG INFO: Created 5-channel LSL outlet with source_id: {info.source_id()}")

        # Send command to start streaming data (e.g., 'd' for Muse 2016)
        # Other commands: 'p' (resume), 'h' (halt), 's' (status)
        # We'll use 'd' which is typically 'resume/start data'
        print("MuseEEG INFO: Pausing for 1.5s before sending 'd' command...")
        await asyncio.sleep(1.5) # Increased delay

        if not self.client or not self.client.is_connected:
            print("MuseEEG ERROR: Client disconnected before sending 'd' command. Aborting start_streaming.")
            self.running = False
            return False

        print("MuseEEG INFO: Sending 'd' command to start EEG data stream...")
        await self._write_control_command_str('d')
        print("MuseEEG INFO: Pausing for 0.5s after sending 'd' command...")
        await asyncio.sleep(0.5) # Give headset time to process command

        if not self.client or not self.client.is_connected:
            print("MuseEEG ERROR: Client disconnected before subscribing to notifications. Aborting start_streaming.")
            self.running = False
            return False

        # Subscribe to notifications for all 5 EEG characteristics
        print("MuseEEG INFO: Subscribing to all 5 EEG characteristics...")
        for char_uuid in ALL_EEG_CHAR_UUIDS:
            if not self.client or not self.client.is_connected:
                print(f"MuseEEG ERROR: Client disconnected before subscribing to {char_uuid}. Aborting further subscriptions.")
                break # Exit the loop if disconnected
            try:
                print(f"MuseEEG DEBUG: Attempting to start notifications for UUID: {char_uuid}")
                await self.client.start_notify(char_uuid, self._notify_handler)
                print(f"MuseEEG DEBUG: Successfully started notifications for {char_uuid}.")
                await asyncio.sleep(0.2) # Stagger notification subscriptions
            except Exception as e:
                print(f"MuseEEG ERROR: Failed to start notifications for {char_uuid}: {e}")
                # If one subscription fails, we might want to stop all and return False
                # For now, let's try to subscribe to others but log the error.
                # Consider a more robust error handling strategy here.
                # self.running = False # Potentially stop if a critical char fails
                # return False

        self.running = True
        print(" BLE EEG→LSL streaming started for 5 channels.")
        return True # End of start_streaming

    async def stop_streaming(self):
        """Stop BLE EEG notifications and disconnect."""
        if self.client and self.client.is_connected:
            print("MuseEEG INFO: Sending 'h' command to stop EEG data stream...")
            await self._write_control_command_str('h') # Send halt command
            # await asyncio.sleep(0.1) # Optional small delay

            print("MuseEEG INFO: Unsubscribing from all EEG characteristics...")
            for char_uuid in ALL_EEG_CHAR_UUIDS:
                try:
                    # print(f"MuseEEG DEBUG: Attempting to stop notifications for UUID: {char_uuid}")
                    await self.client.stop_notify(char_uuid)
                    # print(f"MuseEEG DEBUG: Successfully stopped notifications for {char_uuid}.")
                except Exception as e:
                    print(f"MuseEEG ERROR: Failed to stop notifications for {char_uuid}: {e}")
            
            await self.client.disconnect()
            print("⏹️ BLE client disconnected.")
            self.connected = False
        self.running = False
        return True

    def save_session_data(self):
        """Save session data via underlying MuseEEG."""
        return self.muse.save_session_data()


# UUID for Muse MU-02 EEG characteristic (4 channels)
EEG_CHAR_UUID = '273e0003-4c4d-454d-96be-f03bac821358'

# Example usage
async def example_callback(metrics):
    if metrics:
        print(f"🧠 Attention: {metrics['attention']:.1f}% | "
              f"Meditation: {metrics['meditation']:.1f}% | "
              f"Stress: {metrics['stress_index']:.1f}%")

async def main():
    # Create and start the Muse interface
    muse = BluetoothMuseEEG()
    
    try:
        # Start streaming with callback
        if await muse.start_streaming(example_callback):
            print("🎧 Streaming started. Press Ctrl+C to stop.")
            
            # Keep the script running
            while muse.running:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Clean up
        await muse.stop_streaming()
        muse.save_session_data()

if __name__ == "__main__":
    asyncio.run(main())
