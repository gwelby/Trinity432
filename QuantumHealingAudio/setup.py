"""
Setup script for Quantum Audio Therapy with Muse EEG Integration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import importlib.util

# ASCII Art for the setup
SETUP_ART = """
==================================================
  Quantum Audio Therapy with Muse EEG - Setup
==================================================
"""

def print_colored(text, color):
    """Print colored text"""
    colors = {
        'header': '\033[95m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'green': '\033[92m',
        'warning': '\033[93m',
        'fail': '\033[91m',
        'end': '\033[0m',
        'bold': '\033[1m',
        'underline': '\033[4m'
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def print_header():
    print_colored(SETUP_ART, 'cyan')
    print_colored("🔧 Setting up Quantum Audio Therapy with Muse EEG integration...", 'cyan')
    print_colored("This will install the required Python packages and set up directories.", 'cyan')
    print("-" * 50)

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print_colored("❌ Python 3.7 or higher is required. Please upgrade your Python version.", 'fail')
        sys.exit(1)
    print_colored(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected", 'green')

def create_directories():
    """Create necessary directories for the application"""
    directories = [
        "output",
        "output/audio_sessions",
        "output/eeg_data",
        "presets"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print_colored(f"✓ Created directory: {directory}", 'green')
        except Exception as e:
            print_colored(f"❌ Error creating directory {directory}: {e}", 'fail')

def is_package_installed(package_name):
    """Check if a Python package is installed"""
    return importlib.util.find_spec(package_name) is not None

def install_package(package, upgrade=False, source=None):
    """Install a Python package"""
    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    if source:
        cmd.append(source)
    else:
        cmd.append(package)
    
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def install_dependencies():
    """Install required Python packages"""
    print_colored("\n🔧 Checking and installing dependencies...", 'cyan')
    
    # First install pip packages from requirements.txt
    if os.path.exists("requirements.txt"):
        print_colored("Installing packages from requirements.txt...", 'cyan')
        if not install_package("-r requirements.txt"):
            print_colored("❌ Failed to install packages from requirements.txt", 'fail')
            return False
    
    # Install Muse LSL from GitHub
    print_colored("\n🔍 Setting up Muse LSL...", 'cyan')
    if not is_package_installed("muselsl"):
        print_colored("Installing Muse LSL from GitHub...", 'cyan')
        if not install_package("git+https://github.com/alexandrebarachant/muse-lsl.git"):
            print_colored("❌ Failed to install Muse LSL", 'fail')
            return False
    
    print_colored("✓ All dependencies installed successfully", 'green')
    return True

def check_muse_installation():
    """Check if Muse LSL is properly installed"""
    print_colored("\n🔍 Verifying Muse LSL installation...", 'cyan')
    
    # Check for pylsl
    try:
        import pylsl
        print_colored("✓ pylsl is installed", 'green')
    except ImportError:
        print_colored("❌ pylsl is not installed correctly", 'fail')
        return False
    
    # Check for muselsl
    try:
        from muselsl import list_muses, stream
        print_colored("✓ muse-lsl is installed", 'green')
        
        # Try to list available Muses
        try:
            muses = list_muses()
            if muses:
                print_colored(f"🎧 Found {len(muses)} Muse headset(s) nearby:", 'green')
                for i, muse in enumerate(muses, 1):
                    print_colored(f"  {i}. {muse['name']} (RSSI: {muse['rssi']} dBm)", 'green')
            else:
                print_colored("ℹ️ No Muse headsets found nearby. Make sure your Muse is turned on.", 'warning')
        except Exception as e:
            print_colored(f"⚠️ Could not scan for Muse headsets: {e}", 'warning')
        
        return True
        
    except ImportError as e:
        print_colored(f"❌ muse-lsl is not installed correctly: {e}", 'fail')
        return False

def main():
    print_header()
    check_python_version()
    create_directories()
    
    if install_dependencies() and check_muse_installation():
        print_colored("\n🎉 Setup completed successfully!", 'green')
        print_colored("\nNext steps:", 'bold')
        print("1. Turn on your Muse headset")
        print("2. Run: python quantum_audio_therapy_v2.py")
        print("\nFor help, run: python quantum_audio_therapy_v2.py --help")
    else:
        print_colored("\n❌ Setup encountered some issues. Please check the messages above.", 'fail')
        print_colored("\nTroubleshooting:", 'bold')
        print("- Make sure you have Python 3.7+ installed")
        print("- Try installing Muse LSL manually: pip install git+https://github.com/alexandrebarachant/muse-lsl.git")
        print("- Check your internet connection")
        print("- Run this script as administrator if you encounter permission errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
