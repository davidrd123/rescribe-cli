# Rescribe CLI

A Windows system tray application that converts speech to text using OpenAI's Whisper Large V3 Turbo model. Record audio with a hotkey and get instant transcription copied to your clipboard.

## Features

- **One-Touch Recording**: Press F9 to start/stop recording
- **System Tray Integration**: Easy access and status monitoring
- **Clipboard Integration**: Transcribed text automatically copied to clipboard
- **Visual Feedback**: Color-coded system tray icon shows current status
  - 🟢 Green: Ready
  - 🔴 Red: Recording
  - 🟡 Yellow: Loading model
  - 🟠 Orange: Transcribing
  - ⚫ Gray: Error

## Requirements

- Windows 10/11
- Python 3.8+
- CUDA-compatible GPU (recommended) or CPU
- PyTorch
- Required Python packages:
  ```
  torch
  transformers
  pyaudio
  keyboard
  pyperclip
  pystray
  Pillow
  ```

## Platform Support

Currently, this application is designed for Windows only. The following features are Windows-specific:
- System tray integration
- Global hotkey capture
- Background service setup
- Startup configuration

Linux/MacOS support may be added in the future.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rescribe-cli.git
   cd rescribe-cli
   ```

2. Install Poetry (if not already installed):
   ```powershell
   # Windows (Powershell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   ```

3. Verify Poetry installation and environment:
   ```powershell
   # Check Poetry version
   poetry --version
   
   # See which environment Poetry is using
   poetry env info
   
   # If you have an existing .venv, you might want to remove it first
   Remove-Item -Recurse -Force .venv  # Optional: only if you want to start fresh
   ```

4. Install dependencies:
   ```powershell
   poetry install
   ```

## Usage

### Command Line
```bash
# Check your Poetry environment
poetry env info

# Run the application
poetry run python rescribe.py
```

### Windows Background Service Setup
To run the application in the background without a console window:

1. Right-click on your desktop → New → Shortcut
2. For the location, enter:
   ```
   "C:\Path\To\Your\.venv\Scripts\pythonw.exe" "C:\Path\To\Your\rescribe.py"
   ```
   Replace the paths with your actual Poetry venv location (use `poetry env info --path` to find it)
3. Name the shortcut (e.g., "Rescribe")
4. Optional: Copy the shortcut to your startup folder (`Win + R` → `shell:startup`) to run at system startup

Once running:
1. The application will appear in your system tray
2. Press F9 to start recording
3. Press F9 again to stop recording and begin transcription
4. The transcribed text will automatically copy to your clipboard

## Technical Details

- Uses OpenAI's Whisper Large V3 Turbo model for transcription
- Audio recorded at 16kHz, mono channel
- Supports GPU acceleration with CUDA
- Handles audio buffer overflow protection
- Asynchronous model loading

## License

[Your chosen license]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
