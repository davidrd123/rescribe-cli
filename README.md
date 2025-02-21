# Rescribe CLI

A system tray application that converts speech to text using OpenAI's Whisper Large V3 Turbo model. Record audio with a hotkey and get instant transcription copied to your clipboard.

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

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rescribe-cli.git
   cd rescribe-cli
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python speech_to_text.py
   ```

2. The application will appear in your system tray
3. Press F9 to start recording
4. Press F9 again to stop recording and begin transcription
5. The transcribed text will automatically copy to your clipboard

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
