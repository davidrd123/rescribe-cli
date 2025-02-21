import threading
import keyboard
import pyaudio
import wave 
import torch
import time
import pyperclip
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import pystray
from pystray import MenuItem as item
from pystray import Menu as menu
from pystray import Icon as icon
from PIL import Image, ImageDraw

# --
# Constants
# Audio parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# --
# Initialize Model in Background
# ---------------------------
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = "openai/whisper-large-v3-turbo"

model = None
processor = None
pipe = None
model_loaded = threading.Event()  # Add Event for model loading sync

def load_model():
    """Loads the Whisper model asynchronously."""
    global model, processor, pipe
    print("Loading Whisper Large V3 Turbo model...")
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    ).to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        model_kwargs={"language": "en"},  # Force English language mode
        return_timestamps=True
    )
    print("Model loaded successfully.")
    model_loaded.set()  # Signal model is ready

# Load model asynchronously
threading.Thread(target=load_model, daemon=True).start()

# ---------------------------
# Global State
# ---------------------------
is_recording = False
audio_frames = []
p = pyaudio.PyAudio()  # Create a single PyAudio instance

# ---------------------------
# Audio Recording Functions
# ---------------------------
def start_recording():
    """Start recording audio from the microphone."""
    global is_recording, audio_frames

    try:
        device_info = p.get_default_input_device_info()
    except IOError:
        print("❌ No input device found!")
        return

    print(f"🎤 Using device: {device_info['name']}")

    stream = None
    try:
        stream = p.open(format=FORMAT, 
                       channels=CHANNELS,
                       rate=RATE, 
                       input=True,
                       frames_per_buffer=CHUNK)

        print("Recording started... Press 'F9' to stop.")
        is_recording = True
        audio_frames = []
        
        while is_recording:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_frames.append(data)
            except IOError as e:
                print(f"Warning: Audio buffer overflow occurred. Stopping recording.")
                break
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
    
    save_audio()

def save_audio(filename="temp.wav"):
    """Save recorded audio frames to a WAV file."""
    if not audio_frames:
        return
        
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)   
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_frames))
    
    # Update tray state before transcription
    update_tray_state('transcribing')
    
    # Transcribe and copy to clipboard
    text = transcribe_audio(filename)
    pyperclip.copy(text)
    print("Text copied to clipboard!")
    
    # Return to ready state after transcription
    update_tray_state('ready')

# ---------------------------
# Transcription Function
# ---------------------------
def transcribe_audio(filename="temp.wav"):
    """Use the Whisper model to transcribe the given audio file."""
    if not model_loaded.is_set():
        print("Waiting for model to load...")
        model_loaded.wait()
    
    print("Transcribing audio...")
    try:
        result = pipe(filename)
    except Exception as e:
        print(f"❌ Error transcribing audio: {e}")
        return ""
    
    text = result.get("text", "").strip()
    print("Transcription complete:")
    print(text)
    return text

# ---------------------------
# Hotkey Handlers
# ---------------------------

def toggle_recording(_):
    """Toggle recording state on F9 press."""
    global is_recording, model_loaded
    
    if not model_loaded.is_set():
        print("Please wait while the model loads...")
        update_tray_state('loading', "Model loading...")
        model_loaded.wait()
        print("Model loaded successfully, Proceeding...")
        
    if is_recording:
        is_recording = False
        print("Recording stopped.")
        update_tray_state('ready', "Ready - Not Recording")
    else:
        is_recording = True
        print("Recording started.")
        update_tray_state('recording', "Recording...")
        
        # Launch a thread to handle the recording without blocking 
        threading.Thread(target=start_recording, daemon=True).start()

# ---------------------------------------------------------------------
# Tray Icon Setup
# ---------------------------------------------------------------------
def create_menu():
    """Create the right-click menu for the tray icon."""
    return menu(
        item(
            "Toggle Recording (F9)",
            lambda icon, item: toggle_recording(None),
            default=True  # makes this the default action on left click
        ),
        menu.SEPARATOR,
        item(
            "Exit",
            lambda icon, item: icon.stop()
        )
    )

def tray_setup(icon):
    """Called in a dedicated thread once tray_icon.run() starts."""
    print("Tray icon setup starting...")
    icon.menu = create_menu()
    icon.visible = True
    print("Tray icon setup complete!")

def create_circle_icon(color, size=64):
    """Create a circular icon with the specified color."""
    # Create transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate circle dimensions
    margin = 4
    diameter = size - 2 * margin
    
    # Draw circle with outline
    draw.ellipse(
        [margin, margin, margin + diameter, margin + diameter],
        fill=color,
        outline='white',
        width=2
    )
    
    return img

# Create icons for different states
icon_ready = create_circle_icon("green")
icon_recording = create_circle_icon("red")
icon_loading = create_circle_icon("yellow")
icon_error = create_circle_icon("#666666")  # Gray
icon_transcribing = create_circle_icon("orange")  # Orange for processing state

# Initialize tray icon
tray_icon = pystray.Icon(
    "Speech to Text",  # Name
    icon_loading,      # Initial icon
    title="Loading model...",  # Tooltip
    menu=create_menu()
)

def update_tray_state(state, message=None):
    states = {
        'ready': (icon_ready, "Ready - Not Recording"),
        'recording': (icon_recording, "Recording..."),
        'loading': (icon_loading, "Loading model..."),
        'error': (icon_error, "Error - Check console"),
        'transcribing': (icon_transcribing, "Transcribing..."),  # New state
    }
    
    if state in states:
        icon, default_message = states[state]
        tray_icon.icon = icon
        tray_icon.title = message or default_message

# ---------------------------
# Main
# ---------------------------
def main():
    try:
        print("Press 'F9' to start/stop recording")
        # print("Press 'Esc' to stop recording")
        print("Press 'Ctrl+C' to exit")
        
        keyboard.on_press_key("F9", toggle_recording)
        # keyboard.on_press_key("esc", on_stop_hotkey)
        threading.Thread(target=lambda: tray_icon.run(setup=tray_setup), daemon=True).start()
        
        # Replace keyboard.wait with an infinite loop
        while True:
            time.sleep(0.1)  # Prevent CPU spinning
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        p.terminate()  # Clean up PyAudio when exiting

if __name__ == "__main__":
    main()
