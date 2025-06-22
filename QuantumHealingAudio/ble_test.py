#!/usr/bin/env python3
"""
BLE Connectivity Test for Muse MU-02
Scans and attempts a BLE connection using BluetoothMuseEEG.
"""
import asyncio
from bleak import BleakScanner
from muse_eeg import BluetoothMuseEEG


async def main():
    timeout = 20.0
    print(f"🔍 Scanning for BLE devices for {timeout}s...")
    devices = await BleakScanner.discover(timeout=timeout)
    if devices:
        print("📡 Found BLE devices:")
        for dev in devices:
            print(f"- {dev.name or 'Unknown'} ({dev.address})")
    else:
        print("📡 No BLE devices found.")

    print("🔌 Testing connection via BluetoothMuseEEG...")
    ble = BluetoothMuseEEG(buffer_duration=1.0, sample_rate=256)
    success = await ble.connect(timeout=timeout)
    if success:
        print("✅ BLE test: Connected successfully.")
        print("🎧 Attempting to start EEG streaming...")
        if await ble.start_streaming():
            print("ዥ Streaming started. Will run for 30 seconds...")
            await asyncio.sleep(30)  # Keep streaming for 30 seconds
            print("🛑 Stopping stream after 30s.")
        else:
            print("❌ Failed to start EEG streaming.")
    else:
        print("❌ BLE test: Connection failed.")

    # Ensure cleanup
    if ble.running:  # stop_streaming also handles disconnect
        print("🧹 Stopping EEG stream (auto-disconnects)...")
        await ble.stop_streaming()

if __name__ == "__main__":
    asyncio.run(main())
