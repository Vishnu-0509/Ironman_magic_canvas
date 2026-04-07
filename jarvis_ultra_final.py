import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random
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

# MediaPipe Hands
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
eraser_thickness = 60
mode = "DRAW"
brush_mode = "NORMAL"   # NORMAL, LIGHTNING, FIRE, PORTAL
trail = deque(maxlen=25)
particles = []

toolbar_height = 100
last_click_time = 0
click_delay = 0.45
prev_point = None
t = 0

buttons = [
    {"name": "CYAN",  "x1": 20,  "x2": 120, "color": (255, 255, 0)},
    {"name": "BLUE",  "x1": 140, "x2": 240, "color": (255, 100, 0)},
    {"name": "PINK",  "x1": 260, "x2": 360, "color": (255, 0, 255)},
    {"name": "GREEN", "x1": 380, "x2": 480, "color": (0, 255, 100)},
    {"name": "CLEAR", "x1": 520, "x2": 640, "color": (0, 140, 255)},
    {"name": "SAVE",  "x1": 670, "x2": 790, "color": (0, 255, 255)},
]

# =========================
# HELPERS
# =========================
def fingers_up(lm_list):
    """
    Returns [index, middle, ring, pinky]
    1 = up, 0 = down
    """
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    fingers = []
    for tip, pip in zip(tips, pips):
        fingers.append(1 if lm_list[tip][2] < lm_list[pip][2] else 0)
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
    for tt in glow_layers:
        cv2.line(img, p1, p2, color, tt, cv2.LINE_AA)
    cv2.line(img, p1, p2, (255, 255, 255), max(2, thickness // 2), cv2.LINE_AA)

def draw_lightning(canvas, p1, p2, color):
    x1, y1 = p1
    x2, y2 = p2
    segments = 6
    points = [p1]
    for i in range(1, segments):
        frac = i / segments
        x = int(x1 + (x2 - x1) * frac + random.randint(-10, 10))
        y = int(y1 + (y2 - y1) * frac + random.randint(-10, 10))
        points.append((x, y))
    points.append(p2)
    for i in range(len(points)-1):
        cv2.line(canvas, points[i], points[i+1], color, 2, cv2.LINE_AA)

def draw_fire(canvas, x, y):
    for _ in range(5):
        radius = random.randint(5, 15)
        color = (0, random.randint(100, 255), 255)
        cv2.circle(canvas, (x, y), radius, color, -1, cv2.LINE_AA)

def draw_portal(canvas, x, y, t):
    for i in range(20):
        angle = math.radians(i * 18 + t * 100)
        r = 40 + random.randint(-5, 5)
        px = int(x + r * math.cos(angle))
        py = int(y + r * math.sin(angle))
        cv2.circle(canvas, (px, py), 2, (0, 140, 255), -1)

def draw_arc_reactor(frame, cx, cy, t):
    for i in range(3):
        radius = 40 + i * 15 + int(5 * math.sin(t + i))
        cv2.circle(frame, (cx, cy), radius, (255, 255, 0), 1, cv2.LINE_AA)
    for angle in range(0, 360, 45):
        a = math.radians(angle + t * 50)
        x = int(cx + 60 * math.cos(a))
        y = int(cy + 60 * math.sin(a))
        cv2.line(frame, (cx, cy), (x, y), (0, 255, 255), 1, cv2.LINE_AA)

def draw_cursor(frame, x, y, color):
    cv2.circle(frame, (x, y), 15, color, 2)
    cv2.circle(frame, (x, y), 3, color, -1)
    cv2.line(frame, (x-20, y), (x+20, y), color, 1)
    cv2.line(frame, (x, y-20), (x, y+20), color, 1)

def draw_side_panels(frame):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 120), (180, h-50), (20, 20, 20), -1)
    cv2.rectangle(overlay, (w-200, 120), (w, h-50), (20, 20, 20), -1)
    frame[:] = cv2.addWeighted(overlay, 0.45, frame, 0.55, 0)

    cv2.putText(frame, "SYSTEM", (25, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    cv2.putText(frame, "TRACKING: ON", (25, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 1)
    cv2.putText(frame, "CAMERA: ACTIVE", (25, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 1)
    cv2.putText(frame, "HUD: ONLINE", (25, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 1)

    cv2.putText(frame, "TOOLS", (w-165, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    cv2.putText(frame, f"MODE: {mode}", (w-185, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,255), 1)
    cv2.putText(frame, f"BRUSH: {brush_mode}", (w-185, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,255), 1)
    cv2.putText(frame, f"SIZE: {brush_thickness}", (w-185, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,255), 1)

def draw_hud(frame):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, toolbar_height), (20, 20, 20), -1)
    frame[:] = cv2.addWeighted(overlay, 0.55, frame, 0.45, 0)

    cv2.line(frame, (0, toolbar_height), (w, toolbar_height), (255, 255, 0), 2)
    cv2.line(frame, (0, 20), (150, 20), (255, 255, 0), 1)
    cv2.line(frame, (w-150, 20), (w, 20), (255, 255, 0), 1)

    cv2.putText(frame, "JARVIS ULTRA HUD", (w//2 - 170, 35),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 0), 2)

    cv2.putText(frame, f"ACTIVE MODE: {mode}", (20, 92),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    for btn in buttons:
        x1, x2 = btn["x1"], btn["x2"]
        color = btn["color"]
        cv2.rectangle(frame, (x1, 45), (x2, 85), color, 2)
        cv2.rectangle(frame, (x1+2, 47), (x2-2, 83), color, 1)
        text_size = cv2.getTextSize(btn["name"], cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = x1 + ((x2 - x1) - text_size[0]) // 2
        cv2.putText(frame, btn["name"], (text_x, 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def process_toolbar_click(x, y, current_output):
    global draw_color, mode, canvas
    if 45 < y < 85:
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
                elif btn["name"] == "CLEAR":
                    canvas[:] = 0
                elif btn["name"] == "SAVE":
                    filename = f"jarvis_ultra_{int(time.time())}.png"
                    cv2.imwrite(filename, current_output)
                    print(f"[SAVED] {filename}")

# =========================
# MAIN LOOP
# =========================
while True:
    success, frame = cap.read()
    if not success:
        break

    t += 0.05
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    lm_list = []
    index_finger = None
    middle_finger = None

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            for idx, lm in enumerate(handLms.landmark):
                px, py = int(lm.x * w), int(lm.y * h)
                lm_list.append((idx, px, py))

    if lm_list:
        fingers = fingers_up(lm_list)
        index_finger = (lm_list[8][1], lm_list[8][2])
        middle_finger = (lm_list[12][1], lm_list[12][2])

        # Palm detection = all 4 fingers up
        is_palm = (sum(fingers) == 4)

        # =====================
        # SELECTION MODE ✌
        # =====================
        if fingers[0] == 1 and fingers[1] == 1 and not is_palm:
            prev_point = None
            trail.appendleft(None)

            cv2.rectangle(frame,
                          (index_finger[0], index_finger[1]-25),
                          (middle_finger[0], middle_finger[1]+25),
                          (0, 255, 255), 2)

            cv2.putText(frame, "SELECT MODE", (index_finger[0]-50, index_finger[1]-40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

            if time.time() - last_click_time > click_delay:
                if index_finger[1] < toolbar_height:
                    temp_output = frame.copy()
                    process_toolbar_click(index_finger[0], index_finger[1], temp_output)
                    last_click_time = time.time()

        # =====================
        # PALM ERASE MODE ✋
        # =====================
        elif is_palm:
            trail.appendleft(index_finger)

            cv2.circle(frame, index_finger, 45, (0, 0, 255), 2)
            cv2.circle(frame, index_finger, 25, (0, 0, 255), 1)
            cv2.putText(frame, "ERASE MODE", (index_finger[0]-60, index_finger[1]-55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

            if prev_point is None:
                prev_point = index_finger

            cv2.line(canvas, prev_point, index_finger, (0, 0, 0), eraser_thickness, cv2.LINE_AA)
            prev_point = index_finger

        # =====================
        # DRAW MODE ☝
        # =====================
        elif fingers[0] == 1 and fingers[1] == 0:
            trail.appendleft(index_finger)

            if prev_point is None:
                prev_point = index_finger

            if mode == "DRAW":
                if brush_mode == "NORMAL":
                    draw_glow_line(canvas, prev_point, index_finger, draw_color, brush_thickness)
                    add_particle(index_finger[0], index_finger[1], draw_color)

                elif brush_mode == "LIGHTNING":
                    draw_lightning(canvas, prev_point, index_finger, (255, 255, 0))

                elif brush_mode == "FIRE":
                    draw_fire(canvas, index_finger[0], index_finger[1])

                elif brush_mode == "PORTAL":
                    draw_portal(canvas, index_finger[0], index_finger[1], t)

            prev_point = index_finger

        else:
            prev_point = None
            trail.appendleft(None)
    else:
        prev_point = None
        trail.appendleft(None)

    # =========================
    # VISUAL LAYERS
    # =========================
    blurred = cv2.GaussianBlur(canvas, (0, 0), sigmaX=12, sigmaY=12)
    combined_canvas = cv2.addWeighted(canvas, 0.85, blurred, 0.9, 0)
    output = cv2.addWeighted(frame, 0.75, combined_canvas, 1.0, 0)

    # FX overlays
    draw_arc_reactor(output, w//2, h//2, t)
    draw_side_panels(output)
    draw_hud(output)

    if index_finger:
        draw_cursor(output, index_finger[0], index_finger[1], draw_color)

    particles = update_particles(output)

    # Bottom instructions
    cv2.putText(output,
                "INDEX=DRAW | INDEX+MIDDLE=SELECT | PALM=ERASE | 1/2/3/4=BRUSH | +/- SIZE | ESC EXIT",
                (20, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    cv2.imshow("JARVIS ULTRA - GESTURE HOLOGRAPHIC INTERFACE", output)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == ord('1'):
        brush_mode = "NORMAL"
    elif key == ord('2'):
        brush_mode = "LIGHTNING"
    elif key == ord('3'):
        brush_mode = "FIRE"
    elif key == ord('4'):
        brush_mode = "PORTAL"
    elif key == ord('+') or key == ord('='):
        brush_thickness = min(30, brush_thickness + 2)
    elif key == ord('-'):
        brush_thickness = max(2, brush_thickness - 2)
    elif key == ord('c'):
        canvas[:] = 0
    elif key == ord('s'):
        filename = f"jarvis_ultra_{int(time.time())}.png"
        cv2.imwrite(filename, output)
        print(f"[SAVED] {filename}")

cap.release()
cv2.destroyAllWindows()