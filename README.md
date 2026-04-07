# � Jarvis Ultra Holographic Interface

An enhanced gesture-controlled holographic drawing interface inspired by Iron Man’s JARVIS. This project runs a futuristic webcam-based canvas powered by MediaPipe hand tracking and OpenCV rendering.

## 🚀 Active Application

The main application file is:

- `jarvis_ultra_final.py` — the current primary interface with advanced brush modes, palm erase, Glow HUD, particle effects, and Arc Reactor overlays.

Legacy support file:

- `ironman_magic_canvas.py` — earlier version of the gesture canvas, still available in the repository.

## 🎯 Features

- **Live hand gesture tracking** using MediaPipe Hands
- **Gesture drawing** with your index finger
- **Selection mode** using index + middle finger
- **Palm erase** mode for quick removal of content
- **Multiple brush styles**:
  - `NORMAL` glow brush
  - `LIGHTNING` streak brush
  - `FIRE` particle brush
  - `PORTAL` swirl brush
- **Toolbar buttons** for color selection, clear, and save
- **Interactive HUD** with system panels and mode indicators
- **Arc Reactor effect** and animated overlays for an Iron Man-inspired look
- **Save as PNG** via toolbar or `S` key

## 📋 Requirements

- Python 3.7+
- Webcam or camera
- `opencv-python`
- `mediapipe`
- `numpy`

## 🧩 Installation

```bash
git clone https://github.com/Vishnu-0509/Ironman_magic_canvas.git
cd Ironman_magic_canvas
python -m venv venv
venv\Scripts\activate
pip install opencv-python mediapipe numpy
```

## ▶️ Usage

Run the main interface:

```bash
python jarvis_ultra_final.py
```

### Controls

- `INDEX FINGER` only: Draw
- `INDEX + MIDDLE FINGER`: Enter selection mode for toolbar
- `PALM OPEN`: Erase
- `1` → `NORMAL` brush
- `2` → `LIGHTNING` brush
- `3` → `FIRE` brush
- `4` → `PORTAL` brush
- `+` / `-` → Brush size up/down
- `C` → Clear canvas
- `S` → Save screenshot
- `ESC` → Exit application

## 📂 Project Structure

```
jarvis_ultra_final.py        # Active gesture interface
ironman_magic_canvas.py      # Previous gesture canvas version
README.md                    # Project documentation
.gitignore                   # Files to ignore in git
venv/                        # Python virtual environment (ignored)
```

## 🔧 Notes

- The system uses single-hand detection with `MediaPipe Hands`.
- The UI uses OpenCV overlays for buttons, panels, and glow effects.
- Drawing is rendered on an overlay canvas and blended with the webcam feed.

## 🎨 Customization

Edit `jarvis_ultra_final.py` to change:

- Default brush color: `draw_color`
- Eraser thickness: `eraser_thickness`
- Brush styles in `draw_glow_line`, `draw_lightning`, `draw_fire`, and `draw_portal`
- Detection confidence via `min_detection_confidence` and `min_tracking_confidence`

## ⚡ Performance Tips

- Use good lighting for more stable hand detection
- Keep the camera view clear and centered
- Lower brush thickness if the frame rate drops

## 👤 Author

Vishnu-0509

## 🙏 Acknowledgments

- Built with [OpenCV](https://opencv.org/)
- Powered by [MediaPipe](https://mediapipe.dev/)
- Inspired by the Iron Man JARVIS interface

---

**Enjoy the Jarvis Ultra interface!** ✨
