# Robartist - Intelligent Drone Control System

An intelligent drone control system based on voice recognition, gesture recognition, and logo detection, using DJI Tello drone as the hardware.

## Features

- 🎤 **Voice Control**: Real-time voice command control using Vosk speech recognition engine
- 👋 **Gesture Recognition**: MediaPipe-based gesture recognition supporting multiple gesture controls
- 🔍 **Logo Detection**: Real-time logo detection using YOLOv5 model
- 🚁 **Drone Control**: Integrated DJI Tello drone control functionality
- 📹 **Real-time Video Stream**: Live display of drone camera feed

## Project Structure

```
project/
├── RobartistController_press_vosk.py  # Main controller integrating voice recognition and drone control
├── gesture_utils.py                   # Gesture recognition utility functions
├── Status2_LogoDetection.py          # Logo detection module
├── tello_controller.py               # Basic Tello drone control
├── LogoHunting.ipynb                 # Logo detection training and testing notebook
└── README.md                         # Project documentation
```

## Dependencies

### Python Package Requirements
```bash
pip install djitellopy
pip install vosk
pip install mediapipe
pip install opencv-python
pip install torch torchvision
pip install ultralytics
pip install sounddevice
pip install keyboard
pip install python-dotenv
pip install numpy
```

### System Requirements
- Python 3.7+
- Camera device
- Microphone device
- DJI Tello drone

## Installation and Setup

1. **Clone the project**
```bash
git clone <your-repo-url>
cd project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download Vosk speech model**
   - Download appropriate language model from [Vosk official website](https://alphacephei.com/vosk/models)
   - Extract to project directory

4. **Prepare YOLOv5 model**
   - Ensure you have a trained `best.pt` model file for logo detection

## Usage

### Start the main controller
```bash
python RobartistController_press_vosk.py
```

### Supported Voice Commands
- "takeoff" - Take off
- "land" - Land
- "up" - Fly upward
- "down" - Fly downward
- "left" - Fly left
- "right" - Fly right
- "forward" - Fly forward
- "backward" - Fly backward

### Supported Gesture Controls
- ✊ **Fist**: Stop/Hover
- ✋ **Open Palm**: Takeoff/Land
- ✌️ **Victory Sign**: Special function
- 👍 **Thumbs Up**: Confirm command

### Keyboard Controls
- `q` - Exit program
- `t` - Takeoff
- `l` - Land
- Arrow keys - Control flight direction

## Main Module Description

### RobartistController_press_vosk.py
Main controller class integrating:
- Voice recognition processing
- Drone connection and control
- Real-time video stream processing
- Gesture recognition integration
- Multi-threaded audio processing

### gesture_utils.py
Gesture recognition utility module containing:
- MediaPipe hand detection
- Multiple gesture recognition algorithms
- Gesture state determination

### Status2_LogoDetection.py
Logo detection module featuring:
- YOLOv5 model loading
- Real-time logo detection
- Detection result processing

## Development Guide

### Adding New Voice Commands
Add new command recognition logic in the voice processing function in `RobartistController_press_vosk.py`.

### Adding New Gestures
Add new gesture recognition algorithms in the `detect_gesture` function in `gesture_utils.py`.

### Custom Logo Detection
Use `LogoHunting.ipynb` to train your own YOLOv5 model and replace the `best.pt` file.

## Safety Notes

⚠️ **Safety Reminders**:
- Test in indoor open environments
- Ensure drone battery is sufficient
- Maintain safe distance
- Follow local drone flight regulations

## Troubleshooting

### Common Issues
1. **MediaPipe import error**: Reinstall mediapipe package
2. **Drone connection failure**: Check WiFi connection and drone status
3. **Inaccurate voice recognition**: Check microphone settings and ambient noise
4. **Camera cannot open**: Check camera permissions and device usage

## Contributing

Welcome to submit Issues and Pull Requests to improve this project!

## License

MIT License

## Contact

For questions, please contact through GitHub Issues. 
