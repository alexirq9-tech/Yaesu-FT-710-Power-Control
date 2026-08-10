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

How It Works
The program uses a special low-level sequence that:

Sends a BREAK signal to wake up the COM port

Toggles DTR/RTS hardware control lines

Sends AI0; PS1; commands in specific timing

Immediately closes the connection (no waiting for response)

The transceiver physically powers on as a result, even though the CAT interface is inactive when powered off.


📦 GitHub Repository Structure

yaesu-ft710-power-control/
├── src/
│   └── ft710_control.py          # Main application source code
├── dist/
│   └── FT710_Control.exe         # Compiled executable (if provided)
├── docs/
│   ├── screenshots/              # Application screenshots
│   │   └── main_window.png
│   └── CAT_commands.txt          # Reference CAT commands used
├── README.md                     # This file
├── LICENSE                       # MIT License
├── requirements.txt              # Python dependencies
└── .gitignore                    # Git ignore file


📥 Installation
Option 1: Use the compiled EXE (Windows only)
Download FT710_Control.exe from the dist/ folder and run it as Administrator.

Option 2: Run from source (Python)
Prerequisites:

Python 3.8 or higher

Windows OS (uses Windows API)



Steps:

# Clone the repository
git clone https://github.com/yourusername/yaesu-ft710-power-control.git
cd yaesu-ft710-power-control

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/ft710_control.py


requirements.txt
# No external dependencies required
# Uses only built-in Python libraries and Windows API





🚀 Usage
Quick Start
Run as Administrator (right-click → "Run as administrator")

Select your COM port (e.g., COM8)

Select Baud rate (default: 38400, must match transceiver settings)

Click ON to power on the transceiver

Click OFF to power off the transceiver



Transceiver Settings
Make sure your FT-710 is configured correctly:

Menu Path	Setting	Value
[FUNC] → [OPERATION SETTING] → [GENERAL]	TUN/LIN PORT SELECT	CAT-3
[FUNC] → [OPERATION SETTING] → [GENERAL]	CAT RATE	38400 (or match your PC)
[FUNC] → [OPERATION SETTING] → [GENERAL]	CAT TOT	1000ms or higher



Hardware Connection
Connect the FT-710's TUNER/LINEAR port to your computer via USB

Install the Yaesu USB driver (if not already installed)

Note the COM port number in Device Manager

🛠️ Building the EXE
If you want to build the executable yourself:

# Install PyInstaller
pip install pyinstaller

# Build the EXE (single file, no console window)
pyinstaller --onefile --windowed --name "FT710_Control" src/ft710_control.py

# The EXE will be in the 'dist' folder


Build Options

# With console window (for debugging)
pyinstaller --onefile --name "FT710_Control_Debug" src/ft710_control.py

# With custom icon
pyinstaller --onefile --windowed --name "FT710_Control" --icon=icon.ico src/ft710_control.py





🔧 Troubleshooting
"Permission denied" / "Access denied"
Solution: Right-click the EXE and select "Run as administrator"

"Port not found"
Solution: Check Device Manager for the correct COM port number

The FT-710 usually creates multiple COM ports; try each one

Transceiver doesn't power ON
Solution: Check these settings on the transceiver:

TUN/LIN PORT SELECT must be CAT-3

CAT RATE must match your application speed

USB cable must be connected to the TUNER/LINEAR port

Program freezes or hangs
Solution: This is normal if waiting for response. Try the latest version that doesn't wait for responses.

"Error 5" when opening port
Solution: Run as Administrator (Windows restricts low-level port access)




🧪 Technical Details
CAT Commands Used
Command	Function
AI0;	Disable automatic information (initialization)
PS1;	Power ON command
PS0;	Power OFF command
PS;	Query power status (optional)
Low-Level Sequence (Windows API)
The program uses these Win32 API functions:

CreateFile - Open COM port with direct access

SetCommState - Configure baud rate and serial parameters

EscapeCommFunction - Control DTR/RTS lines and BREAK signal

WriteFile - Send CAT commands

ReadFile - Read responses (optionally)



Sequence Timing

1. Open COM port
2. BREAK signal (250ms)
3. Wait 150ms
4. Toggle DTR/RTS (with 50ms delays)
5. Wait 100ms
6. Send 'AI0;' command
7. Wait 50ms
8. Send 'PS1;' command (power ON)
9. Wait 50ms
10. Close port (no waiting for response)

⚠️ Disclaimer
This software is provided "as is" without warranty of any kind. Use at your own risk. The author is not responsible for any damage to your transceiver or other equipment. Always follow Yaesu's safety guidelines when operating your transceiver.

