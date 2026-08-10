# Yaesu-FT-710-Power-Control
A Windows GUI application for remote power control of Yaesu FT-710 transceiver via CAT interface


📋 Description
This application allows you to turn your Yaesu FT-710 transceiver ON and OFF remotely from your Windows computer. Unlike standard CAT commands that don't work when the transceiver is powered off, this program uses low-level Windows API calls to send a special hardware-level sequence that activates the transceiver even when it's completely off.

Key Features
✅ Remote Power ON/OFF control via USB/COM port

✅ Simple GUI with intuitive buttons

✅ Real-time logging of all operations

✅ Progress indicator during operations

✅ No response waiting - instant operation, no freezes

✅ Admin rights required for low-level port access

✅ Works when transceiver is completely off

📥 Installation
Option 1: Use the compiled EXE (Windows only)
Download FT710_Control.exe from the dist/ folder and run it as Administrator.

Steps:

# Clone the repository
git clone https://github.com/yourusername/yaesu-ft710-power-control.git
cd yaesu-ft710-power-control

# Run the application
python src/ft710_control.py

🚀 Usage
Quick Start
Run as Administrator (right-click → "Run as administrator")

Select your COM port (e.g., COM8)
Select Baud rate (default: 38400, must match transceiver settings)
Click ON to power on the transceiver
Click OFF to power off the transceiver

Build Options

# With console window (for debugging)
pyinstaller --onefile --name "FT710_Control_Debug" src/ft710_control.py

# With custom icon
pyinstaller --onefile --windowed --name "FT710_Control" --icon=icon.ico src/ft710_control.py

⚠️ Disclaimer
This software is provided "as is" without warranty of any kind. Use at your own risk. The author is not responsible for any damage to your transceiver or other equipment. Always follow Yaesu's safety guidelines when operating your transceiver.

