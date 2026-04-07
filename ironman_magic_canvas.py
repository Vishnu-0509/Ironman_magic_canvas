import cv2
import mediapipe as mp
import numpy as np
import math
import time
from collections import deque

# =========================
# INITIALIZATION
# =========================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

ret, frame = cap.read()
if not ret:
    raise RuntimeError("Could not read webcam")

frame = cv2.flip(frame, 1)
h, w, _ = frame.shape

canvas = np.zeros((h, w, 3), dtype=np.uint8)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# =========================
# GLOBALS
# =========================
draw_color = (255, 255, 0)   # Cyan default
brush_thickness = 8
eraser_thickness = 40
mode = "DRAW"
trail = deque(maxlen=25)
particles = []

toolbar_height = 100
last_click_time = 0
click_delay = 0.4

# UI button regions
buttons = [
    {"name": "CYAN", "x1": 20,  "x2": 120, "color": (255, 255, 0)},
    {"name": "BLUE", "x1": 140, "x2": 240, "color": (255, 100, 0)},
    {"name": "PINK", "x1": 260, "x2": 360, "color": (255, 0, 255)},
    {"name": "GREEN", "x1": 380, "x2": 480, "color": (0, 255, 100)},
    {"name": "ERASE", "x1": 520, "x2": 640, "color": (50, 50, 50)},
    {"name": "CLEAR", "x1": 670, "x2": 790, "color": (0, 140, 255)},
    {"name": "SAVE", "x1": 820, "x2": 940, "color": (0, 255, 255)},
]

# =========================
# HELPERS
# =========================
def fingers_up(lm_list):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    fingers = []
    for tip, pip in zip(tips, pips):
        fingers.append(1 if lm_list[tip][1] < lm_list[pip][1] else 0)
    return fingers

def add_particle(x, y, color):
    particles.append([x, y, np.random.randint(2, 5), 15, color])

def update_particles(img):
    alive = []
    for p in particles:
        x, y, r, life, color = p
        if life > 0:
            overlay = img.copy()
            drift_x = np.random.randint(-2, 3)
            drift_y = np.random.randint(-2, 3)
            x += drift_x
            y += drift_y
            cv2.circle(overlay, (x, y), r, color, -1, cv2.LINE_AA)
            alpha = max(life / 15.0, 0.15)
            img[:] = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
            alive.append([x, y, r, life - 1, color])
    return alive

def draw_glow_line(img, p1, p2, color, thickness):
    glow_layers = [thickness + 18, thickness + 12, thickness + 6]
    for t in glow_layers:
        cv2.line(img, p1, p2, color, t, cv2.LINE_AA)
    cv2.line(img, p1, p2, (255, 255, 255), max(2, thickness // 2), cv2.LINE_AA)

def draw_hud(frame):
    overlay = frame.copy()

    # Top futuristic panel
    cv2.rectangle(overlay, (0, 0), (w, toolbar_height), (20, 20, 20), -1)

    # Semi-transparent overlay
    frame[:] = cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)

    # Outer glowing line
    cv2.line(frame, (0, toolbar_height), (w, toolbar_height), (255, 255, 0), 2)

    # Decorative HUD lines
    cv2.line(frame, (0, 20), (150, 20), (255, 255, 0), 1)
    cv2.line(frame, (w-150, 20), (w, 20), (255, 255, 0), 1)
    cv2.line(frame, (0, 80), (120, 80), (0, 255, 255), 1)
    cv2.line(frame, (w-120, 80), (w, 80), (0, 255, 255), 1)

    # Title
    cv2.putText(frame, "JARVIS GESTURE HUD", (w//2 - 180, 35),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 0), 2, cv2.LINE_AA)

    # Status panel
    cv2.putText(frame, f"MODE: {mode}", (20, 92),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, f"BRUSH: {brush_thickness}", (w - 220, 92),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)

    # Buttons
    for btn in buttons:
        x1, x2 = btn["x1"], btn["x2"]
        color = btn["color"]

        # Neon frame
        cv2.rectangle(frame, (x1, 45), (x2, 85), color, 2)
        cv2.rectangle(frame, (x1+2, 47), (x2-2, 83), color, 1)

        # Button text
        text_size = cv2.getTextSize(btn["name"], cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = x1 + ((x2 - x1) - text_size[0]) // 2
        cv2.putText(frame, btn["name"], (text_x, 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

def process_toolbar_click(x, y):
    global draw_color, mode, canvas, brush_thickness

    if y > 45 and y < 85:
        for btn in buttons:
            if btn["x1"] < x < btn["x2"]:
                if btn["name"] == "CYAN":
                    draw_color = (255, 255, 0)
                    mode = "DRAW"
                elif btn["name"] == "BLUE":
                    draw_color = (255, 100, 0)
                    mode = "DRAW"
                elif btn["name"] == "PINK":
                    draw_color = (255, 0, 255)
                    mode = "DRAW"
                elif btn["name"] == "GREEN":
                    draw_color = (0, 255, 100)
                    mode = "DRAW"
                elif btn["name"] == "ERASE":
                    mode = "ERASE"
                elif btn["name"] == "CLEAR":
                    canvas[:] = 0
                elif btn["name"] == "SAVE":
                    filename = f"ironman_canvas_{int(time.time())}.png"
                    cv2.imwrite(filename, output)
                    print(f"[SAVED] {filename}")

def draw_energy_ring(frame, x, y, color=(255, 255, 0)):
    cv2.circle(frame, (x, y), 20, color, 2, cv2.LINE_AA)
    cv2.circle(frame, (x, y), 30, color, 1, cv2.LINE_AA)
    cv2.line(frame, (x-25, y), (x+25, y), color, 1, cv2.LINE_AA)
    cv2.line(frame, (x, y-25), (x, y+25), color, 1, cv2.LINE_AA)

# =========================
# MAIN LOOP
# =========================
prev_point = None

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    lm_list = []
    index_finger = None
    middle_finger = None

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                px, py = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, px, py))

    if lm_list:
        fingers = fingers_up(lm_list)

        index_finger = (lm_list[8][1], lm_list[8][2])
        middle_finger = (lm_list[12][1], lm_list[12][2])

        # =====================
        # SELECTION MODE
        # =====================
        if fingers[0] == 1 and fingers[1] == 1:
            prev_point = None
            trail.appendleft(None)
            mode_display = "SELECT"

            # Selection indicator
            cv2.rectangle(frame,
                          (index_finger[0], index_finger[1]-25),
                          (middle_finger[0], middle_finger[1]+25),
                          (0, 255, 255), 2)

            draw_energy_ring(frame, index_finger[0], index_finger[1], (0, 255, 255))

            if time.time() - last_click_time > click_delay:
                if index_finger[1] < toolbar_height:
                    process_toolbar_click(index_finger[0], index_finger[1])
                    last_click_time = time.time()

        # =====================
        # DRAW MODE
        # =====================
        elif fingers[0] == 1 and fingers[1] == 0:
            trail.appendleft(index_finger)
            draw_energy_ring(frame, index_finger[0], index_finger[1], draw_color)

            if prev_point is None:
                prev_point = index_finger

            if mode == "DRAW":
                draw_glow_line(canvas, prev_point, index_finger, draw_color, brush_thickness)
                add_particle(index_finger[0], index_finger[1], draw_color)

            elif mode == "ERASE":
                cv2.line(canvas, prev_point, index_finger, (0, 0, 0), eraser_thickness, cv2.LINE_AA)

            prev_point = index_finger

        else:
            prev_point = None
            trail.appendleft(None)
    else:
        prev_point = None
        trail.appendleft(None)

    # =========================
    # VISUAL EFFECTS
    # =========================
    blurred = cv2.GaussianBlur(canvas, (0, 0), sigmaX=12, sigmaY=12)
    combined_canvas = cv2.addWeighted(canvas, 0.85, blurred, 0.9, 0)

    output = cv2.addWeighted(frame, 0.75, combined_canvas, 1.0, 0)

    # Particles
    particles = update_particles(output)

    # HUD
    draw_hud(output)

    # Crosshair center effect
    cv2.circle(output, (w//2, h//2), 30, (255, 255, 0), 1, cv2.LINE_AA)
    cv2.circle(output, (w//2, h//2), 5, (0, 255, 255), -1, cv2.LINE_AA)

    # Bottom instructions
    cv2.putText(output, "INDEX = DRAW | INDEX + MIDDLE = SELECT | +/- = BRUSH | ESC = EXIT",
                (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("IRON MAN MAGIC AIR CANVAS", output)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == ord('+') or key == ord('='):
        brush_thickness = min(30, brush_thickness + 2)
    elif key == ord('-'):
        brush_thickness = max(2, brush_thickness - 2)
    elif key == ord('c'):
        canvas[:] = 0
    elif key == ord('s'):
        filename = f"ironman_canvas_{int(time.time())}.png"
        cv2.imwrite(filename, output)
        print(f"[SAVED] {filename}")

cap.release()
cv2.destroyAllWindows()