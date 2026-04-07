# 🧙‍♂️ Iron Man Magic Air Canvas

A futuristic gesture-based drawing application inspired by Iron Man's JARVIS interface. Control an interactive digital canvas using hand gestures detected via your webcam.

## 🎯 Features

- **Hand Gesture Recognition**: Uses MediaPipe to detect hand movements and positions in real-time
- **Air Drawing**: Draw on a virtual canvas using your index finger
- **Multiple Colors**: Choose from Cyan, Blue, Pink, and Green colors
- **Eraser Mode**: Erase drawings with a dedicated eraser tool
- **Particle Effects**: Dynamic particle system for visual enhancement
- **Glow Effects**: Neon-style glowing lines with blur effects
- **Futuristic HUD**: Iron Man-inspired user interface with status displays
- **Save Drawings**: Capture and save your creations as PNG images
- **Gesture Controls**:
  - **Index finger only**: Draw on canvas
  - **Index + Middle finger**: Select/click buttons on toolbar
  - **+/- Keys**: Adjust brush thickness
  - **C Key**: Clear canvas
  - **S Key**: Save drawing
  - **ESC Key**: Exit application

## 📋 Requirements

- Python 3.7+
- Webcam/Camera
- OpenCV (cv2)
- MediaPipe
- NumPy

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/Vishnu-0509/Ironman_magic_canvas.git
cd Ironman_magic_canvas
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install opencv-python mediapipe numpy
```

## 🎮 How to Use

Run the application:
```bash
python ironman_magic_canvas.py
```

**Interactive Controls:**
- Move your **index finger** over the canvas to draw
- Raise both **index and middle fingers** to enter selection mode for the toolbar
- Use the toolbar buttons to:
  - Select drawing colors (CYAN, BLUE, PINK, GREEN)
  - Activate (ERASE) mode
  - (CLEAR) the canvas
  - (SAVE) your drawing
- Press **+** or **-** keys to increase/decrease brush thickness
- Press **C** to clear the canvas
- Press **S** to save drawings
- Press **ESC** to exit

## 🔧 Project Structure

```
ironman_magic_canvas.py      # Main application file
README.md                      # Documentation
.gitignore                     # Git ignore file
```

## 📸 Technical Details

- **Hand Detection**: MediaPipe Hands solution with single hand tracking
- **Finger Recognition**: Custom finger-up detection using landmark positions
- **Visual Effects**: 
  - Gaussian blur for smooth trail effects
  - Particle system for drawing feedback
  - Glow lines for neon aesthetic
  - Semi-transparent overlays for HUD
- **Canvas Rendering**: 2D drawing surface with blend operations

## 🎨 Customization

You can modify the following in `ironman_magic_canvas.py`:

```python
# Drawing colors
draw_color = (255, 255, 0)   # BGR format (Cyan by default)

# Brush settings
brush_thickness = 8           # Default brush size
eraser_thickness = 40         # Default eraser size

# Hand detection confidence
min_detection_confidence=0.7   # Adjust for sensitivity
min_tracking_confidence=0.7    # Adjust for tracking stability

# Particle settings
particles.append([x, y, np.random.randint(2, 5), 15, color])
# Modify lifespan (15) and radius range (2, 5)
```

## ⚡ Performance Tips

- Ensure good lighting for better hand detection
- Keep your webcam clean
- Position yourself 2-3 feet away from the camera for best results
- Reduce brush thickness for faster rendering on slower computers

## 📝 License

This project is open-source and available for educational purposes.

## 👤 Author

Vishnu-0509

## 🙏 Acknowledgments

- Built with [OpenCV](https://opencv.org/)
- Hand detection powered by [MediaPipe](https://mediapipe.dev/)
- Inspired by Iron Man's JARVIS interface

---

**Enjoy creating your digital masterpieces with gesture control!** 🎨✨
